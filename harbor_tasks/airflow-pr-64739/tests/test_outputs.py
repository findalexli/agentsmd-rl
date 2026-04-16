"""
Tests for airflow-helm-worker-extra-containers task.

This PR adds workers.celery.extraContainers and workers.kubernetes.extraContainers
configuration options to the Airflow Helm chart, deprecating workers.extraContainers.
"""

import subprocess
import json
import os
import tempfile
import shutil
import yaml

REPO = "/workspace/airflow"
CHART_DIR = os.path.join(REPO, "chart")


def setup_chart_for_pod_template_test():
    """
    Copy the pod-template-file to templates/ so Helm can render it.
    This mimics what the Airflow helm tests do.
    """
    src = os.path.join(CHART_DIR, "files", "pod-template-file.kubernetes-helm-yaml")
    dst = os.path.join(CHART_DIR, "templates", "pod-template-file.yaml")
    if not os.path.exists(dst):
        shutil.copy(src, dst)
    return dst


def cleanup_pod_template():
    """Remove the copied pod-template-file from templates/."""
    dst = os.path.join(CHART_DIR, "templates", "pod-template-file.yaml")
    if os.path.exists(dst):
        os.remove(dst)


def run_helm_template(values: dict, show_only: str = None, chart_dir: str = None) -> list:
    """Render Helm chart with given values and return parsed YAML docs."""
    if chart_dir is None:
        chart_dir = CHART_DIR

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(values, f)
        values_file = f.name

    try:
        cmd = ["helm", "template", "release-name", chart_dir, "-f", values_file]
        if show_only:
            cmd.extend(["--show-only", show_only])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=chart_dir
        )

        if result.returncode != 0:
            raise RuntimeError(f"Helm template failed: {result.stderr}")

        # Parse all YAML documents
        docs = list(yaml.safe_load_all(result.stdout))
        # Filter out None documents
        docs = [d for d in docs if d is not None]
        return docs

    finally:
        os.unlink(values_file)


def get_containers_from_pod_template(docs: list) -> list:
    """Extract containers from the rendered pod template."""
    for doc in docs:
        if doc and doc.get("kind") == "Pod":
            return doc.get("spec", {}).get("containers", [])
    return []


# ============================================================================
# FAIL-TO-PASS TESTS
# These tests should FAIL on the base commit and PASS after the fix
# ============================================================================


def test_kubernetes_extra_containers_in_pod_template():
    """
    Test that workers.kubernetes.extraContainers adds containers to pod-template-file.

    This is the core feature: the new workers.kubernetes.extraContainers path
    should be recognized and result in extra containers in the pod template.
    """
    # Setup: copy pod-template-file to templates/
    setup_chart_for_pod_template_test()

    try:
        values = {
            "workers": {
                "kubernetes": {
                    "extraContainers": [
                        {"name": "sidecar-k8s", "image": "busybox:1.35"}
                    ]
                }
            }
        }

        docs = run_helm_template(values, "templates/pod-template-file.yaml")
        containers = get_containers_from_pod_template(docs)

        container_names = [c.get("name") for c in containers]
        assert "sidecar-k8s" in container_names, (
            f"Expected 'sidecar-k8s' container in pod-template-file, got: {container_names}"
        )
    finally:
        cleanup_pod_template()


def test_kubernetes_extra_containers_priority_over_legacy():
    """
    Test that workers.kubernetes.extraContainers takes priority over workers.extraContainers.

    When both are specified, the kubernetes-specific path should be used.
    """
    setup_chart_for_pod_template_test()

    try:
        values = {
            "workers": {
                "extraContainers": [
                    {"name": "legacy-sidecar", "image": "legacy:1.0"}
                ],
                "kubernetes": {
                    "extraContainers": [
                        {"name": "new-sidecar", "image": "new:2.0"}
                    ]
                }
            }
        }

        docs = run_helm_template(values, "templates/pod-template-file.yaml")
        containers = get_containers_from_pod_template(docs)

        container_names = [c.get("name") for c in containers]

        # The new kubernetes path should take priority
        assert "new-sidecar" in container_names, (
            f"Expected 'new-sidecar' container (from kubernetes path), got: {container_names}"
        )
        # The legacy container should NOT be present when kubernetes path is specified
        assert "legacy-sidecar" not in container_names, (
            f"Legacy 'legacy-sidecar' should not be present when kubernetes path is specified"
        )
    finally:
        cleanup_pod_template()


