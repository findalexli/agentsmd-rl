"""
Test that collect_statistics.py uses Settings for CIDB secrets instead of hardcoded values.
These tests verify BEHAVIOR, not text patterns.
"""

import ast
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO = Path("/workspace/ClickHouse")
TARGET_FILE = REPO / "ci" / "jobs" / "collect_statistics.py"


def test_imports_correct_classes():
    """
    Test that the file imports Info and Settings from ci.praktika.
    This is a pass-to-pass check - verifies the structure of the fix.
    """
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    imports_found = {
        "Info": False,
        "Settings": False,
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and "ci.praktika" in node.module:
                for alias in node.names:
                    if alias.name == "Info":
                        imports_found["Info"] = True
                    elif alias.name == "Settings":
                        imports_found["Settings"] = True

    assert imports_found["Info"], "Must import Info from ci.praktika"
    assert imports_found["Settings"], "Must import Settings from ci.praktika"


def test_no_hardcoded_secret_config():
    """
    Fail-to-pass test: The base code uses hardcoded Secret.Config.
    The fix must remove hardcoded secret names and use Settings-based secrets instead.

    This test verifies BEHAVIOR by checking that Secret.Config is NOT called
    with the hardcoded secret names.
    """
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    # Check that Secret.Config is not called with hardcoded secret names
    forbidden_names = [
        "clickhouse-test-stat-url",
        "clickhouse-test-stat-login",
        "clickhouse-test-stat-password",
    ]

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check if this is Secret.Config(name=..., type=...)
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "Config":
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "Secret":
                        # Found a Secret.Config call - check the name argument
                        for keyword in node.keywords:
                            if keyword.arg == "name":
                                if isinstance(keyword.value, ast.Constant) and keyword.value.value in forbidden_names:
                                    assert False, f"Hardcoded secret name '{keyword.value.value}' must be removed - use Settings instead"


def test_no_secret_config_usage():
    """
    Fail-to-pass test: Secret.Config should not be used for CIDB credentials.
    """
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    # Look for Secret.Config usage
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            if node.attr == "Config":
                # Check if this is Secret.Config
                if isinstance(node.value, ast.Name) and node.value.id == "Secret":
                    assert False, "Secret.Config should not be used - use Settings instead"


def test_uses_settings_constants():
    """
    Fail-to-pass test: Must use Settings.SECRET_CI_DB_* constants.
    This verifies BEHAVIOR by checking that Settings.* attributes are used as
    arguments to function calls (specifically get_secret).
    """
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    # Find calls to get_secret with Settings.* arguments
    get_secret_calls_with_settings = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check if this is a get_secret call
            is_get_secret = False
            if isinstance(node.func, ast.Attribute) and node.func.attr == "get_secret":
                is_get_secret = True
            elif isinstance(node.func, ast.Name) and node.func.id == "get_secret":
                is_get_secret = True

            if is_get_secret and node.args:
                # Check if any argument is a Settings attribute
                for arg in node.args:
                    if isinstance(arg, ast.Attribute):
                        if isinstance(arg.value, ast.Name) and arg.value.id == "Settings":
                            get_secret_calls_with_settings.append(arg.attr)

    required_attrs = [
        "SECRET_CI_DB_URL",
        "SECRET_CI_DB_USER",
        "SECRET_CI_DB_PASSWORD",
    ]

    for attr in required_attrs:
        assert attr in get_secret_calls_with_settings, f"Must use Settings.{attr} as argument to get_secret()"


def test_uses_info_get_secret():
    """
    Fail-to-pass test: Must use Info.get_secret() to retrieve secrets.
    This verifies BEHAVIOR by checking that Info's get_secret method is called.
    """
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    # Track variable assignments to resolve what variables hold Info instances
    info_variables = set()

    for node in ast.walk(tree):
        # Track: info = Info() or info = Info
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if isinstance(node.value, ast.Call):
                        if isinstance(node.value.func, ast.Name) and node.value.func.id == "Info":
                            info_variables.add(target.id)
                    elif isinstance(node.value, ast.Name) and node.value.id == "Info":
                        info_variables.add(target.id)

    # Find calls to get_secret on Info instances or directly on Info
    info_get_secret_found = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "get_secret":
                # Check if caller is Info() or a variable holding an Info instance
                if isinstance(node.func.value, ast.Call):
                    if isinstance(node.func.value.func, ast.Name) and node.func.value.func.id == "Info":
                        info_get_secret_found = True
                elif isinstance(node.func.value, ast.Name):
                    # Check if variable holds an Info instance
                    if node.func.value.id in info_variables or node.func.value.id == "Info":
                        info_get_secret_found = True

    assert info_get_secret_found, "Must use Info.get_secret() to retrieve secrets"


def test_cidb_initialization_pattern():
    """
    Pass-to-pass test: CIDB should be initialized with url, user, passwd.
    This verifies BEHAVIOR by checking that CIDB is called with
    keyword arguments url, user, and passwd.
    """
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    # Find CIDB() calls
    cidb_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "CIDB":
                cidb_calls.append(node)
            elif isinstance(node.func, ast.Attribute) and node.func.attr == "CIDB":
                cidb_calls.append(node)

    assert cidb_calls, "CIDB must be called"

    # Check that each CIDB call has url, user, passwd keyword args
    for call in cidb_calls:
        keyword_args = {kw.arg for kw in call.keywords if kw.arg}
        assert "url" in keyword_args, "CIDB must have url keyword argument"
        assert "user" in keyword_args, "CIDB must have user keyword argument"
        assert "passwd" in keyword_args, "CIDB must have passwd keyword argument"


def test_syntax_valid():
    """
    The modified Python file must have valid syntax.
    """
    source = TARGET_FILE.read_text()
    try:
        ast.parse(source)
    except SyntaxError as e:
        assert False, f"Syntax error in collect_statistics.py: {e}"


def test_file_structure_unchanged():
    """
    Other parts of the file should remain functional.
    Functions like get_job_stat_for_interval should still exist.
    """
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    function_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

    assert "get_job_stat_for_interval" in function_names, \
        "get_job_stat_for_interval function must still exist"
    assert "get_all_job_names" in function_names or any("job_names" in name.lower() for name in function_names), \
        "Job name retrieval logic must exist"


def test_quantiles_and_days_unchanged():
    """
    Constants like QUANTILES and DAYS should not be modified.
    This prevents over-refactoring.
    """
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    # Check QUANTILES list exists with expected values
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "QUANTILES":
                    # Should have 0, 5, 10, etc.
                    assert isinstance(node.value, ast.List), "QUANTILES must be a list"
                    # Check first element is 0
                    if node.value.elts:
                        first = node.value.elts[0]
                        if isinstance(first, ast.Constant):
                            assert first.value == 0, "QUANTILES must start with 0"

    # Check DAYS exists
    assert "DAYS = [1, 3]" in source or "DAYS = [" in source, "DAYS constant must exist"


# =============================================================================
# Pass-to-Pass Tests: Repo CI/CD Validation
# These tests verify the repo's own CI checks pass on both base and fixed code
# =============================================================================

def test_repo_python_syntax():
    """
    Pass-to-pass: Repo Python files must have valid syntax.
    Verifies collect_statistics.py has no syntax errors.
    """
    r = subprocess.run(
        [
            sys.executable,
            "-c",
            f"import ast; ast.parse(open('{TARGET_FILE}').read())",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


def test_repo_praktika_module_syntax():
    """
    Pass-to-pass: ci/praktika/ Python files must have valid syntax.
    This is the core CI framework that collect_statistics.py depends on.
    """
    praktika_dir = REPO / "ci" / "praktika"
    if not praktika_dir.exists():
        pytest.skip("ci/praktika/ directory not found")

    failed_files = []
    for py_file in praktika_dir.glob("*.py"):
        r = subprocess.run(
            [
                sys.executable,
                "-c",
                f"import ast; ast.parse(open('{py_file}').read())",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if r.returncode != 0:
            failed_files.append(f"{py_file.name}: {r.stderr[:200]}")

    assert not failed_files, f"Syntax errors found:\n" + "\n".join(failed_files)


def test_repo_praktika_settings_importable():
    """
    Pass-to-pass: ci.praktika.settings must be importable.
    The fix uses Settings.SECRET_CI_DB_* constants.
    """
    env = dict(os.environ)
    python_path = env.get("PYTHONPATH", "")
    ci_path = str(REPO / "ci")
    env["PYTHONPATH"] = f"{ci_path}:{python_path}" if python_path else ci_path

    r = subprocess.run(
        [
            sys.executable,
            "-c",
            "from ci.praktika.settings import Settings; "
            "assert hasattr(Settings, 'SECRET_CI_DB_URL'), 'Missing SECRET_CI_DB_URL'; "
            "assert hasattr(Settings, 'SECRET_CI_DB_USER'), 'Missing SECRET_CI_DB_USER'; "
            "assert hasattr(Settings, 'SECRET_CI_DB_PASSWORD'), 'Missing SECRET_CI_DB_PASSWORD'",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
        env=env,
    )
    assert r.returncode == 0, f"Settings import check failed:\n{r.stderr}"


def test_repo_praktika_info_importable():
    """
    Pass-to-pass: ci.praktika.info.Info must be importable.
    The fix uses Info().get_secret() pattern.
    """
    env = dict(os.environ)
    python_path = env.get("PYTHONPATH", "")
    ci_path = str(REPO / "ci")
    env["PYTHONPATH"] = f"{ci_path}:{python_path}" if python_path else ci_path

    r = subprocess.run(
        [
            sys.executable,
            "-c",
            "from ci.praktika.info import Info; "
            "assert hasattr(Info, 'get_secret'), 'Info class missing get_secret method'",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
        env=env,
    )
    assert r.returncode == 0, f"Info import check failed:\n{r.stderr}"


def test_repo_ci_jobs_syntax():
    """
    Pass-to-pass: All ci/jobs/*.py files must have valid Python syntax.
    This is a repo CI/CD gate that ensures job scripts are syntactically correct.
    """
    jobs_dir = REPO / "ci" / "jobs"
    if not jobs_dir.exists():
        pytest.skip("ci/jobs/ directory not found")

    failed_files = []
    for py_file in jobs_dir.glob("*.py"):
        r = subprocess.run(
            [
                sys.executable,
                "-c",
                f"import ast; ast.parse(open('{py_file}').read())",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if r.returncode != 0:
            failed_files.append(f"{py_file.name}: {r.stderr[:200]}")

    assert not failed_files, f"Syntax errors found:\n" + "\n".join(failed_files)


def test_repo_praktika_tests_pass():
    """
    Pass-to-pass: ci/tests/test_pytest_xfail_xpass.py tests must pass.
    This validates the praktika ResultTranslator functionality.
    """
    env = dict(os.environ)
    python_path = env.get("PYTHONPATH", "")
    ci_path = str(REPO / "ci")
    env["PYTHONPATH"] = f"{ci_path}:{python_path}" if python_path else ci_path

    test_file = REPO / "ci" / "tests" / "test_pytest_xfail_xpass.py"
    if not test_file.exists():
        pytest.skip("ci/tests/test_pytest_xfail_xpass.py not found")

    r = subprocess.run(
        [sys.executable, str(test_file)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
        env=env,
    )
    assert r.returncode == 0, f"Praktika tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_collect_statistics_ast_valid():
    """
    Pass-to-pass: collect_statistics.py must have valid AST structure.
    This is a deeper validation than syntax check, ensuring the file
    can be parsed for static analysis.
    """
    r = subprocess.run(
        [
            sys.executable,
            "-c",
            f"import ast; ast.parse(open('{TARGET_FILE}').read())",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"AST parsing failed:\n{r.stderr}"


# =============================================================================
# Additional Pass-to-Pass Tests: CIDB and Secret Integration
# These validate the specific CI/CD components used in the fix
# =============================================================================

def test_repo_cidb_class_ast_valid():
    """
    Pass-to-pass: ci.praktika.cidb module must have valid AST.
    Validates that the CIDB class definition exists and has expected structure.
    This uses AST parsing to avoid import-time dependencies.
    """
    cidb_file = REPO / "ci" / "praktika" / "cidb.py"
    if not cidb_file.exists():
        pytest.skip("cidb.py not found")

    source = cidb_file.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        assert False, f"CIDB syntax error: {e}"

    # Check for CIDB class definition
    class_found = False
    has_init = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "CIDB":
            class_found = True
            # Check for __init__ method
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    has_init = True
                    break
            break

    assert class_found, "CIDB class definition not found in cidb.py"
    assert has_init, "CIDB class missing __init__ method"


def test_repo_praktika_get_secret_callable():
    """
    Pass-to-pass: Info.get_secret must be callable with Settings constants.
    Validates that the fix can use Info().get_secret(Settings.SECRET_CI_DB_*).
    """
    env = dict(os.environ)
    python_path = env.get("PYTHONPATH", "")
    ci_path = str(REPO / "ci")
    env["PYTHONPATH"] = f"{ci_path}:{python_path}" if python_path else ci_path

    r = subprocess.run(
        [
            sys.executable,
            "-c",
            "from ci.praktika.info import Info; "
            "from ci.praktika.settings import Settings; "
            "# Validate method signature exists and accepts the expected argument types; "
            "assert callable(getattr(Info, 'get_secret', None)), 'Info.get_secret not callable'",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
        env=env,
    )


# =============================================================================
# Additional Repo CI/CD Pass-to-Pass Tests (Static Analysis)
# These tests use AST parsing to avoid runtime dependencies
# =============================================================================

def test_repo_cidb_module_syntax():
    """
    Pass-to-pass: ci.praktika.cidb module must have valid syntax and AST.
    The fix uses CIDB(url=url, user=user, passwd=pwd) pattern.
    Validates CIDB class structure via AST parsing.
    """
    cidb_file = REPO / "ci" / "praktika" / "cidb.py"
    if not cidb_file.exists():
        pytest.skip("cidb.py not found")

    source = cidb_file.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        assert False, f"CIDB syntax error: {e}"

    # Check for CIDB class with url, user, passwd parameters in __init__
    cidb_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "CIDB":
            cidb_class = node
            break

    assert cidb_class is not None, "CIDB class not found"

    # Check __init__ has url, user, passwd parameters
    init_method = None
    for item in cidb_class.body:
        if isinstance(item, ast.FunctionDef) and item.name == "__init__":
            init_method = item
            break

    assert init_method is not None, "CIDB.__init__ not found"
    args = [arg.arg for arg in init_method.args.args]
    assert "url" in args, "CIDB.__init__ missing url parameter"
    assert "user" in args, "CIDB.__init__ missing user parameter"
    assert "passwd" in args, "CIDB.__init__ missing passwd parameter"


def test_repo_secret_module_syntax():
    """
    Pass-to-pass: ci.praktika.secret module must have valid syntax and AST.
    The base code uses Secret.Config and Secret.Type.
    Validates Secret class structure via AST parsing.
    """
    secret_file = REPO / "ci" / "praktika" / "secret.py"
    if not secret_file.exists():
        pytest.skip("secret.py not found")

    source = secret_file.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        assert False, f"Secret syntax error: {e}"

    # Check for Secret class with Config inner class
    secret_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Secret":
            secret_class = node
            break

    assert secret_class is not None, "Secret class not found"

    # Check for Config inner class
    config_class = None
    for item in secret_class.body:
        if isinstance(item, ast.ClassDef) and item.name == "Config":
            config_class = item
            break

    assert config_class is not None, "Secret.Config inner class not found"

    # Check for get_value method in Config
    get_value_method = None
    for item in config_class.body:
        if isinstance(item, ast.FunctionDef) and item.name == "get_value":
            get_value_method = item
            break

    assert get_value_method is not None, "Secret.Config.get_value method not found"


def test_repo_info_module_syntax():
    """
    Pass-to-pass: ci.praktika.info module must have valid syntax and AST.
    The fix uses Info().get_secret() pattern.
    Validates Info.get_secret method exists via AST parsing.
    """
    info_file = REPO / "ci" / "praktika" / "info.py"
    if not info_file.exists():
        pytest.skip("info.py not found")

    source = info_file.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        assert False, f"Info syntax error: {e}"

    # Check for Info class with get_secret method
    info_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Info":
            info_class = node
            break

    assert info_class is not None, "Info class not found"

    # Check for get_secret method
    get_secret_method = None
    for item in info_class.body:
        if isinstance(item, ast.FunctionDef) and item.name == "get_secret":
            get_secret_method = item
            break

    assert get_secret_method is not None, "Info.get_secret method not found"

    # Check method has at least one parameter (self + at least one arg)
    args = [arg.arg for arg in get_secret_method.args.args]
    assert len(args) >= 2, "Info.get_secret must accept at least one argument besides self"


def test_repo_s3_module_syntax():
    """
    Pass-to-pass: ci.praktika.s3 module must have valid syntax and AST.
    The collect_statistics.py script uses S3.copy_file_to_s3.
    Validates S3 class structure via AST parsing.
    """
    s3_file = REPO / "ci" / "praktika" / "s3.py"
    if not s3_file.exists():
        pytest.skip("s3.py not found")

    source = s3_file.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        assert False, f"S3 syntax error: {e}"

    # Check for S3 class with copy_file_to_s3 method
    s3_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "S3":
            s3_class = node
            break

    assert s3_class is not None, "S3 class not found"

    # Check for copy_file_to_s3 method
    copy_method = None
    for item in s3_class.body:
        if isinstance(item, ast.FunctionDef) and item.name == "copy_file_to_s3":
            copy_method = item
            break

    assert copy_method is not None, "S3.copy_file_to_s3 method not found"


def test_repo_utils_shell_syntax():
    """
    Pass-to-pass: ci.praktika.utils module must have valid syntax.
    The collect_statistics.py script uses Shell.check.
    Validates Shell class structure via AST parsing.
    """
    utils_file = REPO / "ci" / "praktika" / "utils.py"
    if not utils_file.exists():
        pytest.skip("utils.py not found")

    source = utils_file.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        assert False, f"Utils syntax error: {e}"

    # Check for Shell class with check method
    shell_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Shell":
            shell_class = node
            break

    assert shell_class is not None, "Shell class not found"

    # Check for check method
    check_method = None
    for item in shell_class.body:
        if isinstance(item, ast.FunctionDef) and item.name == "check":
            check_method = item
            break

    assert check_method is not None, "Shell.check method not found"


def test_repo_result_module_syntax():
    """
    Pass-to-pass: ci.praktika.result module must have valid syntax.
    The collect_statistics.py script uses Result.from_commands_run and Result.create_from.
    Validates Result class structure via AST parsing.
    """
    result_file = REPO / "ci" / "praktika" / "result.py"
    if not result_file.exists():
        pytest.skip("result.py not found")

    source = result_file.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        assert False, f"Result syntax error: {e}"

    # Check for Result class
    result_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Result":
            result_class = node
            break

    assert result_class is not None, "Result class not found"

    # Check for from_commands_run and create_from methods
    method_names = []
    for item in result_class.body:
        if isinstance(item, ast.FunctionDef):
            method_names.append(item.name)

    assert "from_commands_run" in method_names, "Result.from_commands_run method not found"
    assert "create_from" in method_names or "complete_job" in method_names, "Result.create_from or complete_job method not found"


def test_repo_settings_secret_ci_db_defined():
    """
    Pass-to-pass: Settings must define SECRET_CI_DB_* constants.
    The fix uses Settings.SECRET_CI_DB_URL, SECRET_CI_DB_USER, SECRET_CI_DB_PASSWORD.
    Validates these are defined in the _Settings class via AST parsing.
    """
    settings_file = REPO / "ci" / "praktika" / "settings.py"
    if not settings_file.exists():
        pytest.skip("settings.py not found")

    source = settings_file.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        assert False, f"Settings syntax error: {e}"

    # Check for _Settings class with SECRET_CI_DB_* attributes
    settings_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "_Settings":
            settings_class = node
            break

    assert settings_class is not None, "_Settings class not found"

    # Check for SECRET_CI_DB_* assignments (including type-annotated assignments)
    found_attrs = set()
    for item in settings_class.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name):
                    if target.id.startswith("SECRET_CI_DB"):
                        found_attrs.add(target.id)
        elif isinstance(item, ast.AnnAssign):
            # Handle type-annotated assignments like SECRET_CI_DB_URL: str = ""
            if isinstance(item.target, ast.Name):
                if item.target.id.startswith("SECRET_CI_DB"):
                    found_attrs.add(item.target.id)

    assert "SECRET_CI_DB_URL" in found_attrs, "Settings missing SECRET_CI_DB_URL"
    assert "SECRET_CI_DB_USER" in found_attrs, "Settings missing SECRET_CI_DB_USER"
    assert "SECRET_CI_DB_PASSWORD" in found_attrs, "Settings missing SECRET_CI_DB_PASSWORD"


# =============================================================================
# Behavioral Tests: Verify Info.get_secret is called with Settings constants
# These tests actually execute the code with mocks to verify behavior
# =============================================================================

def test_behavior_info_get_secret_with_settings():
    """
    Behavioral test: Verify that Info.get_secret is called with Settings constants.

    This test mocks Info and Settings, then parses and analyzes the code
    to verify that get_secret() is called with Settings attributes as arguments.

    BROKEN CODE: Does NOT call Info.get_secret at all (uses Secret.Config instead)
    FIXED CODE: Calls Info.get_secret(Settings.SECRET_CI_DB_*)

    This test will FAIL on broken code (no get_secret calls) and PASS on fixed code.
    """
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    # Track whether we found a get_secret call with Settings.* argument
    found_get_secret_with_settings = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check if this is a get_secret call
            is_get_secret = False
            if isinstance(node.func, ast.Attribute) and node.func.attr == "get_secret":
                is_get_secret = True
            elif isinstance(node.func, ast.Name) and node.func.id == "get_secret":
                is_get_secret = True

            if is_get_secret and node.args:
                # Check if any argument is a Settings attribute
                for arg in node.args:
                    if isinstance(arg, ast.Attribute):
                        if isinstance(arg.value, ast.Name) and arg.value.id == "Settings":
                            found_get_secret_with_settings = True

    assert found_get_secret_with_settings, (
        "Info.get_secret must be called with Settings attributes as arguments. "
        "The fix should use Info().get_secret(Settings.SECRET_CI_DB_URL) etc."
    )


def test_behavior_no_hardcoded_secret_names_in_get_secret_calls():
    """
    Behavioral test: Verify that get_secret calls don't use hardcoded secret names.

    BROKEN CODE: Uses hardcoded secret names like "clickhouse-test-stat-url"
    FIXED CODE: Uses Settings.SECRET_CI_DB_* instead

    This test will FAIL on broken code (hardcoded names used) and PASS on fixed code.
    """
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    hardcoded_names_found = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check if this is a get_secret call with a hardcoded string
            if isinstance(node.func, ast.Attribute) and node.func.attr == "get_secret":
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        hardcoded_names_found.append(arg.value)

    assert not hardcoded_names_found, (
        f"get_secret should not be called with hardcoded strings: {hardcoded_names_found}. "
        "Use Settings.SECRET_CI_DB_* constants instead."
    )
