#!/usr/bin/env python3
"""
Test script for airflow helm chart worker affinity changes.
Tests that workers.celery.affinity and workers.kubernetes.affinity work correctly.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

REPO = Path("/workspace/airflow")
CHART_DIR = REPO / "chart"
HELM_TESTS_DIR = REPO / "helm-tests"


def helm_template(values=None, show_only=None, chart_dir=None):
    """Run helm template and return the rendered output."""
    if chart_dir is None:
        chart_dir = CHART_DIR

    cmd = ["helm", "template", "test-release", str(chart_dir)]

    if values:
        # Create a temporary values file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(values, f)
            values_file = f.name
        cmd.extend(["-f", values_file])

    if show_only:
        for path in show_only:
            cmd.extend(["--show-only", path])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    if values:
        os.unlink(values_file)

    if result.returncode != 0:
        raise RuntimeError(f"helm template failed: {result.stderr}")

    # Parse multi-document YAML output
    docs = list(yaml.safe_load_all(result.stdout))
    return [d for d in docs if d is not None]


def get_doc_by_kind(docs, kind):
    """Get document by Kubernetes kind."""
    for doc in docs:
        if doc and doc.get("kind") == kind:
            return doc
    return None


# =============================================================================
# Fail-to-pass tests (must fail on base commit, pass on fix)
# =============================================================================


def test_kubernetes_affinity_in_pod_template():
    """Test that workers.kubernetes.affinity is applied to pod-template-file.

    This test verifies that the new workers.kubernetes.affinity field
    is properly read and applied in the pod template file template.

    The pod-template-file is stored in a ConfigMap, so we check that the
    template file contains the logic to use workers.kubernetes.affinity.
    """
    # Read the template file directly to verify the logic exists
    template_path = CHART_DIR / "files" / "pod-template-file.kubernetes-helm-yaml"

    with open(template_path) as f:
        template_content = f.read()

    # Check that the template uses workers.kubernetes.affinity with precedence
    assert "workers.kubernetes.affinity" in template_content, \
        "pod-template-file template should reference workers.kubernetes.affinity"

    # Check the order of precedence: kubernetes.affinity > affinity > global affinity
    # The template should check workers.kubernetes.affinity first
    affinity_line = None
    for line in template_content.split("\n"):
        if "$affinity := or" in line and "workers.kubernetes.affinity" in line:
            affinity_line = line
            break

    assert affinity_line is not None, \
        "Template should define $affinity with workers.kubernetes.affinity as first option"
    assert "workers.kubernetes.affinity" in affinity_line, \
        "workers.kubernetes.affinity should be the first option in the or chain"
    assert "workers.affinity" in affinity_line, \
        "workers.affinity should be the fallback option"


def test_celery_affinity_in_worker_deployment():
    """Test that workers.celery.affinity is defined and accessible.

    This test verifies that the new workers.celery.affinity field
    is properly defined in values.yaml and the schema. The worker deployment
    template uses workersMergeValues to merge celery config, so the affinity
    will be available through the merged workers config.
    """
    # Check values.yaml has the celery.affinity field defined
    values_path = CHART_DIR / "values.yaml"

    with open(values_path) as f:
        values_content = f.read()

    # Find the celery section and check it has affinity defined
    # Look for the pattern in values.yaml where celery.affinity should be
    assert "celery:" in values_content, "values.yaml should have celery section"

    # Check that after the celery section there's an affinity: {} defined
    # We need to verify the structure exists - look for affinity defined in the right context
    lines = values_content.split("\n")
    in_celery_section = False
    celery_affinity_found = False
    celery_indent = None

    for i, line in enumerate(lines):
        # Detect start of celery section (should be at certain indent level under workers)
        if line.strip().startswith("celery:") and not line.startswith("  celery:"):
            # This is the top-level celery section, not what we want
            continue
        if line.startswith("  celery:") or line.startswith("    celery:"):
            in_celery_section = True
            celery_indent = len(line) - len(line.lstrip())
            continue

        if in_celery_section:
            # Check if we've exited the celery section
            current_indent = len(line) - len(line.lstrip())
            if line.strip() and current_indent <= celery_indent:
                break

            # Look for affinity definition within celery section
            if "affinity:" in line and current_indent > celery_indent:
                celery_affinity_found = True
                break

    assert celery_affinity_found, \
        "values.yaml should have workers.celery.affinity defined (affinity: {} under celery section)"


def test_deprecated_workers_affinity_deprecation_warning():
    """Test that NOTES.txt includes deprecation warning for workers.affinity.

    When workers.affinity is set, NOTES.txt should display a deprecation warning
    indicating to use workers.celery.affinity and/or workers.kubernetes.affinity.
    """
    notes_path = CHART_DIR / "templates" / "NOTES.txt"

    with open(notes_path) as f:
        notes_content = f.read()

    # Check that NOTES.txt contains a deprecation warning for workers.affinity
    assert "workers.affinity" in notes_content, \
        "NOTES.txt should reference workers.affinity"

    # Check that it suggests the new fields
    assert "workers.celery.affinity" in notes_content or "workers.kubernetes.affinity" in notes_content, \
        "NOTES.txt should suggest workers.celery.affinity and/or workers.kubernetes.affinity as alternatives"

    # Check that there's a deprecation warning
    assert "DEPRECATION" in notes_content.upper() or "deprecated" in notes_content.lower(), \
        "NOTES.txt should contain a deprecation warning"


def test_schema_includes_celery_affinity():
    """Test that values.schema.json includes workers.celery.affinity definition."""
    schema_path = CHART_DIR / "values.schema.json"

    with open(schema_path) as f:
        schema = json.load(f)

    # Navigate to workers.celery.affinity in schema
    properties = schema.get("properties", {})
    workers = properties.get("workers", {})
    worker_props = workers.get("properties", {})
    celery = worker_props.get("celery", {})
    celery_props = celery.get("properties", {})

    assert "affinity" in celery_props, \
        "values.schema.json should include workers.celery.affinity property"

    affinity_prop = celery_props["affinity"]
    assert affinity_prop.get("type") == "object", \
        "workers.celery.affinity should be type object"


def test_schema_includes_kubernetes_affinity():
    """Test that values.schema.json includes workers.kubernetes.affinity definition."""
    schema_path = CHART_DIR / "values.schema.json"

    with open(schema_path) as f:
        schema = json.load(f)

    # Navigate to workers.kubernetes.affinity in schema
    properties = schema.get("properties", {})
    workers = properties.get("workers", {})
    worker_props = workers.get("properties", {})
    kubernetes = worker_props.get("kubernetes", {})
    k8s_props = kubernetes.get("properties", {})

    assert "affinity" in k8s_props, \
        "values.schema.json should include workers.kubernetes.affinity property"

    affinity_prop = k8s_props["affinity"]
    assert affinity_prop.get("type") == "object", \
        "workers.kubernetes.affinity should be type object"


def test_deprecated_affinity_backwards_compatibility():
    """Test that workers.affinity still works for backwards compatibility.

    The old workers.affinity field should still be applied when the new
    fields are not set, maintaining backwards compatibility.
    We verify this by checking the template has the fallback logic.
    """
    template_path = CHART_DIR / "files" / "pod-template-file.kubernetes-helm-yaml"

    with open(template_path) as f:
        template_content = f.read()

    # Check that the template still references the deprecated workers.affinity
    # for backwards compatibility
    assert "workers.affinity" in template_content, \
        "Template should reference workers.affinity for backwards compatibility"

    # Check the deprecation comment in values.yaml
    values_path = CHART_DIR / "values.yaml"
    with open(values_path) as f:
        values_content = f.read()

    # Check that the deprecated affinity field has a deprecation comment
    assert "deprecated" in values_content.lower() and "workers.celery.affinity" in values_content.lower(), \
        "values.yaml should indicate workers.affinity is deprecated and suggest new fields"


# =============================================================================
# Pass-to-pass tests (repo CI tests that should pass on both base and fix)
# =============================================================================


def test_helm_lint():
    """Helm lint passes on the chart (pass_to_pass).

    This validates that the Helm chart has no lint errors.
    """
    result = subprocess.run(
        ["helm", "lint", str(CHART_DIR)],
        capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, f"Helm lint failed:\n{result.stdout}\n{result.stderr}"


def test_chart_values_schema_validation():
    """Chart values validate against schema (pass_to_pass).

    This test validates that the default values.yaml conforms to the schema.
    """
    result = subprocess.run(
        [sys.executable, "-m", "pytest",
         str(HELM_TESTS_DIR / "tests/helm_tests/airflow_aux/test_chart_quality.py"),
         "-k", "test_values_validate_schema",
         "-v", "--tb=short"],
        cwd=str(REPO),
        capture_output=True, text=True, timeout=120,
        env={**os.environ, "PYTHONPATH": str(HELM_TESTS_DIR)}
    )
    assert result.returncode == 0, f"Chart schema validation failed:\n{result.stderr[-1000:]}"


def test_helm_tests_worker_affinity():
    """Run the repo's own worker affinity tests.

    This tests that the existing test structure works and can test affinity.
    """
    test_file = HELM_TESTS_DIR / "tests/helm_tests/airflow_core/test_worker.py"

    if not test_file.exists():
        pytest.skip("Helm test file not found")

    # Run just the affinity-related test
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-k", "affinity", "-v", "--tb=short"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "PYTHONPATH": str(HELM_TESTS_DIR)}
    )

    assert result.returncode == 0, f"Helm worker affinity tests failed:\n{result.stderr[-1000:]}"


def test_helm_tests_pod_template_affinity():
    """Run the repo's own pod template affinity tests."""
    test_file = HELM_TESTS_DIR / "tests/helm_tests/airflow_aux/test_pod_template_file.py"

    if not test_file.exists():
        pytest.skip("Helm test file not found")

    # Run just the affinity-related test
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-k", "affinity", "-v", "--tb=short"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "PYTHONPATH": str(HELM_TESTS_DIR)}
    )

    assert result.returncode == 0, f"Helm pod template affinity tests failed:\n{result.stderr[-1000:]}"


