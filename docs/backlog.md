# Backlog

Ideas deferred from the active week. `plan-and-progress` pulls them into a week's plan and removes them from here.

## Later in the build plan

### Week 5
- **Land raw API files in an S3 landing bucket instead of local `data/`.** Write the fetch output to a SeaweedFS bucket and have Spark read it from there, so the landing zone works like production and survives a laptop reset. *Why deferred:* local files were the simplest version for the thin slice (decision 002). *Fits:* week 5, alongside the archive backfill and the ingestion manifest. *Added:* 2026-10-23
- **Partition `raw.rt_prices` by day before any compaction runs.** The load job's `overwrite(delivery_date = day)` only works while each data file holds a single day. Compaction can merge days into one file, and then the overwrite fails. Day partitioning guarantees files never mix days. *Why deferred:* week 5 benchmarks partitioning before and after, so the table stays unpartitioned until then. *Fits:* week 5, "Partition and sort the cleaned tables", and it must land before week 7's nightly compaction. *Added:* 2026-10-23

### Week 6
- **Re-authenticate when the ERCOT token expires.** The client logs in once per process, which is fine for a batch fetch that finishes in seconds. The long-running producer needs to cache the token, log in again shortly before the hour is up, and retry once on a 401. *Why deferred:* nothing runs longer than an hour until the producer exists. *Fits:* week 6, "write the producer: ... handle token expiry and 429s". *Added:* 2026-10-23

### Week 7

### Week 8

## Stretch (after week 8, pick one)

## Out of scope (binding until job landed)

## Unsorted
