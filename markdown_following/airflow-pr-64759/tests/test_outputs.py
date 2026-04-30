# Licensed under the Apache License, Version 2.0
"""
Tests for airflow-helm-scheduler-name task.

This task tests that the Helm chart correctly supports:
1. workers.kubernetes.schedulerName for pod-template-file
2. workers.celery.schedulerName for celery workers
3. Proper priority order with the new nested options taking precedence
"""
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml

REPO = Path("/workspace/airflow")
CHART_DIR = REPO / "chart"


@pytest.fixture(scope="module")
def prepared_chart_dir(tmp_path_factory):
    """
    Copy the chart to a temp directory and copy the pod-template-file
    to templates/ so Helm can render it.
    """
    tmp_dir = tmp_path_factory.mktemp("chart")
    temp_chart_dir = tmp_dir / "chart"

    # Copy the entire chart
    shutil.copytree(CHART_DIR, temp_chart_dir)

    # Copy pod-template-file to templates/ so helm can render it
    shutil.copyfile(
        temp_chart_dir / "files" / "pod-template-file.kubernetes-helm-yaml",
        temp_chart_dir / "templates" / "pod-template-file.yaml",
    )

    return temp_chart_dir


def render_chart(values: dict, show_only: list[str] | None = None, chart_dir: Path | None = None) -> list[dict]:
    """Render helm chart with given values and return parsed k8s objects."""
    chart_path = chart_dir if chart_dir else CHART_DIR

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(values, f)
        values_file = f.name

    cmd = [
        "helm", "template", "release-name", str(chart_path),
        "--values", values_file,
        "--kube-version", "1.30.0",
        "--namespace", "default",
    ]
    if show_only:
        for item in show_only:
            cmd.extend(["--show-only", item])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=str(chart_path))
    Path(values_file).unlink()

    if result.returncode != 0:
        raise RuntimeError(f"Helm template failed: {result.stderr}")

    # Parse multi-document YAML
    objects = list(yaml.safe_load_all(result.stdout))
    return [obj for obj in objects if obj is not None]


class TestPodTemplateSchedulerName:
    """Tests for workers.kubernetes.schedulerName in pod-template-file."""

    def test_kubernetes_scheduler_name_takes_priority(self, prepared_chart_dir):
        """
        When workers.kubernetes.schedulerName is set, it should take priority
        over workers.schedulerName in the pod template file.

        This is a fail-to-pass test: before the fix, only workers.schedulerName
        was checked, so kubernetes.schedulerName was ignored.
        """
        docs = render_chart(
            values={
                "schedulerName": "global-scheduler",
                "workers": {
                    "schedulerName": "old-worker-scheduler",
                    "kubernetes": {
                        "schedulerName": "k8s-specific-scheduler"
                    }
                }
            },
            show_only=["templates/pod-template-file.yaml"],
            chart_dir=prepared_chart_dir,
        )
        assert len(docs) >= 1, "Expected at least one document from pod-template-file"
        pod = docs[0]
        actual_scheduler = pod.get("spec", {}).get("schedulerName")
        # The kubernetes-specific scheduler should take priority
        assert actual_scheduler == "k8s-specific-scheduler", (
            f"Expected 'k8s-specific-scheduler' but got '{actual_scheduler}'. "
            "workers.kubernetes.schedulerName should take priority."
        )

    def test_kubernetes_scheduler_name_only(self, prepared_chart_dir):
        """
        When only workers.kubernetes.schedulerName is set (not workers.schedulerName),
        the pod template should use that value.
        """
        docs = render_chart(
            values={
                "schedulerName": "global-scheduler",
                "workers": {
                    "kubernetes": {
                        "schedulerName": "kubernetes-only-scheduler"
                    }
                }
            },
            show_only=["templates/pod-template-file.yaml"],
            chart_dir=prepared_chart_dir,
        )
        assert len(docs) >= 1
        pod = docs[0]
        actual_scheduler = pod.get("spec", {}).get("schedulerName")
        assert actual_scheduler == "kubernetes-only-scheduler", (
            f"Expected 'kubernetes-only-scheduler' but got '{actual_scheduler}'"
        )

    def test_fallback_to_workers_scheduler_name(self, prepared_chart_dir):
        """
        When workers.kubernetes.schedulerName is not set, fallback to workers.schedulerName.
        This should work both before and after the fix (pass-to-pass).
        """
        docs = render_chart(
            values={
                "schedulerName": "global-scheduler",
                "workers": {
                    "schedulerName": "fallback-scheduler"
                }
            },
            show_only=["templates/pod-template-file.yaml"],
            chart_dir=prepared_chart_dir,
        )
        assert len(docs) >= 1
        pod = docs[0]
        actual_scheduler = pod.get("spec", {}).get("schedulerName")
        assert actual_scheduler == "fallback-scheduler", (
            f"Expected 'fallback-scheduler' but got '{actual_scheduler}'"
        )

    def test_fallback_to_global_scheduler_name(self, prepared_chart_dir):
        """
        When neither kubernetes nor workers schedulerName is set,
        fallback to global schedulerName.
        """
        docs = render_chart(
            values={
                "schedulerName": "global-only-scheduler",
                "workers": {}
            },
            show_only=["templates/pod-template-file.yaml"],
            chart_dir=prepared_chart_dir,
        )
        assert len(docs) >= 1
        pod = docs[0]
        actual_scheduler = pod.get("spec", {}).get("schedulerName")
        assert actual_scheduler == "global-only-scheduler", (
            f"Expected 'global-only-scheduler' but got '{actual_scheduler}'"
        )


