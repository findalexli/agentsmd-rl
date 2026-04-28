"""Tests for the @effect/sql-sqlite-bun prepare-error-as-failure fix.

The bug: in the SqliteClient `run` and `runValues` helpers, `db.query(sql)`
(prepare) and `statement.safeIntegers(...)` were OUTSIDE the try/catch. When
they threw (e.g., `SELECT * FROM non_existent_table`), the exception escaped
`Effect.withFiberRuntime`'s synchronous body and surfaced as a fiber **defect**
(uncatchable by `Effect.catchAll`).

The fix: move both lines inside the try block so prepare errors are wrapped in
`SqlError` and surface as catchable failures.

Test strategy: run a Bun script that triggers a prepare error and check whether
the resulting Effect failure is a typed failure (catchable) or a defect.
"""

from __future__ import annotations

import json
import os
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/effect")
PKG = REPO / "packages" / "sql-sqlite-bun"

# A scratchpad inside the repo so workspace resolution works (`bun` will pick up
# the workspace `node_modules` symlinks automatically).
SCRATCHPAD = REPO / "scratchpad"
SCRATCHPAD.mkdir(exist_ok=True)


def _write_bun_script(name: str, body: str) -> Path:
    p = SCRATCHPAD / name
    p.write_text(textwrap.dedent(body).lstrip("\n"))
    return p


# ---------------------------------------------------------------------------
# fail-to-pass: behavioral tests for the bug fix
# ---------------------------------------------------------------------------

PROBE_SCRIPT = """
    import { Reactivity } from "@effect/experimental"
    import { SqliteClient } from "@effect/sql-sqlite-bun"
    import { Cause, Effect, Exit } from "effect"

    const program = Effect.gen(function*() {
      const sql = yield* SqliteClient.make({ filename: ":memory:" })
      yield* sql`SELECT * FROM non_existent_table`
    }).pipe(
      Effect.scoped,
      Effect.provide(Reactivity.layer)
    )

    const exit = await Effect.runPromiseExit(program)

    const out: Record<string, unknown> = {}
    if (Exit.isSuccess(exit)) {
      out.kind = "success"
    } else {
      const cause = exit.cause
      const failOpt = Cause.failureOption(cause)
      const dieOpt = Cause.dieOption(cause)
      out.kind = "failure"
      out.has_typed_failure = failOpt._tag === "Some"
      out.has_defect = dieOpt._tag === "Some"
      if (failOpt._tag === "Some") {
        const e: any = failOpt.value
        out.failure_tag = (e && (e._tag ?? e.constructor?.name)) ?? null
        out.failure_message = String(e?.message ?? "")
      }
      if (dieOpt._tag === "Some") {
        const e: any = dieOpt.value
        out.defect_message = String(e?.message ?? e)
      }
    }
    process.stdout.write(JSON.stringify(out))
"""


