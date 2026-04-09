#!/usr/bin/env python3
"""
Test outputs for Airflow Helm chart extraContainers refactoring.

This tests that workers.celery.extraContainers and workers.kubernetes.extraContainers
are properly supported, while workers.extraContainers is deprecated but still works.
"""

import json
import subprocess
import sys
from pathlib import Path

import jmespath
import pytest
import yaml

REPO = Path("/workspace/airflow")
CHART_DIR = REPO / "chart"
HELM_TESTS_DIR = REPO / "helm-tests"


def render_chart(values, show_only, chart_dir=None):
    """Render Helm chart with given values and return the parsed documents."""
    if chart_dir is None:
        chart_dir = CHART_DIR

    # Build values override
    values_str = json.dumps(values)

    # Build show-only arguments
    show_args = []
    for path in show_only:
        show_args.extend(["-s", path])

    # Run helm template
    cmd = [
        "helm", "template", "test-release", str(chart_dir),
        "--namespace", "default",
        "--set", f"_dummy={values_str}",  # We need to use -f for complex values
    ] + show_args

    # Write values to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(values, f)
        values_file = f.name

    try:
        cmd = [
            "helm", "template", "test-release", str(chart_dir),
            "--namespace", "default",
            "-f", values_file,
        ] + show_args

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            raise RuntimeError(f"helm template failed: {result.stderr}")

        # Parse the output (can be multiple YAML documents)
        docs = list(yaml.safe_load_all(result.stdout))
        return [d for d in docs if d is not None]
    finally:
        import os
        os.unlink(values_file)


class TestKubernetesExtraContainers:
    """Tests for workers.kubernetes.extraContainers in pod template file."""

    def test_kubernetes_extra_containers_new_path(self):
        """Test that workers.kubernetes.extraContainers works in pod template."""
        docs = render_chart(
            values={
                "workers": {
                    "kubernetes": {
                        "extraContainers": [
                            {"name": "test-sidecar", "image": "test:1.0"}
                        ]
                    }
                }
            },
            show_only=["templates/pod-template-file.yaml"],
        )

        assert len(docs) > 0, "No documents rendered"
        containers = jmespath.search("spec.containers[1:]", docs[0])
        assert containers == [{"name": "test-sidecar", "image": "test:1.0"}], \
            f"Expected sidecar container, got: {containers}"

    def test_deprecated_extra_containers_still_works(self):
        """Test that deprecated workers.extraContainers still works (backward compatibility)."""
        docs = render_chart(
            values={
                "workers": {
                    "extraContainers": [
                        {"name": "legacy-sidecar", "image": "legacy:1.0"}
                    ]
                }
            },
            show_only=["templates/pod-template-file.yaml"],
        )

        assert len(docs) > 0, "No documents rendered"
        containers = jmespath.search("spec.containers[1:]", docs[0])
        assert containers == [{"name": "legacy-sidecar", "image": "legacy:1.0"}], \
            f"Expected legacy sidecar container, got: {containers}"

    def test_new_path_takes_precedence_over_deprecated(self):
        """Test that workers.kubernetes.extraContainers takes precedence over workers.extraContainers."""
        docs = render_chart(
            values={
                "workers": {
                    "extraContainers": [
                        {"name": "old-sidecar", "image": "old:1.0"}
                    ],
                    "kubernetes": {
                        "extraContainers": [
                            {"name": "new-sidecar", "image": "new:1.0"}
                        ]
                    }
                }
            },
            show_only=["templates/pod-template-file.yaml"],
        )

        assert len(docs) > 0, "No documents rendered"
        containers = jmespath.search("spec.containers[1:]", docs[0])
        # New path should win
        assert containers == [{"name": "new-sidecar", "image": "new:1.0"}], \
            f"Expected new sidecar to take precedence, got: {containers}"

    def test_templating_works_with_new_path(self):
        """Test that Helm templating works with workers.kubernetes.extraContainers."""
        docs = render_chart(
            values={
                "workers": {
                    "kubernetes": {
                        "extraContainers": [
                            {"name": "{{ .Release.Name }}-sidecar", "image": "test:1.0"}
                        ]
                    }
                }
            },
            show_only=["templates/pod-template-file.yaml"],
        )

        assert len(docs) > 0, "No documents rendered"
        containers = jmespath.search("spec.containers[1:]", docs[0])
        # Template should be rendered with release name
        assert len(containers) == 1
        assert containers[0]["name"] == "test-release-sidecar", \
            f"Expected templated name, got: {containers[0]}"


