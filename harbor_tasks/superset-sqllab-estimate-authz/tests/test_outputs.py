# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Oracle tests for Superset PR #38648 — authorization on query cost estimation.

This file is copied by test.sh into
    /workspace/superset/tests/unit_tests/commands/sql_lab/
so that the existing conftest.py at /workspace/superset/tests/unit_tests/
autouses its `app_context` fixture and bootstraps a Flask app context.

The tests deliberately patch the SecurityManager class method (not the
local `security_manager` symbol of the estimate module) so that they
remain robust to whichever style of import the agent uses
(`from superset import security_manager`,
 `from superset.extensions import security_manager`,
 `import superset; superset.security_manager.raise_for_access(...)`, etc.).
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from superset.commands.sql_lab.estimate import (
    EstimateQueryCostType,
    QueryEstimationCommand,
)
from superset.errors import ErrorLevel, SupersetError, SupersetErrorType
from superset.exceptions import SupersetErrorException, SupersetSecurityException
from superset.security.manager import SupersetSecurityManager

REPO = Path("/workspace/superset")


def _params(**kwargs: object) -> EstimateQueryCostType:
    base: EstimateQueryCostType = {
        "database_id": 1,
        "sql": "SELECT 1",
        "template_params": {},
        "catalog": None,
        "schema": None,
    }
    base.update(kwargs)  # type: ignore[typeddict-item]
    return base


def _security_exception() -> SupersetSecurityException:
    return SupersetSecurityException(
        SupersetError(
            message="Access denied",
            error_type=SupersetErrorType.DATASOURCE_SECURITY_ACCESS_ERROR,
            level=ErrorLevel.WARNING,
        )
    )


# ---------------------------------------------------------------------------
# Fail-to-pass: behavioural coverage of the authorization check
# ---------------------------------------------------------------------------


@patch("superset.commands.sql_lab.estimate.db")
def test_validate_invokes_raise_for_access_for_authorised_user(
    mock_db: MagicMock,
) -> None:
    """validate() must call security_manager.raise_for_access with the
    resolved Database, regardless of which import style is used."""
    with patch.object(
        SupersetSecurityManager, "raise_for_access", autospec=True
    ) as mock_raise:
        mock_database = MagicMock()
        mock_db.session.query.return_value.get.return_value = mock_database
        mock_raise.return_value = None

        QueryEstimationCommand(_params()).validate()

        assert mock_raise.call_count == 1, (
            "SupersetSecurityManager.raise_for_access was not called inside "
            "QueryEstimationCommand.validate(). The validation step must "
            "perform a database-level access check on the resolved Database."
        )
        kwargs = mock_raise.call_args.kwargs
        assert kwargs.get("database") is mock_database, (
            "raise_for_access must be called with database=<resolved Database>; "
            f"got call={mock_raise.call_args}"
        )


@patch("superset.commands.sql_lab.estimate.db")
def test_validate_propagates_security_exception(
    mock_db: MagicMock,
) -> None:
    """When raise_for_access denies access, validate() must propagate it."""
    with patch.object(
        SupersetSecurityManager, "raise_for_access", autospec=True
    ) as mock_raise:
        mock_database = MagicMock()
        mock_db.session.query.return_value.get.return_value = mock_database
        mock_raise.side_effect = _security_exception()

        with pytest.raises(SupersetSecurityException):
            QueryEstimationCommand(_params()).validate()


@patch("superset.commands.sql_lab.estimate.db")
def test_validate_skips_access_check_when_database_missing(
    mock_db: MagicMock,
) -> None:
    """A missing database must surface a 404-style error and NOT trigger an
    access check (otherwise unauthenticated lookups would leak existence)."""
    with patch.object(
        SupersetSecurityManager, "raise_for_access", autospec=True
    ) as mock_raise:
        mock_db.session.query.return_value.get.return_value = None

        with pytest.raises(SupersetErrorException) as exc_info:
            QueryEstimationCommand(_params()).validate()

        assert (
            exc_info.value.error.error_type
            == SupersetErrorType.RESULTS_BACKEND_ERROR
        )
        mock_raise.assert_not_called()


@patch("superset.commands.sql_lab.estimate.db")
def test_run_blocks_unauthorized_user_before_engine_call(
    mock_db: MagicMock,
) -> None:
    """run() goes through validate() — an unauthorized caller must not reach
    db_engine_spec.estimate_query_cost (so no plan/cost ever leaks)."""
    with patch.object(
        SupersetSecurityManager, "raise_for_access", autospec=True
    ) as mock_raise:
        mock_database = MagicMock()
        mock_db.session.query.return_value.get.return_value = mock_database
        mock_raise.side_effect = _security_exception()

        with pytest.raises(SupersetSecurityException):
            QueryEstimationCommand(_params()).run()

        # The engine spec must never be queried for cost on an unauthorised call.
        mock_database.db_engine_spec.estimate_query_cost.assert_not_called()


# ---------------------------------------------------------------------------
# Pass-to-pass: existing repo unit tests — regression guards
# ---------------------------------------------------------------------------


def test_repo_streaming_export_unit_tests_still_pass() -> None:
    """Existing SQL-Lab streaming-export unit tests keep passing."""
    target = (
        REPO
        / "tests"
        / "unit_tests"
        / "commands"
        / "sql_lab"
        / "streaming_export_command_test.py"
    )
    assert target.exists(), f"upstream regression test file missing: {target}"
    r = subprocess.run(
        ["python", "-m", "pytest", str(target), "-q", "--no-header"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        "Upstream streaming-export tests must keep passing.\n"
        f"--- stdout ---\n{r.stdout[-1500:]}\n"
        f"--- stderr ---\n{r.stderr[-500:]}"
    )


def test_repo_dataframe_utils_unit_tests_still_pass() -> None:
    """A second, independent unit-test module continues to pass — guards
    against an agent that breaks unrelated imports while editing estimate.py."""
    target = REPO / "tests" / "unit_tests" / "common" / "test_dataframe_utils.py"
    assert target.exists(), f"upstream regression test file missing: {target}"
    r = subprocess.run(
        ["python", "-m", "pytest", str(target), "-q", "--no-header"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        "Upstream dataframe-utils tests must keep passing.\n"
        f"--- stdout ---\n{r.stdout[-1500:]}\n"
        f"--- stderr ---\n{r.stderr[-500:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_superset_extensions_cli_p_run_pytest_with_coverage():
    """pass_to_pass | CI job 'test-superset-extensions-cli-package' → step 'Run pytest with coverage'"""
    r = subprocess.run(
        ["bash", "-lc", 'pytest --cov=superset_extensions_cli --cov-report=xml --cov-report=term-missing --cov-report=html -v --tb=short'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run pytest with coverage' failed (returncode={r.returncode}):\n"
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

def test_ci_test_sqlite_python_integration_tests_sqlite():
    """pass_to_pass | CI job 'test-sqlite' → step 'Python integration tests (SQLite)'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/python_tests.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python integration tests (SQLite)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_mysql_generate_database_diagnostics_for_docs():
    """pass_to_pass | CI job 'test-mysql' → step 'Generate database diagnostics for docs'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -c "'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Generate database diagnostics for docs' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")