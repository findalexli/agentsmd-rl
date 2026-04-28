"""Behavior tests for effect-ts/effect#6065.

Each `def test_*` is a single check executed via pytest; test.sh writes reward
from pytest's exit code to /logs/verifier/reward.txt.
"""
from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/effect")
RPC = REPO / "packages" / "rpc"


def _run_vitest(test_path_rel: str, timeout: int = 600):
    return subprocess.run(
        ["pnpm", "vitest", "run", test_path_rel, "--reporter=basic"],
        cwd=str(RPC),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _run_oracle(name: str, src: str):
    """Write src to packages/rpc/test/<name>, run vitest, then delete it."""
    path = RPC / "test" / name
    path.write_text(src)
    try:
        return _run_vitest(f"test/{name}")
    finally:
        path.unlink(missing_ok=True)


def test_defect_option_threads_to_defect_schema_property():
    """Behavior: Rpc.make({defect: X}) sets rpc.defectSchema = X (fail-to-pass)."""
    src = textwrap.dedent('''\
        import { Rpc } from "@effect/rpc"
        import { assert, describe, it } from "@effect/vitest"
        import { Schema } from "effect"

        describe("oracle:defectSchema-prop", () => {
          it("threads custom defect option to rpc.defectSchema", () => {
            const customSchema = Schema.Unknown
            const rpc: any = Rpc.make("oracleHasDefectSchema", { defect: customSchema })
            assert.strictEqual(rpc.defectSchema, customSchema)
          })
        })
    ''')
    r = _run_oracle("_oracle_defect_prop.test.ts", src)
    assert r.returncode == 0, (
        f"Expected pass but got rc={r.returncode}.\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-1000:]}"
    )


def test_default_rpc_has_default_defect_schema():
    """Behavior: Rpc.make() without `defect` option still populates defectSchema."""
    src = textwrap.dedent('''\
        import { Rpc } from "@effect/rpc"
        import { assert, describe, it } from "@effect/vitest"
        import { Schema } from "effect"

        describe("oracle:defectSchema-default", () => {
          it("default Rpc.make populates a defectSchema", () => {
            const rpc: any = Rpc.make("oracleDefaultDefect", { success: Schema.String })
            assert.isTrue(rpc.defectSchema !== undefined && rpc.defectSchema !== null)
          })
        })
    ''')
    r = _run_oracle("_oracle_defect_default.test.ts", src)
    assert r.returncode == 0, (
        f"Expected pass but got rc={r.returncode}.\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-1000:]}"
    )


def test_exit_schema_uses_custom_defect_for_round_trip():
    """Behavior: exitSchema uses rpc.defectSchema, so a Schema.Unknown defect round-trips
    a plain object identically (Schema.Defect would coerce it through Error semantics)."""
    src = textwrap.dedent('''\
        import { Rpc } from "@effect/rpc"
        import { assert, describe, it } from "@effect/vitest"
        import { Cause, Exit, Schema } from "effect"

        describe("oracle:exitSchema-roundtrip", () => {
          it("preserves full defect object when defect is Schema.Unknown", () => {
            const rpc = Rpc.make("oracleRoundTrip", {
              success: Schema.String,
              defect: Schema.Unknown
            })
            const schema = Rpc.exitSchema(rpc)
            const encode = Schema.encodeSync(schema)
            const decode = Schema.decodeSync(schema)
            const original = { code: 99, detail: "ohno", deep: { x: 1 } }
            const exit = Exit.die(original)
            const roundTripped = decode(encode(exit))
            assert.isTrue(Exit.isFailure(roundTripped))
            const defect = Cause.squash((roundTripped as any).cause)
            assert.deepStrictEqual(defect, original)
          })
        })
    ''')
    r = _run_oracle("_oracle_exitschema.test.ts", src)
    assert r.returncode == 0, (
        f"Expected pass but got rc={r.returncode}.\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-1000:]}"
    )


def test_repo_existing_rpc_tests_still_pass():
    """Pass-to-pass: the repo's existing Rpc.test.ts continues to pass."""
    r = _run_vitest("test/Rpc.test.ts")
    assert r.returncode == 0, (
        f"Existing Rpc tests regressed (rc={r.returncode}).\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-1000:]}"
    )


def test_repo_typecheck_passes():
    """Pass-to-pass: pnpm check (project-wide tsc) passes after agent's changes."""
    r = subprocess.run(
        ["pnpm", "check"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert r.returncode == 0, (
        f"pnpm check failed (rc={r.returncode}).\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-1000:]}"
    )


def test_repo_lint_passes():
    """Pass-to-pass: pnpm lint passes after agent's changes (zero-tolerance per AGENTS.md)."""
    r = subprocess.run(
        ["pnpm", "lint"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"pnpm lint failed (rc={r.returncode}).\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-1000:]}"
    )


def test_changeset_added_for_rpc():
    """Agent-config rule (AGENTS.md): all PRs must include a changeset under .changeset/."""
    changeset_dir = REPO / ".changeset"
    pre_existing = {"shiny-bottles-tap.md"}
    new_changesets = [
        p for p in changeset_dir.glob("*.md")
        if p.name.lower() != "readme.md" and p.name not in pre_existing
    ]
    assert new_changesets, (
        "AGENTS.md requires every PR to add a changeset file under .changeset/. "
        f"Existing files in .changeset/: {[p.name for p in changeset_dir.glob('*.md')]}"
    )
    text = "\n".join(p.read_text() for p in new_changesets)
    assert "@effect/rpc" in text, (
        "Changeset must reference the @effect/rpc package (the package being modified). "
        f"Got:\n{text[:500]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_pnpm():
    """pass_to_pass | CI job 'Build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm docgen'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

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

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_exitSchema_uses_custom_defect_schema():
    """fail_to_pass | PR added test 'exitSchema uses custom defect schema' in 'packages/rpc/test/Rpc.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/rpc/test/Rpc.test.ts" -t "exitSchema uses custom defect schema" 2>&1 || npx vitest run "packages/rpc/test/Rpc.test.ts" -t "exitSchema uses custom defect schema" 2>&1 || pnpm jest "packages/rpc/test/Rpc.test.ts" -t "exitSchema uses custom defect schema" 2>&1 || npx jest "packages/rpc/test/Rpc.test.ts" -t "exitSchema uses custom defect schema" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'exitSchema uses custom defect schema' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
