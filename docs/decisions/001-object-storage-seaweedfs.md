# 001. Use SeaweedFS instead of MinIO for local S3-compatible storage

- **Status:** Accepted
- **Date:** 2026-10-22
- **Hard part:** none (stack choice, found during the week 4 day-1 setup)

## Problem
The spec named MinIO as the local stand-in for S3. When the day-1 Docker Compose file was being written, MinIO's official images were gone from Docker Hub and Quay. MinIO stopped publishing official Docker images in October 2025, and the open-source project moved to maintenance-only mode in late 2025: no new features or contributions, with development continuing only in the paid AIStor product. Building it from source or relying on third-party rebuilds would mean learning on a dead-end dependency.

## Options considered
1. **SeaweedFS:** mature, Apache 2.0, runs as a single container with a built-in S3 gateway and a basic web UI. A hands-on comparison (rmoff.net, Jan 2026) tested it writing Iceberg tables through a REST catalog, the same setup as ours, and it worked as a plain image swap. Con: development leans heavily on one main maintainer.
2. **S3Proxy:** the simplest option. Con: no UI, and it depends on a retired library.
3. **RustFS:** MinIO-like and actively developed. Con: still alpha, with a recent security issue.
4. **Garage:** lightweight and well regarded. Con: AGPL license, and it needs extra init and layout configuration before first use.
5. **Zenko CloudServer:** S3-compatible. Con: heavier, and less used for this kind of local setup.
6. **MinIO rebuilds** (Chainguard, Bitnami legacy, the pgsty fork): keep the spec unchanged. Con: they all rebuild a project that is no longer developed upstream.
7. **No object store:** a shared Docker volume with a `file://` warehouse. The simplest option. Con: we'd lose the experience of configuring Spark and Trino against an S3 API, and the path to AWS would no longer be a straight swap.

## Decision
SeaweedFS (`chrislusf/seaweedfs`) runs as one container with its S3 gateway enabled. All tables live in a `warehouse` bucket, which Spark, Trino and the Iceberg REST catalog reach through the S3 API with path-style access.

## Why
Spark, Trino and the REST catalog only talk to the S3 API, so any S3-compatible store works. Changing stores means changing the endpoint, credentials and path-style setting, not the pipeline code, so the "moves to real S3 on AWS unchanged" story still holds. Among the maintained S3-compatible stores, SeaweedFS has the best balance of maturity, a permissive license and laptop-sized footprint. It also has evidence of working with exactly our Iceberg REST setup. We keep a real S3 API rather than a filesystem warehouse, because S3 configuration (endpoints, credentials, path-style access, regions) is real-world experience this project is meant to build.

## Consequences
- The pipeline code doesn't depend on the storage product. Only the Compose file and the S3 settings in each engine do.
- We accept the single-maintainer risk because this is a local development stand-in; production would use real S3.
- SeaweedFS's S3 gateway is less widely used than MinIO's, so some S3 behaviors may differ. **Fallback:** if SeaweedFS's S3 auth or path-style access blocks the day-1 check after a reasonable attempt, switch to S3Proxy, and nothing else without revisiting this decision.
- At 10x scale, this would be real S3 (or GCS/ADLS) with IAM roles instead of static keys.

## How I'd explain it in an interview
I planned to use MinIO as a local S3, but it stopped shipping open-source images partway through 2025. Because Spark, Trino and the Iceberg catalog only speak the S3 API, storage was a swappable component. I compared five or six S3-compatible options on maturity, license and footprint, and picked SeaweedFS, with S3Proxy as a fallback if it caused problems. Swapping it in only changed the endpoint and credentials, not the pipeline, which is the same property that lets the design move to AWS unchanged.

## Related
- `docker-compose.yml`
- Spec: Stack and setup, "The day-1 integration check"
