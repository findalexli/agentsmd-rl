# Replicate `trigger_source`, `root_trigger_source`, and `is_warm_start` to ClickHouse

The repository at `/workspace/trigger.dev` is the [trigger.dev](https://github.com/triggerdotdev/trigger.dev) monorepo. Analytics for task runs are written to a ClickHouse table named **`trigger_dev.task_runs_v2`**, and the TypeScript side of that table lives in `internal-packages/clickhouse/`.

## What's wrong today

Three pieces of information that the platform already knows about a TaskRun never reach ClickHouse:

1. **`trigger_source`** — a string identifying *how* the run was triggered. It is already extracted as part of the `annotations.triggerSource` field stored on each `TaskRun` in Postgres (whose Zod schema is `RunAnnotations` exported from the `@trigger.dev/core/v3` subpath). Possible values include `"sdk"`, `"api"`, `"dashboard"`, `"cli"`, `"mcp"`, `"schedule"`, plus any other string.
2. **`root_trigger_source`** — the same idea but for the **root** run of a chain (`annotations.rootTriggerSource`).
3. **`is_warm_start`** — a boolean that says whether the latest attempt of this run was a warm start. This information is *not yet captured anywhere*. It needs to be added to the Postgres `TaskRun` row at attempt-start time (the engine code already has a local `isWarmStart` value when it transitions a run into the `EXECUTING` status), and replicated to ClickHouse.

The analytics consumers (the dashboard's run list, billing, and the run-region report) need all three columns to be queryable. Today they cannot be queried because they do not exist.

## What you need to deliver

A change that lets a row inserted into `trigger_dev.task_runs_v2` carry these three new columns end-to-end. Concretely:

### ClickHouse schema

A new Goose-format migration under `internal-packages/clickhouse/schema/` that adds three columns to `trigger_dev.task_runs_v2`:

| Column | ClickHouse type |
| --- | --- |
| `trigger_source` | `LowCardinality(String)` (default `''`) |
| `root_trigger_source` | `LowCardinality(String)` (default `''`) |
| `is_warm_start` | `Nullable(UInt8)` (default `NULL`) |

The migration must include both `-- +goose Up` and `-- +goose Down` sections so the migration is reversible. Use the existing numeric-prefix naming convention in `schema/`.

### TypeScript schema (`internal-packages/clickhouse/src/taskRuns.ts`)

This file declares four parallel structures that **must stay in lockstep**:

* `TaskRunV2` — a `z.object({...})` Zod schema
* `TASK_RUN_COLUMNS` — a `const` tuple of column names whose order *must match the ClickHouse table*
* `TaskRunFieldTypes` — a TypeScript object type mapping each column name to its TS type
* `TaskRunInsertArray` — a positional tuple type used by callers when inserting

When you add the three new columns, extend all four. The Zod field types are:

* `trigger_source: z.string().default("")`
* `root_trigger_source: z.string().default("")`
* `is_warm_start: z.boolean().nullish()`

(equivalently: empty-string default for the two source columns, nullable boolean for warm-start.)

### Postgres `TaskRun` model

* Add a new optional boolean field `isWarmStart Boolean?` to `model TaskRun` in `internal-packages/database/prisma/schema.prisma`.
* Add a corresponding Prisma migration directory under `internal-packages/database/prisma/migrations/` (any descriptive name) containing a `migration.sql` whose body issues:

  ```sql
  ALTER TABLE "public"."TaskRun" ADD COLUMN "isWarmStart" BOOLEAN;
  ```

### Populating `isWarmStart`

The run engine flips a run into the `EXECUTING` state once per attempt-start in `internal-packages/run-engine/src/engine/systems/runAttemptSystem.ts`. The local `isWarmStart` value is already known at that point; thread it into the existing Prisma update so the column is populated at attempt start (default to `false` when no warm-start was performed). Do not introduce a second write — reuse the update that already runs.

### Replicating into ClickHouse

The webapp's `RunsReplicationService` in `apps/webapp/app/services/runsReplicationService.server.ts` builds the positional row written to ClickHouse for each replicated TaskRun. Extend the row builder so the three new columns are populated:

* `trigger_source` — from `annotations.triggerSource` of the run (using the `RunAnnotations` Zod schema's safe-parse output; fall back to the empty string when annotations are missing or invalid).
* `root_trigger_source` — from `annotations.rootTriggerSource`, same fallback.
* `is_warm_start` — directly from the new `isWarmStart` column (fall back to `null`).

Do not import the `RunAnnotations` schema from the package root; use the subpath export documented for `@trigger.dev/core`.

## Acceptance signals

* Parsing a row with `TaskRunV2.parse({...})` retains the three new fields in the parsed output.
* `TASK_RUN_COLUMNS` lists the three new column names.
* The new ClickHouse migration adds the columns on `trigger_dev.task_runs_v2` with the types above.
* `model TaskRun` in `schema.prisma` declares the new `isWarmStart Boolean?` field, and a Prisma migration applies the corresponding `ALTER TABLE`.

## Constraints

* No new dependencies. Use the existing `zod` and `@trigger.dev/core/v3` exports.
* `RunAnnotations.safeParse(...)` is the canonical way to read the `annotations` JSON; do not access fields off the raw value.
* Per the ClickHouse package's conventions, migrations live under `internal-packages/clickhouse/schema/` in Goose format with numeric-prefix file names.
* Per the database package's conventions, every Postgres schema change is paired with a Prisma migration directory; do not edit `schema.prisma` without one.
