# Iceberg snapshots and overwrite

**Tool:** Iceberg (written from Spark, inspected from Trino) · **First used:** week 4, `spark/jobs/load_rt_prices.py`

## What it is
Every successful write to an Iceberg table creates a new **snapshot**: an immutable, complete list of the data files that make up the table at that moment. A commit never edits files in place. It writes new files, builds a new snapshot that adds or removes file references, and swaps the catalog pointer to it in one atomic step.

## Why it works this way
Object storage like S3 has no transactions and no in-place edits, so Iceberg gets atomicity from immutability. Readers always open one specific snapshot, so they see the table either entirely before or entirely after a commit, never halfway through. Old snapshots stay around until they're expired, which is what makes time travel and rollback possible.

## How this project uses it
`load_rt_prices.py` writes with:

```python
df.writeTo("iceberg.raw.rt_prices").overwrite(F.col("delivery_date") == F.lit(day))
```

This deletes the day's existing rows and adds the new ones **in one snapshot**. Alternatives we rejected:

| Write mode | What a rerun does | Problem |
| --- | --- | --- |
| `.append()` | Adds the day again | Duplicates on every rerun |
| `DELETE` then `.append()` | Two commits | A crash in between leaves the day missing |
| `.overwritePartitions()` | Replaces whole partitions | Needs a partitioned table (week 5) |
| `.overwrite(condition)` | Delete and add in one commit | Each data file must match the condition entirely (see gotchas) |

Inspect the history from Trino:

```sql
SELECT committed_at, operation,
       element_at(summary, 'deleted-records') AS deleted,
       element_at(summary, 'added-records')   AS added,
       element_at(summary, 'total-records')   AS total
FROM iceberg.raw."rt_prices$snapshots"
ORDER BY committed_at;
```

On 2026-10-23 this showed 4 `overwrite` snapshots. The reruns of 2026-10-15 each deleted 2,112 rows and added 2,112, and loading 2026-10-16 added 2,112 without deleting anything.

## Gotchas
- **Overwrite by condition deletes whole files only.** Iceberg removes data files whose rows all match the condition. If a file mixes days, the overwrite fails rather than rewriting part of the file. It works today because each load writes files containing one day only. Compaction could merge days, so day partitioning has to come first (backlog, week 5).
- **The first commit is an `overwrite`, not an `append`.** The job always overwrites, even into an empty table, so the first snapshot deletes nothing.
- **Missing summary keys.** Snapshot `summary` keys like `deleted-records` only exist when they apply. Use `element_at(summary, 'key')`, which returns NULL, instead of `summary['key']`, which errors.
- **`DROP TABLE` vs. `DROP TABLE ... PURGE`.** Without `PURGE`, the catalog entry goes away but the data files stay in S3.

## Interview questions
- **Q:** How do you make a daily batch load idempotent on Iceberg?
  **A:** Replace the day in a single commit with an overwrite by condition, or by partition once the table is partitioned. Reruns then delete and re-add the same day atomically. In our load, the snapshot history shows the same number of records deleted and added on each rerun.
- **Q:** What is an Iceberg snapshot, and what does it enable?
  **A:** An immutable list of the table's data files at a commit, made current by an atomic catalog pointer swap. It gives readers consistent views, and enables time travel (`FOR VERSION AS OF`), rollback after a bad load, and incremental reads between snapshots.
- **Q:** Why not delete then insert?
  **A:** That's two commits. A failure between them leaves the table missing that day's data, and readers can see the gap. A single overwrite commit is atomic.

## Further reading
- https://iceberg.apache.org/docs/latest/spark-writes/#overwriting-data
- https://iceberg.apache.org/docs/latest/spark-queries/#inspecting-tables
- https://trino.io/docs/current/connector/iceberg.html#metadata-tables
