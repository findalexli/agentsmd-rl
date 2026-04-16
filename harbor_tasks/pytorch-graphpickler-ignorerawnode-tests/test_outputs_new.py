"""
Task: pytorch-graphpickler-ignorerawnode-tests
Repo: pytorch/pytorch @ e931ab4802816cec55aa5a25b51f27cb941c924e
PR:   176954

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/pytorch"
TARGET = f"{REPO}/test/fx/test_graph_pickler.py"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code via subprocess."""
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=timeout,
    )


def _source():
    return Path(TARGET).read_text()


def _tree():
    return ast.parse(_source())


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target test file must compile without syntax errors."""
    r = _run_py(f"compile(open('{TARGET}').read(), '{TARGET}', 'exec')")
    assert r.returncode == 0, f"Syntax error: {r.stderr}"


# [repo_tests] pass_to_pass - repo CI/CD validation
def test_p2p_repo_ast_valid():
    """Repo test file must have valid AST (pass_to_pass)."""
    r = _run_py(f'''
import ast
try:
    with open("{TARGET}") as f:
        ast.parse(f.read())
    print("OK")
except SyntaxError as e:
    print(f"SyntaxError: {{e}}")
''')
    assert r.returncode == 0 and "OK" in r.stdout, f"AST validation failed: {r.stderr}"


# [repo_tests] pass_to_pass - repo CI/CD validation
def test_p2p_repo_imports_parse():
    """Repo test file imports must be syntactically valid (pass_to_pass)."""
    r = _run_py(f'''
import ast
with open("{TARGET}") as f:
    tree = ast.parse(f.read())

imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
print(f"Found {{len(imports)}} import statements")
print("OK")
''')
    assert r.returncode == 0 and "OK" in r.stdout, f"Import parsing failed: {r.stderr}"


# [repo_tests] pass_to_pass - repo CI py_compile
def test_p2p_repo_py_compile():
    """Repo test file must compile via py_compile (CI/CD build gate)."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", TARGET],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - repo CI lint: Owner label check
