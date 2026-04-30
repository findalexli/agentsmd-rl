"""Held-out tests for apache/superset PR #38738.

The PR fixes ``ReportScheduleDAO.find_by_extra_metadata`` so that ``%`` and
``_`` in the slug are treated as literal characters, not SQL ``LIKE``
wildcards. We invoke the repo's own pytest harness against held-out test
cases that the gold patch's tests do not cover (different slug values and
fixtures), so this scaffold passes only when the contains/autoescape fix is
in place — not when the agent merely copy-pastes the gold tests.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/superset")
HELD_OUT_SRC = Path("/tests/held_out_extra_metadata_test.py")
# Place the held-out test file directly under tests/unit_tests so it picks
# up the existing conftest.py (session/app fixtures) without depending on a
# subdirectory the gold patch creates.
HELD_OUT_DEST = REPO / "tests/unit_tests/held_out_extra_metadata_test.py"


def _ensure_held_out_test_present() -> None:
    HELD_OUT_DEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(HELD_OUT_SRC, HELD_OUT_DEST)


def _run_pytest(test_node_id: str, timeout: int = 300) -> subprocess.CompletedProcess:
    _ensure_held_out_test_present()
    return subprocess.run(
        [
            "pytest",
            "-xvs",
            "--no-header",
            "-p",
            "no:cacheprovider",
            f"tests/unit_tests/held_out_extra_metadata_test.py::{test_node_id}",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _run_pytest_pr(test_node_id: str, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run a pytest node from the PR-added test file (created by the gold patch)."""
    return subprocess.run(
        [
            "pytest",
            "-xvs",
            "--no-header",
            "-p",
            "no:cacheprovider",
            f"tests/unit_tests/daos/test_report_dao.py::{test_node_id}",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _format(r: subprocess.CompletedProcess) -> str:
    tail_out = "\n".join(r.stdout.splitlines()[-80:])
    tail_err = "\n".join(r.stderr.splitlines()[-40:])
    return f"returncode={r.returncode}\n--- STDOUT ---\n{tail_out}\n--- STDERR ---\n{tail_err}"


# === Held-out fail_to_pass tests ===


def test_percent_in_slug_must_be_literal() -> None:
    """f2p — slug 'abc%xyz' must not also match 'abcZZxyz'."""
    r = _run_pytest("test_percent_in_slug_must_be_literal")
    assert r.returncode == 0, _format(r)


def test_underscore_in_slug_must_be_literal() -> None:
    """f2p — slug 'p_q' must not also match 'pXq'."""
    r = _run_pytest("test_underscore_in_slug_must_be_literal")
    assert r.returncode == 0, _format(r)


def test_trailing_percent_no_wildcard() -> None:
    """f2p — slug 'foo%' must not match 'foobar'."""
    r = _run_pytest("test_trailing_percent_no_wildcard")
    assert r.returncode == 0, _format(r)


# === Held-out pass_to_pass tests ===


def test_basic_substring_match_still_works() -> None:
    """p2p — a vanilla slug must still find its row after the fix."""
    r = _run_pytest("test_basic_substring_match_still_works")
    assert r.returncode == 0, _format(r)


def test_no_match_returns_empty_list() -> None:
    """p2p — slug not present anywhere returns []."""
    r = _run_pytest("test_no_match_returns_empty_list")
    assert r.returncode == 0, _format(r)


# === PR-added fail_to_pass tests (test file created by gold patch) ===


def test_pr_added_test_find_by_extra_metadata_returns_matching_rep() -> None:
    """f2p — PR test: basic matching works after fix."""
    r = _run_pytest_pr("test_find_by_extra_metadata_returns_matching_reports")
    assert r.returncode == 0, _format(r)


def test_pr_added_test_find_by_extra_metadata_returns_empty_when_n() -> None:
    """f2p — PR test: no-match slug returns empty list."""
    r = _run_pytest_pr("test_find_by_extra_metadata_returns_empty_when_no_match")
    assert r.returncode == 0, _format(r)


def test_pr_added_test_find_by_extra_metadata_escapes_percent_wild() -> None:
    """f2p — PR test: '%' in slug is treated as literal, not LIKE wildcard."""
    r = _run_pytest_pr("test_find_by_extra_metadata_escapes_percent_wildcard")
    assert r.returncode == 0, _format(r)


def test_pr_added_test_find_by_extra_metadata_escapes_underscore_w() -> None:
    """f2p — PR test: '_' in slug is treated as literal, not LIKE wildcard."""
    r = _run_pytest_pr("test_find_by_extra_metadata_escapes_underscore_wildcard")
    assert r.returncode == 0, _format(r)


# === Scoped CI regression test (pass_to_pass) ===


def test_existing_report_dao_unit_tests_still_pass() -> None:
    """p2p — existing daos and report-command unit tests pass after the fix."""
    r = subprocess.run(
        [
            "python3", "-m", "pytest",
            "tests/unit_tests/daos/",
            "tests/unit_tests/commands/report/",
            "-x", "--no-header", "-p", "no:cacheprovider",
            "-q",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, _format(r)

# === CI-mined tests (taskforge.ci_check_miner) ===
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

def test_ci_build_npm():
    """pass_to_pass | CI job 'build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_npm_2():
    """pass_to_pass | CI job 'build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run ci:release'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_superset_extensions_cli_p_run_pytest_with_coverage():
    """pass_to_pass | CI job 'test-superset-extensions-cli-package' → step 'Run pytest with coverage'"""
    r = subprocess.run(
        ["bash", "-lc", 'pytest --cov=superset_extensions_cli --cov-report=xml --cov-report=term-missing --cov-report=html -v --tb=short'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run pytest with coverage' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_postgres_hive_python_unit_tests_postgresql():
    """pass_to_pass | CI job 'test-postgres-hive' → step 'Python unit tests (PostgreSQL)'"""
    r = subprocess.run(
        ["bash", "-lc", "pip install -e .[hive] && ./scripts/python_tests.sh -m 'chart_data_flow or sql_json_flow'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python unit tests (PostgreSQL)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_postgres_presto_python_unit_tests_postgresql():
    """pass_to_pass | CI job 'test-postgres-presto' → step 'Python unit tests (PostgreSQL)'"""
    r = subprocess.run(
        ["bash", "-lc", "./scripts/python_tests.sh -m 'chart_data_flow or sql_json_flow'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python unit tests (PostgreSQL)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_load_examples_superset_init():
    """pass_to_pass | CI job 'test-load-examples' → step 'superset init'"""
    r = subprocess.run(
        ["bash", "-lc", 'pip install -e .'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'superset init' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_postgres_python_integration_tests_postgresql():
    """pass_to_pass | CI job 'test-postgres' → step 'Python integration tests (PostgreSQL)'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/python_tests.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python integration tests (PostgreSQL)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_test_find_by_extra_metadata_returns_matching_rep():
    """fail_to_pass | PR added test 'test_find_by_extra_metadata_returns_matching_reports' in 'tests/unit_tests/daos/test_report_dao.py' (pytest)"""
    r = subprocess.run(
        ["bash", "-lc", 'python3 -m pytest -x --no-header -p no:cacheprovider "tests/unit_tests/daos/test_report_dao.py::test_find_by_extra_metadata_returns_matching_reports" 2>&1 | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'test_find_by_extra_metadata_returns_matching_reports' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_test_find_by_extra_metadata_returns_empty_when_n():
    """fail_to_pass | PR added test 'test_find_by_extra_metadata_returns_empty_when_no_match' in 'tests/unit_tests/daos/test_report_dao.py' (pytest)"""
    r = subprocess.run(
        ["bash", "-lc", 'python3 -m pytest -x --no-header -p no:cacheprovider "tests/unit_tests/daos/test_report_dao.py::test_find_by_extra_metadata_returns_empty_when_no_match" 2>&1 | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'test_find_by_extra_metadata_returns_empty_when_no_match' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_test_find_by_extra_metadata_escapes_percent_wild():
    """fail_to_pass | PR added test 'test_find_by_extra_metadata_escapes_percent_wildcard' in 'tests/unit_tests/daos/test_report_dao.py' (pytest)"""
    r = subprocess.run(
        ["bash", "-lc", 'python3 -m pytest -x --no-header -p no:cacheprovider "tests/unit_tests/daos/test_report_dao.py::test_find_by_extra_metadata_escapes_percent_wildcard" 2>&1 | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'test_find_by_extra_metadata_escapes_percent_wildcard' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_test_find_by_extra_metadata_escapes_underscore_w():
    """fail_to_pass | PR added test 'test_find_by_extra_metadata_escapes_underscore_wildcard' in 'tests/unit_tests/daos/test_report_dao.py' (pytest)"""
    r = subprocess.run(
        ["bash", "-lc", 'python3 -m pytest -x --no-header -p no:cacheprovider "tests/unit_tests/daos/test_report_dao.py::test_find_by_extra_metadata_escapes_underscore_wildcard" 2>&1 | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'test_find_by_extra_metadata_escapes_underscore_wildcard' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
