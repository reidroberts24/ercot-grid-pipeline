# Week 4: the thin slice

**Goal:** one day of hub and load-zone prices flowing from the ERCOT API into a raw Iceberg table, modeled by one dbt model, queried in Trino.

## Spec item: Bring up the core stack and do the day-1 check

- [x] **Compose file: SeaweedFS, Iceberg REST catalog, Spark, Trino**, starting from the Iceberg Spark quickstart, with MinIO swapped for SeaweedFS (decision 001) and Trino added. *Done when:* all containers are up and the warehouse bucket exists. *Teaches:* the REST catalog keeps track of where each table's metadata lives, so any engine can find the same tables in object storage.
- [x] **Point Trino's Iceberg connector at the REST catalog and SeaweedFS.** *Done when:* `SHOW SCHEMAS FROM iceberg` returns in the Trino CLI. *Teaches:* Trino catalogs and connector properties (S3 endpoint, path-style access).
- [x] **Day-1 check: write a table from Spark, read it from Trino.** *Done when:* a few rows inserted from PySpark return the same `count(*)` in Trino. *Teaches:* an Iceberg table is just metadata and data files in storage; the catalog only stores a pointer to the current metadata file. *Verified 2026-10-22:* Spark wrote 3 rows to `iceberg.smoke.day1_check`, Trino read the same 3, and they survived `docker compose down` / `up`.

## Spec item: Pull one day of hub and load-zone prices into a raw Iceberg table

- [x] **ERCOT API client: authenticate and fetch one day of real-time prices** (`ingestion/`). Get a token using the credentials in `.env` and save the raw API response. Pick a day with no DST change. *Done when:* the file holds one day of 15-minute intervals for every hub and load zone. *Teaches:* token-based API auth, rate limits (30 requests/min). *Verified 2026-10-22:* 2026-10-15 returned 2,112 rows; every point in HU, AH, LZ, LZEW has 96 intervals.
- [x] **Spark batch job: raw file → `raw.rt_prices`** (`spark/jobs/`). Keep the source columns as-is and add a load timestamp. Reruns overwrite that day's data instead of appending. *Done when:* the Trino row count equals the file's row count, and is still the same after a second run. *Teaches:* DataFrame reads/writes, Iceberg writes from Spark, overwrite vs. append. *Verified 2026-10-23:* 2,112 rows for 2026-10-15 (96 intervals per point, no failed casts); a rerun replaced the day (2,112 deleted, 2,112 added); loading 2026-10-16 and rerunning 10-15 left 4,224 rows with 10-16 untouched.

## Spec item: Build one dbt model on top through Trino

- [ ] **dbt project on `dbt-trino`** (`dbt/`), with a profile and a source definition for `raw.rt_prices`. *Done when:* `dbt debug` passes. *Teaches:* dbt sources, profiles, and adapters.
- [ ] **`stg_rt_prices` model + a thin-slice query.** Use a UTC timestamp and clean column names, and state the grain in the description. *Done when:* `dbt run` succeeds and a Trino query returns the average price per hub by hour for the day. *Teaches:* dbt models and materializations, and how dbt compiles SQL and runs it on Trino.

## Retro
<!-- filled in at week close -->
