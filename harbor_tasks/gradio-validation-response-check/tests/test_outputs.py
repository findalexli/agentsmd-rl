"""
Task: gradio-validation-response-check
Repo: gradio @ 0cbbbce8348cbb3254d4f93c48580151fe048daf
PR:   13205

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
import inspect
import ast
from pathlib import Path
from typing import Any

REPO = "/workspace/gradio"


def _get_process_validation_response_func():
    """
    Read and extract the actual process_validation_response function from the repo file.
    This avoids heavy gradio dependencies while testing the real code.
    """
    queueing_path = Path(REPO) / "gradio" / "queueing.py"
    content = queueing_path.read_text()
    
    # Parse the AST
    tree = ast.parse(content)
    
    # Find the function definition
    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "process_validation_response":
            func_node = node
            break
    
    if func_node is None:
        raise RuntimeError("Could not find process_validation_response function in queueing.py")
    
    # Get the source lines
    with open(queueing_path) as f:
        lines = f.readlines()
    
    # Extract the function source
    start_line = func_node.lineno - 1  # AST uses 1-indexed line numbers
    end_line = func_node.end_lineno
    func_source = "".join(lines[start_line:end_line])
    
    # Replace the BlockFunction type hint with Any to avoid import issues
    func_source = func_source.replace("BlockFunction", "Any")
    
    # Create namespace with required imports
    namespace = {'inspect': inspect, 'Any': Any}
    
    # Execute the function definition in the namespace
    exec(compile(ast.parse(func_source), '<string>', 'exec'), namespace)
    
    return namespace['process_validation_response']


# Load the function from the repo
_process_validation_response = _get_process_validation_response_func()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", "gradio/queueing.py"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax error:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_dict_invalid_response_detected():
    """Dict validation_response with is_valid=False must be detected as invalid."""
    # Single dict response indicating invalid input
    response = {"is_valid": False, "message": "Input out of range"}
    all_valid, data = _process_validation_response(response, None)
    assert all_valid is False, (
        f"Expected all_valid=False for invalid dict response, got {all_valid}"
    )


# [pr_diff] fail_to_pass
def test_dict_invalid_response_data_preserved():
    """The invalid dict response must appear in the returned validation_data list."""
    response = {"is_valid": False, "message": "Value too large"}
    all_valid, data = _process_validation_response(response, None)
    assert any(
        d.get("is_valid") is False and d.get("message") == "Value too large"
        for d in data
    ), f"Invalid response not preserved in output: {data}"


# [pr_diff] fail_to_pass
def test_dict_invalid_varied_inputs():
    """Multiple different dict inputs with is_valid=False all detected."""
    cases = [
        {"is_valid": False, "message": "Missing required field"},
        {"is_valid": False, "message": ""},
        {"is_valid": False, "message": "Type mismatch", "extra_key": 42},
    ]
    for response in cases:
        all_valid, data = _process_validation_response(response, None)
        assert all_valid is False, (
            f"Expected all_valid=False for {response}, got {all_valid}"
        )
        assert len(data) == 1, (
            f"Expected exactly 1 entry in data for dict input, got {len(data)}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_list_validation_response_works():
    """List validation responses are still processed correctly."""
    # All-valid list
    response = [
        {"__type__": "validate", "is_valid": True, "message": ""},
        {"__type__": "validate", "is_valid": True, "message": ""},
    ]
    all_valid, data = _process_validation_response(response, None)
    assert all_valid is True, f"Expected all_valid=True for valid list, got {all_valid}"
    assert len(data) == 2

    # List with one invalid entry
    response_invalid = [
        {"__type__": "validate", "is_valid": True, "message": ""},
        {"__type__": "validate", "is_valid": False, "message": "bad"},
    ]
    all_valid2, data2 = _process_validation_response(response_invalid, None)
    assert all_valid2 is False, (
        f"Expected all_valid=False for list with invalid entry, got {all_valid2}"
    )


# [pr_diff] pass_to_pass
def test_dict_valid_fallthrough():
    """Dict without is_valid=False falls through to the else branch (treated as valid)."""
    # Dict with is_valid=True
    response = {"is_valid": True, "message": "all good"}
    all_valid, data = _process_validation_response(response, None)
    assert all_valid is True, (
        f"Expected all_valid=True for valid dict, got {all_valid}"
    )

    # Dict with no is_valid key at all
    response2 = {"some_key": "some_value"}
    all_valid2, data2 = _process_validation_response(response2, None)
    assert all_valid2 is True, (
        f"Expected all_valid=True for dict without is_valid, got {all_valid2}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:43 @ 0cbbbce8348cbb3254d4f93c48580151fe048daf
def test_ruff_format_check():
    """Modified Python file must pass ruff linting (AGENTS.md Code Style rule)."""
    r = subprocess.run(
        ["ruff", "check", "gradio/queueing.py", "--select=E,W,F", "--ignore=E501", "--no-fix"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"ruff check failed on gradio/queueing.py:\n{r.stdout.decode()}"
    )


# ---------------------------------------------------------------------------
# Repo CI tests (pass_to_pass) — repo_tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check_queueing():
    """Repo's ruff lint passes on modified file gradio/queueing.py (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "gradio/queueing.py", "--select=E,W,F", "--ignore=E501", "--no-fix"],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, f"ruff check failed on gradio/queueing.py:\n{r.stdout.decode()[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format_check_queueing():
    """Repo's ruff format check passes on modified file gradio/queueing.py (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", "gradio/queueing.py"],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, f"ruff format check failed on gradio/queueing.py:\n{r.stderr.decode()[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_py_compile_queueing():
    """Modified file gradio/queueing.py compiles without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", "gradio/queueing.py"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in gradio/queueing.py:\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass
def test_repo_ruff_check_gradio_core():
    """Repo's ruff lint passes on core gradio/ directory (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "gradio", "--select=E,W,F", "--ignore=E501", "--no-fix"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, f"ruff check failed on gradio/:\n{r.stdout.decode()[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_block_function_compile():
    """Related file gradio/block_function.py compiles without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", "gradio/block_function.py"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in gradio/block_function.py:\n{r.stderr.decode()}"
