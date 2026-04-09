"""
Task: ruff-e502-fstring-backslash-fix
Repo: ruff @ 62bb07772806a0ca578766531f1ffcba1f2c9c90
PR:   24410

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"
RUFF_BIN = os.path.join(REPO, "target", "debug", "ruff")


def _ensure_ruff():
    """Build ruff binary if not already built."""
    if not os.path.exists(RUFF_BIN):
        r = subprocess.run(
            ["cargo", "build", "--bin", "ruff"],
            cwd=REPO, capture_output=True, timeout=600,
        )
        assert r.returncode == 0, f"Build failed:\n{r.stderr.decode()}"


def _run_e502_check(code: str) -> str:
    """Run ruff E502 check on code, return stdout."""
    _ensure_ruff()
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        tmp = f.name
    try:
        r = subprocess.run(
            [RUFF_BIN, "check", "--preview", "--select", "E502",
             "--output-format", "text", tmp],
            capture_output=True, timeout=30,
        )
        return r.stdout.decode()
    finally:
        os.unlink(tmp)


def _run_e502_fix(code: str) -> str:
    """Run ruff E502 fix on code, return the fixed content."""
    _ensure_ruff()
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        tmp = f.name
    try:
        subprocess.run(
            [RUFF_BIN, "check", "--preview", "--select", "E502", "--fix", tmp],
            capture_output=True, timeout=30,
        )
        return Path(tmp).read_text()
    finally:
        os.unlink(tmp)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_ruff_builds():
    """Ruff compiles successfully after changes."""
    r = subprocess.run(
        ["cargo", "build", "--bin", "ruff"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_fstring_backslash_e502_detection():
    """E502 must detect both redundant backslashes around a multiline f-string."""
    code = 'x = [\n    "a" + \\\nf"""\nb\n""" + \\\n    "c"\n]\n'
    output = _run_e502_check(code)
    assert output.count("E502") >= 2, (
        f"Expected 2+ E502 violations for f-string case, got:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_fstring_backslash_fix_complete():
    """E502 fix removes ALL redundant backslashes, including those after multiline f-strings."""
    code = 'x = [\n    "a" + \\\nf"""\nb\n""" + \\\n    "c"\n]\n'
    fixed = _run_e502_fix(code)
    # After fix, no lines should end with a continuation backslash
    continuation_lines = [
        line for line in fixed.splitlines()
        if line.rstrip().endswith("\\")
    ]
    assert len(continuation_lines) == 0, (
        f"Expected all redundant backslashes removed, but found {len(continuation_lines)} "
        f"remaining continuation line(s):\n" + "\n".join(continuation_lines)
    )


# [pr_diff] fail_to_pass
def test_varied_fstring_e502_detection():
    """E502 detects violation after a multiline f-string with single-quoted triple."""
    code = "data = (\n    f'''\n    hello\n    ''' + \\\n    \"end\"\n)\n"
    output = _run_e502_check(code)
    assert output.count("E502") >= 1, (
        f"Expected E502 violation after multiline f-string, got:\n{output}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_regular_string_e502_works():
    """E502 still correctly detects redundant backslash with regular strings."""
    code = 'x = (\n    "hello" + \\\n    "world"\n)\n'
    output = _run_e502_check(code)
    assert output.count("E502") >= 1, (
        f"Expected E502 for regular string backslash, got:\n{output}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 62bb07772806a0ca578766531f1ffcba1f2c9c90
def test_no_unwrap_panic_in_indexer_production():
    """AGENTS.md:79 — No .unwrap()/panic!/unreachable! in indexer production code."""
    src = Path(REPO, "crates", "ruff_python_index", "src", "indexer.rs").read_text()
    # Split out test code — everything after #[cfg(test)] is test-only
    test_marker = "#[cfg(test)]"
    idx = src.find(test_marker)
    production = src[:idx] if idx != -1 else src
    for pattern in [".unwrap()", "panic!", "unreachable!"]:
        occurrences = [
            (i + 1, line.strip())
            for i, line in enumerate(production.splitlines())
            if pattern in line and not line.strip().startswith("//")
        ]
        assert len(occurrences) == 0, (
            f"Found '{pattern}' in indexer.rs production code at lines: "
            f"{occurrences}. AGENTS.md requires avoiding these patterns."
        )
