"""Behavior tests for effect-ts/effect#6086.

Each `def test_*` here maps 1:1 to a `check` entry in eval_manifest.yaml.
Tests are run inside the Docker image, with the repo at /workspace/effect.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO = Path("/workspace/effect")
EFFECT_PKG = REPO / "packages" / "effect"
PROBE_TEST = EFFECT_PKG / "test" / "Schema" / "SchemaAST" / "probe.test.ts"


def _run_vitest(test_path: str, name_filter: str | None = None, timeout: int = 600) -> tuple[int, str, str]:
    """Run a single vitest file from the effect package, optionally filtering by test name."""
    cmd = ["pnpm", "vitest", "run", test_path, "--reporter=default", "--no-color"]
    if name_filter:
        cmd.extend(["-t", name_filter])
    proc = subprocess.run(
        cmd,
        cwd=str(EFFECT_PKG),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout, proc.stderr


def test_probe_test_file_present():
    """test.sh should have copied the probe behavior test into the repo."""
    assert PROBE_TEST.is_file(), f"probe test missing at {PROBE_TEST}"


def test_behavior_optionalwith_default():
    """getPropertySignatures must not crash on Struct with optionalWith({ default: ... })."""
    rc, out, err = _run_vitest(
        "test/Schema/SchemaAST/probe.test.ts",
        name_filter="handles optionalWith default",
    )
    combined = out + err
    assert rc == 0, (
        f"Probe test for optionalWith default failed.\n"
        f"--- stdout ---\n{out[-2000:]}\n--- stderr ---\n{err[-2000:]}"
    )
    assert "Unsupported schema (Transformation)" not in combined, (
        "Underlying bug ('Unsupported schema (Transformation)') still surfaces:\n"
        + combined[-2000:]
    )


def test_behavior_optionalwith_as_option():
    """getPropertySignatures must not crash on Struct with optionalWith({ as: 'Option' })."""
    rc, out, err = _run_vitest(
        "test/Schema/SchemaAST/probe.test.ts",
        name_filter="handles optionalWith as Option",
    )
    combined = out + err
    assert rc == 0, (
        f"Probe test for optionalWith as Option failed.\n"
        f"--- stdout ---\n{out[-2000:]}\n--- stderr ---\n{err[-2000:]}"
    )
    assert "Unsupported schema (Transformation)" not in combined


def test_behavior_optionalwith_nullable():
    """getPropertySignatures must not crash on Struct with optionalWith({ nullable: true, default: ... })."""
    rc, out, err = _run_vitest(
        "test/Schema/SchemaAST/probe.test.ts",
        name_filter="handles optionalWith nullable",
    )
    combined = out + err
    assert rc == 0, (
        f"Probe test for optionalWith nullable failed.\n"
        f"--- stdout ---\n{out[-2000:]}\n--- stderr ---\n{err[-2000:]}"
    )
    assert "Unsupported schema (Transformation)" not in combined


def test_behavior_single_key_struct():
    """Single-key Transformation Struct should also work."""
    rc, out, err = _run_vitest(
        "test/Schema/SchemaAST/probe.test.ts",
        name_filter="handles a single-key Transformation Struct",
    )
    assert rc == 0, (
        f"Probe test for single-key Transformation Struct failed.\n"
        f"--- stdout ---\n{out[-2000:]}\n--- stderr ---\n{err[-2000:]}"
    )


def test_behavior_no_regression_plain_struct():
    """Plain Struct (no Transformation) must still work — no regression."""
    rc, out, err = _run_vitest(
        "test/Schema/SchemaAST/probe.test.ts",
        name_filter="does NOT regress non-Transformation Struct",
    )
    assert rc == 0, (
        f"Plain Struct regression detected.\n"
        f"--- stdout ---\n{out[-2000:]}\n--- stderr ---\n{err[-2000:]}"
    )


def test_existing_getpropertysignatures_suite_passes():
    """Pre-existing getPropertySignatures.test.ts must still pass (pass-to-pass)."""
    rc, out, err = _run_vitest("test/Schema/SchemaAST/getPropertySignatures.test.ts")
    assert rc == 0, (
        f"Existing getPropertySignatures test suite regressed.\n"
        f"--- stdout ---\n{out[-2000:]}\n--- stderr ---\n{err[-2000:]}"
    )


def test_typecheck_passes():
    """`tsc -b tsconfig.json` (the repo's `pnpm check`) must succeed at the package level."""
    proc = subprocess.run(
        ["pnpm", "check"],
        cwd=str(EFFECT_PKG),
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert proc.returncode == 0, (
        f"`pnpm check` failed.\n"
        f"--- stdout ---\n{proc.stdout[-2000:]}\n"
        f"--- stderr ---\n{proc.stderr[-2000:]}"
    )


def test_changeset_present():
    """AGENTS.md mandates a changeset entry in `.changeset/` for every PR."""
    changeset_dir = REPO / ".changeset"
    assert changeset_dir.is_dir(), f".changeset directory missing at {changeset_dir}"
    md_files = [
        p
        for p in changeset_dir.glob("*.md")
        if p.name.lower() not in {"readme.md"}
    ]
    assert md_files, (
        ".changeset/ has no changeset markdown files; AGENTS.md requires one per PR."
    )
    has_relevant = False
    for p in md_files:
        text = p.read_text(encoding="utf-8", errors="replace")
        head = text.lstrip()
        if not head.startswith("---"):
            continue
        try:
            front_end = head.index("---", 3)
        except ValueError:
            continue
        front = head[3:front_end]
        if 'effect' not in front and "'effect'" not in front and "effect:" not in front:
            continue
        body = head[front_end + 3:].lower()
        if "getpropertysignatures" in body or "transformation" in body or "optionalwith" in body:
            has_relevant = True
            break
    assert has_relevant, (
        "No changeset describes this fix. Expected a `.changeset/*.md` entry "
        "with `\"effect\": patch` (or similar) frontmatter mentioning the "
        "fix to getPropertySignatures / Transformation / optionalWith."
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

def test_ci_lint_check_for_codegen_changes():
    """pass_to_pass | CI job 'Lint' → step 'Check for codegen changes'"""
    r = subprocess.run(
        ["bash", "-lc", 'git diff --exit-code'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check for codegen changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_pnpm():
    """pass_to_pass | CI job 'Build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm docgen'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_Transformation_Struct_with_optionalWith_default():
    """fail_to_pass | PR added test 'Transformation (Struct with optionalWith default)' in 'packages/effect/test/Schema/SchemaAST/getPropertySignatures.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/effect/test/Schema/SchemaAST/getPropertySignatures.test.ts" -t "Transformation (Struct with optionalWith default)" 2>&1 || npx vitest run "packages/effect/test/Schema/SchemaAST/getPropertySignatures.test.ts" -t "Transformation (Struct with optionalWith default)" 2>&1 || pnpm jest "packages/effect/test/Schema/SchemaAST/getPropertySignatures.test.ts" -t "Transformation (Struct with optionalWith default)" 2>&1 || npx jest "packages/effect/test/Schema/SchemaAST/getPropertySignatures.test.ts" -t "Transformation (Struct with optionalWith default)" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'Transformation (Struct with optionalWith default)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_Transformation_Struct_with_optionalWith_as_Optio():
    """fail_to_pass | PR added test 'Transformation (Struct with optionalWith as Option)' in 'packages/effect/test/Schema/SchemaAST/getPropertySignatures.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/effect/test/Schema/SchemaAST/getPropertySignatures.test.ts" -t "Transformation (Struct with optionalWith as Option)" 2>&1 || npx vitest run "packages/effect/test/Schema/SchemaAST/getPropertySignatures.test.ts" -t "Transformation (Struct with optionalWith as Option)" 2>&1 || pnpm jest "packages/effect/test/Schema/SchemaAST/getPropertySignatures.test.ts" -t "Transformation (Struct with optionalWith as Option)" 2>&1 || npx jest "packages/effect/test/Schema/SchemaAST/getPropertySignatures.test.ts" -t "Transformation (Struct with optionalWith as Option)" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'Transformation (Struct with optionalWith as Option)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
