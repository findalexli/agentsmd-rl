"""
Task: ruff-up008-lambda-scope
Repo: astral-sh/ruff @ 09f645d49f1337866d63e62570cb9a43a4a875b3
PR:   #24274

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import tempfile
from pathlib import Path

import pytest

REPO = "/workspace/ruff"
RUST_FILE = Path(REPO) / "crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs"
FIXTURE = Path(REPO) / "crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py"


@pytest.fixture(scope="module")
def ruff_bin():
    """Build ruff once for all tests that need it."""
    r = subprocess.run(
        ["cargo", "build", "--bin", "ruff"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr.decode()[-2000:]}"
    return f"{REPO}/target/debug/ruff"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_build_compiles(ruff_bin):
    """Modified ruff code compiles without errors."""
    assert Path(ruff_bin).exists()


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_lambda_super_detected(ruff_bin):
    """UP008 detects super(ClassName, self) inside lambda class attributes."""
    r = subprocess.run(
        [ruff_bin, "check", "--select", "UP008", "--no-cache",
         "--output-format", "text", str(FIXTURE)],
        capture_output=True, text=True, cwd=REPO, timeout=30,
    )
    output = r.stdout + r.stderr
    assert "LambdaMethod" in output and "UP008" in output, (
        f"UP008 did not detect super() in LambdaMethod lambda.\nOutput: {output[:500]}"
    )


# [pr_diff] fail_to_pass
def test_lambda_super_fix_available(ruff_bin):
    """UP008 offers an autofix that simplifies lambda super(Cls, self) to super()."""
    r = subprocess.run(
        [ruff_bin, "check", "--select", "UP008", "--fix", "--diff",
         "--no-cache", str(FIXTURE)],
        capture_output=True, text=True, cwd=REPO, timeout=30,
    )
    output = r.stdout + r.stderr
    assert "LambdaMethod" in output and "super()" in output, (
        f"No fix offered for lambda super() call.\nOutput: {output[:500]}"
    )


# [pr_diff] fail_to_pass
def test_lambda_super_varied_inputs(ruff_bin):
    """UP008 detects lambda super() across multiple class/nesting patterns."""
    test_code = '''\
class Base:
    def method(self):
        pass

class Simple(Base):
    action = lambda self: super(Simple, self).method()

class WithMultipleArgs(Base):
    compute = lambda self, x=1: super(WithMultipleArgs, self).method()

class Outer:
    class Inner(Base):
        handler = lambda self: super(Outer.Inner, self).method()
'''
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        tmp_path = f.name
    try:
        r = subprocess.run(
            [ruff_bin, "check", "--select", "UP008", "--no-cache",
             "--output-format", "text", tmp_path],
            capture_output=True, text=True, cwd=REPO, timeout=30,
        )
        output = r.stdout + r.stderr
        assert "Simple" in output, (
            f"UP008 missed Simple lambda.\nOutput: {output[:500]}"
        )
        assert "WithMultipleArgs" in output, (
            f"UP008 missed WithMultipleArgs lambda.\nOutput: {output[:500]}"
        )
        assert "Inner" in output, (
            f"UP008 missed Outer.Inner lambda.\nOutput: {output[:500]}"
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)


# [pr_diff] fail_to_pass
def test_todo_comment_removed():
    """TODO(charlie) about missed lambda rewrite is removed from fixture."""
    content = FIXTURE.read_text()
    assert "TODO(charlie): class-body lambda" not in content, (
        "TODO comment about lambda case still present in fixture"
    )
    assert "lambda rewrite is still missed" not in content, (
        "TODO comment about lambda still present (alternate wording)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_upstream_up008_tests_pass():
    """Upstream UP008 test suite still passes (including snapshot tests)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_linter", "--lib", "--",
         "rules::pyupgrade::tests::UP008"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"Upstream UP008 tests failed:\n{output[-2000:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 09f645d49f1337866d63e62570cb9a43a4a875b3
# Text inspection because: Rust source cannot be imported/executed in Python
def test_no_excessive_panic_unwrap():
    """Avoid panic!/unreachable!/unwrap() per AGENTS.md:79."""
    content = RUST_FILE.read_text()
    count = 0
    for line in content.splitlines():
        code = line.split("//")[0].strip()
        if not code:
            continue
        if "panic!(" in code or "unreachable!(" in code or ".unwrap()" in code:
            count += 1
    assert count <= 3, (
        f"Found {count} uses of panic!/unreachable!/unwrap() in changed file (max 3)"
    )


# [agent_config] pass_to_pass — AGENTS.md:76 @ 09f645d49f1337866d63e62570cb9a43a4a875b3
# Text inspection because: Rust source cannot be imported/executed in Python
def test_no_local_rust_imports():
    """Rust imports must be at top of file, not local in functions (AGENTS.md:76)."""
    import re
    content = RUST_FILE.read_text()
    # Filter out 'use' inside mod tests {} which is acceptable
    tests_start = content.find("mod tests")
    main_section = content[:tests_start] if tests_start != -1 else content
    # Top-level 'use' starts at column 0; local imports are indented inside fn bodies
    local_uses = re.findall(r"^\s{4,}use\s+", main_section, re.MULTILINE)
    assert len(local_uses) == 0, (
        f"Found {len(local_uses)} local 'use' import(s) in function bodies; "
        "Rust imports should go at the top of the file (AGENTS.md:76)"
    )
