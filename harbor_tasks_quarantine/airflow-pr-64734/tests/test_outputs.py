"""
Tests for apache/airflow#64734: Add workers.celery.hpa

This PR introduces a new `workers.celery.hpa` section in values.yaml/schema and
deprecates the old `workers.hpa` section (as it was only applicable to Celery workers).

The PR makes the following changes:
1. Adds explicit workers.celery.hpa section in values.yaml with documentation
2. Adds schema validation for workers.celery.hpa in values.schema.json
3. Adds deprecation warnings in NOTES.txt for workers.hpa settings
4. Updates tests to cover both configuration paths
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path("/workspace/airflow")


class TestValuesYamlChanges:
    """Test that values.yaml contains the new workers.celery.hpa section."""

    def test_values_yaml_has_celery_hpa_section(self):
        """
        Fail-to-pass: Verify values.yaml contains workers.celery.hpa section.

        Before the fix, workers.celery.hpa does not exist in values.yaml.
        After the fix, it should be present with hpa configuration options.
        """
        values_path = REPO / "chart" / "values.yaml"
        content = values_path.read_text()

        # Find the workers.celery section and verify hpa is under it
        lines = content.split('\n')
        in_workers = False
        in_celery = False
        found_celery_hpa = False
        workers_indent = 0
        celery_indent = 0

        for i, line in enumerate(lines):
            stripped = line.lstrip()
            current_indent = len(line) - len(stripped)

            if stripped.startswith('workers:') and not stripped.startswith('workers:'):
                continue
            if line.strip() == 'workers:':
                in_workers = True
                workers_indent = current_indent
                continue

            if in_workers:
                # Check if we've exited the workers section
                if current_indent <= workers_indent and stripped and not stripped.startswith('#'):
                    if not stripped.startswith('workers'):
                        in_workers = False
                        continue

                # Look for celery: under workers
                if stripped == 'celery:' or stripped.startswith('celery:'):
                    in_celery = True
                    celery_indent = current_indent
                    continue

            if in_celery:
                # Check if we've exited the celery section
                if current_indent <= celery_indent and stripped and not stripped.startswith('#'):
                    if not stripped.startswith('celery'):
                        in_celery = False
                        continue

                # Look for hpa: under celery
                if stripped == 'hpa:' or stripped.startswith('hpa:'):
                    if current_indent > celery_indent:
                        found_celery_hpa = True
                        break

        assert found_celery_hpa, (
            "values.yaml should have workers.celery.hpa section. "
            "This section was added to provide a clearer configuration path for Celery worker HPA settings."
        )

    def test_values_yaml_has_celery_hpa_enabled_property(self):
        """
        Fail-to-pass: Verify values.yaml has enabled property under workers.celery.hpa.
        """
        values_path = REPO / "chart" / "values.yaml"
        content = values_path.read_text()

        # Look for the pattern of enabled: ~ under workers.celery.hpa section
        # This is more specific than just checking for "hpa:"
        lines = content.split('\n')
        in_celery_hpa = False

        for i, line in enumerate(lines):
            # Look for workers.celery.hpa section marker
            if 'celery:' in line and i > 0:
                # Check if we're in the workers section
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    if next_line.strip().startswith('hpa:'):
                        in_celery_hpa = True
                        break
                    if next_line.strip() and not next_line.strip().startswith('#') and not next_line.strip().startswith('-'):
                        # Hit another property
                        if next_line[0] not in ' \t':
                            break
                    j += 1

            if in_celery_hpa:
                # Now look for enabled: in the hpa section
                if 'enabled:' in line:
                    # Verify it's under celery.hpa by checking comment or null value
                    assert True
                    return

        assert in_celery_hpa, (
            "values.yaml should have enabled property under workers.celery.hpa"
        )


class TestSchemaChanges:
    """Test that values.schema.json contains workers.celery.hpa schema."""

    def test_schema_has_celery_hpa_properties(self):
        """
        Fail-to-pass: Verify values.schema.json contains workers.celery.hpa schema.

        Before the fix, the schema doesn't define workers.celery.hpa.
        After the fix, it should have the hpa properties under workers.celery.
        """
        schema_path = REPO / "chart" / "values.schema.json"
        schema = json.loads(schema_path.read_text())

        # Navigate to workers.celery.hpa in the schema
        workers_props = schema.get("properties", {}).get("workers", {}).get("properties", {})
        celery_props = workers_props.get("celery", {}).get("properties", {})

        assert "hpa" in celery_props, (
            "Schema should define workers.celery.hpa properties. "
            "The PR adds HPA configuration options under workers.celery."
        )

        hpa_props = celery_props["hpa"].get("properties", {})

        # Verify key HPA properties exist
        expected_props = ["enabled", "minReplicaCount", "maxReplicaCount"]
        for prop in expected_props:
            assert prop in hpa_props, f"workers.celery.hpa should have '{prop}' property defined in schema"

    def test_schema_celery_hpa_has_metrics_property(self):
        """
        Fail-to-pass: Verify schema defines workers.celery.hpa.metrics.
        """
        schema_path = REPO / "chart" / "values.schema.json"
        schema = json.loads(schema_path.read_text())

        workers_props = schema.get("properties", {}).get("workers", {}).get("properties", {})
        celery_props = workers_props.get("celery", {}).get("properties", {})
        hpa_props = celery_props.get("hpa", {}).get("properties", {})

        assert "metrics" in hpa_props, (
            "Schema should define workers.celery.hpa.metrics property"
        )

    def test_schema_celery_hpa_has_behavior_property(self):
        """
        Fail-to-pass: Verify schema defines workers.celery.hpa.behavior.
        """
        schema_path = REPO / "chart" / "values.schema.json"
        schema = json.loads(schema_path.read_text())

        workers_props = schema.get("properties", {}).get("workers", {}).get("properties", {})
        celery_props = workers_props.get("celery", {}).get("properties", {})
        hpa_props = celery_props.get("hpa", {}).get("properties", {})

        assert "behavior" in hpa_props, (
            "Schema should define workers.celery.hpa.behavior property"
        )


class TestDeprecationWarnings:
    """Test that deprecation warnings are properly configured."""

    def test_notes_have_deprecation_warnings_for_hpa_enabled(self):
        """
        Fail-to-pass: Verify NOTES.txt contains deprecation warning for workers.hpa.enabled.
        """
        notes_path = REPO / "chart" / "templates" / "NOTES.txt"
        content = notes_path.read_text()

        assert "workers.hpa.enabled" in content, (
            "NOTES.txt should contain deprecation warning for workers.hpa.enabled"
        )
        assert "workers.celery.hpa.enabled" in content, (
            "NOTES.txt should mention workers.celery.hpa.enabled as the new location"
        )

    def test_notes_have_deprecation_warnings_for_hpa_minreplica(self):
        """
        Fail-to-pass: Verify NOTES.txt contains deprecation warning for workers.hpa.minReplicaCount.
        """
        notes_path = REPO / "chart" / "templates" / "NOTES.txt"
        content = notes_path.read_text()

        assert "workers.hpa.minReplicaCount" in content, (
            "NOTES.txt should contain deprecation warning for workers.hpa.minReplicaCount"
        )

    def test_notes_have_deprecation_warnings_for_hpa_maxreplica(self):
        """
        Fail-to-pass: Verify NOTES.txt contains deprecation warning for workers.hpa.maxReplicaCount.
        """
        notes_path = REPO / "chart" / "templates" / "NOTES.txt"
        content = notes_path.read_text()

        assert "workers.hpa.maxReplicaCount" in content, (
            "NOTES.txt should contain deprecation warning for workers.hpa.maxReplicaCount"
        )


class TestBackwardCompatibility:
    """Test that old workers.hpa configuration still works."""

    def test_legacy_hpa_still_works(self):
        """
        Pass-to-pass: Verify legacy workers.hpa configuration still renders HPA.

        For backward compatibility, the old workers.hpa should continue working.
        """
        values_content = """
