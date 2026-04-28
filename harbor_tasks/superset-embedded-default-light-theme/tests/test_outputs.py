"""Pytest harness that runs Jest once on the relevant test files
and exposes per-test pass/fail to pytest, plus structural checks
for the embedded provider fix and basic sanity p2p tests."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/superset/superset-frontend")
EMBEDDED_FILE = REPO / "src/embedded/EmbeddedContextProviders.tsx"
THEME_TYPES_FILE = REPO / "packages/superset-core/src/theme/types.ts"
INITIAL_MODE_TEST_FILE = REPO / "src/theme/tests/ThemeControllerInitialMode.test.ts"
ORIGINAL_TEST_FILE = REPO / "src/theme/tests/ThemeController.test.ts"


def _run_jest(test_path_pattern: str, json_out: Path) -> dict:
    """Run jest with --json on a given test path pattern.
    Returns the parsed json. If jest cannot run at all, raises."""
    json_out.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [
            "npx", "--no-install", "jest",
            "--testPathPatterns", test_path_pattern,
            "--json", "--outputFile", str(json_out),
            "--colors=false",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=900,
    )
    if not json_out.exists():
        raise RuntimeError(
            f"jest did not produce a json report. stderr tail:\n{proc.stderr[-1500:]}"
        )
    return json.loads(json_out.read_text())


@pytest.fixture(scope="session")
def initial_mode_results() -> dict[str, str]:
    """Run jest on our InitialMode test file. Returns dict of testName -> status."""
    json_out = Path("/tmp/jest-initial-mode.json")
    report = _run_jest("src/theme/tests/ThemeControllerInitialMode", json_out)
    out: dict[str, str] = {}
    for tr in report.get("testResults", []):
        for assertion in tr.get("assertionResults", []):
            out[assertion["title"]] = assertion["status"]
    return out


@pytest.fixture(scope="session")
def existing_themecontroller_results() -> dict[str, str]:
    """Run jest on the pre-existing ThemeController test file (p2p)."""
    json_out = Path("/tmp/jest-existing.json")
    report = _run_jest("src/theme/tests/ThemeController.test", json_out)
    out: dict[str, str] = {}
    for tr in report.get("testResults", []):
        for assertion in tr.get("assertionResults", []):
            out[assertion["title"]] = assertion["status"]
    return out


# -------------------- fail-to-pass jest behavioural tests --------------------

def _assert_jest_passed(results: dict[str, str], name: str) -> None:
    assert name in results, (
        f"Expected jest test {name!r} not found. "
        f"Available: {sorted(results)[:20]}"
    )
    assert results[name] == "passed", (
        f"Expected jest test {name!r} to pass, got {results[name]!r}"
    )


def test_initialMode_used_when_no_saved_mode(initial_mode_results):
    _assert_jest_passed(initial_mode_results, "initialMode_used_when_no_saved_mode")


def test_initialMode_default_overrides_system_dark_preference(initial_mode_results):
    _assert_jest_passed(
        initial_mode_results,
        "initialMode_default_overrides_system_dark_preference",
    )


def test_setThemeMode_works_after_init_with_initialMode(initial_mode_results):
    _assert_jest_passed(
        initial_mode_results, "setThemeMode_works_after_init_with_initialMode"
    )


def test_no_initialMode_defaults_to_system(initial_mode_results):
    _assert_jest_passed(initial_mode_results, "no_initialMode_defaults_to_system")


def test_saved_mode_takes_precedence_over_initialMode(initial_mode_results):
    _assert_jest_passed(
        initial_mode_results, "saved_mode_takes_precedence_over_initialMode"
    )


def test_initialMode_ignored_when_no_dark_theme(initial_mode_results):
    _assert_jest_passed(
        initial_mode_results, "initialMode_ignored_when_no_dark_theme"
    )


def test_invalid_initialMode_falls_back_to_system(initial_mode_results):
    _assert_jest_passed(
        initial_mode_results, "invalid_initialMode_falls_back_to_system"
    )


# -------------------- structural fix in the embedded provider --------------------

def test_themeControllerOptions_declares_initialMode_field():
    """The public ThemeControllerOptions interface must declare an
    optional `initialMode?: ThemeMode` so embedded contexts can set it."""
    src = THEME_TYPES_FILE.read_text()
    iface_match = re.search(
        r"export interface ThemeControllerOptions\s*\{([^}]*)\}", src, re.DOTALL
    )
    assert iface_match, "ThemeControllerOptions interface not found"
    body = iface_match.group(1)
    assert re.search(r"\binitialMode\??\s*:\s*ThemeMode\b", body), (
        "ThemeControllerOptions must declare an optional `initialMode: ThemeMode` "
        f"field. Current body:\n{body}"
    )


def test_embedded_provider_constructs_controller_with_default_initialMode():
    """The embedded provider's ThemeController must be constructed with an
    explicit initial light/default mode so that an embedded dashboard does
    not pick up the host OS dark-mode preference on first render."""
    src = EMBEDDED_FILE.read_text()
    # ThemeMode must be imported (a value, not just a type) from the core theme module.
    assert re.search(
        r"import\s*\{[^}]*\bThemeMode\b[^}]*\}\s*from\s*['\"]@apache-superset/core/theme['\"]",
        src,
    ), (
        "EmbeddedContextProviders.tsx must import the ThemeMode value from "
        "'@apache-superset/core/theme'."
    )

    # The ThemeController construction must pass initialMode: ThemeMode.DEFAULT
    ctor_match = re.search(
        r"new\s+ThemeController\s*\(\s*\{([^}]*)\}\s*\)", src, re.DOTALL
    )
    assert ctor_match, "Could not locate `new ThemeController({ ... })` call"
    body = ctor_match.group(1)
    assert re.search(r"\binitialMode\s*:\s*ThemeMode\.DEFAULT\b", body), (
        "Embedded ThemeController must be constructed with "
        "`initialMode: ThemeMode.DEFAULT`. Constructor options were:\n"
        f"{body}"
    )


# -------------------- pass-to-pass: existing test suite must still pass --------------------

def test_p2p_existing_themecontroller_suite_passes(existing_themecontroller_results):
    """The repo's pre-existing ThemeController.test.ts suite must still pass.
    We don't enumerate every individual test - we just assert nothing in the
    suite has regressed."""
    assert existing_themecontroller_results, (
        "Expected the existing ThemeController test suite to produce results "
        "but got an empty report."
    )
    failed = [
        n for n, s in existing_themecontroller_results.items() if s != "passed"
    ]
    assert not failed, (
        f"Existing ThemeController tests regressed: {failed[:10]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
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

def test_ci_test_superset_extensions_cli_p_run_pytest_with_coverage():
    """pass_to_pass | CI job 'test-superset-extensions-cli-package' → step 'Run pytest with coverage'"""
    r = subprocess.run(
        ["bash", "-lc", 'pytest --cov=superset_extensions_cli --cov-report=xml --cov-report=term-missing --cov-report=html -v --tb=short'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run pytest with coverage' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_frontend_check_translations_lint():
    """pass_to_pass | CI job 'frontend-check-translations' → step 'lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build-translation'], cwd=os.path.join(REPO, './superset-frontend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_load_examples_superset_init():
    """pass_to_pass | CI job 'test-load-examples' → step 'superset init'"""
    r = subprocess.run(
        ["bash", "-lc", 'pip install -e .'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'superset init' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")