class TestValuesSchemaUpdate:
    """Tests for values.schema.json updates."""

    def test_schema_has_kubernetes_scheduler_name(self):
        """
        The values.schema.json should have workers.kubernetes.schedulerName defined.
        """
        schema_path = CHART_DIR / "values.schema.json"
        schema = json.loads(schema_path.read_text())

        # Navigate to workers.kubernetes.schedulerName in schema
        workers_props = schema.get("properties", {}).get("workers", {}).get("properties", {})
        kubernetes_props = workers_props.get("kubernetes", {}).get("properties", {})

        assert "schedulerName" in kubernetes_props, (
            "workers.kubernetes.schedulerName should be defined in values.schema.json"
        )

        scheduler_schema = kubernetes_props["schedulerName"]
        assert "description" in scheduler_schema, (
            "workers.kubernetes.schedulerName should have a description"
        )
        assert "pods created with pod-template-file" in scheduler_schema["description"].lower() or \
               "pod-template-file" in scheduler_schema["description"], (
            f"Description should mention pod-template-file: {scheduler_schema['description']}"
        )

    def test_schema_has_celery_scheduler_name(self):
        """
        The values.schema.json should have workers.celery.schedulerName defined.
        """
        schema_path = CHART_DIR / "values.schema.json"
        schema = json.loads(schema_path.read_text())

        # Navigate to workers.celery.schedulerName in schema
        workers_props = schema.get("properties", {}).get("workers", {}).get("properties", {})
        celery_props = workers_props.get("celery", {}).get("properties", {})

        assert "schedulerName" in celery_props, (
            "workers.celery.schedulerName should be defined in values.schema.json"
        )

        scheduler_schema = celery_props["schedulerName"]
        assert "description" in scheduler_schema, (
            "workers.celery.schedulerName should have a description"
        )
        assert "celery" in scheduler_schema["description"].lower(), (
            f"Description should mention celery: {scheduler_schema['description']}"
        )

    def test_old_scheduler_name_marked_deprecated(self):
        """
        The workers.schedulerName field should be marked as deprecated in description.
        """
        schema_path = CHART_DIR / "values.schema.json"
        schema = json.loads(schema_path.read_text())

        workers_props = schema.get("properties", {}).get("workers", {}).get("properties", {})
        old_scheduler = workers_props.get("schedulerName", {})

        description = old_scheduler.get("description", "")
        assert "deprecated" in description.lower(), (
            f"workers.schedulerName description should mention 'deprecated': {description}"
        )


