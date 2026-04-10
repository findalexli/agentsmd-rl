"""
Tests for OpenLineage injection in EmrServerlessStartJobOperator.

These tests verify that:
1. The operator has the new openlineage_inject_parent_job_info and openlineage_inject_transport_info parameters
2. The helper functions for injecting configuration exist and work correctly
3. The injection logic properly modifies configuration_overrides
4. The repo's existing CI/CD tests pass (pass_to_pass gates)
"""

import pytest
import subprocess
import sys
import os
from unittest import mock

# Add the airflow paths
sys.path.insert(0, "/workspace/airflow/airflow-core/src")
sys.path.insert(0, "/workspace/airflow/task-sdk/src")
sys.path.insert(0, "/workspace/airflow/providers/common/compat/src")
sys.path.insert(0, "/workspace/airflow/providers/openlineage/src")
sys.path.insert(0, "/workspace/airflow/providers/amazon/src")

REPO = "/workspace/airflow"

# Constants for tests
EXAMPLE_CONTEXT = {
    "task_instance": mock.MagicMock(
        dag_id="test_dag",
        task_id="test_task",
        try_number=1,
        run_id="test_run_1234",
        logical_date="2024-01-01T00:00:00+00:00",
    ),
    "run_id": "test_run_1234",
}

EXAMPLE_HTTP_TRANSPORT_CONFIG = {
    "type": "http",
    "url": "https://some-custom.url",
    "endpoint": "api/v1/lineage",
    "timeout": 5,
}


class TestEmrServerlessOperatorOpenLineageParams:
    """Test that EmrServerlessStartJobOperator has OpenLineage injection parameters."""

    def test_operator_has_inject_parent_job_info_param(self):
        """Verify operator accepts openlineage_inject_parent_job_info parameter."""
        from airflow.providers.amazon.aws.operators.emr import EmrServerlessStartJobOperator

        operator = EmrServerlessStartJobOperator(
            task_id="test_task",
            application_id="app_123",
            execution_role_arn="arn:aws:iam::123456789012:role/EMRServerlessRole",
            job_driver={"sparkSubmit": {"entryPoint": "s3://bucket/script.py"}},
            openlineage_inject_parent_job_info=True,
        )
        assert hasattr(operator, "openlineage_inject_parent_job_info")
        assert operator.openlineage_inject_parent_job_info is True

    def test_operator_has_inject_transport_info_param(self):
        """Verify operator accepts openlineage_inject_transport_info parameter."""
        from airflow.providers.amazon.aws.operators.emr import EmrServerlessStartJobOperator

        operator = EmrServerlessStartJobOperator(
            task_id="test_task",
            application_id="app_123",
            execution_role_arn="arn:aws:iam::123456789012:role/EMRServerlessRole",
            job_driver={"sparkSubmit": {"entryPoint": "s3://bucket/script.py"}},
            openlineage_inject_transport_info=True,
        )
        assert hasattr(operator, "openlineage_inject_transport_info")
        assert operator.openlineage_inject_transport_info is True

    def test_operator_params_default_to_false(self):
        """Verify OpenLineage params default to False when not specified."""
        from airflow.providers.amazon.aws.operators.emr import EmrServerlessStartJobOperator

        operator = EmrServerlessStartJobOperator(
            task_id="test_task",
            application_id="app_123",
            execution_role_arn="arn:aws:iam::123456789012:role/EMRServerlessRole",
            job_driver={"sparkSubmit": {"entryPoint": "s3://bucket/script.py"}},
        )
        assert operator.openlineage_inject_parent_job_info is False
        assert operator.openlineage_inject_transport_info is False


