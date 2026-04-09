"""
Task: gradio-validation-response-check
Repo: gradio @ 0cbbbce8348cbb3254d4f93c48580151fe048daf
PR:   13205

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/gradio"


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
    sys.path.insert(0, REPO)
    from gradio.queueing import process_validation_response

    # Single dict response indicating invalid input
    response = {"is_valid": False, "message": "Input out of range"}
    all_valid, data = process_validation_response(response)
    assert all_valid is False, (
        f"Expected all_valid=False for invalid dict response, got {all_valid}"
    )


# [pr_diff] fail_to_pass
def test_dict_invalid_response_data_preserved():
    """The invalid dict response must appear in the returned validation_data list."""
    sys.path.insert(0, REPO)
    from gradio.queueing import process_validation_response

    response = {"is_valid": False, "message": "Value too large"}
    all_valid, data = process_validation_response(response)
    assert any(
        d.get("is_valid") is False and d.get("message") == "Value too large"
        for d in data
    ), f"Invalid response not preserved in output: {data}"


# [pr_diff] fail_to_pass
def test_dict_invalid_varied_inputs():
    """Multiple different dict inputs with is_valid=False all detected."""
    sys.path.insert(0, REPO)
    from gradio.queueing import process_validation_response

    cases = [
        {"is_valid": False, "message": "Missing required field"},
        {"is_valid": False, "message": ""},
        {"is_valid": False, "message": "Type mismatch", "extra_key": 42},
    ]
    for response in cases:
        all_valid, data = process_validation_response(response)
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
    sys.path.insert(0, REPO)
    from gradio.queueing import process_validation_response

    # All-valid list
    response = [
        {"__type__": "validate", "is_valid": True, "message": ""},
        {"__type__": "validate", "is_valid": True, "message": ""},
    ]
    all_valid, data = process_validation_response(response)
    assert all_valid is True, f"Expected all_valid=True for valid list, got {all_valid}"
    assert len(data) == 2

    # List with one invalid entry
    response_invalid = [
        {"__type__": "validate", "is_valid": True, "message": ""},
        {"__type__": "validate", "is_valid": False, "message": "bad"},
    ]
    all_valid2, data2 = process_validation_response(response_invalid)
    assert all_valid2 is False, (
        f"Expected all_valid=False for list with invalid entry, got {all_valid2}"
    )


# [pr_diff] pass_to_pass
def test_dict_valid_fallthrough():
    """Dict without is_valid=False falls through to the else branch (treated as valid)."""
    sys.path.insert(0, REPO)
    from gradio.queueing import process_validation_response

    # Dict with is_valid=True
    response = {"is_valid": True, "message": "all good"}
    all_valid, data = process_validation_response(response)
    assert all_valid is True, (
        f"Expected all_valid=True for valid dict, got {all_valid}"
    )

    # Dict with no is_valid key at all
    response2 = {"some_key": "some_value"}
    all_valid2, data2 = process_validation_response(response2)
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
        ["ruff", "check", "gradio/queueing.py", "--select=E,W,F", "--no-fix"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"ruff check failed on gradio/queueing.py:\n{r.stdout.decode()}"
    )
