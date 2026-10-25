# dbt project structure: dbt_project.yml and profiles.yml

**Tool:** dbt Core (dbt-trino adapter) · **First used:** week 4, `dbt/dbt_project.yml`

## What it is
`dbt_project.yml` is the file that makes a folder a dbt project. dbt looks for it
in the current directory on every command, and it says which connection profile to
use, where each kind of file lives, and how models are built by default.
`profiles.yml` holds the connection itself.

## Why it works this way
- **Project vs. connection are split on purpose.** `dbt_project.yml` describes the
  project and is the same for everyone. `profiles.yml` holds hosts and credentials,
  which differ per person and per environment (dev, prod). The project only names a
  profile (`profile: 'ercot'`); dbt looks that name up in `profiles.yml`.
- **Folders carry config.** The `models:` block mirrors the folder tree, so a whole
  layer (staging, marts) gets one consistent setting instead of one per file. The
  `+` prefix marks a config setting rather than a folder name.
- **Config cascades from general to specific:**
  `dbt_project.yml` (per folder) → the model's `.yml` → `{{ config(...) }}` in the
  `.sql`. The most specific one wins.

## What `dbt run` does
1. Reads `dbt_project.yml`, which gives the profile name and file paths.
2. Reads `profiles.yml`, which gives the Trino connection.
3. Scans `models/` and builds a dependency graph from every `ref()` and `source()`.
4. Works out each model's config (materialization, schema).
5. Compiles Jinja to plain SQL in `target/`, e.g.
   `{{ source('ercot','rt_prices') }}` → `"iceberg"."raw"."rt_prices"`, wrapped in
   `CREATE VIEW ... AS`.
6. Sends the SQL to Trino in dependency order. Trino does the compute; dbt only
   compiles and orchestrates.

## How this project uses it
- Project `ercot` at `dbt/`; run dbt from inside that folder.
- `profiles.yml` lives in the repo, not `~/.dbt/`, because local Trino has no auth
  and no secrets. dbt (1.3+) checks the current directory for `profiles.yml` before
  `~/.dbt/`, so running from `dbt/` needs no flag; `--profiles-dir` is only for
  running from elsewhere.
- Profile: `database: iceberg` = the Trino catalog, `schema: staging` = the Iceberg
  namespace dbt builds into.
- `models/staging/` → `+materialized: view`. Planned for week 7: marts as tables,
  `snapshots/` for the Type 2 `dim_settlement_point`.

## Gotchas
- `dbt init` without `--skip-profile-setup` appends a profile to
  `~/.dbt/profiles.yml` filled with placeholders like `[database name]`. YAML reads
  `[...]` as a list, so `dbt debug` fails with "is not of type 'string'".
- `dbt init <name>` creates a folder named after the project, and the project
  name can't be `dbt`. We created `ercot/` and moved its contents into `dbt/`.
- "Connection refused" on `localhost:8080` means Trino isn't running, not a bad
  profile. `docker compose up -d` and wait about 30s.

## Interview questions
- **Q:** Why are `dbt_project.yml` and `profiles.yml` separate files?
  **A:** One describes the project and is shared; the other holds environment-specific
  connections and credentials. The same project runs against dev or prod by switching
  the target, without editing code, and secrets stay out of the repo.
- **Q:** How do you make all marts tables but staging views?
  **A:** Folder-level config in `dbt_project.yml` (`staging: +materialized: view`,
  `marts: +materialized: table`). Override a single model with `{{ config() }}`.
- **Q:** Does dbt process data?
  **A:** No. It compiles SQL and runs it in dependency order on the warehouse engine.
  Here Trino does the work, reading and writing Iceberg tables in SeaweedFS.

## Further reading
- https://docs.getdbt.com/reference/dbt_project.yml
- https://docs.getdbt.com/docs/core/connect-data-platform/trino-setup