class TestSparkUtilsHelperFunctions:
    """Test helper functions for EMR Serverless OpenLineage injection."""

    def test_inject_parent_job_info_into_emr_serverless_exists(self):
        """Verify inject_parent_job_information_into_emr_serverless_properties function exists."""
        from airflow.providers.openlineage.utils.spark import (
            inject_parent_job_information_into_emr_serverless_properties,
        )

        assert callable(inject_parent_job_information_into_emr_serverless_properties)

    def test_inject_transport_info_into_emr_serverless_exists(self):
        """Verify inject_transport_information_into_emr_serverless_properties function exists."""
        from airflow.providers.openlineage.utils.spark import (
            inject_transport_information_into_emr_serverless_properties,
        )

        assert callable(inject_transport_information_into_emr_serverless_properties)

    def test_get_or_create_spark_defaults_exists(self):
        """Verify _get_or_create_spark_defaults_properties helper exists."""
        from airflow.providers.openlineage.utils.spark import (
            _get_or_create_spark_defaults_properties,
        )

        assert callable(_get_or_create_spark_defaults_properties)

    @mock.patch(
        "airflow.providers.openlineage.utils.spark._get_parent_job_information_as_spark_properties"
    )
    def test_inject_parent_job_info_creates_structure_when_none(self, mock_get_parent):
        """When configuration_overrides is None, creates the full structure."""
        from airflow.providers.openlineage.utils.spark import (
            inject_parent_job_information_into_emr_serverless_properties,
        )

        mock_get_parent.return_value = {
            "spark.openlineage.parentJobNamespace": "default",
            "spark.openlineage.parentJobName": "test_dag.test_task",
            "spark.openlineage.parentRunId": "test-run-id-123",
        }

        result = inject_parent_job_information_into_emr_serverless_properties(
            None, EXAMPLE_CONTEXT
        )

        assert "applicationConfiguration" in result
        assert len(result["applicationConfiguration"]) == 1
        assert result["applicationConfiguration"][0]["classification"] == "spark-defaults"
        props = result["applicationConfiguration"][0]["properties"]
        assert props["spark.openlineage.parentJobNamespace"] == "default"
        assert props["spark.openlineage.parentJobName"] == "test_dag.test_task"
        assert props["spark.openlineage.parentRunId"] == "test-run-id-123"

    @mock.patch(
        "airflow.providers.openlineage.utils.spark._get_parent_job_information_as_spark_properties"
    )
    def test_inject_parent_job_info_appends_to_existing_spark_defaults(self, mock_get_parent):
        """Appends parent job info to existing spark-defaults properties."""
        from airflow.providers.openlineage.utils.spark import (
            inject_parent_job_information_into_emr_serverless_properties,
        )

        mock_get_parent.return_value = {"spark.openlineage.parentJobNamespace": "default"}

        config = {
            "applicationConfiguration": [
                {
                    "classification": "spark-defaults",
                    "properties": {"spark.driver.memory": "8G", "spark.executor.cores": "4"},
                }
            ]
        }

        result = inject_parent_job_information_into_emr_serverless_properties(
            config, EXAMPLE_CONTEXT
        )

        props = result["applicationConfiguration"][0]["properties"]
        assert props["spark.driver.memory"] == "8G"
        assert props["spark.executor.cores"] == "4"
        assert props["spark.openlineage.parentJobNamespace"] == "default"

    @mock.patch(
        "airflow.providers.openlineage.utils.spark._get_parent_job_information_as_spark_properties"
    )
    def test_inject_parent_job_info_creates_spark_defaults_when_missing(self, mock_get_parent):
        """Creates spark-defaults entry when only other classifications exist."""
        from airflow.providers.openlineage.utils.spark import (
            inject_parent_job_information_into_emr_serverless_properties,
        )

        mock_get_parent.return_value = {"spark.openlineage.parentJobNamespace": "default"}

        config = {
            "applicationConfiguration": [
                {"classification": "spark-env", "properties": {"PYSPARK_PYTHON": "/usr/bin/python3"}}
            ]
        }

        result = inject_parent_job_information_into_emr_serverless_properties(
            config, EXAMPLE_CONTEXT
        )

        # Original entry preserved
        assert result["applicationConfiguration"][0]["classification"] == "spark-env"
        # New spark-defaults entry added
        spark_defaults = result["applicationConfiguration"][1]
        assert spark_defaults["classification"] == "spark-defaults"
        assert spark_defaults["properties"]["spark.openlineage.parentJobNamespace"] == "default"

    @mock.patch(
        "airflow.providers.openlineage.utils.spark._get_parent_job_information_as_spark_properties"
    )
    def test_inject_parent_job_info_skips_if_already_present(self, mock_get_parent):
        """Injection is skipped when parent job info is already in spark-defaults."""
        from airflow.providers.openlineage.utils.spark import (
            inject_parent_job_information_into_emr_serverless_properties,
        )

        config = {
            "applicationConfiguration": [
                {
                    "classification": "spark-defaults",
                    "properties": {"spark.openlineage.parentJobNamespace": "already_set"},
                }
            ]
        }

        result = inject_parent_job_information_into_emr_serverless_properties(
            config, EXAMPLE_CONTEXT
        )

        assert (
            result["applicationConfiguration"][0]["properties"][
                "spark.openlineage.parentJobNamespace"
            ]
            == "already_set"
        )
        mock_get_parent.assert_not_called()

    @mock.patch(
        "airflow.providers.openlineage.utils.spark._get_parent_job_information_as_spark_properties"
    )
    def test_inject_parent_job_info_preserves_other_config(self, mock_get_parent):
        """Other keys like monitoringConfiguration are preserved."""
        from airflow.providers.openlineage.utils.spark import (
            inject_parent_job_information_into_emr_serverless_properties,
        )

        mock_get_parent.return_value = {"spark.openlineage.parentJobNamespace": "default"}

        config = {
            "applicationConfiguration": [
                {"classification": "spark-defaults", "properties": {}}
            ],
            "monitoringConfiguration": {
                "s3MonitoringConfiguration": {"logUri": "s3://bucket/logs"}
            },
        }

        result = inject_parent_job_information_into_emr_serverless_properties(
            config, EXAMPLE_CONTEXT
        )

        assert (
            result["monitoringConfiguration"]["s3MonitoringConfiguration"]["logUri"]
            == "s3://bucket/logs"
        )
        assert (
            result["applicationConfiguration"][0]["properties"][
                "spark.openlineage.parentJobNamespace"
            ]
            == "default"
        )

    @mock.patch("airflow.providers.openlineage.utils.spark.get_openlineage_listener")
    def test_inject_transport_info_creates_structure_when_empty(self, mock_ol_listener):
        """With no existing config, transport props are injected into new spark-defaults."""
        from airflow.providers.openlineage.utils.spark import (
            inject_transport_information_into_emr_serverless_properties,
        )
        from openlineage.client.transport.http import HttpTransport, HttpConfig

        fake_listener = mock.MagicMock()
        mock_ol_listener.return_value = fake_listener
        fake_listener.adapter.get_or_create_openlineage_client.return_value.transport = HttpTransport(
            HttpConfig.from_dict(EXAMPLE_HTTP_TRANSPORT_CONFIG)
        )

        result = inject_transport_information_into_emr_serverless_properties(
            None, EXAMPLE_CONTEXT
        )

        props = result["applicationConfiguration"][0]["properties"]
        assert props["spark.openlineage.transport.type"] == "http"
        assert props["spark.openlineage.transport.url"] == "https://some-custom.url"

    @mock.patch("airflow.providers.openlineage.utils.spark.get_openlineage_listener")
    def test_inject_transport_info_skips_if_already_present(self, mock_ol_listener):
        """Injection is skipped when transport info is already in spark-defaults."""
        from airflow.providers.openlineage.utils.spark import (
            inject_transport_information_into_emr_serverless_properties,
        )

        fake_listener = mock.MagicMock()
        mock_ol_listener.return_value = fake_listener

        config = {
            "applicationConfiguration": [
                {
                    "classification": "spark-defaults",
                    "properties": {"spark.openlineage.transport.type": "http"},
                }
            ]
        }

        result = inject_transport_information_into_emr_serverless_properties(
            config, EXAMPLE_CONTEXT
        )

        assert (
            result["applicationConfiguration"][0]["properties"][
                "spark.openlineage.transport.type"
            ]
            == "http"
        )
        fake_listener.adapter.get_or_create_openlineage_client.assert_not_called()


