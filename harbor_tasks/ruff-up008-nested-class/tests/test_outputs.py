"""
Task: ruff-up008-nested-class
Repo: astral-sh/ruff @ 0f41bc554bd89d14dbeb7e1791b34dc7319339bc
PR:   24273

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import pytest
from pathlib import Path

REPO = "/workspace/ruff"
FIXTURE = f"{REPO}/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py"
RULE_FILE = f"{REPO}/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs"


@pytest.fixture(scope="session")
def ruff_bin():
    """Build ruff (incremental) and return binary path."""
    r = subprocess.run(
        ["cargo", "build", "--bin", "ruff"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo build failed:\n{r.stderr[-3000:]}"
    binary = Path(REPO) / "target" / "debug" / "ruff"
    assert binary.exists(), f"Binary not found at {binary}"
    return str(binary)


def _run_ruff_check(ruff_bin, code, tmp_path):
    """Write code to a temp file and run ruff check --select UP008."""
    test_file = tmp_path / "test_input.py"
    test_file.write_text(code)
    return subprocess.run(
        [ruff_bin, "check", "--select", "UP008", "--no-cache", str(test_file)],
        capture_output=True, text=True, timeout=30,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_nested_class_super_no_false_positive(ruff_bin, tmp_path):
    """super(Inner, self) inside a nested class must NOT trigger UP008.
    The inner class name is not in scope — using it would be a NameError."""
    code = """\
class Base:
    def __init__(self, foo):
        self.foo = foo

class Outer:
    class Inner(Base):
        def __init__(self, foo):
            super(Inner, self).__init__(foo)

class CommonNesting:
    class C(Base):
        def __init__(self, foo):
            super(C, self).__init__(foo)
"""
    r = _run_ruff_check(ruff_bin, code, tmp_path)
    assert "UP008" not in r.stdout and "UP008" not in r.stderr, (
        f"UP008 false positive on nested class super():\n{r.stdout}"
    )


# [pr_diff] fail_to_pass
def test_dotted_chain_super_no_false_positive(ruff_bin, tmp_path):
    """super(Inner.C, self) with extra outer nesting must NOT trigger UP008."""
    code = """\
class Base:
    def __init__(self, foo):
        self.foo = foo

class HigherLevelsOfNesting:
    class Inner:
        class C(Base):
            def __init__(self, foo):
                super(Inner.C, self).__init__(foo)
"""
    r = _run_ruff_check(ruff_bin, code, tmp_path)
    assert "UP008" not in r.stdout and "UP008" not in r.stderr, (
        f"UP008 false positive on dotted chain super(Inner.C, self):\n{r.stdout}"
    )


# [pr_diff] fail_to_pass
def test_todo_comments_removed():
    """The TODO(charlie) comments about nested class false positives must be removed."""
    content = Path(FIXTURE).read_text()
    assert "false positive until nested class matching is fixed" not in content, (
        "TODO comment about nested class false positive still present in fixture"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_top_level_super_still_triggers(ruff_bin, tmp_path):
    """Regular super(ClassName, self) at top level must still trigger UP008."""
    code = """\
class Base:
    def __init__(self, foo):
        self.foo = foo

class MyClass(Base):
    def __init__(self, foo):
        super(MyClass, self).__init__(foo)

class AnotherClass(Base):
    def method(self):
        super(AnotherClass, self).method()
"""
    r = _run_ruff_check(ruff_bin, code, tmp_path)
    assert "UP008" in r.stdout or "UP008" in r.stderr, (
        f"UP008 should trigger on top-level super(ClassName, self):\n{r.stdout}"
    )


# [pr_diff] pass_to_pass
def test_full_chain_dotted_super_triggers(ruff_bin, tmp_path):
    """super(A.B.C, self) where the chain matches full class nesting must trigger UP008."""
    code = """\
class Base:
    def __init__(self, foo):
        self.foo = foo

class A:
    class B:
        class C(Base):
            def __init__(self, foo):
                super(A.B.C, self).__init__(foo)
