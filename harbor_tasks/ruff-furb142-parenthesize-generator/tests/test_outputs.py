"""
Task: ruff-furb142-parenthesize-generator
Repo: astral-sh/ruff @ 20ca73626d71189ed000806938e1de688c1d3e55
PR:   24200

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"
RULE_FILE = Path(REPO) / "crates/ruff_linter/src/rules/refurb/rules/for_loop_set_mutations.rs"
RUFF_BIN = Path(REPO) / "target/release/ruff"


def _ensure_ruff_built():
    """Compile ruff release binary (incremental after Docker pre-build)."""
    r = subprocess.run(
        ["cargo", "build", "--release", "-p", "ruff"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"cargo build failed:\n{r.stderr.decode()[-2000:]}"


def _ruff_fix(code: str) -> str:
    """Run ruff check --select FURB142 --fix on code, return fixed content."""
    _ensure_ruff_built()
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, dir="/tmp"
    ) as f:
        f.write(code)
        path = f.name
    try:
        subprocess.run(
            [str(RUFF_BIN), "check", "--select", "FURB142", "--fix", "--quiet", path],
            capture_output=True, timeout=30,
        )
        return Path(path).read_text()
    finally:
        Path(path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compiles():
    """Rust code in ruff_linter crate must compile."""
    _ensure_ruff_built()


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_unparen_generator_parenthesized():
    """Unparenthesized generator in s.add() gets wrapped in parens by FURB142 fix."""
    code = (
        "s = set()\n"
        'for x in ("abc", "def"):\n'
        "    s.add(c for c in x)\n"
    )
    fixed = _ruff_fix(code)
    assert "(c for c in x)" in fixed, (
        f"Generator not parenthesized in output:\n{fixed}"
    )
    # Must NOT have buggy merged comprehension
    without_paren = fixed.replace("(c for c in x)", "PLACEHOLDER")
    assert "c for c in x for x in" not in without_paren, (
        f"Generator merged with outer comprehension (bug not fixed):\n{fixed}"
    )


# [pr_diff] fail_to_pass
def test_varied_unparen_generator():
    """Different unparenthesized generator expression also gets parenthesized."""
    code = (
        "s = set()\n"
        'for item in [["a", "b"], ["c"]]:\n'
        "    s.add(v.upper() for v in item)\n"
    )
    fixed = _ruff_fix(code)
    assert "(v.upper() for v in item)" in fixed, (
        f"Generator not parenthesized in output:\n{fixed}"
    )


# [pr_diff] fail_to_pass
def test_conditional_unparen_generator():
    """Unparenthesized generator with if-clause also gets parenthesized."""
    code = (
        "s = set()\n"
        "for word in ['hello', 'world']:\n"
        "    s.add(ch for ch in word if ch != 'o')\n"
    )
    fixed = _ruff_fix(code)
    assert "(ch for ch in word if ch != 'o')" in fixed, (
        f"Conditional generator not parenthesized in output:\n{fixed}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + structural checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_already_paren_preserved():
    """Already-parenthesized generator in s.add() is not double-wrapped."""
    # Case 1: simple generator
    code1 = (
        "s = set()\n"
        'for x in ("abc", "def"):\n'
        "    s.add((c for c in x))\n"
    )
    fixed1 = _ruff_fix(code1)
    assert "(c for c in x)" in fixed1, (
        f"Generator missing from output:\n{fixed1}"
    )
    assert "((c for c in x))" not in fixed1, (
        f"Generator was double-wrapped:\n{fixed1}"
    )
    # Case 2: conditional generator already parenthesized
    code2 = (
        "s = set()\n"
        "for word in ['hello', 'world']:\n"
        "    s.add((ch for ch in word if ch != 'o'))\n"
    )
    fixed2 = _ruff_fix(code2)
    assert "((ch for ch in word" not in fixed2, (
        f"Conditional generator was double-wrapped:\n{fixed2}"
    )


# [repo_tests] pass_to_pass
def test_upstream_furb142_tests():
    """Upstream tests for FURB142 run without panics or compile errors.

    Uses INSTA_UPDATE=always so new test fixtures added by the agent don't
    cause snapshot-mismatch failures (the solve.sh doesn't update snapshots,
    and snapshot diffs are evaluated separately). This still catches panics,
    ICEs, and runtime failures.
    """
    env = {**os.environ, "INSTA_UPDATE": "always", "INSTA_FORCE_PASS": "1"}
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_linter", "--", "FURB142"],
        cwd=REPO, capture_output=True, timeout=600, env=env,
    )
    assert r.returncode == 0, (
        f"FURB142 tests failed:\n"
        f"{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 20ca73626d71189ed000806938e1de688c1d3e55
# Text inspection because: Rust source cannot be imported/executed in Python
def test_no_panic_unwrap_unreachable():
    """Rule file avoids panic!/unwrap()/unreachable!() per AGENTS.md guidance."""
    source = RULE_FILE.read_text()
    violations = []
    for i, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        if "panic!(" in stripped:
            violations.append(f"  line {i}: {stripped}")
        if ".unwrap()" in stripped:
            violations.append(f"  line {i}: {stripped}")
        if "unreachable!(" in stripped:
            violations.append(f"  line {i}: {stripped}")
    assert not violations, (
        f"panic!/unwrap/unreachable found in for_loop_set_mutations.rs:\n"
        + "\n".join(violations)
    )


# [agent_config] pass_to_pass — AGENTS.md:76 @ 20ca73626d71189ed000806938e1de688c1d3e55
# Text inspection because: Rust source cannot be imported/executed in Python
def test_imports_at_top():
    """Rust imports (use statements) must be at top of file, not inside functions."""
    source = RULE_FILE.read_text()
    in_function = False
    depth = 0
    violations = []
    for i, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        if "fn " in stripped and "{" in stripped:
            in_function = True
            depth = 0
        if in_function:
            depth += stripped.count("{") - stripped.count("}")
            if depth <= 0:
                in_function = False
            if stripped.startswith("use ") and not stripped.startswith("use super"):
                violations.append(f"  line {i}: {stripped}")
    assert not violations, (
        f"Local use-imports found inside functions in for_loop_set_mutations.rs:\n"
        + "\n".join(violations)
    )


# [agent_config] pass_to_pass — AGENTS.md:81 @ 20ca73626d71189ed000806938e1de688c1d3e55
# Text inspection because: Rust source cannot be imported/executed in Python
def test_prefer_expect_over_allow():
    """If Clippy lints are suppressed, #[expect()] is preferred over #[allow()]."""
    source = RULE_FILE.read_text()
    violations = []
    for i, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        if "#[allow(clippy::" in stripped:
            violations.append(f"  line {i}: {stripped}")
    assert not violations, (
        f"#[allow(clippy::...)] found — use #[expect()] instead per AGENTS.md:\n"
        + "\n".join(violations)
    )
