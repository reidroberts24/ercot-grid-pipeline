# ERCOT Grid Pipeline

A streaming and batch data pipeline on public Texas power-grid data, built on the open-source core of Netflix's data stack: Kafka, Spark, Iceberg, and Trino, with dbt for modeling and Airflow for orchestration. Everything runs locally in Docker Compose for $0.

This is a portfolio and learning project. Its purpose is to build hands-on depth in streaming and distributed processing, and to produce something defensible in data engineering interviews.

**The spec is the source of truth:** `docs/ercot-portfolio-project.md`. Read it before starting any task. It covers the architecture, data model, the hard parts, the week-by-week build plan, and the stack.

## Current phase

**Week 4: the thin slice.** See the build plan in the spec. Update this line as each week finishes, and tick the checkboxes in the spec as items are completed.

## Scope rules

Past side projects stalled from scope creep and from building platform before product. These rules exist to prevent that.

- **Build only what the current week's plan calls for.** If a task would pull in work from a later week, say so and ask before doing it.
- **Thin slice before widening.** One day of data flowing end to end beats a perfect ingestion layer with nothing downstream.
- **No new tools or services** beyond the stack table in the spec without asking first.
- **The out-of-scope list in the spec is binding:** no ML or forecasting, no custom web front end, no cloud deployment, no Terraform or Kubernetes.
- **Week 8 is write-up, then stop.** Stretch goals start only after the README is done.

## Working style

- **I'm learning these tools.** When you introduce a Spark, Kafka, Iceberg, Trino, or dbt concept for the first time, explain briefly why it works that way, not just what to type. Keep explanations short.
- **Prefer the simplest working version first,** then improve it. Name the tradeoff when you choose one approach over another.
- **When something is an interview-worthy decision** (anything in the spec's hard parts table), write a short decision record in `docs/decisions/` as part of the work: the problem, the options, what we chose, and why.
- **Measure before optimizing.** Record query times and file counts before and after any partitioning, sorting, or compaction change in `docs/benchmarks.md`.

## Project memory

Project skills in `.claude/skills/` keep the docs current as work happens. When a correction, decision, out-of-scope idea, finished task, or new concept comes up, use the matching skill. Every skill proposes its change with a short synopsis and waits for approval before writing.

| Skill | When | Maintains |
| --- | --- | --- |
| `capture-lesson` | I correct you, or you notice a mistake | `CLAUDE.md` rules, `docs/lessons.md` |
| `record-decision` | A key technical choice is settled | `docs/decisions/` (use instead of `/adr` here) |
| `park-idea` | An idea is out of scope for the current week | `docs/backlog.md` |
| `plan-and-progress` | Planning, "what's next", finishing work, closing a week | `docs/weeks/`, spec checkboxes, Current phase line |
| `learning-notes` | A stack concept comes up for the first time | `docs/learning/<tool>/` |
| `wrap-session` | End of a work session | Sweeps all of the above, suggests a commit |

## Data conventions

- **All timestamps are stored in UTC.** Convert to Central time only in `dim_date` and the marts.
- **Raw tables stay as close to the source as possible.** Business logic belongs in dbt, not in ingestion.
- **Every load is idempotent.** Reruns and restarts must never create gaps or duplicates.
- **Every dbt model states its grain** in its description.
- **Extreme prices are real.** Tests must not reject negative prices or large spikes.

## Repo layout (planned)

Create these as the work needs them, not up front.

```
docker-compose.yml     The local stack
.env                   Secrets and config (never committed; see .env.example)
ingestion/             Kafka producer and API clients
spark/jobs/            Batch jobs: backfills, daily loads, maintenance
spark/streaming/       Structured Streaming jobs
dbt/                   dbt project (dbt-trino)
airflow/dags/          Orchestration
docs/                  Spec, decision records, benchmarks
  decisions/           Decision records + README index
  weeks/               Task breakdown and retro per week
  learning/            Interview-prep notes by tool
  lessons.md           Technical lessons learned
  backlog.md           Deferred ideas
.claude/skills/        Project-memory skills (see above)
```

## Environment notes

- The full stack wants about 16GB of RAM. Run only the services the current week needs: Kafka can stay off until week 6, and Airflow and Superset until week 7.
- The ERCOT API token expires hourly and can't be refreshed. Credentials live in `.env` only.
- Do the day-1 integration check from the spec first: write an Iceberg table from Spark and read it from Trino.

## Commands

Fill this in as commands come to exist (starting the stack, running a job, running dbt, running tests).

## Git

- Commit after each working step, with short messages like `spark: batch load one day of hub prices` or `dbt: add stg_rt_prices`.
- Never commit `.env`, credentials, data files, Spark checkpoints, or MinIO volumes.
- No AI attribution in commits or PRs: no "Co-Authored-By: Claude", "Generated with Claude Code", or similar lines. Commits are authored as me. Why: this is a portfolio repo, and the history should read as my own work.
