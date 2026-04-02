"""
Task: ruff-w391-consecutive-empty-cell-panic
Repo: astral-sh/ruff @ 627e2a04269400ea88f65e64797666ad32604204
PR:   24236

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import tempfile
from pathlib import Path

REPO = "/repo"
RUFF = f"{REPO}/target/debug/ruff"


def _build_ruff():
    """Build ruff if not already built."""
    ruff = Path(RUFF)
    if not ruff.exists():
        r = subprocess.run(
            ["cargo", "build", "--bin", "ruff"],
            cwd=REPO, capture_output=True, timeout=600,
        )
        assert r.returncode == 0, f"cargo build failed:\n{r.stderr.decode()[-2000:]}"


def _write_notebook(cells_source: list[list[str]]) -> str:
    """Write a .ipynb notebook to a temp file, return the path."""
    cells = []
    for src in cells_source:
        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": src,
        })
    nb = {
        "cells": cells,
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    f = tempfile.NamedTemporaryFile(suffix=".ipynb", mode="w", delete=False)
    json.dump(nb, f)
    f.close()
    return f.name


def _run_ruff_w391(path: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run ruff check --preview --select W391 on the given file."""
    return subprocess.run(
        [RUFF, "check", "--preview", "--select", "W391", path],
        capture_output=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gate: code compiles
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_build():
    """Modified Rust code compiles successfully."""
    _build_ruff()
    assert Path(RUFF).exists(), "ruff binary not found after build"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_panic_consecutive_empty_cells():
    """Consecutive empty notebook cells don't cause a panic."""
    _build_ruff()
    nb = _write_notebook([
        ["1+1\n"],
        ["\n", "\n"],
        ["\n", "\n"],
        ["\n", "\n"],
    ])
    r = _run_ruff_w391(nb)
    assert r.returncode <= 2, f"ruff crashed (exit {r.returncode})"
    assert b"panic" not in r.stderr.lower(), f"ruff panicked:\n{r.stderr.decode()[:1000]}"


# [pr_diff] fail_to_pass
def test_no_panic_many_consecutive_empty_cells():
    """Five+ consecutive empty cells don't cause a panic (stress variant)."""
    _build_ruff()
    nb = _write_notebook([
        ["a = 1\n"],
        ["\n"], ["\n"], ["\n"], ["\n"], ["\n"],
    ])
    r = _run_ruff_w391(nb)
    assert r.returncode <= 2, f"ruff crashed (exit {r.returncode})"
    assert b"panic" not in r.stderr.lower(), f"ruff panicked:\n{r.stderr.decode()[:1000]}"


# [pr_diff] fail_to_pass
def test_w391_diagnostics_emitted():
    """W391 diagnostics are emitted for cells with trailing newlines."""
    _build_ruff()
    nb = _write_notebook([
        ["1+1\n"],
        ["\n", "\n"],
        ["\n", "\n"],
        ["\n", "\n"],
    ])
    r = _run_ruff_w391(nb)
    assert r.returncode <= 2, f"ruff crashed (exit {r.returncode})"
    stdout = r.stdout.decode()
    w391_count = stdout.count("W391")
    assert w391_count >= 1, f"Expected W391 diagnostics, got none. Output:\n{stdout}"


# [pr_diff] fail_to_pass
def test_no_panic_single_empty_cell():
    """A single empty cell after a code cell doesn't panic."""
    _build_ruff()
    nb = _write_notebook([
        ["x = 1\n"],
        ["\n", "\n"],
    ])
    r = _run_ruff_w391(nb)
    assert r.returncode <= 2, f"ruff crashed (exit {r.returncode})"
    assert b"panic" not in r.stderr.lower(), f"ruff panicked:\n{r.stderr.decode()[:1000]}"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_w391_regular_python_file():
    """W391 detection on regular .py files is unaffected."""
    _build_ruff()
    f = tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False)
    f.write("x = 1\n\n\n")
    f.close()
    r = _run_ruff_w391(f.name)
    stdout = r.stdout.decode()
    assert "W391" in stdout, f"W391 not triggered on .py file. Output:\n{stdout}"


# [repo_tests] pass_to_pass
def test_upstream_w391_tests():
    """Upstream snapshot tests for W391 still pass."""
    _build_ruff()
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_linter", "--", "too_many_newlines"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"Upstream W391 tests failed:\n{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 627e2a0
def test_no_unwrap_in_fix_file():
    """No bare .unwrap() in the diagnostic file (AGENTS.md:79: avoid panic!/unwrap())."""
    fix_file = Path(REPO) / "crates/ruff_linter/src/rules/pycodestyle/rules/too_many_newlines_at_end_of_file.rs"
    content = fix_file.read_text()
    unwrap_count = content.count(".unwrap()")
    assert unwrap_count == 0, f"Found {unwrap_count} bare .unwrap() calls in {fix_file.name}"