def test_values_schema_has_kubernetes_extra_containers():
    """
    Test that values.schema.json defines workers.kubernetes.extraContainers.

    The schema must include the new property for validation to work correctly.
    """
    schema_path = os.path.join(CHART_DIR, "values.schema.json")
    with open(schema_path) as f:
        schema = json.load(f)

    # Navigate to workers.kubernetes properties
    workers_props = schema.get("properties", {}).get("workers", {}).get("properties", {})
    kubernetes_props = workers_props.get("kubernetes", {}).get("properties", {})

    assert "extraContainers" in kubernetes_props, (
        f"Expected 'extraContainers' in workers.kubernetes properties, "
        f"found: {list(kubernetes_props.keys())}"
    )


def test_values_schema_has_celery_extra_containers():
    """
    Test that values.schema.json defines workers.celery.extraContainers.

    The schema must include the new property for validation to work correctly.
    """
    schema_path = os.path.join(CHART_DIR, "values.schema.json")
    with open(schema_path) as f:
        schema = json.load(f)

    # Navigate to workers.celery properties
    workers_props = schema.get("properties", {}).get("workers", {}).get("properties", {})
    celery_props = workers_props.get("celery", {}).get("properties", {})

    assert "extraContainers" in celery_props, (
        f"Expected 'extraContainers' in workers.celery properties, "
        f"found: {list(celery_props.keys())}"
    )


