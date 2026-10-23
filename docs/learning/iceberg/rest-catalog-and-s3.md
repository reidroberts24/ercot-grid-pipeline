# Iceberg REST catalog and S3 storage

**Tool:** Iceberg (with Spark and Trino) · **First used:** week 4, `docker-compose.yml`

## What it is
An Iceberg table is a set of files in object storage: data files (Parquet), manifests that list them, and a metadata JSON file that describes the table's schema, partitioning and snapshots. The **catalog** stores one thing per table: a pointer to its current metadata file. The REST catalog serves that pointer over a standard HTTP API.

## Why it works this way
- **Engines can share tables.** Engines never talk to each other. Spark and Trino each ask the catalog "where is `smoke.day1_check`?", get the metadata file location, then read the files from S3 directly.
- **Commits are atomic.** A write adds new files, then asks the catalog to swap the pointer from the old metadata file to the new one. If two writers race, only one swap succeeds and the other retries. Readers always see a complete snapshot, never a half-written one.
- **The REST protocol is engine-neutral.** Any catalog that speaks it (Polaris, Nessie, Glue, Lakekeeper) is a drop-in replacement, and that's what moving to AWS changes: the catalog, not the pipeline.

## How this project uses it
- `rest` service: `apache/iceberg-rest-fixture`, with its backing database on the `catalog-data` volume.
- Warehouse: `s3://warehouse/` on SeaweedFS.
- Both engines name the catalog `iceberg` (`spark/conf/spark-defaults.conf`, `trino/catalog/iceberg.properties`), so the same SQL works in either.
- Every component needs the same four S3 settings:

| Setting | Value | Why |
| --- | --- | --- |
| Endpoint | `http://seaweedfs:8333` | Otherwise the AWS SDK goes to real Amazon |
| Credentials | `S3_*` in `.env` → `AWS_*` in containers | Requests are signed with this key pair |
| Path-style access | `true` | No DNS for `warehouse.seaweedfs`, so the bucket goes in the URL path |
| Region | `us-east-1` | The SDK requires one, even though SeaweedFS ignores it |

## Gotchas
- **The catalog fixture keeps its database in `/tmp` by default.** Recreating the container forgets every table, while the data files stay orphaned in S3. Fix: point `CATALOG_URI` at a file on a volume.
- **Trino's JVM takes 80% of the memory it can see.** Without `mem_limit`, it would claim most of Docker's 12GB.
- **The Spark image's default catalog is named `demo` and points at `minio:9000`.** We mount our own `spark-defaults.conf` over it.
- **Trino needs explicit S3 credentials.** Its native S3 client doesn't read the AWS environment variables on its own, so they're filled in with `${ENV:...}`.

## Interview questions
- **Q:** What does an Iceberg catalog actually store?
  **A:** Just a pointer per table to the current metadata file. Schema, partitions, snapshots and file lists all live in files in object storage. That's why the catalog stays tiny and engines can share tables.
- **Q:** How does Iceberg give atomic commits on S3, which has no transactions?
  **A:** Writers create new immutable files, then do one atomic compare-and-swap of the catalog pointer. A failed swap means someone else committed first, so the writer retries on top of the new snapshot.
- **Q:** How would this setup change on AWS?
  **A:** SeaweedFS becomes S3 with IAM roles instead of static keys, and the REST catalog becomes Glue or Polaris. The pipeline code is unchanged, because it only depends on the catalog API and S3 paths.

## Further reading
- https://iceberg.apache.org/spec/
- https://iceberg.apache.org/docs/latest/spark-quickstart/
- https://trino.io/docs/current/connector/iceberg.html
