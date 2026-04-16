"""
Test suite for superset-mcp-execute-sql-limit-suggestion task.

Tests that the execute_sql tool's error message properly suggests the limit parameter
when responses are too large.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/superset")


def _load_token_utils():
    """Load token_utils module directly without going through superset package."""
    token_utils_path = REPO / "superset" / "mcp_service" / "utils" / "token_utils.py"
    spec = importlib.util.spec_from_file_location("token_utils", token_utils_path)
    token_utils = importlib.util.module_from_spec(spec)
    sys.modules["token_utils"] = token_utils
    spec.loader.exec_module(token_utils)
    return token_utils


def test_execute_sql_suggests_tool_limit_parameter_when_not_set():
    """
    When execute_sql response is too large and no limit is set,
    should suggest using the execute_sql 'limit' parameter (fail_to_pass).

    The fix adds a suggestion like:
    "Use the 'limit' parameter (e.g., limit=100) to cap the number of rows returned"
    """
    token_utils = _load_token_utils()

    suggestions = token_utils.generate_size_reduction_suggestions(
        tool_name="execute_sql",
        params={"sql": "SELECT * FROM large_table", "database_id": 1},
        estimated_tokens=50000,
        token_limit=25000,
    )

    combined = " ".join(suggestions).lower()

    # Must suggest the tool's limit parameter (not just SQL LIMIT)
    # The fix adds: "Use the 'limit' parameter (e.g., limit=100)"
    assert "limit' parameter" in combined or "limit=" in combined, (
        f"Should suggest using the tool's 'limit' parameter when not set. Got: {suggestions}"
    )


def test_execute_sql_suggests_limit_param_for_different_queries():
    """
    Test that execute_sql suggests the limit parameter for different SQL queries (fail_to_pass).
    """
    token_utils = _load_token_utils()

    # Test with a different SQL query
    suggestions = token_utils.generate_size_reduction_suggestions(
        tool_name="execute_sql",
        params={"sql": "SELECT id, name, email FROM customers WHERE active = true"},
        estimated_tokens=45000,
        token_limit=20000,
    )

    combined = " ".join(suggestions).lower()

    # Should suggest the tool's limit parameter
    assert "limit' parameter" in combined or "limit=" in combined, (
        f"Should suggest using 'limit' parameter. Got: {suggestions}"
    )


def test_execute_sql_no_duplicate_limit_suggestion_when_already_set():
    """
    When limit param is already set, should NOT suggest adding it again (fail_to_pass).
    The fix adds conditional logic to skip the limit parameter suggestion when limit is already set.
    """
    token_utils = _load_token_utils()

    # Test with limit NOT set - should have limit parameter suggestion
    suggestions_without_limit = token_utils.generate_size_reduction_suggestions(
        tool_name="execute_sql",
        params={"sql": "SELECT * FROM table"},
        estimated_tokens=50000,
        token_limit=25000,
    )

    # Test with limit already set - should NOT suggest adding it
    suggestions_with_limit = token_utils.generate_size_reduction_suggestions(
        tool_name="execute_sql",
        params={"sql": "SELECT * FROM table", "limit": 500},
        estimated_tokens=50000,
        token_limit=25000,
    )

    combined_without = " ".join(suggestions_without_limit).lower()
    combined_with = " ".join(suggestions_with_limit).lower()

    # Without limit: should suggest the limit parameter
    assert "limit' parameter" in combined_without or "limit=" in combined_without, (
        f"Should suggest limit parameter when not set. Got: {suggestions_without_limit}"
    )

    # With limit already set: should have FEWER or same suggestions
    # The key is that we shouldn't be suggesting "use the limit parameter" when it's already used
    # Count mentions of "execute_sql" and "limit' parameter" which is the specific suggestion added by the fix
    specific_suggestion = "execute_sql 'limit' parameter"

    has_specific_without = specific_suggestion in combined_without
    has_specific_with = specific_suggestion in combined_with

    # When limit is already set, should NOT have the "use execute_sql 'limit' parameter" suggestion
    # OR should have fewer total suggestions
    assert not has_specific_with or len(suggestions_with_limit) < len(suggestions_without_limit), (
        f"When limit is already set, should not suggest 'Use the execute_sql limit parameter'.\n"
        f"With limit: {suggestions_with_limit}\nWithout limit: {suggestions_without_limit}"
    )


def test_execute_sql_limit_suggestion_with_varying_inputs():
    """
    Test with varying SQL queries to ensure limit suggestion works consistently (fail_to_pass).
    """
    token_utils = _load_token_utils()

    test_cases = [
        {"sql": "SELECT * FROM orders WHERE status='pending'"},
        {"sql": "SELECT id, name FROM customers"},
        {"sql": "SELECT COUNT(*) FROM products", "database_id": 2},
    ]

    for params in test_cases:
        suggestions = token_utils.generate_size_reduction_suggestions(
            tool_name="execute_sql",
            params=params,
            estimated_tokens=50000,
            token_limit=25000,
        )

        combined = " ".join(suggestions).lower()

        # Should suggest using the limit parameter
        assert "limit" in combined and ("parameter" in combined or "limit=" in combined), (
            f"Should suggest limit parameter for params {params}. Got: {suggestions}"
        )


def test_execute_sql_suggests_sql_limit_clause():
    """
    When execute_sql response is too large, should suggest adding SQL LIMIT clause (pass_to_pass).
    This behavior exists both before and after the fix.
    """
    token_utils = _load_token_utils()

    suggestions = token_utils.generate_size_reduction_suggestions(
        tool_name="execute_sql",
        params={"sql": "SELECT * FROM users"},
        estimated_tokens=40000,
        token_limit=20000,
    )

    combined = " ".join(suggestions)

    # Must suggest SQL LIMIT clause (uppercase)
    assert "LIMIT" in combined, (
        f"Should suggest SQL LIMIT clause. Got: {suggestions}"
    )


def test_generate_size_reduction_suggestions_function_exists():
    """
    Verify generate_size_reduction_suggestions is importable and callable (pass_to_pass).
    """
    token_utils = _load_token_utils()

    assert callable(token_utils.generate_size_reduction_suggestions), (
        "generate_size_reduction_suggestions should be callable"
    )

    # Verify it returns a list
    result = token_utils.generate_size_reduction_suggestions(
        tool_name="test_tool",
        params={},
        estimated_tokens=1000,
        token_limit=500,
    )

    assert isinstance(result, list), (
        f"generate_size_reduction_suggestions should return list, got {type(result)}"
    )


def test_repo_ruff_check_mcp_utils():
    """
    Repo's ruff linter passes on mcp_service/utils directory (pass_to_pass).

    This is a real CI check from the repo's pre-commit config.
    """
    # Install ruff if not present
    subprocess.run(
        ["pip", "install", "--no-cache-dir", "ruff"],
        capture_output=True,
        timeout=120,
    )

    r = subprocess.run(
        ["ruff", "check", str(REPO / "superset" / "mcp_service" / "utils")],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr[-500:]}"


def test_repo_ruff_format_mcp_utils():
    """
    Repo's ruff formatter check passes on mcp_service/utils directory (pass_to_pass).

    This is a real CI check from the repo's pre-commit config.
    """
    # Install ruff if not present
    subprocess.run(
        ["pip", "install", "--no-cache-dir", "ruff"],
        capture_output=True,
        timeout=120,
    )

    r = subprocess.run(
        ["ruff", "format", "--check", str(REPO / "superset" / "mcp_service" / "utils")],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr[-500:]}"


def test_repo_python_compile_token_utils():
    """
    Python syntax check passes on token_utils.py (pass_to_pass).
    """
    r = subprocess.run(
        ["python", "-m", "py_compile", str(REPO / "superset" / "mcp_service" / "utils" / "token_utils.py")],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Python compile check failed:\n{r.stderr[-500:]}"
