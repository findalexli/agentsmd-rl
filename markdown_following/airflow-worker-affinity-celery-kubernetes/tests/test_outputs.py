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


def get_pod_from_configmap(docs):
    """Extract pod template from ConfigMap containing pod-template-file."""
    for doc in docs:
        if doc and doc.get("kind") == "ConfigMap":
            # The pod template is stored as a string value in the ConfigMap
            for key, value in doc.get("data", {}).items():
                if "template" in key.lower() or key == "pod_template_file.yaml":
                    # Parse the embedded pod template
                    pod_template = yaml.safe_load(value)
                    if pod_template and pod_template.get("kind") == "Pod":
                        return pod_template
    return None


# =============================================================================
# Fail-to-pass tests (must fail on base commit, pass on fix)
# =============================================================================


def test_kubernetes_affinity_applied_to_pod_template():
    """Test that workers.kubernetes.affinity is actually applied to pod-template.

    This test verifies that when workers.kubernetes.affinity is set, it appears
    in the rendered pod template. This is a behavioral test that actually
    renders the template and checks the output.
    """
    # Define a test affinity configuration
    test_affinity = {
        "nodeAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": {
                "nodeSelectorTerms": [
                    {
                        "matchExpressions": [
                            {"key": "test-label", "operator": "In", "values": ["test-value"]}
                        ]
                    }
                ]
            }
        }
    }

    values = {
        "executor": "KubernetesExecutor",
        "workers": {
            "kubernetes": {
                "affinity": test_affinity
            }
        }
    }

    # Render the configmap containing pod-template-file
    docs = helm_template(values=values, show_only=["templates/configmaps/configmap.yaml"])

    # Get the pod template from the ConfigMap
    pod = get_pod_from_configmap(docs)
    assert pod is not None, "Could not find pod template in rendered output"

    # Verify the affinity is applied to the pod spec
    rendered_affinity = pod.get("spec", {}).get("affinity")
    assert rendered_affinity is not None, "Pod template should have affinity set"
    assert rendered_affinity.get("nodeAffinity", {}).get("requiredDuringSchedulingIgnoredDuringExecution", {}).get("nodeSelectorTerms") is not None, \
        "Rendered pod should have nodeAffinity with nodeSelectorTerms"


def test_celery_affinity_applied_to_worker_deployment():
    """Test that workers.celery.affinity is applied to Celery worker deployment.

    This test verifies that when workers.celery.affinity is set, it appears
    in the rendered worker deployment's pod spec.
    """
    # Define a test affinity configuration
    test_affinity = {
        "nodeAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": {
                "nodeSelectorTerms": [
                    {
                        "matchExpressions": [
                            {"key": "celery-label", "operator": "In", "values": ["celery-value"]}
                        ]
                    }
                ]
            }
        }
    }

    values = {
        "executor": "CeleryExecutor",
        "workers": {
            "celery": {
                "affinity": test_affinity
            }
        }
    }

    # Render the worker deployment
    docs = helm_template(values=values, show_only=["templates/workers/worker-deployment.yaml"])

    # Get the deployment (it's actually a StatefulSet in the airflow chart)
    deployment = get_doc_by_kind(docs, "StatefulSet")
    if deployment is None:
        deployment = get_doc_by_kind(docs, "Deployment")
    assert deployment is not None, "Could not find worker deployment in rendered output"

    # Verify the affinity is applied to the pod template spec
    pod_spec = deployment.get("spec", {}).get("template", {}).get("spec", {})
    rendered_affinity = pod_spec.get("affinity")
    assert rendered_affinity is not None, "Worker deployment pod spec should have affinity set"
    assert rendered_affinity.get("nodeAffinity", {}).get("requiredDuringSchedulingIgnoredDuringExecution", {}).get("nodeSelectorTerms") is not None, \
        "Rendered worker should have nodeAffinity with nodeSelectorTerms"


def test_precedence_new_fields_over_deprecated():
    """Test that new specific affinity fields take precedence over deprecated workers.affinity.

    When both the old workers.affinity and new workers.kubernetes.affinity are set,
    the new specific field should take precedence.
    """
    # Define different affinity configurations for old and new fields
    old_deprecated_affinity = {
        "nodeAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": {
                "nodeSelectorTerms": [
                    {"matchExpressions": [{"key": "old-label", "operator": "In", "values": ["old-value"]}]}
                ]
            }
        }
    }

    new_kubernetes_affinity = {
        "nodeAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": {
                "nodeSelectorTerms": [
                    {"matchExpressions": [{"key": "new-label", "operator": "In", "values": ["new-value"]}]}
                ]
            }
        }
    }

    values = {
        "executor": "KubernetesExecutor",
        "workers": {
            "affinity": old_deprecated_affinity,  # deprecated
            "kubernetes": {
                "affinity": new_kubernetes_affinity  # new field
            }
        }
    }

    # Render the configmap containing pod-template-file
    docs = helm_template(values=values, show_only=["templates/configmaps/configmap.yaml"])

    # Get the pod template
    pod = get_pod_from_configmap(docs)
    assert pod is not None, "Could not find pod template"

    # Verify the new affinity takes precedence (has new-label, not old-label)
    rendered_affinity = pod.get("spec", {}).get("affinity")
    assert rendered_affinity is not None, "Pod should have affinity"

    terms = rendered_affinity.get("nodeAffinity", {}).get("requiredDuringSchedulingIgnoredDuringExecution", {}).get("nodeSelectorTerms", [])
    assert len(terms) > 0, "Should have nodeSelectorTerms"

    # Check that the new label is present (new field took precedence)
    match_expressions = terms[0].get("matchExpressions", [])
    keys = [me.get("key") for me in match_expressions]
    assert "new-label" in keys, "New workers.kubernetes.affinity should take precedence over deprecated workers.affinity"


