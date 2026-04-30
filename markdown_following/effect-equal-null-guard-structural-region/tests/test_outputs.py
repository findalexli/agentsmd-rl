"""Tests for effect-ts/effect#6133 — Equal null guard in structuralRegion."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/effect")
EFFECT_PKG = REPO / "packages" / "effect"
PROBE_SRC = Path("/tests/__probe.ts")
PROBE_DST = EFFECT_PKG / "__probe.ts"


def setup_module(module):
    """Copy the probe TS into packages/effect/ so its `import 'effect'` resolves via the workspace alias."""
    if not PROBE_SRC.exists():
        raise RuntimeError(f"missing probe source at {PROBE_SRC}")
    shutil.copy(PROBE_SRC, PROBE_DST)


def teardown_module(module):
    try:
        PROBE_DST.unlink()
    except FileNotFoundError:
        pass


def _run_probe(case: str, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["pnpm", "exec", "tsx", "__probe.ts", case],
        cwd=str(EFFECT_PKG),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ── fail-to-pass: behavior broken at base ────────────────────────────────

def test_null_vs_object_in_structural_region():
    """Equal.equals(null, {a:1}) inside structuralRegion must return false, not throw."""
    r = _run_probe("null_vs_object")
    assert r.returncode == 0, f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"


def test_object_vs_null_in_structural_region():
    """Equal.equals({a:1}, null) inside structuralRegion must return false, not throw."""
    r = _run_probe("object_vs_null")
    assert r.returncode == 0, f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"


def test_null_vs_array_in_structural_region():
    """Equal.equals(null, [1,2,3]) inside structuralRegion must return false, not throw."""
    r = _run_probe("null_vs_array")
    assert r.returncode == 0, f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"


def test_array_vs_null_in_structural_region():
    """Equal.equals([1,2,3], null) inside structuralRegion must return false, not throw."""
    r = _run_probe("array_vs_null")
    assert r.returncode == 0, f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"


def test_object_with_null_field_vs_object_with_object_field():
    """Recursive compare reaching null vs nested object must return false, not throw."""
    r = _run_probe("object_with_null_field_vs_object_with_object_field")
    assert r.returncode == 0, f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"


def test_no_exception_on_null_object_combinations():
    """Calling Equal.equals on (null, object) combinations inside structuralRegion must never throw."""
    r = _run_probe("no_throw_on_pure_null_object_compare")
    assert r.returncode == 0, f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"


# ── pass-to-pass: behavior already correct, must remain correct ──────────

def test_null_vs_null_in_structural_region():
    """Equal.equals(null, null) inside structuralRegion is true."""
    r = _run_probe("null_vs_null")
    assert r.returncode == 0, f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"


def test_null_vs_string_in_structural_region():
    """Equal.equals(null, 'hello') inside structuralRegion is false."""
    r = _run_probe("null_vs_string")
    assert r.returncode == 0, f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"


def test_null_vs_undefined_in_structural_region():
    """Equal.equals(null, undefined) inside structuralRegion is false."""
    r = _run_probe("null_vs_undefined")
    assert r.returncode == 0, f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"


def test_nested_null_equality():
    """Two structurally identical nested objects with null leaves are equal."""
    r = _run_probe("nested_null_equality")
    assert r.returncode == 0, f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"


def test_nested_null_vs_nonnull():
    """Nested objects differing in a null vs non-null leaf are not equal."""
    r = _run_probe("nested_null_vs_nonnull")
    assert r.returncode == 0, f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"


# ── pass-to-pass from repo CI/CD ─────────────────────────────────────────

def test_repo_existing_equal_tests_pass():
    """Repo's existing Equal.test.ts vitest suite passes (run with -t to skip newly-added cases)."""
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "test/Equal.test.ts"],
        cwd=str(REPO / "packages" / "effect"),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"vitest failed:\nstdout:\n{r.stdout[-2000:]}\nstderr:\n{r.stderr[-2000:]}"


def test_repo_eslint_clean_on_equal():
    """Repo's eslint passes on the patched Equal.ts source."""
    r = subprocess.run(
        ["pnpm", "exec", "eslint", "packages/effect/src/Equal.ts"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"eslint failed:\nstdout:\n{r.stdout[-2000:]}\nstderr:\n{r.stderr[-2000:]}"


# ── agent_config: rules from AGENTS.md ───────────────────────────────────

def test_changeset_present_for_fix():
    """AGENTS.md: All pull requests must include a changeset in the .changeset/ directory.

    A changeset .md file (other than the existing pre-PR ones at the base commit) must exist
    bumping the `effect` package.
    """
    pre_existing = {"config.json", "huge-peaches-jump.md"}
    cs_dir = REPO / ".changeset"
    new_cs = [p for p in cs_dir.glob("*.md") if p.name not in pre_existing]
    assert new_cs, (
        "No changeset added. AGENTS.md requires a changeset in .changeset/ for every PR."
    )
    found_effect_bump = False
    for p in new_cs:
        text = p.read_text()
        if '"effect"' in text and ("patch" in text or "minor" in text or "major" in text):
            found_effect_bump = True
            break
    assert found_effect_bump, (
        f"No new changeset bumps the 'effect' package. New changesets seen: {[p.name for p in new_cs]}"
    )


def test_index_barrel_files_unchanged():
    """AGENTS.md: index.ts barrel files are auto-generated and must not be manually edited.

    Verify packages/effect/src/index.ts is byte-for-byte identical to the base commit.
    """
    r = subprocess.run(
        ["git", "diff", "5c80e578bd95e0cf6fceffc72fa0b130ca11ec8e", "--", "packages/effect/src/index.ts"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git diff failed: {r.stderr}"
    assert r.stdout.strip() == "", (
        f"packages/effect/src/index.ts was modified. AGENTS.md forbids manual edits to barrel files.\n"
        f"diff:\n{r.stdout[:2000]}"
    )


def test_no_scratchpad_files_left_behind():
    """AGENTS.md: scratchpad/ files for testing/debugging must be deleted after use.

    Compares against base commit — only flag NEW (untracked) files in scratchpad/, not the
    repo-tracked package.json / tsconfig.json that already live there.
    """
    r = subprocess.run(
        ["git", "status", "--porcelain", "--", "scratchpad/"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"
    leftover_lines = [
        line for line in r.stdout.splitlines()
        if line.strip() and "node_modules" not in line
    ]
    assert not leftover_lines, (
        "scratchpad/ contains untracked or modified files that should have been cleaned up:\n"
        + "\n".join(leftover_lines)
    )
