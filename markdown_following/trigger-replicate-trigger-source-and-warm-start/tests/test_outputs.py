"""
test_outputs.py — verifier for trigger.dev PR #3274.

PR #3274 ("feat: replicate trigger_source, root_trigger_source, and
is_warm_start to ClickHouse") adds three new columns to the analytics
ClickHouse table `trigger_dev.task_runs_v2` and a backing nullable
boolean `isWarmStart` field on the Postgres `TaskRun` table. The TS
side of this is a Zod schema (`TaskRunV2`) and a column-name array
(`TASK_RUN_COLUMNS`) that must each be extended.

Strategy:
- We exercise the actual Zod schema and column array at runtime by
  bundling `internal-packages/clickhouse/src/taskRuns.ts` with esbuild
  and require()-ing the bundle from a small Node introspection script.
  This is behavioral, not text grepping — Zod's parser actively strips
  unknown fields, so on the base commit the new fields disappear from
  the parsed output, and on the fix they survive.
- We also verify the SQL migrations and Prisma schema contain the
  expected DDL — these files are the substantive deliverable of this
  PR and have no runtime to exercise.
"""

import json
import os
import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/trigger.dev")
HARNESS_NODE_MODULES = "/opt/harness/node_modules"
ESBUILD = f"{HARNESS_NODE_MODULES}/.bin/esbuild"
BUNDLE = "/tmp/taskRuns.bundle.js"

TASK_RUNS_TS = REPO / "internal-packages/clickhouse/src/taskRuns.ts"
CH_SCHEMA_DIR = REPO / "internal-packages/clickhouse/schema"
PG_MIGRATIONS_DIR = REPO / "internal-packages/database/prisma/migrations"
PRISMA_SCHEMA = REPO / "internal-packages/database/prisma/schema.prisma"


_introspection_cache = None