"""
    r = _run_ruff_check(ruff_bin, code, tmp_path)
    assert "UP008" in r.stdout or "UP008" in r.stderr, (
        f"UP008 should trigger on super(A.B.C, self) with matching chain:\n{r.stdout}"
    )


# [repo_tests] pass_to_pass
def test_up008_snapshot_tests_pass():
    """Upstream UP008 snapshot tests must pass (verifies snapshots are updated)."""
    r = subprocess.run(
        ["cargo", "test", "--package", "ruff_linter", "--", "UP008"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"UP008 snapshot tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# [repo_tests] pass_to_pass — CI/CD: cargo check
def test_cargo_check_ruff_linter():
    """Repo's cargo check passes on ruff_linter package (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "--package", "ruff_linter"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo check failed:\n{r.stderr[-2000:]}"
    )


# [repo_tests] pass_to_pass — CI/CD: cargo test
def test_cargo_test_ruff_linter():
    """Repo's cargo test passes on ruff_linter package (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "--package", "ruff_linter"],
        cwd=REPO, capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, (
        f"cargo test failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 0f41bc554bd89d14dbeb7e1791b34dc7319339bc
def test_no_unwrap_or_panic():
    """Modified rule file must not introduce panic!(), unreachable!(), or .unwrap()."""
    content = Path(RULE_FILE).read_text()
    for pattern, label in [
        (r'\bunwrap\(\)', '.unwrap()'),
        (r'\bpanic!\s*\(', 'panic!()'),
        (r'\bunreachable!\s*\(', 'unreachable!()'),
    ]:
        matches = re.findall(pattern, content)
        assert not matches, (
            f"Found {label} in super_call_with_parameters.rs — "
            f"AGENTS.md line 79 says to avoid these patterns"
        )


# [agent_config] pass_to_pass — AGENTS.md:76 @ 0f41bc554bd89d14dbeb7e1791b34dc7319339bc
def test_rust_imports_at_top():
    """Rust imports must be at the top of the file, not locally inside functions."""
    content = Path(RULE_FILE).read_text()
    in_function = False
    brace_depth = 0
    for line in content.splitlines():
        stripped = line.strip()
        if re.match(r'(pub(\(crate\))?\s+)?fn\s+', stripped):
            in_function = True
        if in_function:
            brace_depth += line.count('{') - line.count('}')
            if stripped.startswith('use '):
                assert False, (
                    f"Found local import inside function body: {stripped!r} — "
                    f"AGENTS.md line 76 says imports must be at the top of the file"
                )
            if brace_depth <= 0:
                in_function = False
                brace_depth = 0


# [agent_config] pass_to_pass — AGENTS.md:80 @ 0f41bc554bd89d14dbeb7e1791b34dc7319339bc
def test_no_nested_if_let():
    """Modified rule file must not use nested if-let blocks; prefer let chains (AGENTS.md line 80)."""
    content = Path(RULE_FILE).read_text()
    lines = content.splitlines()
    # Track open if-let blocks by their indentation level.
    # When we encounter another `if let` while one is already open at a shallower indent,
    # that is a nested if-let pattern that should be a let chain instead.
    if_let_indent_stack = []
    for lineno, line in enumerate(lines, 1):
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        # Remove closed blocks (returned to or past their opening indent)
        if_let_indent_stack = [lvl for lvl in if_let_indent_stack if lvl < indent]
        stripped = line.strip()
        # Match bare `if let` openers (not `} else if let` which is a continuation)
        if re.match(r'if let\b', stripped) and not re.match(r'\}.*if let\b', stripped):
            if if_let_indent_stack:
                assert False, (
                    f"Line {lineno}: nested `if let` detected: {stripped!r} — "
                    f"prefer let chains (if let A && let B) per AGENTS.md line 80"
                )
            if_let_indent_stack.append(indent)


# [agent_config] pass_to_pass — AGENTS.md:81 @ 0f41bc554bd89d14dbeb7e1791b34dc7319339bc
def test_clippy_expect_not_allow():
    """If suppressing a Clippy lint, must use #[expect()] not #[allow()]."""
    content = Path(RULE_FILE).read_text()
    for line in content.splitlines():
        stripped = line.strip()
        if re.match(r'#\[allow\(clippy::', stripped):
            assert False, (
                f"Found #[allow(clippy::...)] in rule file: {stripped!r} — "
                f"AGENTS.md line 81 says to prefer #[expect()] over #[allow()]"
            )
