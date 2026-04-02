"""
Task: ruff-ruf073-fstring-percent-format
Repo: astral-sh/ruff @ b491f7ebed9ea3be8ff7990dd6119c77c57baa74
PR:   24162

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"
RUFF_BIN = None


def _build_ruff():
    """Build ruff binary once, cache the path."""
    global RUFF_BIN
    if RUFF_BIN is not None:
        return RUFF_BIN
    r = subprocess.run(
        ["cargo", "build", "--bin", "ruff"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    path = Path(REPO) / "target" / "debug" / "ruff"
    assert path.exists(), f"Failed to build ruff:\n{r.stderr.decode()[-2000:]}"
    RUFF_BIN = str(path)
    return RUFF_BIN


def _run_ruff(code: str, select: str = "RUF073", extra_args: list[str] | None = None) -> str:
    """Write code to a temp file, run ruff check, return stdout+stderr."""
    ruff = _build_ruff()
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        f.flush()
        args = [ruff, "check", "--select", select, "--preview", "--no-cache", f.name]
        if extra_args:
            args.extend(extra_args)
        r = subprocess.run(args, capture_output=True, timeout=60)
        return r.stdout.decode() + r.stderr.decode()


def _count_violations(output: str, code: str = "RUF073") -> int:
    # Count actual violation lines: "file.py:line:col: CODE message"
    # Avoids counting ruff warnings that mention the rule name in prose.
    return sum(1 for line in output.splitlines() if f": {code} " in line)


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """ruff_linter crate compiles without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ruff_linter"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_fstring_percent_variable():
    """f-string with % and a variable RHS is flagged as RUF073."""
    output = _run_ruff('banana = "banana"\nf"{banana}" % banana\n')
    assert _count_violations(output) >= 1, f"Expected RUF073 violation:\n{output}"


# [pr_diff] fail_to_pass
def test_fstring_percent_tuple():
    """f-string with % and a tuple RHS is flagged as RUF073."""
    output = _run_ruff('f"hello %s %s" % (1, 2)\n')
    assert _count_violations(output) >= 1, f"Expected RUF073 violation:\n{output}"


# [pr_diff] fail_to_pass
def test_fstring_percent_dict():
    """f-string with % and a dict RHS is flagged as RUF073."""
    output = _run_ruff('x = 42\nf"value: {x}" % {"key": "value"}\n')
    assert _count_violations(output) >= 1, f"Expected RUF073 violation:\n{output}"


# [pr_diff] fail_to_pass
def test_fstring_percent_literal_and_nested():
    """f-string with nested expressions and literal RHS both flagged."""
    code = 'x = 1\nf"{\'nested\'} %s" % 42\nf"no placeholders" % "banana"\n'
    output = _run_ruff(code)
    assert _count_violations(output) >= 2, f"Expected >=2 RUF073 violations:\n{output}"


# [pr_diff] fail_to_pass
def test_rule_requires_preview():
    """RUF073 is a preview rule — must not fire without --preview flag."""
    ruff = _build_ruff()
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write('f"hello %s" % "world"\n')
        f.flush()
        # Run WITHOUT --preview
        r = subprocess.run(
            [ruff, "check", "--select", "RUF073", "--no-cache", f.name],
            capture_output=True, timeout=60,
        )
        output = r.stdout.decode() + r.stderr.decode()
    assert _count_violations(output) == 0, (
        f"RUF073 should not fire without --preview:\n{output}"
    )
    # Also confirm it DOES fire with --preview (double-check)
    output2 = _run_ruff('f"hello %s" % "world"\n')
    assert _count_violations(output2) >= 1, (
        f"RUF073 should fire with --preview:\n{output2}"
    )


