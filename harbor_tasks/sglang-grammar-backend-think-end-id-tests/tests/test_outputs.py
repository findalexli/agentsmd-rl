"""
Task: sglang-grammar-backend-think-end-id-tests
Repo: sgl-project/sglang @ 5dd2c243eb52dfd04f27b998e2595fe0c66437b1
PR:   #22158

Tests verify that create_grammar_backend test calls correctly pass think_end_id
as an explicit keyword argument instead of setting tokenizer.think_end_id.

NOTE: sglang imports torch at top level, so we cannot import modules directly.
Tests use AST analysis to verify correct API usage patterns.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/sglang"
TEST_FILE = f"{REPO}/test/registered/unit/constrained/test_base_grammar_backend.py"
PROD_FILE = f"{REPO}/python/sglang/srt/constrained/base_grammar_backend.py"


def _get_class_methods(filepath, class_name):
    """Parse file and return dict of method_name -> ast.FunctionDef for a class."""
    source = Path(filepath).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {
                item.name: item
                for item in node.body
                if isinstance(item, ast.FunctionDef)
            }
    return {}


def _get_calls_in_method(method_node, func_name):
    """Find all Call nodes for func_name within a method."""
    calls = []
    for node in ast.walk(method_node):
        if isinstance(node, ast.Call):
            func = node.func
            # Match direct function call: func_name(...)
            if isinstance(func, ast.Name) and func.id == func_name:
                calls.append(node)
    return calls


def _has_keyword_arg(call_node, keyword_name):
    """Check if a Call node has a specific keyword argument."""
    for kw in call_node.keywords:
        if kw.arg == keyword_name:
            return True
    return False


def _get_keyword_value(call_node, keyword_name):
    """Get the value node of a keyword argument, or None."""
    for kw in call_node.keywords:
        if kw.arg == keyword_name:
            return kw.value
    return None


def _count_assignments(method_node, target_attr):
    """Count attribute assignments like self.x = ... or tokenizer.think_end_id = 42."""
    count = 0
    for node in ast.walk(method_node):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (isinstance(target, ast.Attribute) and
                        target.attr == target_attr):
                    count += 1
    return count


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified test file must parse without errors."""
    source = Path(TEST_FILE).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_think_end_id_passed_in_reasoner_test():
    """test_reasoner_wrapping_on_builtin_backend must pass think_end_id=42 to create_grammar_backend."""
    methods = _get_class_methods(TEST_FILE, "TestCreateGrammarBackend")
    assert "test_reasoner_wrapping_on_builtin_backend" in methods, \
        "test_reasoner_wrapping_on_builtin_backend method missing"

    method = methods["test_reasoner_wrapping_on_builtin_backend"]
    calls = _get_calls_in_method(method, "create_grammar_backend")
    assert len(calls) >= 1, "No create_grammar_backend call found in test_reasoner_wrapping_on_builtin_backend"

    # At least one call must pass think_end_id=42
    found = False
    for call in calls:
        if _has_keyword_arg(call, "think_end_id"):
            val = _get_keyword_value(call, "think_end_id")
            # Check the value is 42 (ast.Constant for Python 3.8+)
            if isinstance(val, ast.Constant) and val.value == 42:
                found = True
                break
    assert found, "No create_grammar_backend(..., think_end_id=42) call found"


# [pr_diff] fail_to_pass
def test_think_end_id_none_in_no_wrapping_test():
    """test_no_reasoner_wrapping_without_think_end_id must pass think_end_id=None."""
    methods = _get_class_methods(TEST_FILE, "TestCreateGrammarBackend")
    assert "test_no_reasoner_wrapping_without_think_end_id" in methods, \
        "test_no_reasoner_wrapping_without_think_end_id method missing"

    method = methods["test_no_reasoner_wrapping_without_think_end_id"]
    calls = _get_calls_in_method(method, "create_grammar_backend")
    assert len(calls) >= 1, "No create_grammar_backend call found"

    found = False
    for call in calls:
        if _has_keyword_arg(call, "think_end_id"):
            val = _get_keyword_value(call, "think_end_id")
            if isinstance(val, ast.Constant) and val.value is None:
                found = True
                break
    assert found, "No create_grammar_backend(..., think_end_id=None) call found"