def test_deprecation_warning_for_legacy_extra_containers():
    """
    Test that using workers.extraContainers triggers a deprecation warning
    in the rendered chart output.

    When the legacy workers.extraContainers is set to a non-empty value,
    the rendered chart should communicate to the user that this config
    path is deprecated (e.g. via NOTES.txt).
    """
    values = {
        "workers": {
            "extraContainers": [
                {"name": "test-sidecar", "image": "busybox:1.35"}
            ]
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(values, f)
        values_file = f.name

    try:
        result = subprocess.run(
            ["helm", "template", "release-name", CHART_DIR, "-f", values_file],
            capture_output=True, text=True, timeout=120, cwd=CHART_DIR
        )

        assert result.returncode == 0, f"Helm template failed: {result.stderr}"

        # The rendered output should mention the legacy workers.extraContainers
        # config path, indicating a deprecation notice to the user.
        output_lower = result.stdout.lower()
        assert "workers.extracontainers" in output_lower, (
            "Expected chart output to mention 'workers.extraContainers' when "
            "the legacy configuration is used, indicating a deprecation notice"
        )
    finally:
        os.unlink(values_file)


def test_values_yaml_has_kubernetes_extra_containers_default():
    """
    Test that values.yaml includes workers.kubernetes.extraContainers default.
    """
    values_path = os.path.join(CHART_DIR, "values.yaml")
    with open(values_path) as f:
        values = yaml.safe_load(f)

    kubernetes_section = values.get("workers", {}).get("kubernetes", {})

    assert "extraContainers" in kubernetes_section, (
        f"Expected 'extraContainers' in workers.kubernetes section of values.yaml"
    )


def test_values_yaml_has_celery_extra_containers_default():
    """
    Test that values.yaml includes workers.celery.extraContainers default.
    """
    values_path = os.path.join(CHART_DIR, "values.yaml")
    with open(values_path) as f:
        values = yaml.safe_load(f)

    celery_section = values.get("workers", {}).get("celery", {})

    assert "extraContainers" in celery_section, (
        f"Expected 'extraContainers' in workers.celery section of values.yaml"
    )


# ============================================================================
# PASS-TO-PASS TESTS
# These tests should PASS both before and after the fix (backward compatibility)
# ============================================================================


def test_legacy_extra_containers_still_works():
    """
    Test that workers.extraContainers (legacy path) still works for backward compatibility.

    Even though it's deprecated, the old configuration path should continue to work.
    """
    setup_chart_for_pod_template_test()

    try:
        values = {
            "workers": {
                "extraContainers": [
                    {"name": "legacy-sidecar", "image": "busybox:1.34"}
                ]
            }
        }

        docs = run_helm_template(values, "templates/pod-template-file.yaml")
        containers = get_containers_from_pod_template(docs)

        container_names = [c.get("name") for c in containers]
        assert "legacy-sidecar" in container_names, (
            f"Expected 'legacy-sidecar' container from legacy path, got: {container_names}"
        )
    finally:
        cleanup_pod_template()


def test_helm_template_renders_successfully():
    """
    Test that the chart renders without errors using default values.
    """
    result = subprocess.run(
        ["helm", "template", "release-name", CHART_DIR],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=CHART_DIR
    )

    assert result.returncode == 0, f"Helm template failed: {result.stderr}"


def test_pod_template_file_renders():
    """
    Test that pod-template-file.yaml template renders when copied to templates/.
    """
    setup_chart_for_pod_template_test()

    try:
        result = subprocess.run(
            ["helm", "template", "release-name", CHART_DIR, "--show-only", "templates/pod-template-file.yaml"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=CHART_DIR
        )

        assert result.returncode == 0, f"Pod template rendering failed: {result.stderr}"
        assert "kind: Pod" in result.stdout or "kind:" in result.stdout, (
            "Expected Pod kind in output"
        )
    finally:
        cleanup_pod_template()


def test_values_schema_valid_json():
    """
    Test that values.schema.json is valid JSON.
    """
    schema_path = os.path.join(CHART_DIR, "values.schema.json")
    with open(schema_path) as f:
        schema = json.load(f)

    assert "properties" in schema, "Schema should have properties"
    assert "workers" in schema.get("properties", {}), "Schema should have workers property"


def test_repo_helm_lint():
    """
    Helm lint passes on the chart (pass_to_pass).

    This is a real CI check from the repo's pre-commit hooks.
    """
    result = subprocess.run(
        ["helm", "lint", ".", "-f", "values.yaml"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=CHART_DIR
    )

    assert result.returncode == 0, f"Helm lint failed:\n{result.stderr}"
    assert "chart(s) linted, 0 chart(s) failed" in result.stdout


def test_repo_helm_lint_strict():
    """
    Helm lint passes in strict mode (pass_to_pass).

    Strict mode catches additional issues like missing required fields.
    """
    result = subprocess.run(
        ["helm", "lint", ".", "--strict"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=CHART_DIR
    )

    assert result.returncode == 0, f"Helm lint strict failed:\n{result.stderr}"


def test_repo_chart_yaml_valid():
    """
    Chart.yaml is valid and parseable by helm (pass_to_pass).

    Uses 'helm show chart' which validates the Chart.yaml structure.
    """
    result = subprocess.run(
        ["helm", "show", "chart", CHART_DIR],
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, f"helm show chart failed:\n{result.stderr}"
    assert "name: airflow" in result.stdout, "Chart name should be 'airflow'"
    assert "apiVersion:" in result.stdout, "Chart should have apiVersion"


def test_repo_helm_template_all_executors():
    """
    Helm template renders for all executor types (pass_to_pass).

    Validates that the chart renders correctly with different executor configurations.
    """
    for executor in ["LocalExecutor", "CeleryExecutor", "KubernetesExecutor"]:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({"executor": executor}, f)
            values_file = f.name

        try:
            result = subprocess.run(
                ["helm", "template", "release-name", CHART_DIR, "-f", values_file],
                capture_output=True,
                text=True,
                timeout=120,
            )

            assert result.returncode == 0, f"Helm template failed for {executor}:\n{result.stderr}"
        finally:
            os.unlink(values_file)


if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