class TestCompatModuleExports:
    """Test that compat module exports the new functions."""

    def test_compat_exports_inject_parent_job_info_emr(self):
        """Verify compat module exports inject_parent_job_information_into_emr_serverless_properties."""
        from airflow.providers.common.compat.openlineage.utils.spark import (
            inject_parent_job_information_into_emr_serverless_properties,
        )

        assert callable(inject_parent_job_information_into_emr_serverless_properties)

    def test_compat_exports_inject_transport_info_emr(self):
        """Verify compat module exports inject_transport_information_into_emr_serverless_properties."""
        from airflow.providers.common.compat.openlineage.utils.spark import (
            inject_transport_information_into_emr_serverless_properties,
        )

        assert callable(inject_transport_information_into_emr_serverless_properties)

    def test_compat_functions_work_with_none_input(self):
        """Compat fallback functions work when openlineage not available."""
        from airflow.providers.common.compat.openlineage.utils.spark import (
            inject_parent_job_information_into_emr_serverless_properties,
            inject_transport_information_into_emr_serverless_properties,
        )

        # These should return empty dict when openlineage is not available
        # (may return None or empty dict depending on implementation)
        parent_result = inject_parent_job_information_into_emr_serverless_properties(
            None, EXAMPLE_CONTEXT
        )
        transport_result = inject_transport_information_into_emr_serverless_properties(
            None, EXAMPLE_CONTEXT
        )

        # Results should be dict-like (either empty dict or the input)
        assert parent_result is not None
        assert transport_result is not None


