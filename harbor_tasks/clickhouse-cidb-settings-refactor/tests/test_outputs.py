"""Tests for the CIDB Settings refactor in collect_statistics.py.

This test verifies that collect_statistics.py uses Settings for CIDB secrets
instead of hardcoded Secret.Config names.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/ClickHouse")
TARGET_FILE = REPO / "ci" / "jobs" / "collect_statistics.py"


def test_syntax_valid():
    """Verify the Python file has valid syntax."""
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(TARGET_FILE)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Syntax error: {result.stderr}"


def test_no_hardcoded_secret_names():
    """Fail-to-pass: Old code had hardcoded secret names that should be removed."""
    content = TARGET_FILE.read_text()

    # These hardcoded secret names should NOT appear in the refactored code
    hardcoded_names = [
        "clickhouse-test-stat-url",
        "clickhouse-test-stat-login",
        "clickhouse-test-stat-password",
    ]

    for name in hardcoded_names:
        assert name not in content, f"Hardcoded secret name '{name}' found - should use Settings instead"


def test_settings_imported():
    """Verify that Settings is imported from ci.praktika.settings."""
    content = TARGET_FILE.read_text()
    tree = ast.parse(content)

    found_settings_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "ci.praktika.settings":
                for alias in node.names:
                    if alias.name == "Settings":
                        found_settings_import = True
                        break

    assert found_settings_import, "Settings not imported from ci.praktika.settings"


def test_info_imported():
    """Verify that Info is imported from ci.praktika.info."""
    content = TARGET_FILE.read_text()
    tree = ast.parse(content)

    found_info_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "ci.praktika.info":
                for alias in node.names:
                    if alias.name == "Info":
                        found_info_import = True
                        break

    assert found_info_import, "Info not imported from ci.praktika.info"


def test_settings_constants_used():
    """Fail-to-pass: Verify Settings.SECRET_CI_DB_* constants are used."""
    content = TARGET_FILE.read_text()

    # Should use Settings constants instead of hardcoded strings
    required_settings = [
        "Settings.SECRET_CI_DB_URL",
        "Settings.SECRET_CI_DB_USER",
        "Settings.SECRET_CI_DB_PASSWORD",
    ]

    for setting in required_settings:
        assert setting in content, f"Missing required setting: {setting}"


def test_info_get_secret_used():
    """Fail-to-pass: Verify Info().get_secret() is used instead of Secret.Config().get_value()."""
    content = TARGET_FILE.read_text()

    # Should use info.get_secret() pattern
    assert "info.get_secret(" in content, "Should use info.get_secret() pattern"

    # Should NOT use the old Secret.Config pattern
    assert "Secret.Config(" not in content, "Should not use Secret.Config() - use Settings instead"


def test_cidb_initialized_with_variables():
    """Verify CIDB is initialized with url/user/pwd variables, not Secret.Config."""
    content = TARGET_FILE.read_text()
    tree = ast.parse(content)

    # Find the CIDB constructor call
    found_cidb_call = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "CIDB":
                found_cidb_call = True
                # Check that keywords are url=, user=, passwd= with Name arguments
                # (not Attribute/Symbol from Secret.Config().get_value())
                keywords = {kw.arg for kw in node.keywords}
                assert "url" in keywords, "CIDB should be called with url= parameter"
                assert "user" in keywords, "CIDB should be called with user= parameter"
                assert "passwd" in keywords or "pwd" in keywords, "CIDB should be called with passwd= or pwd= parameter"

    assert found_cidb_call, "CIDB constructor call not found"


def test_no_secret_class_import():
    """Verify Secret is not imported from ci.praktika (only used via Info/Settings now)."""
    content = TARGET_FILE.read_text()

    # The old code had: from ci.praktika import Secret
    # This should be removed or changed
    assert "from ci.praktika import Secret" not in content, \
        "Should not import Secret from ci.praktika directly"


# =============================================================================
# Pass-to-pass tests: Repo CI/CD checks
# These ensure the fix doesn't break existing repo quality checks
# =============================================================================


def test_repo_black_formatting():
    """Repo's Black formatting check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "black", "--check", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Black formatting check failed:\n{r.stderr[-500:]}"


def test_repo_python_ast_valid():
    """Repo's Python files have valid AST (pass_to_pass)."""
    content = TARGET_FILE.read_text()
    try:
        ast.parse(content)
    except SyntaxError as e:
        assert False, f"Invalid AST in {TARGET_FILE}: {e}"