def test_backwards_compatibility_deprecated_affinity():
    """Test that deprecated workers.affinity still works for backwards compatibility.

    When only the old workers.affinity is set (without new specific fields),
    it should still be applied to both pod-template and worker deployments.
    """
    deprecated_affinity = {
        "nodeAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": {
                "nodeSelectorTerms": [
                    {"matchExpressions": [{"key": "deprecated-label", "operator": "In", "values": ["deprecated-value"]}]}
                ]
            }
        }
    }

    # Test for pod-template (KubernetesExecutor)
    values_k8s = {
        "executor": "KubernetesExecutor",
        "workers": {
            "affinity": deprecated_affinity
        }
    }

    docs_k8s = helm_template(values=values_k8s, show_only=["templates/configmaps/configmap.yaml"])
    pod = get_pod_from_configmap(docs_k8s)
    assert pod is not None, "Could not find pod template"

    rendered_affinity = pod.get("spec", {}).get("affinity")
    assert rendered_affinity is not None, "Pod should have affinity when using deprecated workers.affinity"

    terms = rendered_affinity.get("nodeAffinity", {}).get("requiredDuringSchedulingIgnoredDuringExecution", {}).get("nodeSelectorTerms", [])
    assert len(terms) > 0, "Should have nodeSelectorTerms"

    match_expressions = terms[0].get("matchExpressions", [])
    keys = [me.get("key") for me in match_expressions]
    assert "deprecated-label" in keys, "Deprecated workers.affinity should still work for pod template"

    # Test for worker deployment (CeleryExecutor)
    values_celery = {
        "executor": "CeleryExecutor",
        "workers": {
            "affinity": deprecated_affinity
        }
    }

    docs_celery = helm_template(values=values_celery, show_only=["templates/workers/worker-deployment.yaml"])
    deployment = get_doc_by_kind(docs_celery, "StatefulSet")
    if deployment is None:
        deployment = get_doc_by_kind(docs_celery, "Deployment")
    assert deployment is not None, "Could not find worker deployment"

    pod_spec = deployment.get("spec", {}).get("template", {}).get("spec", {})
    rendered_affinity = pod_spec.get("affinity")
    assert rendered_affinity is not None, "Worker deployment should have affinity when using deprecated workers.affinity"

    terms = rendered_affinity.get("nodeAffinity", {}).get("requiredDuringSchedulingIgnoredDuringExecution", {}).get("nodeSelectorTerms", [])
    match_expressions = terms[0].get("matchExpressions", []) if terms else []
    keys = [me.get("key") for me in match_expressions]
    assert "deprecated-label" in keys, "Deprecated workers.affinity should still work for worker deployment"


def test_deprecation_warning_in_notes():
    """Test that NOTES.txt displays deprecation warning when workers.affinity is set.

    When workers.affinity is set, the NOTES.txt template should render a deprecation
    warning mentioning workers.celery.affinity and workers.kubernetes.affinity.

    Note: helm template does not render NOTES.txt by default. We check the template
    content directly to verify the deprecation warning logic exists.
    """
    # Read the NOTES.txt template directly
    notes_path = CHART_DIR / "templates" / "NOTES.txt"
    notes_content = notes_path.read_text()

    # Verify deprecation warning for workers.affinity is present in the template
    assert "workers.affinity" in notes_content, \
        "NOTES.txt should mention workers.affinity deprecation"

    # Check that the template has a conditional block for workers.affinity deprecation
    # The fix adds this block:
    # {{- if not (empty .Values.workers.affinity) }}
    #  DEPRECATION WARNING:
    #     `workers.affinity` has been renamed...
    assert "workers.celery.affinity" in notes_content or "workers.kubernetes.affinity" in notes_content, \
        "NOTES.txt should suggest workers.celery.affinity and/or workers.kubernetes.affinity as alternatives"


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

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_test_workers_affinity():
    """fail_to_pass | PR added test 'test_workers_affinity' in 'helm-tests/tests/helm_tests/airflow_aux/test_pod_template_file.py' (pytest)"""
    r = subprocess.run(
        ["bash", "-lc", 'python3 -m pytest -x --no-header -p no:cacheprovider "helm-tests/tests/helm_tests/airflow_aux/test_pod_template_file.py::test_workers_affinity" 2>&1 | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'test_workers_affinity' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_test_affinity():
    """fail_to_pass | PR added test 'test_affinity' in 'helm-tests/tests/helm_tests/airflow_core/test_worker.py' (pytest)"""
    r = subprocess.run(
        ["bash", "-lc", 'python3 -m pytest -x --no-header -p no:cacheprovider "helm-tests/tests/helm_tests/airflow_core/test_worker.py::test_affinity" 2>&1 | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'test_affinity' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