# [pr_diff] fail_to_pass
def test_think_end_id_passed_in_no_parser_test():
    """test_no_reasoner_wrapping_without_reasoning_parser must pass think_end_id=42."""
    methods = _get_class_methods(TEST_FILE, "TestCreateGrammarBackend")
    assert "test_no_reasoner_wrapping_without_reasoning_parser" in methods, \
        "test_no_reasoner_wrapping_without_reasoning_parser method missing"

    method = methods["test_no_reasoner_wrapping_without_reasoning_parser"]
    calls = _get_calls_in_method(method, "create_grammar_backend")
    assert len(calls) >= 1, "No create_grammar_backend call found"

    found = False
    for call in calls:
        if _has_keyword_arg(call, "think_end_id"):
            val = _get_keyword_value(call, "think_end_id")
            if isinstance(val, ast.Constant) and val.value == 42:
                found = True
                break
    assert found, "No create_grammar_backend(..., think_end_id=42) call found"


# [pr_diff] fail_to_pass
def test_no_tokenizer_think_end_id_assignment():
    """tokenizer.think_end_id = N assignments must be removed from reasoner tests.

    The old API set tokenizer.think_end_id as an attribute. The new API passes
    it as an explicit keyword argument. Setting it on the tokenizer is dead code.
    """
    methods = _get_class_methods(TEST_FILE, "TestCreateGrammarBackend")

    # These four methods previously had tokenizer.think_end_id = 42
    method_names = [
        "test_custom_backend_skips_reasoner_wrapping",
        "test_reasoner_wrapping_on_builtin_backend",
        "test_no_reasoner_wrapping_without_think_end_id",
        "test_no_reasoner_wrapping_without_reasoning_parser",
    ]

    for name in method_names:
        assert name in methods, f"{name} method missing"
        count = _count_assignments(methods[name], "think_end_id")
        assert count == 0, \
            f"{name} still has {count} assignment(s) to .think_end_id — should be removed"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_production_function_has_think_end_id_param():
    """Production create_grammar_backend must accept think_end_id parameter.

    This is a sanity check that the base commit has the updated API.
    """
    source = Path(PROD_FILE).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "create_grammar_backend":
            param_names = [arg.arg for arg in node.args.args]
            kwonly_names = [arg.arg for arg in node.args.kwonlyargs]
            assert "think_end_id" in param_names or "think_end_id" in kwonly_names, \
                f"create_grammar_backend does not accept think_end_id. Params: {param_names}, kwonly: {kwonly_names}"
            return
    raise AssertionError("create_grammar_backend function not found in production code")


# [static] pass_to_pass
def test_test_methods_preserved():
    """All original test methods must still exist (agent didn't delete tests)."""
    methods = _get_class_methods(TEST_FILE, "TestCreateGrammarBackend")
    required = [
        "test_reasoner_wrapping_on_builtin_backend",
        "test_no_reasoner_wrapping_without_think_end_id",
        "test_no_reasoner_wrapping_without_reasoning_parser",
        "test_custom_backend_skips_reasoner_wrapping",
    ]
    for name in required:
        assert name in methods, f"Required test method {name} was deleted"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_syntax_test_file():
    """Test file must have valid Python syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"import ast; ast.parse(open('{TEST_FILE}').read())"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in test file:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_test_file():
    """Test file must pass ruff linting (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["ruff", "check", "--select=E9,F63,F7,F82", TEST_FILE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff check failed on test file:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_black_test_file():
    """Test file must pass black formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "black", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["black", "--check", TEST_FILE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Black check failed on test file:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_prod_file():
    """Production file must pass ruff linting (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["ruff", "check", "--select=E9,F63,F7,F82", PROD_FILE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff check failed on production file:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_black_prod_file():
    """Production file must pass black formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "black", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["black", "--check", PROD_FILE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Black check failed on production file:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_isort_test_file():
    """Test file must pass isort import sorting check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "isort", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["isort", "--check-only", TEST_FILE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"isort check failed on test file:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_isort_prod_file():
    """Production file must pass isort import sorting check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "isort", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["isort", "--check-only", PROD_FILE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"isort check failed on production file:\n{r.stdout}{r.stderr}"
