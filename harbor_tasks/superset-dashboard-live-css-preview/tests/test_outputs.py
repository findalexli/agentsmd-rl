#!/usr/bin/env python3
"""
Tests for superset PR #38960: Live CSS preview in PropertiesModal

Key behaviors to verify:
1. handleCustomCssChange exists and implements debounced dispatch
2. handleOnCancel clears timers and restores original CSS
3. Timer cleanup on component unmount
4. Original CSS is captured on modal open
5. TypeScript types are correct (no 'any' types in new code)
6. Redux actions are properly dispatched
"""

import subprocess
import sys
import os
import re

REPO = "/workspace/superset"
FRONTEND = f"{REPO}/superset-frontend"
TARGET_FILE = f"{FRONTEND}/src/dashboard/components/PropertiesModal/index.tsx"


def test_original_css_ref_exists():
    """Fail-to-pass: originalCss ref must exist to store original CSS."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    assert "const originalCss = useRef<string | null>(null)" in content, \
        "Missing originalCss ref with proper type"
    assert "const cssDebounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null)" in content, \
        "Missing cssDebounceTimer ref with proper type"


def test_handle_custom_css_change_exists():
    """Fail-to-pass: handleCustomCssChange callback must exist with debounce logic."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    assert "const handleCustomCssChange = useCallback" in content, \
        "Missing handleCustomCssChange useCallback"
    assert "cssDebounceTimer.current = setTimeout" in content, \
        "Missing setTimeout for debounce"
    assert "500" in content, \
        "Missing 500ms debounce delay"
    assert 'dispatch(dashboardInfoChanged({ css }))' in content or \
           'dispatch(dashboardInfoChanged({css}))' in content, \
        "Missing dispatch of dashboardInfoChanged with CSS"


def test_cancel_handler_restores_css():
    """Fail-to-pass: handleOnCancel must restore original CSS and clear timers."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    cancel_pattern = r'const handleOnCancel = \(\) => \{'
    match = re.search(cancel_pattern, content)
    assert match, "handleOnCancel should be defined as a function body, not arrow to onHide"

    assert "cssDebounceTimer.current" in content and "clearTimeout" in content, \
        "Missing timer cleanup in cancel handler"
    assert "originalCss.current" in content, \
        "Missing reference to originalCss in cancel handler"
    assert "dispatch(dashboardInfoChanged({ css: originalCss.current }))" in content or \
           'dispatch(dashboardInfoChanged({css: originalCss.current}))' in content, \
        "Missing dispatch to restore original CSS on cancel"


def test_unmount_cleanup_exists():
    """Fail-to-pass: useEffect cleanup must clear debounce timer on unmount."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    cleanup_pattern = r'useEffect\(\s*\(\)\s*=>\s*\(\)\s*=>\s*\{[^}]*cssDebounceTimer\.current[^}]*\}'
    assert re.search(cleanup_pattern, content, re.DOTALL), \
        "Missing useEffect cleanup to clear debounce timer on unmount"


def test_original_css_capture_on_open():
    """Fail-to-pass: Original CSS must be captured when modal opens."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    assert "originalCss.current = null" in content, \
        "Missing logic to reset originalCss reference when modal opens"
    assert "if (originalCss.current === null)" in content, \
        "Missing null check to prevent overwriting original CSS"


def test_dashboard_info_changed_imported():
    """Fail-to-pass: dashboardInfoChanged action must be imported."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    assert "import { dashboardInfoChanged } from 'src/dashboard/actions/dashboardInfo'" in content or \
           'import {dashboardInfoChanged} from "src/dashboard/actions/dashboardInfo"' in content or \
           "dashboardInfoChanged" in content, \
        "Missing dashboardInfoChanged import or usage"


def test_no_explicit_any_types():
    """Fail-to-pass: New code should not use explicit 'any' types (per AGENTS.md)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    bad_patterns = [
        "useRef<any>",
        "useRef<any[]>",
    ]

    for pattern in bad_patterns:
        assert pattern not in content, \
            f"Found forbidden 'any' type pattern: {pattern}"


def test_props_use_handler_not_setter():
    """Fail-to-pass: onCustomCssChange prop should use handler, not direct setter."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    assert "onCustomCssChange={handleCustomCssChange}" in content, \
        "onCustomCssChange prop should use handleCustomCssChange, not setCustomCss"
    assert "setCustomCss(css)" in content or "setCustomCss(css)" in content.replace(" ", ""), \
        "setCustomCss should still be called within handleCustomCssChange"


