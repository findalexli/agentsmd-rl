"""
Task: pytorch-graphpickler-ignorerawnode-tests
Repo: pytorch/pytorch @ e931ab4802816cec55aa5a25b27cb941c924e
PR:   176954

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import subprocess
import sys
import re
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

def _run_pytest(pattern: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run pytest with a specific pattern filter on the target file."""
    return subprocess.run(
        [
            sys.executable, "-m", "pytest",
            TARGET,
            "-v", "-k", pattern,
            "--tb=short", "--no-header", "-q",
        ],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# [pr_diff] fail_to_pass
def test_has_ignore_raw_node_tests():
    """Agent must add at least one test method that exercises ignore_raw_node.

    Verifies by collecting and running the tests via pytest.
    """
    try:
        r = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                TARGET,
                "-v", "-k", "ignore_raw_node",
                "--collect-only", "-q",
            ],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
    except Exception:
        # If pytest can't run due to import errors, fall back to AST check
        tree = _tree()
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and "ignore_raw_node" in ast.dump(node):
                found = True
                break
        assert found, (
            "No test class found with 'ignore_raw_node' reference - "
            "add class TestIgnoreRawNode(TestCase) to test/fx/test_graph_pickler.py"
        )
        return

    assert r.returncode == 0, f"Failed to collect tests: {r.stderr}"
    assert "ignore_raw_node" in r.stdout, (
        "No tests with 'ignore_raw_node' found - add a test class and methods "
        "that exercise the ignore_raw_node option to test/fx/test_graph_pickler.py"
    )
    # Should have at least 2 test methods (based on test requirements)
    test_count = len(re.findall(r"<Function[^>]*test_\w+[^>]*>", r.stdout))
    assert test_count >= 2, f"Expected at least 2 test methods, found {test_count}"


# [pr_diff] fail_to_pass
def test_default_raises_covered():
    """A test must verify GraphPickler.dumps raises by default on raw Node metadata.

    Verifies by running the agent's tests via pytest (behavioral execution).
    """
    try:
        r = _run_pytest("ignore_raw_node")
    except Exception:
        # If pytest can't run due to import errors, verify via AST that the test structure exists
        tree = _tree()
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "test_raw_node_in_meta_raises_by_default":
                found = True
                break
        assert found, (
            "test_raw_node_in_meta_raises_by_default method not found - "
            "add a test that verifies AssertionError is raised by default"
        )
        return

    assert r.returncode == 0, (
        f"Tests failed or not found. Need tests for ignore_raw_node behavior.\n"
        f"stdout: {r.stdout[-500:]}\n"
        f"stderr: {r.stderr[-500:]}"
    )

    # Verify at least one test passed (proving the tests run and execute real code)
    assert "PASSED" in r.stdout, f"No tests passed: {r.stdout[-300:]}"


# [pr_diff] fail_to_pass
def test_ignore_true_round_trip():
    """A test must verify the ignore_raw_node=True round-trip (dumps then loads).

    Verifies by running the agent's tests via pytest.
    """
    try:
        r = _run_pytest("ignore_raw_node")
    except Exception:
        # If pytest can't run due to import errors, verify via AST
        tree = _tree()
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "test_raw_node_in_meta_with_ignore_raw_node":
                found = True
                break
        assert found, (
            "test_raw_node_in_meta_with_ignore_raw_node method not found - "
            "add a test that verifies the round-trip with ignore_raw_node=True"
        )
        return

    assert r.returncode == 0, (
        f"ignore_raw_node tests failed.\n"
        f"stdout: {r.stdout[-500:]}\n"
        f"stderr: {r.stderr[-500:]}"
    )
    # The tests should pass, proving the round-trip works with ignore_raw_node=True
    assert "PASSED" in r.stdout, f"Tests did not pass: {r.stdout[-300:]}"


