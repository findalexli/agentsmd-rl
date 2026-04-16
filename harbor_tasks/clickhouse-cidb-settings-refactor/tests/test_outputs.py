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
    """Fail-to-pass: Verify Settings.SECRET_CI_DB_* constants are used instead of hardcoded strings."""
    content = TARGET_FILE.read_text()
    tree = ast.parse(content)

    settings_constants_found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id == "Settings" and node.attr.startswith("SECRET_CI_DB_"):
                settings_constants_found.add(node.attr)

    required_constants = {"SECRET_CI_DB_URL", "SECRET_CI_DB_USER", "SECRET_CI_DB_PASSWORD"}
    assert required_constants.issubset(settings_constants_found), \
        f"Missing Settings constants: {required_constants - settings_constants_found}"


def test_info_get_secret_used():
    """Fail-to-pass: Verify Info.get_secret() is used with Settings constants.

    Uses AST to find get_secret() calls without requiring specific variable names.
    """
    content = TARGET_FILE.read_text()
    tree = ast.parse(content)

    get_secret_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "get_secret":
                # Found a get_secret call - check it's called on an instance (Name node),
                # not on the class itself (which would be invalid Python pattern for this)
                if isinstance(node.func.value, ast.Name):
                    # Check first argument is a Settings constant
                    if len(node.args) > 0:
                        first_arg = node.args[0]
                        if isinstance(first_arg, ast.Attribute):
                            if isinstance(first_arg.value, ast.Name) and first_arg.value.id == "Settings":
                                if first_arg.attr.startswith("SECRET_CI_DB_"):
                                    get_secret_calls.append(first_arg.attr)

    assert len(get_secret_calls) >= 3, \
        f"Expected at least 3 get_secret calls with Settings constants, found {len(get_secret_calls)}"
    assert "SECRET_CI_DB_URL" in get_secret_calls, "Missing Settings.SECRET_CI_DB_URL in get_secret call"
    assert "SECRET_CI_DB_USER" in get_secret_calls, "Missing Settings.SECRET_CI_DB_USER in get_secret call"
    assert "SECRET_CI_DB_PASSWORD" in get_secret_calls, "Missing Settings.SECRET_CI_DB_PASSWORD in get_secret call"


def _get_base_name(node):
    """Walk an Attribute/Call chain to find the base Name node.

    Handles:
    - Name nodes directly
    - Attribute chains like x.y.z (returns x.id)
    - Call chains like x.y().z() (returns x.id after unwinding)
    """
    while isinstance(node, (ast.Attribute, ast.Call)):
        if isinstance(node, ast.Attribute):
            node = node.value
        elif isinstance(node, ast.Call):
            # For calls like x.y(), the func is an Attribute
            if isinstance(node.func, ast.Attribute):
                node = node.func.value
            elif isinstance(node.func, ast.Name):
                node = node.func
            else:
                return None
    if isinstance(node, ast.Name):
        return node.id
    return None