class TestInputImmutability:
    """Test that input configuration is not mutated."""

    @mock.patch(
        "airflow.providers.openlineage.utils.spark._get_parent_job_information_as_spark_properties"
    )
    def test_inject_parent_job_info_does_not_mutate_input(self, mock_get_parent):
        """The original configuration_overrides dict is not mutated."""
        from airflow.providers.openlineage.utils.spark import (
            inject_parent_job_information_into_emr_serverless_properties,
        )
        import copy

        mock_get_parent.return_value = {"spark.openlineage.parentJobNamespace": "default"}

        original = {
            "applicationConfiguration": [
                {
                    "classification": "spark-defaults",
                    "properties": {"spark.driver.memory": "4G"},
                }
            ]
        }
        original_copy = copy.deepcopy(original)

        inject_parent_job_information_into_emr_serverless_properties(
            original, EXAMPLE_CONTEXT
        )

        assert original == original_copy


# =============================================================================
# PASS-TO-PASS TESTS (Repo CI/CD Tests)
# These tests verify that existing repo tests pass on both base and gold commits
# =============================================================================


class TestRepoEmrTestsPass:
    """Pass-to-pass: EMR Serverless operator tests from the repo pass."""

    def test_repo_emr_serverless_operator_tests(self):
        """Repo's EMR Serverless operator unit tests pass (pass_to_pass)."""
        r = subprocess.run(
            [
                "uv", "run", "--project", "providers/amazon",
                "pytest", "providers/amazon/tests/unit/amazon/aws/operators/test_emr_serverless.py",
                "-v", "--tb=short"
            ],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO,
        )
        assert r.returncode == 0, f"EMR Serverless operator tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"

    def test_repo_emr_serverless_hook_tests(self):
        """Repo's EMR Serverless hook unit tests pass (pass_to_pass)."""
        r = subprocess.run(
            [
                "uv", "run", "--project", "providers/amazon",
                "pytest", "providers/amazon/tests/unit/amazon/aws/hooks/test_emr_serverless.py",
                "-v", "--tb=short"
            ],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO,
        )
        assert r.returncode == 0, f"EMR Serverless hook tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


class TestRepoOpenlineageTestsPass:
    """Pass-to-pass: OpenLineage spark utils tests from the repo pass."""

    def test_repo_openlineage_spark_utils_tests(self):
        """Repo's OpenLineage spark utils unit tests pass (pass_to_pass)."""
        r = subprocess.run(
            [
                "uv", "run", "--project", "providers/openlineage",
                "pytest", "providers/openlineage/tests/unit/openlineage/utils/test_spark.py",
                "-v", "--tb=short"
            ],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO,
        )
        assert r.returncode == 0, f"OpenLineage spark utils tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


class TestRepoCompatTestsPass:
    """Pass-to-pass: Common compat module tests from the repo pass."""

    def test_repo_common_compat_openlineage_tests(self):
        """Repo's common compat openlineage tests pass (pass_to_pass)."""
        r = subprocess.run(
            [
                "uv", "run", "--project", "providers/common/compat",
                "pytest", "providers/common/compat/tests/unit/common/compat/openlineage/utils/test_spark.py",
                "-v", "--tb=short"
            ],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Common compat tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


class TestRepoCodeQuality:
    """Pass-to-pass: Code quality checks from the repo pass."""

    def test_repo_amazon_ruff_check(self):
        """Repo's Amazon provider code passes ruff linting (pass_to_pass)."""
        r = subprocess.run(
            [
                "uv", "run", "--project", "providers/amazon",
                "ruff", "check", "providers/amazon/src/airflow/providers/amazon/aws/operators/emr.py"
            ],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Amazon provider ruff check failed:\n{r.stdout}\n{r.stderr}"

    def test_repo_openlineage_ruff_check(self):
        """Repo's OpenLineage provider code passes ruff linting (pass_to_pass)."""
        r = subprocess.run(
            [
                "uv", "run", "--project", "providers/openlineage",
                "ruff", "check", "providers/openlineage/src/airflow/providers/openlineage/utils/spark.py"
            ],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=REPO,
        )
        assert r.returncode == 0, f"OpenLineage provider ruff check failed:\n{r.stdout}\n{r.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