# [pr_diff] pass_to_pass
def test_no_false_positives():
    """Plain strings, byte strings, f-strings without %, and integer modulo are NOT flagged."""
    code = (
        'name = "world"\n'
        '"hello %s" % "world"\n'
        '"%s %s" % (1, 2)\n'
        'f"hello {name}"\n'
        'result = 42 % 10\n'
    )
    output = _run_ruff(code)
    assert _count_violations(output) == 0, f"Unexpected RUF073 violations:\n{output}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_ruf07x_tests():
    """Existing RUF07x snapshot tests still pass (snapshots auto-updated via INSTA_FORCE_PASS)."""
    env = {**os.environ, "INSTA_FORCE_PASS": "1", "INSTA_UPDATE": "always"}
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_linter", "--", "RUF07", "--test-threads=1"],
        cwd=REPO, capture_output=True, timeout=300, env=env,
    )
    assert r.returncode == 0, (
        f"RUF07x tests failed:\n{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_existing_f50x_still_works():
    """Existing F507 percent-format rules still fire on plain strings."""
    code = "'%s %s' % (1,)\n'%s' % (1, 2)\n"
    output = _run_ruff(code, select="F507")
    count = _count_violations(output, "F507")
    assert count >= 2, f"Expected >=2 F507 violations, got {count}:\n{output}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:85 @ b491f7ebed9ea3be8ff7990dd6119c77c57baa74
def test_schema_updated():
    """ruff.schema.json must include RUF073 after cargo dev generate-all (AGENTS.md:85)."""
    schema = Path(REPO) / "ruff.schema.json"
    assert schema.exists(), "ruff.schema.json not found"
    content = schema.read_text()
    assert "RUF073" in content, (
        "RUF073 not found in ruff.schema.json — run `cargo dev generate-all` after adding a new rule"
    )


# [agent_config] pass_to_pass — AGENTS.md:76 @ b491f7ebed9ea3be8ff7990dd6119c77c57baa74
def test_no_local_rust_imports():
    """Rust imports should be at file top, not locally in functions (AGENTS.md:76)."""
    # Collect changed .rs files
    r = subprocess.run(
        ["git", "diff", "--name-only", "task-branch", "HEAD"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    committed = r.stdout.decode().strip().splitlines()
    r2 = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    uncommitted = r2.stdout.decode().strip().splitlines()
    rs_files = sorted({f for f in committed + uncommitted if f.endswith(".rs")})
    for f in rs_files:
        fpath = Path(REPO) / f
        if not fpath.exists():
            continue
        lines = fpath.read_text().splitlines()
        in_fn = False
        brace_depth = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("fn ") or stripped.startswith("pub fn ") or stripped.startswith("pub(crate) fn "):
                in_fn = True
            if in_fn:
                brace_depth += line.count("{") - line.count("}")
                if stripped.startswith("use ") and brace_depth > 0:
                    assert False, f"Local import found in function body in {f}: {stripped}"
                if brace_depth <= 0:
                    in_fn = False
                    brace_depth = 0


# [agent_config] pass_to_pass — AGENTS.md:79 @ b491f7ebed9ea3be8ff7990dd6119c77c57baa74
def test_no_new_unwrap_panic():
    """No new .unwrap()/.expect()/panic!/unreachable! added (AGENTS.md:79)."""
    import re
    pattern = re.compile(r"\.(unwrap|expect)\(\)|panic!\(|unreachable!\(")
    r = subprocess.run(
        ["git", "diff", "--name-only", "task-branch", "HEAD"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    committed = r.stdout.decode().strip().splitlines()
    r2 = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    uncommitted = r2.stdout.decode().strip().splitlines()
    rs_files = sorted({f for f in committed + uncommitted if f.endswith(".rs")})
    new_count = 0
    base_count = 0
    for f in rs_files:
        fpath = Path(REPO) / f
        if fpath.exists():
            new_count += len(pattern.findall(fpath.read_text()))
        # Base version
        br = subprocess.run(
            ["git", "show", f"task-branch:{f}"],
            cwd=REPO, capture_output=True, timeout=10,
        )
        if br.returncode == 0:
            base_count += len(pattern.findall(br.stdout.decode()))
    assert new_count <= base_count, (
        f"New unwrap/panic/unreachable calls added: {new_count} (was {base_count})"
    )