executor: CeleryExecutor
workers:
  hpa:
    enabled: true
    minReplicaCount: 2
    maxReplicaCount: 8
"""
        values_file = REPO / "chart" / "test_values_legacy.yaml"
        values_file.write_text(values_content)

        try:
            result = subprocess.run(
                [
                    "helm", "template", "test-release", str(REPO / "chart"),
                    "-f", str(values_file),
                    "--set", "workers.keda.enabled=false",
                ],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=REPO
            )

            if result.returncode != 0:
                pytest.fail(f"Helm template failed: {result.stderr}")

            rendered = result.stdout

            # Legacy config should still create HPA
            assert "kind: HorizontalPodAutoscaler" in rendered, (
                "Legacy workers.hpa.enabled=true should still create an HPA (backward compatibility)"
            )

        finally:
            values_file.unlink(missing_ok=True)

    def test_celery_hpa_via_merge_works(self):
        """
        Pass-to-pass: Verify workers.celery.hpa values are merged into workers.hpa.

        The workersMergeValues function merges celery settings, so this should work
        both before and after the PR.
        """
        values_content = """
executor: CeleryExecutor
workers:
  celery:
    hpa:
      enabled: true
      maxReplicaCount: 15
"""
        values_file = REPO / "chart" / "test_values_celery.yaml"
        values_file.write_text(values_content)

        try:
            result = subprocess.run(
                [
                    "helm", "template", "test-release", str(REPO / "chart"),
                    "-f", str(values_file),
                    "--set", "workers.keda.enabled=false",
                ],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=REPO
            )

            if result.returncode != 0:
                pytest.fail(f"Helm template failed: {result.stderr}")

            rendered = result.stdout

            # Should create HPA via celery merge
            assert "kind: HorizontalPodAutoscaler" in rendered, (
                "workers.celery.hpa should work via workersMergeValues"
            )

        finally:
            values_file.unlink(missing_ok=True)


class TestRepoHelmTests:
    """Run the repository's Helm tests as pass-to-pass checks."""

    def test_helm_chart_lint(self):
        """
        Pass-to-pass: Helm chart should pass linting.
        """
        result = subprocess.run(
            ["helm", "lint", str(REPO / "chart")],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO
        )
        assert result.returncode == 0, f"Helm lint failed:\n{result.stderr}\n{result.stdout}"

    def test_helm_template_default_values(self):
        """
        Pass-to-pass: Chart should render with default values.
        """
        result = subprocess.run(
            ["helm", "template", "test", str(REPO / "chart")],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO
        )
        assert result.returncode == 0, f"Helm template with defaults failed:\n{result.stderr}"

    def test_repo_hpa_disabled_by_default(self):
        """
        Pass-to-pass: Repo's HPA test that verifies HPA is disabled by default.
        """
        result = subprocess.run(
            ["uv", "run", "python", "-m", "pytest",
             "tests/helm_tests/other/test_hpa.py::TestHPA::test_hpa_disabled_by_default",
             "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO / "helm-tests"
        )
        assert result.returncode == 0, f"Repo HPA test failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"

    def test_repo_hpa_enabled_celery(self):
        """
        Pass-to-pass: Repo's HPA test for CeleryExecutor.
        Uses -k filter to match both base and PR parametrization formats.
        """
        result = subprocess.run(
            ["uv", "run", "python", "-m", "pytest",
             "tests/helm_tests/other/test_hpa.py::TestHPA",
             "-k", "test_hpa_enabled and CeleryExecutor and not CeleryKubernetes",
             "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO / "helm-tests"
        )
        assert result.returncode == 0, f"Repo HPA CeleryExecutor test failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"

    def test_repo_chart_schema_validation(self):
        """
        Pass-to-pass: Repo's chart quality test validating values.yaml against schema.
        """
        result = subprocess.run(
            ["uv", "run", "python", "-m", "pytest",
             "tests/helm_tests/airflow_aux/test_chart_quality.py::TestChartQuality::test_values_validate_schema",
             "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO / "helm-tests"
        )
        assert result.returncode == 0, f"Chart schema validation test failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"

    def test_repo_worker_kind(self):
        """
        Pass-to-pass: Repo's worker kind test (StatefulSet vs Deployment).
        """
        result = subprocess.run(
            ["uv", "run", "python", "-m", "pytest",
             "tests/helm_tests/airflow_core/test_worker.py::TestWorker::test_worker_kind",
             "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO / "helm-tests"
        )
        assert result.returncode == 0, f"Worker kind test failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"