def _bundle_and_introspect():
    """Bundle taskRuns.ts and run a Node script that exercises its exports."""
    assert TASK_RUNS_TS.exists(), f"missing source file {TASK_RUNS_TS}"

    build = subprocess.run(
        [
            ESBUILD,
            str(TASK_RUNS_TS),
            "--bundle",
            "--format=cjs",
            "--platform=node",
            "--external:@clickhouse/client",
            "--external:zod",
            f"--outfile={BUNDLE}",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert build.returncode == 0, (
        f"esbuild bundle failed (rc={build.returncode}):\n"
        f"--- stdout ---\n{build.stdout}\n--- stderr ---\n{build.stderr}"
    )

    introspect_js = r"""
const path = require("path");
const m = require(process.argv[1]);
const fullInput = {
  environment_id: "env_1",
  organization_id: "org_1",
  project_id: "proj_1",
  run_id: "run_1",
  updated_at: 1,
  created_at: 1,
  status: "PENDING",
  environment_type: "DEVELOPMENT",
  friendly_id: "friend_1",
  engine: "V2",
  task_identifier: "task",
  queue: "queue",
  schedule_id: "",
  batch_id: "",
  task_version: "v",
  sdk_version: "v",
  cli_version: "v",
  machine_preset: "small",
  root_run_id: "",
  parent_run_id: "",
  span_id: "",
  trace_id: "",
  idempotency_key: "",
  expiration_ttl: "",
  _version: "1",
  trigger_source: "api",
  root_trigger_source: "dashboard",
  is_warm_start: true,
};
let parsed = null;
let parseError = null;
try {
  parsed = m.TaskRunV2.parse(fullInput);
} catch (e) {
  parseError = String(e && e.message ? e.message : e);
}
const out = {
  columns: m.TASK_RUN_COLUMNS ? [...m.TASK_RUN_COLUMNS] : null,
  exports: Object.keys(m).sort(),
  parsed: parsed,
  parse_error: parseError,
};
process.stdout.write(JSON.stringify(out));
"""
    env = {**os.environ, "NODE_PATH": HARNESS_NODE_MODULES}
    proc = subprocess.run(
        ["node", "-e", introspect_js, BUNDLE],
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )
    assert proc.returncode == 0, (
        f"node introspection failed (rc={proc.returncode}):\n"
        f"--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}"
    )
    return json.loads(proc.stdout)


def _data():
    global _introspection_cache
    if _introspection_cache is None:
        _introspection_cache = _bundle_and_introspect()
    return _introspection_cache


# -------- pass-to-pass: base sanity (these pass on both base and gold) -------

def test_module_exports_schema_and_columns():
    """Bundle exposes the Zod schema and column-name list."""
    data = _data()
    assert "TaskRunV2" in data["exports"], data["exports"]
    assert "TASK_RUN_COLUMNS" in data["exports"], data["exports"]


def test_existing_columns_preserved():
    """Pre-existing required columns must remain in TASK_RUN_COLUMNS."""
    cols = _data()["columns"]
    for required in (
        "environment_id",
        "organization_id",
        "project_id",
        "run_id",
        "task_identifier",
        "worker_queue",
        "max_duration_in_seconds",
        "_version",
        "_is_deleted",
    ):
        assert required in cols, f"required column {required!r} missing from {cols!r}"


def test_zod_schema_validates_existing_required_fields():
    """Zod schema still parses a minimally valid input — existing contract preserved."""
    parsed = _data()["parsed"]
    assert parsed is not None, f"parse failed: {_data()['parse_error']}"
    assert parsed["environment_id"] == "env_1"
    assert parsed["organization_id"] == "org_1"
    assert parsed["task_identifier"] == "task"
    assert parsed["_version"] == "1"


# ---- fail-to-pass: new behavior introduced by PR #3274 ----------------------

def test_task_run_columns_includes_trigger_source():
    """`trigger_source` must be exported from TASK_RUN_COLUMNS."""
    cols = _data()["columns"]
    assert "trigger_source" in cols, (
        f"'trigger_source' missing from TASK_RUN_COLUMNS: {cols!r}"
    )


def test_task_run_columns_includes_root_trigger_source():
    """`root_trigger_source` must be exported from TASK_RUN_COLUMNS."""
    cols = _data()["columns"]
    assert "root_trigger_source" in cols, (
        f"'root_trigger_source' missing from TASK_RUN_COLUMNS: {cols!r}"
    )


def test_task_run_columns_includes_is_warm_start():
    """`is_warm_start` must be exported from TASK_RUN_COLUMNS."""
    cols = _data()["columns"]
    assert "is_warm_start" in cols, (
        f"'is_warm_start' missing from TASK_RUN_COLUMNS: {cols!r}"
    )


def test_zod_schema_accepts_trigger_source():
    """`TaskRunV2.parse({...trigger_source: 'api'})` keeps the field in the output."""
    data = _data()
    assert data["parsed"] is not None, f"parse error: {data['parse_error']}"
    parsed = data["parsed"]
    assert parsed.get("trigger_source") == "api", (
        f"Zod stripped trigger_source; parsed={parsed!r}"
    )


def test_zod_schema_accepts_root_trigger_source():
    """`TaskRunV2.parse({...root_trigger_source: 'dashboard'})` keeps the field."""
    data = _data()
    parsed = data["parsed"]
    assert parsed is not None, f"parse error: {data['parse_error']}"
    assert parsed.get("root_trigger_source") == "dashboard", (
        f"Zod stripped root_trigger_source; parsed={parsed!r}"
    )


def test_zod_schema_accepts_is_warm_start():
    """`TaskRunV2.parse({...is_warm_start: true})` keeps the boolean."""
    data = _data()
    parsed = data["parsed"]
    assert parsed is not None, f"parse error: {data['parse_error']}"
    assert parsed.get("is_warm_start") is True, (
        f"Zod stripped is_warm_start; parsed={parsed!r}"
    )


def test_clickhouse_migration_alters_task_runs_v2():
    """A Goose migration must add the three columns to trigger_dev.task_runs_v2.

    Verified by parsing the SQL with sqlparse and asserting that the
    ADD COLUMN statements name each new column on the correct table.
    """
    import sqlparse

    candidates = []
    for f in CH_SCHEMA_DIR.glob("*.sql"):
        text = f.read_text()
        if "trigger_source" in text and "task_runs_v2" in text:
            candidates.append((f, text))
    assert candidates, (
        f"no Goose migration in {CH_SCHEMA_DIR} adds trigger_source to "
        f"task_runs_v2"
    )

    # Use the migration that explicitly adds all three new columns.
    migration_path, sql = next(
        (
            (p, t)
            for p, t in candidates
            if "trigger_source" in t
            and "root_trigger_source" in t
            and "is_warm_start" in t
        ),
        (None, None),
    )
    assert migration_path is not None, (
        "no single migration adds all three of trigger_source, "
        "root_trigger_source, is_warm_start"
    )

    statements = [s.strip() for s in sqlparse.split(sql) if s.strip()]
    add_column_stmts = [s for s in statements if re.search(r"ADD\s+COLUMN", s, re.I)]
    assert len(add_column_stmts) >= 3, (
        f"expected ≥3 ADD COLUMN statements, got {len(add_column_stmts)}: "
        f"{add_column_stmts!r}"
    )

    # Each new column should appear in an ADD COLUMN on task_runs_v2.
    joined = " \n".join(add_column_stmts)
    for col in ("trigger_source", "root_trigger_source", "is_warm_start"):
        assert re.search(
            rf"ADD\s+COLUMN\s+{col}\b", joined, re.I
        ), f"ADD COLUMN {col} not found in migration {migration_path}"
    assert "task_runs_v2" in sql, (
        f"migration does not target task_runs_v2 table: {migration_path}"
    )


def test_clickhouse_migration_column_types():
    """ClickHouse migration must use the documented column types.

    `trigger_source` and `root_trigger_source` are LowCardinality(String);
    `is_warm_start` is Nullable(UInt8).
    """
    target = None
    for f in CH_SCHEMA_DIR.glob("*.sql"):
        text = f.read_text()
        if all(c in text for c in ("trigger_source", "root_trigger_source", "is_warm_start")):
            target = text
            break
    assert target, "migration with all three new columns not found"

    assert re.search(
        r"trigger_source\s+LowCardinality\(String\)", target, re.I
    ), "trigger_source must be LowCardinality(String)"
    assert re.search(
        r"root_trigger_source\s+LowCardinality\(String\)", target, re.I
    ), "root_trigger_source must be LowCardinality(String)"
    assert re.search(
        r"is_warm_start\s+Nullable\(UInt8\)", target, re.I
    ), "is_warm_start must be Nullable(UInt8)"


def test_postgres_migration_adds_is_warm_start_column():
    """A Prisma migration must ALTER public.TaskRun ADD COLUMN isWarmStart BOOLEAN."""
    assert PG_MIGRATIONS_DIR.exists(), f"missing {PG_MIGRATIONS_DIR}"
    found = False
    for d in PG_MIGRATIONS_DIR.iterdir():
        if not d.is_dir():
            continue
        for sql_file in d.glob("*.sql"):
            text = sql_file.read_text()
            if (
                re.search(r"ALTER\s+TABLE\s+\"?public\"?\.\"TaskRun\"", text, re.I)
                and re.search(r"ADD\s+COLUMN\s+\"isWarmStart\"\s+BOOLEAN", text, re.I)
            ):
                found = True
                break
        if found:
            break
    assert found, (
        "no Prisma migration ALTERs public.TaskRun to ADD COLUMN isWarmStart "
        "BOOLEAN"
    )


def test_prisma_schema_has_is_warm_start_field():
    """The TaskRun model in schema.prisma must declare `isWarmStart Boolean?`."""
    text = PRISMA_SCHEMA.read_text()
    # Locate the `model TaskRun { ... }` block.
    m = re.search(r"model\s+TaskRun\s*\{(.*?)^\}", text, re.DOTALL | re.MULTILINE)
    assert m, "model TaskRun not found in prisma schema"
    body = m.group(1)
    assert re.search(
        r"^\s*isWarmStart\s+Boolean\?\s*$", body, re.MULTILINE
    ), f"isWarmStart Boolean? not declared in TaskRun model body"


def test_prisma_schema_validates():
    """`prisma validate` (the repo's own CI command) accepts the schema.

    This is the same command the repo's `db:migrate` flow runs and is
    therefore a pass-to-pass regression guard from the repo's CI.
    """
    prisma_bin = f"{HARNESS_NODE_MODULES}/.bin/prisma"
    assert Path(prisma_bin).exists(), f"prisma CLI missing at {prisma_bin}"
    env = {
        **os.environ,
        # Prisma reads env at validate time even though it does not connect.
        "DATABASE_URL": "postgresql://placeholder:placeholder@localhost:5432/placeholder",
        "DIRECT_URL": "postgresql://placeholder:placeholder@localhost:5432/placeholder",
    }
    proc = subprocess.run(
        [prisma_bin, "validate", f"--schema={PRISMA_SCHEMA}"],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
        cwd=str(REPO),
    )
    assert proc.returncode == 0, (
        f"prisma validate failed (rc={proc.returncode}):\n"
        f"--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}"
    )


