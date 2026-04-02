"""
Task: ruff-up008-lambda-scope
Repo: astral-sh/ruff @ 09f645d49f1337866d63e62570cb9a43a4a875b3
PR:   24274

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"
RUST_FILE = Path(REPO) / "crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs"
FIXTURE = Path(REPO) / "crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py"
RUFF_BIN = Path(REPO) / "target/release/ruff"


def _ensure_ruff_built():
    """Compile ruff release binary (no-op if already cached)."""
    if RUFF_BIN.exists():
        return
    r = subprocess.run(
        ["cargo", "build", "--release", "-p", "ruff"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"cargo build failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_build_compiles():
    """Modified ruff code compiles without errors."""
    _ensure_ruff_built()


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_lambda_super_detected():
    """UP008 detects super(ClassName, self) inside lambda class attributes."""
    _ensure_ruff_built()
    r = subprocess.run(
        [str(RUFF_BIN), "check", "--select", "UP008", "--output-format", "text",
         str(FIXTURE)],
        capture_output=True, text=True, cwd=REPO, timeout=30,
    )
    output = r.stdout + r.stderr
    assert "LambdaMethod" in output and "UP008" in output, (
        f"UP008 did not detect super() in LambdaMethod lambda.\nOutput: {output[:500]}"
    )


# [pr_diff] fail_to_pass
def test_lambda_super_fix_available():
    """UP008 offers an autofix that simplifies lambda super(Cls, self) to super()."""
    _ensure_ruff_built()
    r = subprocess.run(
        [str(RUFF_BIN), "check", "--select", "UP008", "--fix", "--diff",
         str(FIXTURE)],
        capture_output=True, text=True, cwd=REPO, timeout=30,
    )
    output = r.stdout + r.stderr
    assert "LambdaMethod" in output and "super()" in output, (
        f"No fix offered for lambda super() call.\nOutput: {output[:500]}"
    )


# [pr_diff] fail_to_pass
def test_lambda_super_varied_inputs():
    """UP008 detects lambda super() across multiple class/nesting patterns."""
    _ensure_ruff_built()
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
            [str(RUFF_BIN), "check", "--select", "UP008", "--output-format", "text",
             tmp_path],
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
    content = RUST_FILE.read_text()
    local_imports = []
    in_test_mod = False
    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        # Skip #[cfg(test)] mod blocks — test modules conventionally use local imports
        if stripped.startswith("#[cfg(test)]"):
            in_test_mod = True
            continue
        if in_test_mod:
            continue
        # A `use` statement that is indented is a local import
        if stripped.startswith("use ") and stripped.endswith(";") and line != stripped:
            local_imports.append(f"  line {i}: {stripped}")
    assert not local_imports, (
        f"Found local imports (should be at top of file per AGENTS.md:76):\n"
        + "\n".join(local_imports)
    )