def _run_probe() -> dict:
    script = _write_bun_script("probe_prepare_error.ts", PROBE_SCRIPT)
    r = subprocess.run(
        ["bun", "run", str(script)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # The probe writes JSON to stdout. Bun may print other diagnostics on stderr;
    # we ignore those. Parse the LAST line that looks like a JSON object.
    stdout = r.stdout.strip()
    if not stdout:
        raise AssertionError(
            f"Bun probe produced no stdout.\n"
            f"returncode={r.returncode}\nstderr:\n{r.stderr[-2000:]}"
        )
    # The script ends with a single JSON write, so the whole stdout is JSON
    # (last line, in case Bun prepends warnings).
    last = stdout.splitlines()[-1].strip()
    try:
        return json.loads(last)
    except json.JSONDecodeError as e:
        raise AssertionError(
            f"Could not parse probe output as JSON: {e}\n"
            f"stdout:\n{r.stdout[-2000:]}\nstderr:\n{r.stderr[-2000:]}"
        )


def test_prepare_error_surfaces_as_typed_failure():
    """Querying a non-existent table must yield a catchable typed failure
    (not a defect). This is the primary fail-to-pass behavioral check."""
    result = _run_probe()
    assert result["kind"] == "failure", (
        f"Expected the program to fail, got: {result}"
    )
    assert result.get("has_typed_failure") is True, (
        "Prepare error must surface as a typed Cause.Fail (catchable with "
        "Effect.catchAll) — found defect-only cause instead. "
        f"Probe result: {result}"
    )


def test_prepare_error_is_not_a_defect():
    """The cause must not contain a Cause.Die — defects are uncatchable."""
    result = _run_probe()
    assert result["kind"] == "failure", (
        f"Expected the program to fail, got: {result}"
    )
    assert result.get("has_defect") is False, (
        "Prepare error leaked through as a defect (Cause.Die). It must be "
        "wrapped in SqlError and surface as a typed failure instead. "
        f"Probe result: {result}"
    )


def test_prepare_error_is_sql_error():
    """The typed failure must be a SqlError (the package's documented error
    type), not some random thrown Error."""
    result = _run_probe()
    assert result["kind"] == "failure"
    assert result.get("has_typed_failure") is True
    tag = result.get("failure_tag")
    # SqlError has _tag === "SqlError" in @effect/sql.
    assert tag == "SqlError", (
        f"Failure must be a SqlError, got tag={tag!r}. Probe result: {result}"
    )


# Same probe but for the `runValues` path (the equivalent bug existed in both
# `run` and `runValues`). Use `executeValues` via the raw connection or just a
# different SQL shape that exercises `.values()`. The Sql client routes most
# queries through `.all()` (run), so to be safe we exercise the same prepare
# path with a syntax error too — that also goes through db.query() and must be
# catchable.
SYNTAX_PROBE_SCRIPT = """
    import { Reactivity } from "@effect/experimental"
    import { SqliteClient } from "@effect/sql-sqlite-bun"
    import { Cause, Effect, Exit } from "effect"

    const program = Effect.gen(function*() {
      const sql = yield* SqliteClient.make({ filename: ":memory:" })
      // Syntax error → fails at db.query(sql) prepare time.
      yield* sql`THIS IS NOT VALID SQL`
    }).pipe(
      Effect.scoped,
      Effect.provide(Reactivity.layer)
    )

    const exit = await Effect.runPromiseExit(program)
    const out: Record<string, unknown> = {}
    if (Exit.isSuccess(exit)) {
      out.kind = "success"
    } else {
      const cause = exit.cause
      const failOpt = Cause.failureOption(cause)
      const dieOpt = Cause.dieOption(cause)
      out.kind = "failure"
      out.has_typed_failure = failOpt._tag === "Some"
      out.has_defect = dieOpt._tag === "Some"
    }
    process.stdout.write(JSON.stringify(out))
"""


def test_syntax_error_also_catchable():
    """Syntax errors hit the same db.query() prepare path and must also
    surface as a typed failure rather than a defect."""
    script = _write_bun_script("probe_syntax_error.ts", SYNTAX_PROBE_SCRIPT)
    r = subprocess.run(
        ["bun", "run", str(script)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    stdout = r.stdout.strip()
    assert stdout, (
        f"Bun probe produced no stdout. rc={r.returncode}\nstderr:\n{r.stderr[-2000:]}"
    )
    result = json.loads(stdout.splitlines()[-1])
    assert result["kind"] == "failure", f"Expected failure, got {result}"
    assert result.get("has_typed_failure") is True, (
        f"Syntax error must yield a typed failure, got {result}"
    )
    assert result.get("has_defect") is False, (
        f"Syntax error must not surface as a defect, got {result}"
    )


def test_subsequent_query_after_prepare_failure_works():
    """After a prepare-error is properly wrapped (caught by `Effect.catchAll`),
    the SqliteClient must still be usable for subsequent valid queries.
    Before the fix, the defect would tear down the fiber and you couldn't
    catch-and-continue."""
    body = """
        import { Reactivity } from "@effect/experimental"
        import { SqliteClient } from "@effect/sql-sqlite-bun"
        import { Effect } from "effect"

        const program = Effect.gen(function*() {
          const sql = yield* SqliteClient.make({ filename: ":memory:" })
          // Fail-then-recover-then-succeed.
          const recovered = yield* sql`SELECT * FROM non_existent_table`.pipe(
            Effect.catchAll(() => Effect.succeed("recovered"))
          )
          const ok = yield* sql`SELECT 1 AS one`
          return { recovered, ok }
        }).pipe(
          Effect.scoped,
          Effect.provide(Reactivity.layer)
        )

        const result = await Effect.runPromise(program)
        process.stdout.write(JSON.stringify(result))
    """
    script = _write_bun_script("probe_recover_continue.ts", body)
    r = subprocess.run(
        ["bun", "run", str(script)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"Recover-and-continue program failed (rc={r.returncode}). "
        f"This means the prepare error wasn't catchable. "
        f"stderr:\n{r.stderr[-2000:]}\nstdout:\n{r.stdout[-1000:]}"
    )
    result = json.loads(r.stdout.strip().splitlines()[-1])
    assert result["recovered"] == "recovered", (
        f"Expected 'recovered' from catchAll, got {result}"
    )
    assert result["ok"] == [{"one": 1}], (
        f"Expected subsequent valid query to return [{{'one': 1}}], got {result}"
    )


# ---------------------------------------------------------------------------
# pass-to-pass: repo CI commands that should keep passing
# ---------------------------------------------------------------------------


def test_typescript_typecheck_sqlite_bun():
    """The TypeScript typechecker (used by the repo's own CI as `pnpm check`)
    must still succeed on the sql-sqlite-bun package after the fix."""
    r = subprocess.run(
        ["pnpm", "exec", "tsc", "-b", "tsconfig.json"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"TypeScript typecheck failed (rc={r.returncode}).\n"
        f"stdout:\n{r.stdout[-2000:]}\nstderr:\n{r.stderr[-2000:]}"
    )


def test_repo_existing_vitest_runs():
    """The package's existing vitest suite (a stub at base) must keep passing."""
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "true"},
    )
    assert r.returncode == 0, (
        f"vitest failed (rc={r.returncode}).\n"
        f"stdout:\n{r.stdout[-2000:]}\nstderr:\n{r.stderr[-2000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_lint_pnpm():
    """pass_to_pass | CI job 'Lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm circular'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_pnpm_2():
    """pass_to_pass | CI job 'Lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_pnpm_3():
    """pass_to_pass | CI job 'Lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm codegen'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_pnpm():
    """pass_to_pass | CI job 'Build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm docgen'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")