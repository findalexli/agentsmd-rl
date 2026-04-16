# SPDX-License-Identifier: Apache-2.0
"""
Tests for EMR Serverless OpenLineage injection functions.

These tests verify that the functions for injecting OpenLineage parent job
and transport information into EMR Serverless configuration exist and work
correctly.
"""

import copy
import importlib.util
import sys
from unittest import mock

import pytest

# Path to the airflow repo
REPO = "/workspace/airflow"


def load_spark_module():
    """Load the spark.py module directly, bypassing package __init__.py files."""
    spark_path = f"{REPO}/providers/openlineage/src/airflow/providers/openlineage/utils/spark.py"
    spec = importlib.util.spec_from_file_location("spark", spark_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {spark_path}")
    module = importlib.util.module_from_spec(spec)
    # Need to add fake modules for imports within spark.py
    sys.modules["airflow"] = mock.MagicMock()
    sys.modules["airflow.providers"] = mock.MagicMock()
    sys.modules["airflow.providers.openlineage"] = mock.MagicMock()
    sys.modules["airflow.providers.openlineage.plugins"] = mock.MagicMock()
    sys.modules["airflow.providers.openlineage.plugins.listener"] = mock.MagicMock()
    sys.modules["airflow.providers.openlineage.plugins.macros"] = mock.MagicMock()
    sys.modules["openlineage.client.transport.http"] = mock.MagicMock()
    spec.loader.exec_module(module)
    return module


def load_compat_spark_module():
    """Load the compat spark.py module directly."""
    compat_path = f"{REPO}/providers/common/compat/src/airflow/providers/common/compat/openlineage/utils/spark.py"
    spec = importlib.util.spec_from_file_location("compat_spark", compat_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {compat_path}")
    module = importlib.util.module_from_spec(spec)
    # Add mocks for required imports
    sys.modules["airflow.sdk"] = mock.MagicMock()

    # Try to load the openlineage spark module first
    try:
        ol_spark = load_spark_module()
        sys.modules["airflow.providers.openlineage.utils.spark"] = ol_spark
    except Exception:
        pass

    spec.loader.exec_module(module)
    return module


class TestEmrServerlessInjectionFunctionsExist:
    """Tests that EMR Serverless injection functions exist and are importable."""

    def test_inject_parent_job_function_exists(self):
        """The inject_parent_job_information_into_emr_serverless_properties function should exist (fail_to_pass)."""
        spark = load_spark_module()
        assert hasattr(spark, "inject_parent_job_information_into_emr_serverless_properties")
        assert callable(spark.inject_parent_job_information_into_emr_serverless_properties)

    def test_inject_transport_function_exists(self):
        """The inject_transport_information_into_emr_serverless_properties function should exist (fail_to_pass)."""
        spark = load_spark_module()
        assert hasattr(spark, "inject_transport_information_into_emr_serverless_properties")
        assert callable(spark.inject_transport_information_into_emr_serverless_properties)

    # NOTE: We do NOT test for the private helper function name directly.
    # Alternative correct implementations may use different internal helper names.
    # Behavior is tested through the public functions instead.


class TestEmrServerlessHelperBehavior:
    """Tests for EMR Serverless helper behavior - verified through public API."""

    def test_parent_injection_creates_spark_defaults_structure(self):
        """Parent injection creates the spark-defaults structure when missing (fail_to_pass)."""
        spark = load_spark_module()
        mock_context = mock.MagicMock()

        spark._get_parent_job_information_as_spark_properties = mock.MagicMock(return_value={
            "spark.openlineage.parentJobNamespace": "test_namespace",
            "spark.openlineage.parentJobName": "test_dag.test_task",
        })

        result = spark.inject_parent_job_information_into_emr_serverless_properties(None, mock_context)

        # Behavior: should create the nested structure
        assert "applicationConfiguration" in result
        assert len(result["applicationConfiguration"]) >= 1
        # Find the spark-defaults entry
        spark_defaults = next(
            (e for e in result["applicationConfiguration"] if e.get("classification") == "spark-defaults"),
            None
        )
        assert spark_defaults is not None, "spark-defaults classification should be created"
        assert isinstance(spark_defaults.get("properties"), dict)

    def test_transport_injection_creates_spark_defaults_structure(self):
        """Transport injection creates the spark-defaults structure when missing (fail_to_pass)."""
        spark = load_spark_module()
        mock_context = mock.MagicMock()

        spark._get_transport_information_as_spark_properties = mock.MagicMock(return_value={
            "spark.openlineage.transport.type": "http",
            "spark.openlineage.transport.url": "https://example.com",
        })

        result = spark.inject_transport_information_into_emr_serverless_properties(None, mock_context)

        # Behavior: should create the nested structure
        assert "applicationConfiguration" in result
        assert len(result["applicationConfiguration"]) >= 1
        # Find the spark-defaults entry
        spark_defaults = next(
            (e for e in result["applicationConfiguration"] if e.get("classification") == "spark-defaults"),
            None
        )
        assert spark_defaults is not None, "spark-defaults classification should be created"
        assert isinstance(spark_defaults.get("properties"), dict)


class TestGetOrCreateSparkDefaultsProperties:
    """Tests for spark-defaults entry creation/finding behavior - verified through public API."""

    def test_creates_spark_defaults_when_empty(self):
        """When applicationConfiguration is empty, creates spark-defaults entry (fail_to_pass)."""
        spark = load_spark_module()
        mock_context = mock.MagicMock()

        spark._get_parent_job_information_as_spark_properties = mock.MagicMock(return_value={
            "spark.openlineage.testKey": "testValue",
        })

        config = {}
        result = spark.inject_parent_job_information_into_emr_serverless_properties(config, mock_context)

        assert "applicationConfiguration" in result
        assert len(result["applicationConfiguration"]) == 1
        assert result["applicationConfiguration"][0]["classification"] == "spark-defaults"

    def test_finds_existing_spark_defaults(self):
        """When spark-defaults exists, uses it for injection (fail_to_pass)."""
        spark = load_spark_module()
        mock_context = mock.MagicMock()
        existing_props = {"spark.driver.memory": "4G"}
        config = {
            "applicationConfiguration": [
                {"classification": "spark-defaults", "properties": existing_props}
            ]
        }

        spark._get_parent_job_information_as_spark_properties = mock.MagicMock(return_value={
            "spark.openlineage.parentJobNamespace": "test_ns",
        })

        result = spark.inject_parent_job_information_into_emr_serverless_properties(config, mock_context)

        # The existing properties should be present
        spark_defaults = next(
            e for e in result["applicationConfiguration"]
            if e.get("classification") == "spark-defaults"
        )
        assert spark_defaults["properties"]["spark.driver.memory"] == "4G"
        assert spark_defaults["properties"]["spark.openlineage.parentJobNamespace"] == "test_ns"

    def test_creates_spark_defaults_alongside_other_configs(self):
        """When other classifications exist but not spark-defaults, adds it (fail_to_pass)."""
        spark = load_spark_module()
        mock_context = mock.MagicMock()

        spark._get_parent_job_information_as_spark_properties = mock.MagicMock(return_value={
            "spark.openlineage.testKey": "testValue",
        })

        config = {
            "applicationConfiguration": [
                {"classification": "spark-env", "properties": {"KEY": "value"}}
            ]
        }
        result = spark.inject_parent_job_information_into_emr_serverless_properties(config, mock_context)

        # Original entry preserved
        assert result["applicationConfiguration"][0]["classification"] == "spark-env"
        # New spark-defaults added
        assert len(result["applicationConfiguration"]) == 2
        assert result["applicationConfiguration"][1]["classification"] == "spark-defaults"


class TestInjectParentJobInformation:
    """Tests for inject_parent_job_information_into_emr_serverless_properties."""

    def test_inject_parent_into_none_config(self):
        """When configuration_overrides is None, creates full structure (fail_to_pass)."""
        spark = load_spark_module()
        mock_context = mock.MagicMock()

        # Mock the helper that gets parent job info
        spark._get_parent_job_information_as_spark_properties = mock.MagicMock(return_value={
            "spark.openlineage.parentJobNamespace": "test_namespace",
            "spark.openlineage.parentJobName": "test_dag.test_task",
        })

        result = spark.inject_parent_job_information_into_emr_serverless_properties(None, mock_context)

        assert "applicationConfiguration" in result
        spark_defaults = result["applicationConfiguration"][0]
        assert spark_defaults["classification"] == "spark-defaults"
        assert spark_defaults["properties"]["spark.openlineage.parentJobNamespace"] == "test_namespace"
        assert spark_defaults["properties"]["spark.openlineage.parentJobName"] == "test_dag.test_task"

    def test_inject_parent_preserves_existing_properties(self):
        """Existing spark-defaults properties are preserved when injecting (fail_to_pass)."""
        spark = load_spark_module()
        mock_context = mock.MagicMock()
        config = {
            "applicationConfiguration": [
                {"classification": "spark-defaults", "properties": {"spark.driver.memory": "8G"}}
            ]
        }

        spark._get_parent_job_information_as_spark_properties = mock.MagicMock(
            return_value={"spark.openlineage.parentJobNamespace": "ns"}
        )

        result = spark.inject_parent_job_information_into_emr_serverless_properties(config, mock_context)

        props = result["applicationConfiguration"][0]["properties"]
        assert props["spark.driver.memory"] == "8G"  # preserved
        assert props["spark.openlineage.parentJobNamespace"] == "ns"  # injected

    def test_inject_parent_does_not_mutate_input(self):
        """The original configuration_overrides dict is not mutated (fail_to_pass)."""
        spark = load_spark_module()
        mock_context = mock.MagicMock()
        original = {
            "applicationConfiguration": [
                {"classification": "spark-defaults", "properties": {"spark.driver.memory": "4G"}}
            ]
        }
        original_copy = copy.deepcopy(original)

        spark._get_parent_job_information_as_spark_properties = mock.MagicMock(
            return_value={"spark.openlineage.parentJobNamespace": "ns"}
        )

        spark.inject_parent_job_information_into_emr_serverless_properties(original, mock_context)

        assert original == original_copy

    def test_inject_parent_skips_if_already_present(self):
        """Injection is skipped when parent job info already exists (fail_to_pass)."""
        spark = load_spark_module()
        mock_context = mock.MagicMock()
        config = {
            "applicationConfiguration": [
                {
                    "classification": "spark-defaults",
                    "properties": {"spark.openlineage.parentJobNamespace": "existing_ns"},
                }
            ]
        }

        mock_get_parent = mock.MagicMock()
        spark._get_parent_job_information_as_spark_properties = mock_get_parent

        result = spark.inject_parent_job_information_into_emr_serverless_properties(config, mock_context)

        mock_get_parent.assert_not_called()
        assert result["applicationConfiguration"][0]["properties"]["spark.openlineage.parentJobNamespace"] == "existing_ns"


class TestInjectTransportInformation:
    """Tests for inject_transport_information_into_emr_serverless_properties."""

    def test_inject_transport_into_none_config(self):
        """When configuration_overrides is None, creates full structure (fail_to_pass)."""
        spark = load_spark_module()
        mock_context = mock.MagicMock()

        spark._get_transport_information_as_spark_properties = mock.MagicMock(return_value={
            "spark.openlineage.transport.type": "http",
            "spark.openlineage.transport.url": "https://example.com",
        })

        result = spark.inject_transport_information_into_emr_serverless_properties(None, mock_context)

        assert "applicationConfiguration" in result
        props = result["applicationConfiguration"][0]["properties"]
        assert props["spark.openlineage.transport.type"] == "http"
        assert props["spark.openlineage.transport.url"] == "https://example.com"

    def test_inject_transport_skips_if_already_present(self):
        """Injection is skipped when transport info already exists (fail_to_pass)."""
        spark = load_spark_module()
        mock_context = mock.MagicMock()
        config = {
            "applicationConfiguration": [
                {
                    "classification": "spark-defaults",
                    "properties": {"spark.openlineage.transport.type": "console"},
                }
            ]
        }

        mock_get_transport = mock.MagicMock()
        spark._get_transport_information_as_spark_properties = mock_get_transport

        result = spark.inject_transport_information_into_emr_serverless_properties(config, mock_context)

        mock_get_transport.assert_not_called()
        assert result["applicationConfiguration"][0]["properties"]["spark.openlineage.transport.type"] == "console"


class TestCompatLayerExports:
    """Tests that the compat layer exports the new functions."""

    def test_compat_layer_exports_parent_injection_function(self):
        """The compat layer should export inject_parent_job_information_into_emr_serverless_properties (fail_to_pass)."""
        compat = load_compat_spark_module()
        assert hasattr(compat, "inject_parent_job_information_into_emr_serverless_properties")
        assert callable(compat.inject_parent_job_information_into_emr_serverless_properties)

    def test_compat_layer_exports_transport_injection_function(self):
        """The compat layer should export inject_transport_information_into_emr_serverless_properties (fail_to_pass)."""
        compat = load_compat_spark_module()
        assert hasattr(compat, "inject_transport_information_into_emr_serverless_properties")
        assert callable(compat.inject_transport_information_into_emr_serverless_properties)

    def test_compat_layer_all_exports_include_new_functions(self):
        """The __all__ in compat layer should include the new EMR functions (fail_to_pass)."""
        compat = load_compat_spark_module()
        assert hasattr(compat, "__all__")
        assert "inject_parent_job_information_into_emr_serverless_properties" in compat.__all__
        assert "inject_transport_information_into_emr_serverless_properties" in compat.__all__


class TestPreservesMonitoringConfiguration:
    """Tests that other configuration keys are preserved."""

    def test_monitoring_config_preserved(self):
        """The monitoringConfiguration key should be preserved after injection (fail_to_pass)."""
        spark = load_spark_module()
        mock_context = mock.MagicMock()
        config = {
            "applicationConfiguration": [{"classification": "spark-defaults", "properties": {}}],
            "monitoringConfiguration": {
                "s3MonitoringConfiguration": {"logUri": "s3://my-bucket/logs"}
            },
        }

        spark._get_parent_job_information_as_spark_properties = mock.MagicMock(
            return_value={"spark.openlineage.parentJobNamespace": "ns"}
        )

        result = spark.inject_parent_job_information_into_emr_serverless_properties(config, mock_context)

        # monitoringConfiguration preserved
        assert result["monitoringConfiguration"]["s3MonitoringConfiguration"]["logUri"] == "s3://my-bucket/logs"
        # OpenLineage properties injected
        assert result["applicationConfiguration"][0]["properties"]["spark.openlineage.parentJobNamespace"] == "ns"


class TestMultipleConfigurationClassifications:
    """Tests handling of multiple configuration classifications."""

    def test_multiple_classifications_preserved(self):
        """Multiple applicationConfiguration entries are preserved (fail_to_pass)."""
        spark = load_spark_module()
        mock_context = mock.MagicMock()
        config = {
            "applicationConfiguration": [
                {"classification": "spark-env", "properties": {"PYSPARK_PYTHON": "/usr/bin/python3"}},
                {"classification": "spark-defaults", "properties": {"spark.executor.memory": "2G"}},
            ]
        }

        spark._get_parent_job_information_as_spark_properties = mock.MagicMock(
            return_value={"spark.openlineage.parentJobNamespace": "ns"}
        )

        result = spark.inject_parent_job_information_into_emr_serverless_properties(config, mock_context)

        # spark-env preserved
        assert result["applicationConfiguration"][0]["classification"] == "spark-env"
        assert result["applicationConfiguration"][0]["properties"]["PYSPARK_PYTHON"] == "/usr/bin/python3"
        # spark-defaults has both original and new props
        spark_defaults = next(e for e in result["applicationConfiguration"] if e["classification"] == "spark-defaults")
        assert spark_defaults["properties"]["spark.executor.memory"] == "2G"
        assert spark_defaults["properties"]["spark.openlineage.parentJobNamespace"] == "ns"


class TestExistingFunctionsStillWork:
    """Pass-to-pass tests: existing functionality should still work after changes."""

    def test_existing_glue_injection_function_exists(self):
        """The existing inject_parent_job_information_into_glue_arguments function still exists (pass_to_pass)."""
        spark = load_spark_module()
        assert hasattr(spark, "inject_parent_job_information_into_glue_arguments")
        assert callable(spark.inject_parent_job_information_into_glue_arguments)

    def test_existing_spark_properties_injection_function_exists(self):
        """The existing inject_parent_job_information_into_spark_properties function still exists (pass_to_pass)."""
        spark = load_spark_module()
        assert hasattr(spark, "inject_parent_job_information_into_spark_properties")
        assert callable(spark.inject_parent_job_information_into_spark_properties)

    def test_existing_transport_glue_function_exists(self):
        """The existing inject_transport_information_into_glue_arguments function still exists (pass_to_pass)."""
        spark = load_spark_module()
        assert hasattr(spark, "inject_transport_information_into_glue_arguments")
        assert callable(spark.inject_transport_information_into_glue_arguments)

    def test_existing_transport_spark_function_exists(self):
        """The existing inject_transport_information_into_spark_properties function still exists (pass_to_pass)."""
        spark = load_spark_module()
        assert hasattr(spark, "inject_transport_information_into_spark_properties")
        assert callable(spark.inject_transport_information_into_spark_properties)

    def test_existing_is_parent_job_info_present_function_exists(self):
        """The existing _is_parent_job_information_present_in_spark_properties helper still exists (pass_to_pass)."""
        spark = load_spark_module()
        assert hasattr(spark, "_is_parent_job_information_present_in_spark_properties")
        assert callable(spark._is_parent_job_information_present_in_spark_properties)

    def test_is_parent_job_info_present_detects_namespace(self):
        """The _is_parent_job_information_present_in_spark_properties correctly detects namespace key (pass_to_pass)."""
        spark = load_spark_module()
        props_with_namespace = {"spark.openlineage.parentJobNamespace": "test"}
        props_without = {"spark.driver.memory": "4G"}

        assert spark._is_parent_job_information_present_in_spark_properties(props_with_namespace) is True
        assert spark._is_parent_job_information_present_in_spark_properties(props_without) is False

    def test_is_transport_info_present_function_exists(self):
        """The existing _is_transport_information_present_in_spark_properties helper still exists (pass_to_pass)."""
        spark = load_spark_module()
        assert hasattr(spark, "_is_transport_information_present_in_spark_properties")
        assert callable(spark._is_transport_information_present_in_spark_properties)

    def test_is_transport_info_present_detects_transport_type(self):
        """The _is_transport_information_present_in_spark_properties correctly detects transport key (pass_to_pass)."""
        spark = load_spark_module()
        props_with_transport = {"spark.openlineage.transport.type": "http"}
        props_without = {"spark.executor.memory": "2G"}

        assert spark._is_transport_information_present_in_spark_properties(props_with_transport) is True
        assert spark._is_transport_information_present_in_spark_properties(props_without) is False


import subprocess


class TestRepoCI:
    """Pass-to-pass tests: actual CI commands that should pass on base commit."""

    def test_repo_syntax_check_spark_py(self):
        """Python syntax check on spark.py passes (pass_to_pass)."""
        r = subprocess.run(
            ["python", "-m", "py_compile",
             f"{REPO}/providers/openlineage/src/airflow/providers/openlineage/utils/spark.py"],
            capture_output=True, text=True, timeout=60,
        )
        assert r.returncode == 0, f"Syntax check failed:\n{r.stderr[-500:]}"

    def test_repo_syntax_check_compat_spark_py(self):
        """Python syntax check on compat spark.py passes (pass_to_pass)."""
        r = subprocess.run(
            ["python", "-m", "py_compile",
             f"{REPO}/providers/common/compat/src/airflow/providers/common/compat/openlineage/utils/spark.py"],
            capture_output=True, text=True, timeout=60,
        )
        assert r.returncode == 0, f"Syntax check failed:\n{r.stderr[-500:]}"

    def test_repo_lint_spark_module(self):
        """Ruff linting on spark.py module passes (pass_to_pass)."""
        # Install ruff if not present
        subprocess.run(["pip", "install", "ruff", "--quiet"], capture_output=True, timeout=120)
        r = subprocess.run(
            ["ruff", "check", "--no-cache",
             f"{REPO}/providers/openlineage/src/airflow/providers/openlineage/utils/spark.py",
             "--config", f"{REPO}/pyproject.toml"],
            capture_output=True, text=True, timeout=120,
        )
        assert r.returncode == 0, f"Lint failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"

    def test_repo_lint_compat_spark_module(self):
        """Ruff linting on compat spark.py module passes (pass_to_pass)."""
        # Install ruff if not present
        subprocess.run(["pip", "install", "ruff", "--quiet"], capture_output=True, timeout=120)
        r = subprocess.run(
            ["ruff", "check", "--no-cache",
             f"{REPO}/providers/common/compat/src/airflow/providers/common/compat/openlineage/utils/spark.py",
             "--config", f"{REPO}/pyproject.toml"],
            capture_output=True, text=True, timeout=120,
        )
        assert r.returncode == 0, f"Lint failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"

    def test_repo_format_check_spark_module(self):
        """Ruff format check on spark.py module passes (pass_to_pass)."""
        # Install ruff if not present
        subprocess.run(["pip", "install", "ruff", "--quiet"], capture_output=True, timeout=120)
        r = subprocess.run(
            ["ruff", "format", "--check", "--no-cache",
             f"{REPO}/providers/openlineage/src/airflow/providers/openlineage/utils/spark.py",
             "--config", f"{REPO}/pyproject.toml"],
            capture_output=True, text=True, timeout=120,
        )
        assert r.returncode == 0, f"Format check failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"