def test_helm_tests_worker_sets_affinity():
    """Run the repo's worker sets affinity tests (pass_to_pass).

    This tests that worker sets affinity configuration works correctly.
    """
    test_file = HELM_TESTS_DIR / "tests/helm_tests/airflow_core/test_worker_sets.py"

    if not test_file.exists():
        pytest.skip("Helm test file not found")

    # Run just the affinity-related tests
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-k", "affinity", "-v", "--tb=short"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "PYTHONPATH": str(HELM_TESTS_DIR)}
    )

    assert result.returncode == 0, f"Helm worker sets affinity tests failed:\n{result.stderr[-1000:]}"


def test_schema_is_valid_json():
    """Test that values.schema.json is valid JSON."""
    schema_path = CHART_DIR / "values.schema.json"

    with open(schema_path) as f:
        schema = json.load(f)

    assert "properties" in schema, "Schema should have properties key"
    assert "workers" in schema["properties"], "Schema should have workers property"


def test_values_yaml_is_valid_yaml():
    """Test that values.yaml is valid YAML."""
    values_path = CHART_DIR / "values.yaml"

    with open(values_path) as f:
        values = yaml.safe_load(f)

    assert "workers" in values, "values.yaml should have workers key"


def test_repo_helm_tests_scheduler_affinity():
    """Repo's scheduler affinity tests pass (pass_to_pass).

    Validates that scheduler affinity, tolerations, and node selector
    configurations work correctly.
    """
    test_file = HELM_TESTS_DIR / "tests/helm_tests/airflow_core/test_scheduler.py"

    if not test_file.exists():
        pytest.skip("Helm test file not found")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-k", "affinity", "-v", "--tb=short"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "PYTHONPATH": str(HELM_TESTS_DIR)}
    )
    assert result.returncode == 0, f"Helm scheduler affinity tests failed:\n{result.stderr[-1000:]}"