class TestCeleryExtraContainers:
    """Tests for workers.celery.extraContainers in worker deployment."""

    def test_celery_extra_containers_new_path(self):
        """Test that workers.celery.extraContainers works in worker deployment."""
        docs = render_chart(
            values={
                "executor": "CeleryExecutor",
                "workers": {
                    "celery": {
                        "extraContainers": [
                            {"name": "celery-sidecar", "image": "celery:1.0"}
                        ]
                    }
                }
            },
            show_only=["templates/workers/worker-deployment.yaml"],
        )

        assert len(docs) > 0, "No documents rendered"
        # Skip main worker container (index 0) and log-groomer (index 1)
        containers = jmespath.search("spec.template.spec.containers[2:]", docs[0])
        assert containers == [{"name": "celery-sidecar", "image": "celery:1.0"}], \
            f"Expected celery sidecar container, got: {containers}"

    def test_deprecated_extra_containers_celery_still_works(self):
        """Test that deprecated workers.extraContainers still works for Celery."""
        docs = render_chart(
            values={
                "executor": "CeleryExecutor",
                "workers": {
                    "extraContainers": [
                        {"name": "legacy-celery-sidecar", "image": "legacy:1.0"}
                    ]
                }
            },
            show_only=["templates/workers/worker-deployment.yaml"],
        )

        assert len(docs) > 0, "No documents rendered"
        containers = jmespath.search("spec.template.spec.containers[2:]", docs[0])
        assert containers == [{"name": "legacy-celery-sidecar", "image": "legacy:1.0"}], \
            f"Expected legacy celery sidecar, got: {containers}"

    def test_new_celery_path_takes_precedence(self):
        """Test that workers.celery.extraContainers takes precedence over workers.extraContainers."""
        docs = render_chart(
            values={
                "executor": "CeleryExecutor",
                "workers": {
                    "extraContainers": [
                        {"name": "old-celery", "image": "old:1.0"}
                    ],
                    "celery": {
                        "extraContainers": [
                            {"name": "new-celery", "image": "new:1.0"}
                        ]
                    }
                }
            },
            show_only=["templates/workers/worker-deployment.yaml"],
        )

        assert len(docs) > 0, "No documents rendered"
        containers = jmespath.search("spec.template.spec.containers[2:]", docs[0])
        assert containers == [{"name": "new-celery", "image": "new:1.0"}], \
            f"Expected new celery path to take precedence, got: {containers}"

    def test_templating_works_with_celery_new_path(self):
        """Test that Helm templating works with workers.celery.extraContainers."""
        docs = render_chart(
            values={
                "executor": "CeleryExecutor",
                "workers": {
                    "celery": {
                        "extraContainers": [
                            {"name": "{{ .Chart.Name }}-sidecar", "image": "test:1.0"}
                        ]
                    }
                }
            },
            show_only=["templates/workers/worker-deployment.yaml"],
        )

        assert len(docs) > 0, "No documents rendered"
        containers = jmespath.search("spec.template.spec.containers[2:]", docs[0])
        assert len(containers) == 1
        # Chart name is "airflow" based on Chart.yaml
        assert containers[0]["name"] == "airflow-sidecar", \
            f"Expected templated name with Chart.Name, got: {containers[0]}"


class TestValuesSchema:
    """Tests for values.schema.json changes."""

    def test_celery_extra_containers_in_schema(self):
        """Test that workers.celery.extraContainers is defined in the JSON schema."""
        schema_path = CHART_DIR / "values.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)

        # Navigate to workers.celery.extraContainers
        celery_props = schema.get("properties", {}).get("workers", {}).get("properties", {}).get("celery", {}).get("properties", {})
        assert "extraContainers" in celery_props, \
            "workers.celery.extraContainers not found in schema"

        prop = celery_props["extraContainers"]
        assert prop.get("type") == "array", \
            f"Expected array type, got: {prop.get('type')}"

    def test_kubernetes_extra_containers_in_schema(self):
        """Test that workers.kubernetes.extraContainers is defined in the JSON schema."""
        schema_path = CHART_DIR / "values.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)

        # Navigate to workers.kubernetes.extraContainers
        k8s_props = schema.get("properties", {}).get("workers", {}).get("properties", {}).get("kubernetes", {}).get("properties", {})
        assert "extraContainers" in k8s_props, \
            "workers.kubernetes.extraContainers not found in schema"

        prop = k8s_props["extraContainers"]
        assert prop.get("type") == "array", \
            f"Expected array type, got: {prop.get('type')}"

    def test_deprecated_description_updated(self):
        """Test that workers.extraContainers description mentions deprecation."""
        schema_path = CHART_DIR / "values.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)

        workers_props = schema.get("properties", {}).get("workers", {}).get("properties", {})
        extra_containers = workers_props.get("extraContainers", {})
        desc = extra_containers.get("description", "")

        assert "deprecated" in desc.lower(), \
            f"Expected deprecation notice in description, got: {desc}"


class TestValuesYaml:
    """Tests for values.yaml changes."""

    def test_celery_extra_containers_default_empty(self):
        """Test that workers.celery.extraContainers defaults to empty list."""
        values_path = CHART_DIR / "values.yaml"
        with open(values_path) as f:
            values = yaml.safe_load(f)

        celery_extra = values.get("workers", {}).get("celery", {}).get("extraContainers", "NOT_FOUND")
        assert celery_extra == [], \
            f"Expected empty list for workers.celery.extraContainers, got: {celery_extra}"

    def test_kubernetes_extra_containers_default_empty(self):
        """Test that workers.kubernetes.extraContainers defaults to empty list."""
        values_path = CHART_DIR / "values.yaml"
        with open(values_path) as f:
            values = yaml.safe_load(f)

        k8s_extra = values.get("workers", {}).get("kubernetes", {}).get("extraContainers", "NOT_FOUND")
        assert k8s_extra == [], \
            f"Expected empty list for workers.kubernetes.extraContainers, got: {k8s_extra}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