def test_repo_jest_tests_pass():
    """Pass-to-pass: Existing PropertiesModal Jest tests should pass."""
    result = subprocess.run(
        ["npm", "run", "test", "--", "--testPathPatterns", "PropertiesModal", "--watchAll=false"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, \
        f"PropertiesModal tests failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_repo_lint_full_passes():
    """Pass-to-pass: Full lint (oxlint + custom rules) passes on the repo."""
    result = subprocess.run(
        ["npm", "run", "lint:full"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, \
        f"Lint full failed:\n{result.stderr[-500:] if result.stderr else result.stdout[-500:]}"


def test_repo_custom_rules_pass():
    """Pass-to-pass: Superset custom rules check passes."""
    result = subprocess.run(
        ["npm", "run", "check:custom-rules"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Custom rules check failed:\n{result.stderr[-500:] if result.stderr else result.stdout[-500:]}"


def test_repo_dashboard_actions_tests_pass():
    """Pass-to-pass: Dashboard actions tests pass (covering dashboardInfoChanged and related actions)."""
    result = subprocess.run(
        ["npm", "run", "test", "--", "--testPathPatterns", "src/dashboard/actions/", "--watchAll=false", "--maxWorkers=2"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Dashboard actions tests failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_typescript_compiles():
    """Pass-to-pass: TypeScript should compile without errors in target file."""
    result = subprocess.run(
        ["npm", "run", "type"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    output = result.stdout + result.stderr
    target_file_errors = [
        line for line in output.split('\n')
        if 'PropertiesModal/index.tsx' in line and 'error TS' in line
    ]

    assert not target_file_errors, \
        f"TypeScript errors in PropertiesModal/index.tsx:\n{chr(10).join(target_file_errors[-10:])}"


def test_eslint_no_errors():
    """Pass-to-pass: ESLint should pass on the target file."""
    result = subprocess.run(
        ["npm", "run", "lint", "--", "src/dashboard/components/PropertiesModal/index.tsx"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    output = result.stdout + result.stderr

    target_file_errors = [
        line for line in output.split('\n')
        if 'PropertiesModal/index.tsx' in line and 'error' in line.lower()
    ]

    assert not target_file_errors, \
        f"ESLint errors in PropertiesModal/index.tsx:\n{chr(10).join(target_file_errors[-10:])}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_unit_tests_python_unit_tests():
    """pass_to_pass | CI job 'unit-tests' → step 'Python unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pytest --durations-min=0.5 --cov-report= --cov=superset ./tests/common ./tests/unit_tests --cache-clear --maxfail=50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_tests_python_100_coverage_unit_tests():
    """pass_to_pass | CI job 'unit-tests' → step 'Python 100% coverage unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pytest --durations-min=0.5 --cov=superset/sql/ ./tests/unit_tests/sql/ --cache-clear --cov-fail-under=100'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python 100% coverage unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_load_examples_superset_init():
    """pass_to_pass | CI job 'test-load-examples' → step 'superset init'"""
    r = subprocess.run(
        ["bash", "-lc", 'pip install -e .'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'superset init' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_frontend_check_translations_lint():
    """pass_to_pass | CI job 'frontend-check-translations' → step 'lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build-translation'], cwd=os.path.join(REPO, './superset-frontend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_python_deps_run_uv():
    """pass_to_pass | CI job 'check-python-deps' → step 'Run uv'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/uv-pip-compile.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run uv' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_python_deps_check_for_uncommitted_changes():
    """pass_to_pass | CI job 'check-python-deps' → step 'Check for uncommitted changes'"""
    r = subprocess.run(
        ["bash", "-lc", 'echo "Full diff (for logging/debugging):"\ngit diff\n\necho "Filtered diff (excluding comments and whitespace):"\nfiltered_diff=$(git diff -U0 | grep \'^[-+]\' | grep -vE \'^[-+]{3}\' | grep -vE \'^[-+][[:space:]]*#\' | grep -vE \'^[-+][[:space:]]*$\' || true)\necho "$filtered_diff"\n\nif [[ -n "$filtered_diff" ]]; then\n  echo\n  echo "ERROR: The pinned dependencies are not up-to-date."\n  echo "Please run \'./scripts/uv-pip-compile.sh\' and commit the changes."\n  echo "More info: https://github.com/apache/superset/tree/master/requirements"\n  exit 1\nelse\n  echo "Pinned dependencies are up-to-date."\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check for uncommitted changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_superset_extensions_cli_p_run_pytest_with_coverage():
    """pass_to_pass | CI job 'test-superset-extensions-cli-package' → step 'Run pytest with coverage'"""
    r = subprocess.run(
        ["bash", "-lc", 'pytest --cov=superset_extensions_cli --cov-report=xml --cov-report=term-missing --cov-report=html -v --tb=short'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run pytest with coverage' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_postgres_presto_python_unit_tests_postgresql():
    """pass_to_pass | CI job 'test-postgres-presto' → step 'Python unit tests (PostgreSQL)'"""
    r = subprocess.run(
        ["bash", "-lc", "./scripts/python_tests.sh -m 'chart_data_flow or sql_json_flow'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python unit tests (PostgreSQL)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_postgres_hive_python_unit_tests_postgresql():
    """pass_to_pass | CI job 'test-postgres-hive' → step 'Python unit tests (PostgreSQL)'"""
    r = subprocess.run(
        ["bash", "-lc", "pip install -e .[hive] && ./scripts/python_tests.sh -m 'chart_data_flow or sql_json_flow'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python unit tests (PostgreSQL)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_mysql_python_integration_tests_mysql():
    """pass_to_pass | CI job 'test-mysql' → step 'Python integration tests (MySQL)'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/python_tests.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python integration tests (MySQL)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_mysql_generate_database_diagnostics_for_docs():
    """pass_to_pass | CI job 'test-mysql' → step 'Generate database diagnostics for docs'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -c "'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Generate database diagnostics for docs' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")