class TestValuesYamlUpdate:
    """Tests for values.yaml updates."""

    def test_values_has_kubernetes_scheduler_name(self):
        """
        The values.yaml should have workers.kubernetes.schedulerName defined as a key.
        """
        values_path = CHART_DIR / "values.yaml"
        values = yaml.safe_load(values_path.read_text())

        workers = values.get("workers", {})
        kubernetes = workers.get("kubernetes", {})

        # Check that schedulerName is explicitly defined as a key
        assert "schedulerName" in kubernetes, (
            "workers.kubernetes.schedulerName should be defined in values.yaml"
        )

    def test_values_has_celery_scheduler_name(self):
        """
        The values.yaml should have workers.celery.schedulerName defined as a key.
        """
        values_path = CHART_DIR / "values.yaml"
        values = yaml.safe_load(values_path.read_text())

        workers = values.get("workers", {})
        celery = workers.get("celery", {})

        # Check that schedulerName is explicitly defined as a key
        assert "schedulerName" in celery, (
            "workers.celery.schedulerName should be defined in values.yaml"
        )


class TestDeprecationWarning:
    """Tests for deprecation warning in NOTES.txt."""

    def test_deprecation_warning_in_notes_template(self):
        """
        The NOTES.txt template should contain logic to show a deprecation
        warning when workers.schedulerName is used.
        """
        notes_path = CHART_DIR / "templates" / "NOTES.txt"
        notes_content = notes_path.read_text()

        # Check for deprecation warning related to workers.schedulerName
        has_deprecation_check = (
            ".Values.workers.schedulerName" in notes_content and
            ("DEPRECATION" in notes_content.upper() or
             "workers.celery.schedulerName" in notes_content or
             "workers.kubernetes.schedulerName" in notes_content)
        )

        assert has_deprecation_check, (
            "NOTES.txt should contain a deprecation warning for workers.schedulerName "
            "mentioning workers.celery.schedulerName or workers.kubernetes.schedulerName"
        )


class TestHelmTemplateRenders:
    """Pass-to-pass tests: basic helm template rendering should still work."""

    def test_helm_template_renders_without_error(self, prepared_chart_dir):
        """Basic helm template should render without errors."""
        result = subprocess.run(
            ["helm", "template", "release-name", str(prepared_chart_dir)],
            capture_output=True, text=True, timeout=120, cwd=str(prepared_chart_dir)
        )
        assert result.returncode == 0, f"Helm template failed: {result.stderr}"

    def test_pod_template_file_renders(self, prepared_chart_dir):
        """Pod template file should render correctly."""
        docs = render_chart(
            values={},
            show_only=["templates/pod-template-file.yaml"],
            chart_dir=prepared_chart_dir,
        )
        assert len(docs) >= 1, "Pod template file should render"
        assert docs[0].get("kind") == "Pod", "Should render a Pod"


class TestRepoCI:
    """Pass-to-pass tests: repo's actual CI/CD tests must pass (pass_to_pass)."""

    def test_repo_helm_lint(self):
        """Repo's helm lint passes (pass_to_pass)."""
        r = subprocess.run(
            ["helm", "lint", "chart"],
            capture_output=True, text=True, timeout=60, cwd=str(REPO),
        )
        assert r.returncode == 0, f"Helm lint failed:\n{r.stderr[-1000:]}"

    def test_repo_values_schema_validation(self):
        """Repo's values.yaml validates against values.schema.json (pass_to_pass)."""
        r = subprocess.run(
            ["python", "-m", "pytest",
             "tests/helm_tests/airflow_aux/test_chart_quality.py::TestChartQuality::test_values_validate_schema",
             "-v", "--tb=short"],
            capture_output=True, text=True, timeout=60, cwd=str(REPO / "helm-tests"),
        )
        assert r.returncode == 0, f"Schema validation failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"

    def test_repo_scheduler_name_pod_template(self):
        """Repo's scheduler name tests for pod template pass (pass_to_pass)."""
        r = subprocess.run(
            ["python", "-m", "pytest",
             "tests/helm_tests/airflow_aux/test_pod_template_file.py::TestPodTemplateFile::test_scheduler_name",
             "-v", "--tb=short"],
            capture_output=True, text=True, timeout=120, cwd=str(REPO / "helm-tests"),
        )
        assert r.returncode == 0, f"Pod template scheduler tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"

    def test_repo_scheduler_name_worker(self):
        """Repo's scheduler name tests for celery worker pass (pass_to_pass)."""
        r = subprocess.run(
            ["python", "-m", "pytest",
             "tests/helm_tests/airflow_core/test_worker.py::TestWorker::test_scheduler_name",
             "-v", "--tb=short"],
            capture_output=True, text=True, timeout=120, cwd=str(REPO / "helm-tests"),
        )
        assert r.returncode == 0, f"Worker scheduler tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"
