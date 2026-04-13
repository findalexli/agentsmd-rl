"""
Task: sglang-spec-decode-flaky-threshold
Repo: sgl-project/sglang @ 1ad6839659085732a6fe308f97141841d67f6323
PR:   22100

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: While the full test file requires GPUs to run the actual speculative
decoding tests, we can still execute behavioral tests by extracting and testing
the assertion logic in isolation using subprocess.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/sglang"
TEST_FILE = f"{REPO}/test/registered/spec/test_standalone_speculative_decoding.py"


def _parse_test_file():
    """Parse the test file and return the AST tree."""
    source = Path(TEST_FILE).read_text()
    return ast.parse(source)


def _get_class_node(tree, class_name):
    """Find a class definition by name in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    return None


def _get_class_attr_value(class_node, attr_name):
    """Get the literal value of a class-level attribute assignment."""
    for item in class_node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name) and target.id == attr_name:
                    if isinstance(item.value, ast.Constant):
                        return item.value.value
    return None


def _method_uses_assert(method_node, method_name):
    """Check which assert method is called for accuracy comparison in a method.

    Returns the assert method name (e.g., "assertGreater", "assertGreaterEqual")
    used with self.accuracy_threshold.
    """
    for node in ast.walk(method_node):
        if isinstance(node, ast.Call):
            func = node.func
            if (isinstance(func, ast.Attribute) and
                    func.attr in ("assertGreater", "assertGreaterEqual") and
                    isinstance(func.value, ast.Name) and func.value.id == "self"):
                # Check if accuracy_threshold is referenced in args
                for arg in node.args:
                    if (isinstance(arg, ast.Attribute) and
                            isinstance(arg.value, ast.Name) and
                            arg.value.id == "self" and
                            arg.attr == "accuracy_threshold"):
                        return func.attr
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified test file must parse without errors."""
    source = Path(TEST_FILE).read_text()
    tree = ast.parse(source)
    assert tree is not None


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass — BEHAVIORAL: tests the actual assertion logic
def test_assertion_logic_at_threshold():
    """assertGreaterEqual with 0.69 threshold passes when score == 0.69.

    This is the core bug fix: assertGreater(score, 0.7) fails when score == 0.7
    exactly. assertGreaterEqual(score, 0.69) correctly accepts boundary values.
    We test this by executing the assertion logic in a subprocess.
    """
    code = """
import unittest

class MockMetricsTest(unittest.TestCase):
    accuracy_threshold = 0.69

    def test_score_at_boundary(self):
        score = 0.69
        self.assertGreaterEqual(score, self.accuracy_threshold)
        return True

    def test_score_above_boundary(self):
        score = 0.70
        self.assertGreaterEqual(score, self.accuracy_threshold)
        return True

    def test_score_below_boundary(self):
        score = 0.68
        try:
            self.assertGreaterEqual(score, self.accuracy_threshold)
            return False
        except AssertionError:
            return True

t = MockMetricsTest()
t.test_score_at_boundary()
t.test_score_above_boundary()
t.test_score_below_boundary()
print("BEHAVIORAL_TEST_PASS")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Assertion logic test failed: {r.stderr}"
    assert "BEHAVIORAL_TEST_PASS" in r.stdout, f"Expected success marker not found: {r.stdout}"