def test_repo_helm_tests_triggerer_affinity():
    """Repo's triggerer affinity tests pass (pass_to_pass).

    Validates that triggerer affinity, tolerations, and node selector
    configurations work correctly.
    """
    test_file = HELM_TESTS_DIR / "tests/helm_tests/airflow_core/test_triggerer.py"

    if not test_file.exists():
        pytest.skip("Helm test file not found")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-k", "affinity", "-v", "--tb=short"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "PYTHONPATH": str(HELM_TESTS_DIR)}
    )
    assert result.returncode == 0, f"Helm triggerer affinity tests failed:\n{result.stderr[-1000:]}"


def test_repo_helm_tests_dag_processor_affinity():
    """Repo's DAG processor affinity tests pass (pass_to_pass).

    Validates that DAG processor affinity, tolerations, and node selector
    configurations work correctly.
    """
    test_file = HELM_TESTS_DIR / "tests/helm_tests/airflow_core/test_dag_processor.py"

    if not test_file.exists():
        pytest.skip("Helm test file not found")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-k", "affinity", "-v", "--tb=short"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "PYTHONPATH": str(HELM_TESTS_DIR)}
    )
    assert result.returncode == 0, f"Helm DAG processor affinity tests failed:\n{result.stderr[-1000:]}"


def test_repo_helm_tests_celery_kubernetes_executor():
    """Repo's CeleryKubernetes executor tests pass (pass_to_pass).

    Validates that the CeleryKubernetes executor configuration works correctly,
    including worker deployment generation.
    """
    test_file = HELM_TESTS_DIR / "tests/helm_tests/airflow_aux/test_celery_kubernetes_executor.py"

    if not test_file.exists():
        pytest.skip("Helm test file not found")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "PYTHONPATH": str(HELM_TESTS_DIR)}
    )
    assert result.returncode == 0, f"Helm CeleryKubernetes executor tests failed:\n{result.stderr[-1000:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
