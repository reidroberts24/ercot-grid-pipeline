# 002. Fetch from the ERCOT API in plain Python; Spark only reads landed files

- **Status:** Accepted
- **Date:** 2026-10-23
- **Hard part:** Two ways in (live stream and bulk archives), partly. Also touches the rate-limit and token row.

## Problem
The spec's week 4 item says to "pull one day of prices from the API and write them to a raw Iceberg table with a Spark batch job." Calling the API is awkward inside Spark: login produces a one-hour token that can't be refreshed, ERCOT allows only 30 requests per minute, and Spark is built to run work in parallel across executors that each have their own process. We had to decide where the HTTP calls happen and what gets handed to Spark.

## Options considered
1. **Call the API from inside Spark** (in the driver, or as tasks spread across executors). Pros: one job does everything. Cons: login and rate limiting would have to be coordinated across executors, a failed load means calling ERCOT again, and Spark adds nothing to a handful of small HTTP requests.
2. **Plain Python fetch that lands raw responses as files; a Spark job parses the files into Iceberg.** Pros: auth and throttling live in one simple process, the raw files are a replayable record, and Spark does what it's good at, parsing and writing tables. Cons: two steps to run and orchestrate, and an extra copy of the data.
3. **Python fetch that writes straight into Iceberg** (for example with PyIceberg). Pros: one step, no landing files. Cons: adds a library outside the stack, gives up replayability, and moves table writes out of Spark, where the rest of the pipeline does them.

## Decision
`ingestion/fetch_rt_prices.py` calls the API and saves each response unchanged to `data/raw/ercot/np6-905-cd/delivery_date=<date>/<type>.json`. Then `spark/jobs/load_rt_prices.py` reads those files into `iceberg.raw.rt_prices`, replacing the day atomically. For the thin slice, raw files land on the local disk, mounted read-only into the Spark container.

## Why
It separates the two concerns that fail differently. API problems (expired tokens, 429s, outages) stay in a small Python process that's easy to retry. Table problems (schema, types, rerun safety) stay in Spark, and can be replayed from the landed files as often as needed without touching ERCOT's rate limit. It's also the same shape as the week 5 backfill, where ERCOT's archive files are downloaded first and then processed by Spark. Tradeoff accepted: two steps instead of one, which Airflow will chain in week 7.

## Consequences
- Any Spark load can be rerun or fixed without calling ERCOT again.
- The landing folder is a second copy of the data. It's tiny for prices, and it becomes an S3 landing bucket later (backlog).
- The streaming path (week 6) doesn't use landing files: the producer publishes to Kafka, and Spark Structured Streaming reads from there.
- At 10x scale: land in S3 with lifecycle rules, record each landed file in the ingestion manifest (week 5), and trigger Spark loads from new files rather than from a date argument.

## How I'd explain it in an interview
ERCOT's API has a 30-requests-per-minute limit and one-hour tokens, which don't fit Spark's model of many parallel workers. So I split ingestion in two: a small Python fetcher that handles login and throttling and lands the raw responses unchanged, and a Spark job that parses those files into Iceberg. That separates "the API is having a bad day" from "the table load has a bug," and it means I can replay any load from the raw files without calling ERCOT again. It's the same land-then-process pattern I use for the bulk historical archives.

## Related
- `ingestion/ercot_client.py`, `ingestion/fetch_rt_prices.py`, `spark/jobs/load_rt_prices.py`
- Backlog: move landing to an S3 bucket; re-authenticate on token expiry
- `docs/learning/iceberg/snapshots-and-overwrite.md`