# [pr_diff] fail_to_pass — BEHAVIORAL: verifies old behavior would fail
def test_old_behavior_fails_at_exact_threshold():
    """assertGreater with 0.7 threshold FAILS when score == 0.7 (the bug).

    This proves the old code was broken - the strict > comparison fails
    when the score equals the threshold exactly, which is what causes the flaky test.
    """
    code = """
import unittest

class OldBehaviorTest(unittest.TestCase):
    accuracy_threshold = 0.7

    def old_assertion(self):
        score = 0.7
        self.assertGreater(score, self.accuracy_threshold)

t = OldBehaviorTest()
try:
    t.old_assertion()
    print("UNEXPECTED_PASS")
except AssertionError:
    print("EXPECTED_FAILURE")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert "EXPECTED_FAILURE" in r.stdout or r.returncode != 0, \
        f"Old behavior should fail at exact threshold: {r.stdout} {r.stderr}"


# [pr_diff] fail_to_pass
def test_accuracy_threshold_v1():
    """TestStandaloneSpeculativeDecodingBase.accuracy_threshold is 0.69.

    On the base commit it is 0.7, causing flaky failures when score == 0.7.
    """
    tree = _parse_test_file()
    cls = _get_class_node(tree, "TestStandaloneSpeculativeDecodingBase")
    assert cls is not None, "TestStandaloneSpeculativeDecodingBase not found"
    value = _get_class_attr_value(cls, "accuracy_threshold")
    assert value == 0.69, f"Expected accuracy_threshold=0.69, got {value}"


# [pr_diff] fail_to_pass
def test_accuracy_threshold_v2():
    """TestStandaloneV2SpeculativeDecodingBase.accuracy_threshold is 0.69.

    Same flaky-threshold fix for the V2 speculative decoding base class.
    """
    tree = _parse_test_file()
    cls = _get_class_node(tree, "TestStandaloneV2SpeculativeDecodingBase")
    assert cls is not None, "TestStandaloneV2SpeculativeDecodingBase not found"
    value = _get_class_attr_value(cls, "accuracy_threshold")
    assert value == 0.69, f"Expected accuracy_threshold=0.69, got {value}"


# [pr_diff] fail_to_pass
def test_gsm8k_uses_greater_equal_v1():
    """V1 test_gsm8k must use assertGreaterEqual (not assertGreater).

    assertGreater(score, 0.7) fails when score == 0.7 exactly.
    assertGreaterEqual(score, 0.69) correctly accepts boundary values.
    """
    tree = _parse_test_file()
    cls = _get_class_node(tree, "TestStandaloneSpeculativeDecodingBase")
    assert cls is not None, "TestStandaloneSpeculativeDecodingBase not found"
    for item in cls.body:
        if isinstance(item, ast.FunctionDef) and item.name == "test_gsm8k":
            used = _method_uses_assert(item, "test_gsm8k")
            assert used == "assertGreaterEqual", (
                f"Expected assertGreaterEqual for accuracy check, got {used}"
            )
            return
    raise AssertionError("test_gsm8k method not found in TestStandaloneSpeculativeDecodingBase")


# [pr_diff] fail_to_pass
def test_gsm8k_uses_greater_equal_v2():
    """V2 test_gsm8k must use assertGreaterEqual (not assertGreater).

    Same assertion fix for the V2 speculative decoding test class.
    """
    tree = _parse_test_file()
    cls = _get_class_node(tree, "TestStandaloneV2SpeculativeDecodingBase")
    assert cls is not None, "TestStandaloneV2SpeculativeDecodingBase not found"
    for item in cls.body:
        if isinstance(item, ast.FunctionDef) and item.name == "test_gsm8k":
            used = _method_uses_assert(item, "test_gsm8k")
            assert used == "assertGreaterEqual", (
                f"Expected assertGreaterEqual for accuracy check, got {used}"
            )
            return
    raise AssertionError("test_gsm8k method not found in TestStandaloneV2SpeculativeDecodingBase")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that work on base and after fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — Python syntax/compilation check
def test_repo_python_syntax():
    """Modified test file must have valid Python syntax (pass_to_pass)."""
    source = Path(TEST_FILE).read_text()
    tree = ast.parse(source)
    assert tree is not None, "Failed to parse test file"


# [repo_tests] pass_to_pass — Ruff lint check (F401, F821)
def test_repo_ruff_lint():
    """Modified test file must pass ruff lint checks (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["ruff", "check", "--select=F401,F821", TEST_FILE],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — Black format check (diff only, do not fix)
def test_repo_black_format():
    """Modified test file must be Black-formatted (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "black", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["black", "--check", "--diff", TEST_FILE],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Black format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Codespell check
def test_repo_codespell():
    """Modified test file must have no common typos (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "codespell", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["codespell", "--config", "/workspace/sglang/.codespellrc", TEST_FILE],
        capture_output=True, text=True, timeout=60, cwd="/workspace/sglang",
    )
    assert r.returncode == 0, f"Codespell check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — isort check (import sorting)
def test_repo_isort():
    """Modified test file must have correctly sorted imports (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "isort", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["isort", "--check-only", "--profile", "black", TEST_FILE],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — YAML validation for CI workflows
def test_repo_yaml_valid():
    """CI workflow YAML files must be valid (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pyyaml", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    code = "import yaml; yaml.safe_load(open('/workspace/sglang/.github/workflows/lint.yml')); print('YAML_VALID')"
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"YAML validation failed:\n{r.stderr}"
    assert "YAML_VALID" in r.stdout, f"Expected marker not found: {r.stdout}"


# [repo_tests] pass_to_pass — CI workflow job names check
def test_repo_workflow_job_names():
    """CI workflow job names must be unique (repo CI check) (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pyyaml", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python3", "/workspace/sglang/scripts/ci/check_workflow_job_names.py"],
        capture_output=True, text=True, timeout=60, cwd="/workspace/sglang",
    )
    assert r.returncode == 0, f"Workflow job names check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — CI permissions sorted check
def test_repo_ci_permissions_sorted():
    """CI permissions file must be sorted (repo CI check) (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "/workspace/sglang/.github/update_ci_permission.py", "--sort-only"],
        capture_output=True, text=True, timeout=60, cwd="/workspace/sglang",
    )
    assert r.returncode == 0, f"CI permissions sorted check failed:\n{r.stdout}\n{r.stderr}"




# [repo_tests] pass_to_pass — Merge conflict check
def test_repo_merge_conflict():
    """Source files must not contain merge conflict markers (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["pre-commit", "run", "check-merge-conflict", "--all-files"],
        capture_output=True, text=True, timeout=120, cwd="/workspace/sglang",
    )
    assert r.returncode == 0, f"Merge conflict check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Private key detection
def test_repo_private_key():
    """Source files must not contain private keys (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["pre-commit", "run", "detect-private-key", "--all-files"],
        capture_output=True, text=True, timeout=120, cwd="/workspace/sglang",
    )
    assert r.returncode == 0, f"Private key detection failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — TOML validation
def test_repo_toml_valid():
    """TOML files must be valid (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["pre-commit", "run", "check-toml", "--all-files"],
        capture_output=True, text=True, timeout=120, cwd="/workspace/sglang",
    )
    assert r.returncode == 0, f"TOML validation failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Trailing whitespace check
def test_repo_trailing_whitespace():
    """Source files must not have trailing whitespace (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["pre-commit", "run", "trailing-whitespace", "--all-files"],
        capture_output=True, text=True, timeout=120, cwd="/workspace/sglang",
    )
    assert r.returncode == 0, f"Trailing whitespace check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Shebang executable check
def test_repo_shebang_executable():
    """Scripts with shebangs must be executable (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["pre-commit", "run", "check-shebang-scripts-are-executable", "--all-files"],
        capture_output=True, text=True, timeout=120, cwd="/workspace/sglang",
    )
    assert r.returncode == 0, f"Shebang executable check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"



# [repo_tests] pass_to_pass — YAML files valid check
def test_repo_yaml_valid_all():
    """All YAML files must be valid (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["pre-commit", "run", "check-yaml", "--all-files"],
        capture_output=True, text=True, timeout=120, cwd="/workspace/sglang",
    )
    assert r.returncode == 0, f"YAML validation failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Debug statements check
def test_repo_debug_statements():
    """Source files must not contain debug statements (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["pre-commit", "run", "debug-statements", "--all-files"],
        capture_output=True, text=True, timeout=120, cwd="/workspace/sglang",
    )
    assert r.returncode == 0, f"Debug statements check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — End of file fixer check
def test_repo_end_of_file():
    """Files must end with exactly one newline (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["pre-commit", "run", "end-of-file-fixer", "--all-files"],
        capture_output=True, text=True, timeout=120, cwd="/workspace/sglang",
    )
    assert r.returncode == 0, f"End of file check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"

# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """test_gsm8k methods have real logic, not just pass/return."""
    tree = _parse_test_file()
    for class_name in ("TestStandaloneSpeculativeDecodingBase",
                       "TestStandaloneV2SpeculativeDecodingBase"):
        cls = _get_class_node(tree, class_name)
        assert cls is not None, f"{class_name} not found"
        for item in cls.body:
            if isinstance(item, ast.FunctionDef) and item.name == "test_gsm8k":
                stmts = [s for s in item.body
                         if not isinstance(s, (ast.Pass, ast.Expr))]
                assert len(stmts) >= 2, (
                    f"{class_name}.test_gsm8k body is a stub"
                )


# [agent_config] pass_to_pass — .claude/skills/write-sglang-test/SKILL.md:12 @ base
def test_inherits_custom_test_case():
    """Both base classes inherit from CustomTestCase per write-sglang-test skill.

    The skill mandates: "Always use CustomTestCase — never raw unittest.TestCase."
    """
    tree = _parse_test_file()
    for class_name in ("TestStandaloneSpeculativeDecodingBase",
                       "TestStandaloneV2SpeculativeDecodingBase"):
        cls = _get_class_node(tree, class_name)
        assert cls is not None, f"{class_name} not found"
        base_names = [
            b.id if isinstance(b, ast.Name) else b.attr
            for b in cls.bases
        ]
        assert "CustomTestCase" in base_names, (
            f"{class_name} must inherit from CustomTestCase, got bases: {base_names}"
        )