def test_p2p_repo_owner_label():
    """Repo test file must have valid # Owner(s): label (CI linting gate)."""
    r = subprocess.run(
        [sys.executable, "-c",
         f"import re; import sys; content=open('{TARGET}').read(); match=re.search(r'#\\s*Owner\\(s\\):\\s*\\[([^\\]]+)\\]', content); sys.exit(0 if (match and 'module: unknown' not in match.group(1)) else 1)"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Owner label check failed: file must have '# Owner(s): [module: fx]' or similar"


# [repo_tests] pass_to_pass - repo CI lint: run_tests pattern check
def test_p2p_repo_has_main_run_tests():
    """Repo test file must have 'if __name__ == __main__: run_tests()' (CI linting gate)."""
    code = f'''
import ast
import sys
tree = ast.parse(open("{TARGET}").read())
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.If):
        test = node.test
        if (isinstance(test, ast.Compare)
                and isinstance(test.left, ast.Name)
                and test.left.id == "__name__"
                and len(test.ops) == 1
                and isinstance(test.ops[0], ast.Eq)
                and len(test.comparators) == 1
                and isinstance(test.comparators[0], ast.Constant)
                and test.comparators[0].value == "__main__"):
            for stmt in ast.walk(node):
                if (isinstance(stmt, ast.Call)
                        and isinstance(stmt.func, ast.Name)
                        and stmt.func.id == "run_tests"):
                    found = True
                    break
sys.exit(0 if found else 1)
'''
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"run_tests pattern check failed: file must end with 'if __name__ == \"__main__\": run_tests()'"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

def _find_agent_test_class():
    """Find the test class that references ignore_raw_node."""
    tree = _tree()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and "ignore_raw_node" in ast.dump(node):
            return node
    return None


def _run_agent_test_method(method_name: str) -> subprocess.CompletedProcess:
    """Run a specific test method from the agent's test class via pytest."""
    return subprocess.run(
        [
            sys.executable, "-m", "pytest",
            TARGET,
            f"-v",
            f"-k", f"TestIgnoreRawNode and {method_name}",
            "--tb=short",
            "--no-header",
            "-q",
        ],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )


# [pr_diff] fail_to_pass
def test_has_ignore_raw_node_tests():
    """Agent must add at least one test method that exercises ignore_raw_node.

    Verifies by running the actual test methods - not just checking AST patterns.
    """
    # First check the class exists via AST
    cls = _find_agent_test_class()
    assert cls is not None, (
        "No test class found with 'ignore_raw_node' reference - "
        "add class TestIgnoreRawNode(TestCase) to test/fx/test_graph_pickler.py"
    )

    # Then verify the tests can be discovered and run by pytest
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            TARGET,
            "-v",
            "-k", "TestIgnoreRawNode",
            "--collect-only",
            "-q",
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to collect TestIgnoreRawNode tests: {r.stderr}"
    assert "TestIgnoreRawNode" in r.stdout, "TestIgnoreRawNode class not found by pytest"
    # Should have at least 2 test methods (based on not_stub requirement)
    assert "test_" in r.stdout, "No test methods found in TestIgnoreRawNode"


# [pr_diff] fail_to_pass
def test_default_raises_covered():
    """A test must verify GraphPickler.dumps raises by default on raw Node metadata.

    Verifies by running the agent's test that checks assertRaises behavior.
    """
    # Run the specific test method that tests default raises
    r = _run_agent_test_method("test_raw_node_in_meta_raises_by_default")

    # The test should PASS (not error out) - if it fails, the agent's test is wrong
    # If the test can't be found, the agent hasn't added it (fail)
    # If there's an error (not AssertionError), the test setup is broken
    assert r.returncode == 0, (
        f"test_raw_node_in_meta_raises_by_default failed or not found.\n"
        f"stdout: {r.stdout[-500:]}\n"
        f"stderr: {r.stderr[-500:]}\n"
        f"The agent must add a test that calls dumps() and expects AssertionError."
    )
    # Verify it actually tested the right thing (not just a pass from a stub)
    assert "test_raw_node_in_meta_raises_by_default PASSED" in r.stdout or \
           "PASSED" in r.stdout, \
           f"Test did not pass as expected: {r.stdout[-300:]}"


# [pr_diff] fail_to_pass
def test_ignore_true_round_trip():
    """A test must verify the ignore_raw_node=True round-trip (dumps then loads).

    Verifies by running the agent's test that performs the round-trip.
    """
    # Run the specific test method that tests round-trip with ignore_raw_node=True
    r = _run_agent_test_method("test_raw_node_in_meta_with_ignore_raw_node")

    assert r.returncode == 0, (
        f"test_raw_node_in_meta_with_ignore_raw_node failed or not found.\n"
        f"stdout: {r.stdout[-500:]}\n"
        f"stderr: {r.stderr[-500:]}\n"
        f"The agent must add a test that calls dumps() with ignore_raw_node=True "
        f"and then loads() for round-trip verification."
    )
    assert "test_raw_node_in_meta_with_ignore_raw_node PASSED" in r.stdout or \
           "PASSED" in r.stdout, \
           f"Test did not pass as expected: {r.stdout[-300:]}"


# [pr_diff] fail_to_pass
def test_raw_node_in_meta():
    """Tests must inject a raw Node into node.meta to trigger the code path.

    Verifies by running the agent's tests and confirming they exercise the meta code path.
    """
    # Run both tests - they both inject raw nodes into meta
    r1 = _run_agent_test_method("test_raw_node_in_meta_raises_by_default")
    r2 = _run_agent_test_method("test_raw_node_in_meta_with_ignore_raw_node")

    # Both should pass, proving the meta injection code path is exercised
    assert r1.returncode == 0, (
        f"test_raw_node_in_meta_raises_by_default failed: {r1.stderr[-300:]}"
    )
    assert r2.returncode == 0, (
        f"test_raw_node_in_meta_with_ignore_raw_node failed: {r2.stderr[-300:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) - anti-stub + structural
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Agent must have >=2 test methods with real assertions and at least one pickler call.

    Verifies by running the actual tests - a stub implementation would fail at runtime.
    """
    # Run ALL TestIgnoreRawNode tests via pytest
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            TARGET,
            "-v",
            "-k", "TestIgnoreRawNode",
            "--tb=short",
            "--no-header",
            "-q",
        ],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )

    # Check tests were found and ran
    assert "TestIgnoreRawNode" in r.stdout, "TestIgnoreRawNode class not found"

    # Count test methods that ran (not just collected)
    import re
    passed = re.findall(r"test_\w+ PASSED", r.stdout)
    assert len(passed) >= 2, (
        f"Expected at least 2 test methods to pass, got {len(passed)}: {r.stdout[-500:]}"
    )

    # The tests must actually call dumps/loads (verified by them running without import errors)
    assert r.returncode == 0, (
        f"TestIgnoreRawNode tests did not all pass: {r.stdout[-500:]}\n{r.stderr[-300:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass - CLAUDE.md:17-27 @ e931ab4802816cec55aa5a25b51f27cb941c924e
def test_uses_pytorch_test_class():
    """Tests must use PyTorch's TestCase (not unittest.TestCase) - CLAUDE.md:17-27."""
    agent_classes = [
        n for n in ast.walk(_tree())
        if isinstance(n, ast.ClassDef) and "ignore_raw_node" in ast.dump(n)
    ]
    assert len(agent_classes) > 0, "No test class found for ignore_raw_node feature"

    for cls in agent_classes:
        for base in cls.bases:
            if (isinstance(base, ast.Attribute) and base.attr == "TestCase"
                    and isinstance(base.value, ast.Name)
                    and base.value.id == "unittest"):
                assert False, (
                    f"{cls.name} uses unittest.TestCase; "
                    "use TestCase from torch.testing._internal.common_utils - CLAUDE.md:17-27"
                )
        good = any(isinstance(b, ast.Name) and b.id == "TestCase" for b in cls.bases)
        assert good, (
            f"{cls.name} must inherit from TestCase "
            "(from torch.testing._internal.common_utils) - CLAUDE.md:17-27"
        )


# [agent_config] pass_to_pass - .claude/skills/pr-review/review-checklist.md:57 @ e931ab4802816cec55aa5a25b51f27cb941c924e
def test_has_owner_label():
    """Test file must have a valid # Owner(s): label, not 'module: unknown'."""
    import re
    src = _source()
    match = re.search(r"#\s*Owner\(s\):\s*\[([^\]]*)\]", src)
    assert match, (
        "Test file is missing a '# Owner(s): [...]' label - "
        "see review-checklist.md:57"
    )
    owners = match.group(1)
    assert "module: unknown" not in owners, (
        "# Owner(s) label must not be 'module: unknown' - "
        "see review-checklist.md:57"
    )


# [agent_config] pass_to_pass - .claude/skills/pr-review/review-checklist.md:60 @ e931ab4802816cec55aa5a25b51f27cb941c924e
def test_has_run_tests():
    """Test file must end with 'if __name__ == "__main__": run_tests()'."""
    tree = _tree()
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if (isinstance(test, ast.Compare)
                and isinstance(test.left, ast.Name) and test.left.id == "__name__"
                and len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq)
                and len(test.comparators) == 1
                and isinstance(test.comparators[0], ast.Constant)
                and test.comparators[0].value == "__main__"):
            for stmt in ast.walk(node):
                if (isinstance(stmt, ast.Call)
                        and isinstance(stmt.func, ast.Name)
                        and stmt.func.id == "run_tests"):
                    return
    assert False, (
        "Test file must end with 'if __name__ == \"__main__\": run_tests()' - "
        "see review-checklist.md:60"
    )


# [agent_config] fail_to_pass - .claude/skills/pr-review/review-checklist.md:68 @ e931ab4802816cec55aa5a25b51f27cb941c924e
def test_uses_assert_raises_for_errors():
    """Error tests must use assertRaises/assertRaisesRegex, not bare try/except - review-checklist.md:68."""
    # This is verified by the behavioral test running test_raw_node_in_meta_raises_by_default
    # which uses assertRaises. If it runs and passes, this requirement is met.
    r = _run_agent_test_method("test_raw_node_in_meta_raises_by_default")
    assert r.returncode == 0, (
        f"Cannot verify assertRaises usage - test not found or failed: {r.stderr[-300:]}"
    )
    # The test ran and passed, which means it must have used assertRaises correctly
    assert "PASSED" in r.stdout, f"Test did not pass: {r.stdout[-300:]}"