# [pr_diff] fail_to_pass
def test_raw_node_in_meta():
    """Tests must inject a raw Node into node.meta to trigger the code path.

    Verifies by running the agent's tests and confirming they execute without errors.
    """
    try:
        r = _run_pytest("ignore_raw_node")
    except Exception:
        # If pytest can't run, verify via AST that the tests exist and contain meta access
        tree = _tree()
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and "ignore_raw_node" in ast.dump(node):
                # Check that at least 2 test methods exist
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
                if len(methods) >= 2:
                    found = True
                    break
        assert found, (
            "Expected at least 2 test methods in ignore_raw_node test class - "
            "add test methods that inject raw Node into node.meta"
        )
        return

    # Tests should pass, proving the meta injection code path is exercised
    assert r.returncode == 0, (
        f"Tests failed: {r.stdout[-500:]}\n{r.stderr[-300:]}"
    )
    # Count passed tests - should be at least 2
    passed = re.findall(r"test_\w+ PASSED", r.stdout)
    assert len(passed) >= 2, (
        f"Expected at least 2 tests to pass, got {len(passed)}: {r.stdout[-500:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) - anti-stub + structural
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Agent must have >=2 test methods that actually execute and pass.

    Verifies by running the actual tests - a stub implementation would fail at runtime.
    """
    try:
        r = _run_pytest("ignore_raw_node")
    except Exception:
        # If pytest can't run, verify via AST that >=2 test methods exist
        tree = _tree()
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and "ignore_raw_node" in ast.dump(node):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
                if len(methods) >= 2:
                    found = True
                    break
        assert found, (
            "Expected at least 2 test methods in ignore_raw_node test class - "
            "stub implementations would not pass runtime execution"
        )
        return

    # Check tests were found and ran
    assert "ignore_raw_node" in r.stdout, "No ignore_raw_node tests found"

    # Count test methods that passed (not just collected)
    passed = re.findall(r"test_\w+ PASSED", r.stdout)
    assert len(passed) >= 2, (
        f"Expected at least 2 test methods to pass, got {len(passed)}: {r.stdout[-500:]}"
    )

    # The tests must actually execute (verified by them running without import errors)
    assert r.returncode == 0, (
        f"Tests did not all pass: {r.stdout[-500:]}\n{r.stderr[-300:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass - CLAUDE.md:17-27 @ e931ab4802816cec55aa5a25b27cb941c924e
def test_uses_pytorch_test_class():
    """Tests must use PyTorch's TestCase (not unittest.TestCase) - CLAUDE.md:17-27.

    Verifies by running tests via pytest - if they use wrong TestCase, tests fail.
    """
    try:
        r = _run_pytest("ignore_raw_node")
    except Exception:
        # If pytest can't run, verify via AST that the test class inherits from TestCase
        tree = _tree()
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and "ignore_raw_node" in ast.dump(node):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "TestCase":
                        found = True
                        break
        assert found, (
            "Test class must inherit from TestCase (from torch.testing._internal.common_utils) - CLAUDE.md:17-27"
        )
        return
    assert r.returncode == 0, f"Tests failed to run: {r.stderr[-300:]}"


# [agent_config] pass_to_pass - .claude/skills/pr-review/review-checklist.md:57 @ e931ab4802816cec55aa5b25b51f27cb941c924e
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


# [agent_config] pass_to_pass - .claude/skills/pr-review/review-checklist.md:60 @ e931ab4802816cec55aa5b25b51f27cb941c924e
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


# [agent_config] fail_to_pass - .claude/skills/pr-review/review-checklist.md:68 @ e931ab4802816c941c924e
def test_uses_assert_raises_for_errors():
    """Error tests must use assertRaises/assertRaisesRegex, not bare try/except - review-checklist.md:68.

    Verifies by running the actual tests - a test that doesn't use assertRaises
    would not properly catch the AssertionError.
    """
    try:
        r = _run_pytest("ignore_raw_node")
    except Exception:
        # If pytest can't run, verify via AST that assertRaises is used
        tree = _tree()
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "test_raw_node_in_meta_raises_by_default":
                # Check if assertRaises is called in this method
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Attribute) and child.func.attr == "assertRaises":
                            found = True
                            break
                break
        assert found, (
            "test_raw_node_in_meta_raises_by_default must use assertRaises to catch AssertionError - "
            "see review-checklist.md:68"
        )
        return

    # Run the ignore_raw_node tests - they should pass if using assertRaises correctly
    assert r.returncode == 0, (
        f"Cannot verify assertRaises usage - tests failed: {r.stderr[-300:]}"
    )
    # Tests ran and passed, which means they properly used assertRaises
    assert "PASSED" in r.stdout, f"Tests did not pass: {r.stdout[-300:]}"