def _trace_assignment_chain(var_name, tree):
    """Find what a variable is assigned from. Returns the assigned value node or None.

    Handles single-target assignments like:
      x = <expr>
      x, y = <expr>
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == var_name:
                    return node.value
                # Handle tuple unpacking like x, y = ...
                if isinstance(target, ast.Tuple):
                    for i, elt in enumerate(target.elts):
                        if isinstance(elt, ast.Name) and elt.id == var_name:
                            # Check if the assigned value is a tuple
                            if isinstance(node.value, ast.Tuple):
                                return node.value.elts[i]
                            # Could be a call returning multiple values - look at the Call node
                            if isinstance(node.value, ast.Call):
                                # For chained calls like a().b().c() - can't easily trace
                                return node.value
                            return None
        # Handle AnnAssign with a single target
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == var_name:
                return node.value
    return None


def _is_from_secret_chain(node, secret_var_names):
    """Check if node is or derives from a secret variable.

    Returns True if node traces back to a variable in secret_var_names via
    method call chains (like join_with().get_value()).
    """
    if node is None:
        return False

    if isinstance(node, ast.Name):
        if node.id in secret_var_names:
            return True
        # Trace the assignment chain
        assigned = _trace_assignment_chain(node.id, tree if 'tree' in locals() else None)
        # We'll need to pass tree around - let's do this differently
        return False

    # If it's a Call node (like join_with().get_value()), check the base
    if isinstance(node, ast.Call):
        base_name = _get_base_name(node)
        if base_name and base_name in secret_var_names:
            return True

    # If it's an Attribute node (like x.y), check the base
    if isinstance(node, ast.Attribute):
        base_name = _get_base_name(node)
        if base_name and base_name in secret_var_names:
            return True

    return False


def test_cidb_initialized_with_variables():
    """Fail-to-pass: Verify CIDB is initialized with variables derived from Info.get_secret().

    Uses AST to verify that:
    1. CIDB is called with keyword arguments (url, user, pwd/passwd)
    2. The keyword values are derived from Info.get_secret() calls (not hardcoded strings)
    """
    content = TARGET_FILE.read_text()
    tree = ast.parse(content)

    # Build a map of variable names to their assignment values
    # Handles both single-target and tuple unpacking assignments
    assign_map = {}  # var_name -> assigned_value_node
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assign_map[target.id] = node.value
                elif isinstance(target, ast.Tuple):
                    # Handle tuple unpacking like x, y = expr
                    for elt in target.elts:
                        if isinstance(elt, ast.Name):
                            assign_map[elt.id] = node.value

    # First, find Info.get_secret() calls and track what variables they assign to
    secret_var_names = set()  # Set of variable names that hold get_secret results
    for var_name, value in assign_map.items():
        if isinstance(value, ast.Call):
            func = value.func
            if isinstance(func, ast.Attribute) and func.attr == "get_secret":
                # func.value could be Name (info) or Attribute (info.get_secret is Attribute on info)
                # Either way, the base of that should be the variable holding Info instance
                if isinstance(func.value, ast.Name):
                    # Simple case: info.get_secret()
                    if len(value.args) > 0:
                        arg = value.args[0]
                        if isinstance(arg, ast.Attribute):
                            if isinstance(arg.value, ast.Name) and arg.value.id == "Settings":
                                if arg.attr.startswith("SECRET_CI_DB_"):
                                    secret_var_names.add(var_name)

    # Find CIDB constructor call
    found_cidb = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "CIDB":
                found_cidb = True
                keywords = {kw.arg: kw.value for kw in node.keywords}

                # Check required keywords exist
                assert "url" in keywords, "CIDB should be called with url= keyword argument"
                assert "user" in keywords, "CIDB should be called with user= keyword argument"
                assert "passwd" in keywords or "pwd" in keywords, "CIDB should be called with passwd= or pwd= keyword argument"

                # Check that keyword values are derived from Info.get_secret() calls
                for kw_name, kw_value in keywords.items():
                    if kw_name in ["url", "user", "passwd", "pwd"]:
                        # Check if the keyword value is derived from secret_var_names
                        valid = False

                        if isinstance(kw_value, ast.Name):
                            # Direct variable reference
                            var_name = kw_value.id
                            # Check if it's directly in secret_var_names
                            if var_name in secret_var_names:
                                valid = True
                            # Or trace back through assignments
                            elif var_name in assign_map:
                                assigned_val = assign_map[var_name]
                                # If assigned from a method chain on a secret var, it's valid
                                if isinstance(assigned_val, (ast.Call, ast.Attribute)):
                                    base_name = _get_base_name(assigned_val)
                                    if base_name and base_name in secret_var_names:
                                        valid = True
                                elif isinstance(assigned_val, ast.Name):
                                    if assigned_val.id in secret_var_names:
                                        valid = True
                        elif isinstance(kw_value, (ast.Call, ast.Attribute)):
                            # Method chain like url_secret.join_with(...).get_value()
                            base_name = _get_base_name(kw_value)
                            if base_name and base_name in secret_var_names:
                                valid = True

                        assert valid, \
                            f"CIDB keyword '{kw_name}' should come from Info.get_secret(), not hardcoded or incorrect source"

    assert found_cidb, "CIDB constructor call not found"


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


def test_repo_ci_pytest_xfail():
    """Repo's CI internal pytest xfail/xpass tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pytest", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # pytest install should succeed
    assert r.returncode == 0, f"Failed to install pytest:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["python3", "-m", "pytest", "tests/test_pytest_xfail_xpass.py", "-v"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO / "ci",
    )
    assert r.returncode == 0, f"CI pytest xfail/xpass tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
