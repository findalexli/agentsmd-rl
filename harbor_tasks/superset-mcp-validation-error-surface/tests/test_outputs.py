"""Behavioral tests for the validation-pipeline error-surfacing fix.

The bug under test: when ``ChartErrorBuilder.build_error`` is called with
``template_key="validation_error"``, the builder produced a generic
``"An error occurred"`` response with empty details and no suggestions
because the ``"validation_error"`` template was missing from
``ChartErrorBuilder.TEMPLATES``. Additionally, when the underlying error
came from Pydantic's tagged-union validation, the long
``"1 validation error for tagged-union[...]"`` header consumed the entire
200-character truncation budget, leaving no room for the actionable
``Value error, ...`` / ``Input should be ...`` body.
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

REPO = Path("/workspace/superset")
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _passthrough_normalize(request, *_args, **_kwargs):
    return request


# ---------------------------------------------------------------------------
# fail_to_pass
# ---------------------------------------------------------------------------

def test_validation_error_template_registered():
    from superset.mcp_service.utils.error_builder import ChartErrorBuilder

    assert "validation_error" in ChartErrorBuilder.TEMPLATES, (
        "ChartErrorBuilder.TEMPLATES is missing the 'validation_error' "
        "template that ValidationPipeline.validate_request_with_warnings "
        "passes to build_error()."
    )
    template = ChartErrorBuilder.TEMPLATES["validation_error"]
    assert "{reason}" in template["message"], (
        "validation_error.message must reference the {reason} template var "
        "so the sanitized error reaches the user."
    )
    assert "{reason}" in template["details"], (
        "validation_error.details must reference the {reason} template var."
    )
    assert template["suggestions"], (
        "validation_error.suggestions must be a non-empty list."
    )


def test_validation_error_template_is_chart_type_agnostic():
    """The template fires for every chart type, so its suggestions must
    not bake in chart-type-specific field names."""
    from superset.mcp_service.utils.error_builder import ChartErrorBuilder

    template = ChartErrorBuilder.TEMPLATES["validation_error"]
    joined = " ".join(template["suggestions"]).lower()
    assert "mixed_timeseries" not in joined
    assert "primary_kind" not in joined
    assert "secondary_kind" not in joined


def test_build_error_with_validation_error_template_surfaces_reason():
    from superset.mcp_service.utils.error_builder import ChartErrorBuilder

    error = ChartErrorBuilder.build_error(
        error_type="validation_system_error",
        template_key="validation_error",
        template_vars={"reason": "Unknown field 'kind'"},
        error_code="VALIDATION_PIPELINE_ERROR",
    )
    dumped = error.model_dump()
    assert dumped["message"] != "An error occurred", (
        "build_error must use the validation_error template instead of "
        "falling back to the default 'An error occurred' message."
    )
    assert "Unknown field" in dumped["message"]
    assert "Unknown field" in dumped["details"]
    assert dumped["suggestions"], "suggestions list must be non-empty"
    assert dumped["error_code"] == "VALIDATION_PIPELINE_ERROR"


def test_mixed_timeseries_kind_returns_actionable_error():
    """End-to-end: a mixed_timeseries config that uses XY-style ``kind`` /
    ``kind_secondary`` field names must produce an error whose message and
    details name the offending fields."""
    from superset.mcp_service.chart.validation.pipeline import ValidationPipeline

    request_data = {
        "dataset_id": 1,
        "config": {
            "chart_type": "mixed_timeseries",
            "x": {"name": "order_date"},
            "y": [{"name": "revenue", "aggregate": "SUM"}],
            "y_secondary": [{"name": "orders", "aggregate": "COUNT"}],
            "kind": "line",
            "kind_secondary": "bar",
        },
    }

    with (
        patch.object(ValidationPipeline, "_get_dataset_context", return_value=None),
        patch.object(ValidationPipeline, "_validate_dataset", return_value=(True, None)),
        patch.object(ValidationPipeline, "_validate_runtime", return_value=(True, None)),
        patch.object(
            ValidationPipeline,
            "_normalize_column_names",
            side_effect=_passthrough_normalize,
        ),
    ):
        result = ValidationPipeline.validate_request_with_warnings(request_data)

    assert result.is_valid is False
    assert result.error is not None
    dumped = result.error.model_dump()

    assert dumped["message"] != "An error occurred", (
        f"Expected an actionable validation message, got: {dumped['message']!r}"
    )
    assert dumped["details"] != "", "details must carry the actionable error body"
    # The Pydantic tagged-union prefix is internal noise — it must not
    # leak into the user-facing payload.
    assert "tagged-union" not in dumped["message"], (
        f"message still contains the Pydantic tagged-union prefix: "
        f"{dumped['message']!r}"
    )
    assert "tagged-union" not in dumped["details"], (
        f"details still contains the Pydantic tagged-union prefix: "
        f"{dumped['details']!r}"
    )
    # The actionable content must survive truncation.
    assert "kind" in dumped["details"], (
        f"details should name the invalid field 'kind', got: {dumped['details']!r}"
    )
    assert dumped["suggestions"], "suggestions list must be non-empty"
    assert dumped["error_code"] == "VALIDATION_PIPELINE_ERROR"


def test_pie_chart_invalid_aggregate_surfaces_input_should_be():
    """Regression for non-Value-error Pydantic bodies: an invalid aggregate
    value triggers a literal_error whose body starts with ``Input should be``,
    not ``Value error,``. The cleanup must surface it past the 200-char
    truncation."""
    from superset.mcp_service.chart.validation.pipeline import ValidationPipeline

    request_data = {
        "dataset_id": 1,
        "config": {
            "chart_type": "pie",
            "dimension": {"name": "product"},
            "metric": {"name": "revenue", "aggregate": "BOGUS"},
        },
    }

    with (
        patch.object(ValidationPipeline, "_get_dataset_context", return_value=None),
        patch.object(ValidationPipeline, "_validate_dataset", return_value=(True, None)),
        patch.object(ValidationPipeline, "_validate_runtime", return_value=(True, None)),
        patch.object(
            ValidationPipeline,
            "_normalize_column_names",
            side_effect=_passthrough_normalize,
        ),
    ):
        result = ValidationPipeline.validate_request_with_warnings(request_data)

    assert result.is_valid is False
    assert result.error is not None
    dumped = result.error.model_dump()
    assert dumped["error_code"] == "VALIDATION_PIPELINE_ERROR"
    assert "tagged-union" not in dumped["message"]
    assert "tagged-union" not in dumped["details"]
    assert "Input should be" in dumped["details"], (
        f"details must surface the Pydantic literal_error body 'Input should "
        f"be ...', got: {dumped['details']!r}"
    )


# ---------------------------------------------------------------------------
# pass_to_pass
# ---------------------------------------------------------------------------

def test_valid_mixed_timeseries_config_still_passes():
    """Sanity: the correct field names (``primary_kind`` / ``secondary_kind``)
    keep validating successfully — the fix must not regress the happy path."""
    from superset.mcp_service.chart.validation.pipeline import ValidationPipeline

    request_data = {
        "dataset_id": 1,
        "config": {
            "chart_type": "mixed_timeseries",
            "x": {"name": "order_date"},
            "y": [{"name": "revenue", "aggregate": "SUM"}],
            "y_secondary": [{"name": "orders", "aggregate": "COUNT"}],
            "primary_kind": "line",
            "secondary_kind": "bar",
        },
    }

    with (
        patch.object(ValidationPipeline, "_get_dataset_context", return_value=None),
        patch.object(ValidationPipeline, "_validate_dataset", return_value=(True, None)),
        patch.object(ValidationPipeline, "_validate_runtime", return_value=(True, None)),
        patch.object(
            ValidationPipeline,
            "_normalize_column_names",
            side_effect=_passthrough_normalize,
        ),
    ):
        result = ValidationPipeline.validate_request_with_warnings(request_data)

    assert result.is_valid is True
    assert result.error is None


def test_existing_error_templates_preserved():
    """Sanity: the fix must add ``validation_error`` without removing any of
    the existing template keys."""
    from superset.mcp_service.utils.error_builder import ChartErrorBuilder

    expected_existing = {
        "missing_field",
        "invalid_type",
        "invalid_value",
        "dataset_not_found",
        "column_not_found",
    }
    keys = set(ChartErrorBuilder.TEMPLATES.keys())
    assert expected_existing.issubset(keys), (
        f"Existing templates were removed: {expected_existing - keys}"
    )


def test_repo_ruff_check_passes_on_modified_files():
    """Repo's linter (ruff) passes on the files the fix lives in."""
    files = [
        REPO / "superset/mcp_service/chart/validation/pipeline.py",
        REPO / "superset/mcp_service/utils/error_builder.py",
    ]
    r = subprocess.run(
        ["ruff", "check", *[str(p) for p in files]],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"ruff check failed:\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )


def test_repo_ruff_format_passes_on_modified_files():
    """Repo's formatter (ruff format) reports clean on the modified files."""
    files = [
        REPO / "superset/mcp_service/chart/validation/pipeline.py",
        REPO / "superset/mcp_service/utils/error_builder.py",
    ]
    r = subprocess.run(
        ["ruff", "format", "--check", *[str(p) for p in files]],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"ruff format check failed:\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )

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

def test_ci_test_postgres_python_integration_tests_postgresql():
    """pass_to_pass | CI job 'test-postgres' → step 'Python integration tests (PostgreSQL)'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/python_tests.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python integration tests (PostgreSQL)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_mysql_generate_database_diagnostics_for_docs():
    """pass_to_pass | CI job 'test-mysql' → step 'Generate database diagnostics for docs'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -c "'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Generate database diagnostics for docs' failed (returncode={r.returncode}):\n"
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