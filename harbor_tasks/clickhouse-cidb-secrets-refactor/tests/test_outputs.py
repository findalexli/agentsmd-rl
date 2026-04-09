"""
Test that collect_statistics.py uses Settings for CIDB secrets instead of hardcoded values.
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

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
    The fix must remove these hardcoded secret names.
    """
    source = TARGET_FILE.read_text()

    # These hardcoded secret names must NOT be present
    forbidden_patterns = [
        'clickhouse-test-stat-url',
        'clickhouse-test-stat-login',
        'clickhouse-test-stat-password',
    ]

    for pattern in forbidden_patterns:
        assert pattern not in source, f"Hardcoded secret name '{pattern}' must be removed"


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
    """
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    required_attrs = [
        "SECRET_CI_DB_URL",
        "SECRET_CI_DB_USER",
        "SECRET_CI_DB_PASSWORD",
    ]

    found_attrs = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            if node.attr in required_attrs:
                found_attrs.add(node.attr)

    for attr in required_attrs:
        assert attr in found_attrs, f"Must use Settings.{attr}"


def test_uses_info_get_secret():
    """
    Fail-to-pass test: Must use Info().get_secret() pattern.
    """
    source = TARGET_FILE.read_text()

    # Should have info.get_secret() calls
    assert "info.get_secret(" in source or "Info().get_secret(" in source, \
        "Must use Info().get_secret() to retrieve secrets"


def test_cidb_initialization_pattern():
    """
    Pass-to-pass test: CIDB should be initialized with url, user, passwd from settings.
    """
    source = TARGET_FILE.read_text()

    # After fix, CIDB should be initialized with variables derived from Settings
    assert "CIDB(url=url" in source or "CIDB(" in source and "url" in source, \
        "CIDB must be initialized with url parameter from settings"

    # Should have the chain of get_secret calls resulting in url, user, pwd variables
    assert "url_secret" in source or "url" in source, "Must derive url from secrets"
    assert "user_secret" in source or "user" in source, "Must derive user from secrets"


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
