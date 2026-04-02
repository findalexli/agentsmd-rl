"""
Task: ruff-f507-zero-placeholder-format
Repo: astral-sh/ruff @ 690ef81f553ca0ce2f477e8030f4ab49abea4b01
PR:   #24215

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"
RULE_FILE = Path(REPO) / "crates/ruff_linter/src/rules/pyflakes/rules/strings.rs"
FIXTURE_FILE = Path(REPO) / "crates/ruff_linter/resources/test/fixtures/pyflakes/F50x.py"

_ruff_bin = None


def _build_ruff():
    """Build ruff binary once, return path."""
    global _ruff_bin
    if _ruff_bin is not None:
        return _ruff_bin
    r = subprocess.run(
        ["cargo", "build", "--bin", "ruff"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo build failed:\n{r.stderr.decode()[-2000:]}"
    path = f"{REPO}/target/debug/ruff"
    assert os.path.isfile(path), f"ruff binary not found at {path}"
    _ruff_bin = path
    return _ruff_bin


def _count_f507(code: str) -> int:
    """Run ruff check --select F507 on code snippet, return violation count."""
    ruff = _build_ruff()
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        f.flush()
        try:
            r = subprocess.run(
                [ruff, "check", "--select", "F507", "--no-cache", f.name],
                capture_output=True, timeout=30,
            )
            output = r.stdout.decode() + r.stderr.decode()
            return output.count("F507")
        finally:
            os.unlink(f.name)


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_cargo_build():
    """Ruff compiles and strings.rs is not truncated."""
    assert RULE_FILE.is_file(), f"{RULE_FILE} does not exist"
    line_count = len(RULE_FILE.read_text().splitlines())
    assert line_count > 500, f"strings.rs only has {line_count} lines (likely truncated)"
    _build_ruff()


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_literal_rhs_flagged():
    """Zero-placeholder format strings with literal or tuple RHS are flagged as F507.

    Literals (42) and non-empty tuples ((1,)) were already caught by the base
    code via ResolvedPythonType::Atom; this is a regression test.
    """
    code = "'hello' % 42\n'' % 42\n'hello' % (1,)\n"
    count = _count_f507(code)
    assert count >= 3, f"Expected >=3 F507 violations for literal RHS, got {count}"


# [pr_diff] fail_to_pass
def test_variable_rhs_flagged():
    """Zero-placeholder format strings with variable RHS are flagged as F507."""
    code = "banana = 42\n'hello' % banana\n'' % banana\n"
    count = _count_f507(code)
    assert count >= 2, f"Expected >=2 F507 violations for variable RHS, got {count}"


# [pr_diff] fail_to_pass
def test_dynamic_rhs_flagged():
    """Zero-placeholder format strings with dynamic RHS (calls, attrs) are flagged."""
    code = "'hello' % unknown_var\n'hello' % get_value()\n'hello' % obj.attr\n"
    count = _count_f507(code)
    assert count >= 3, f"Expected >=3 F507 violations for dynamic RHS, got {count}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_empty_tuple_not_flagged():
    """Empty tuple RHS is valid at runtime and must NOT be flagged."""
    code = "'hello' % ()\n'' % ()\n'no placeholders' % ()\n"
    count = _count_f507(code)
    assert count == 0, f"Expected 0 F507 violations for empty tuple RHS, got {count}"


# [pr_diff] pass_to_pass
def test_existing_mismatches_still_flagged():
    """Pre-existing non-zero-placeholder mismatch cases still detected."""
    code = "'%s %s' % (1,)\n'%s' % (1, 2)\n'%d %d %d' % (1, 2)\n"
    count = _count_f507(code)
    assert count >= 3, f"Expected >=3 F507 violations for existing mismatches, got {count}"


# [pr_diff] pass_to_pass
def test_correct_usage_not_flagged():
    """Correct %-format usage must produce zero F507 violations."""
    code = "'%s' % 42\n'%s %s' % (1, 2)\n'%d items: %s' % (3, 'abc')\n"
    count = _count_f507(code)
    assert count == 0, f"Expected 0 F507 violations for correct usage, got {count}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:76 @ 690ef81f
def test_no_function_local_imports():
    """Rust imports at file top, not inside function bodies (AGENTS.md:76)."""
    content = RULE_FILE.read_text()
    in_fn = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("pub fn ") or stripped.startswith("fn "):
            in_fn = True
        if in_fn and stripped.startswith("use "):
            assert False, f"Found local import inside function: {stripped}"
        if stripped == "}" and in_fn and not line.startswith(" "):
            in_fn = False


# [agent_config] pass_to_pass — AGENTS.md:79 @ 690ef81f
def test_no_new_unsafe_patterns():
    """No new .unwrap(), panic!(), or unreachable!() calls in strings.rs (AGENTS.md:79)."""
    patterns = [".unwrap()", "panic!(", "unreachable!("]
    r = subprocess.run(
        ["git", "show", "HEAD:crates/ruff_linter/src/rules/pyflakes/rules/strings.rs"],
        cwd=REPO, capture_output=True, timeout=10,
    )
    base_text = r.stdout.decode() if r.returncode == 0 else ""
    curr_text = RULE_FILE.read_text()
    for pat in patterns:
        base_count = base_text.count(pat)
        curr_count = curr_text.count(pat)
        assert curr_count <= base_count, (
            f"New {pat} added to strings.rs: {base_count} -> {curr_count}"
        )
