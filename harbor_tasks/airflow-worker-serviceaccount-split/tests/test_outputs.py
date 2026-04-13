"""Tests for workers.celery.serviceAccount & workers.kubernetes.serviceAccount feature."""

import os
import re
import subprocess
import yaml
from pathlib import Path

REPO = "/workspace/airflow"
CHART_DIR = f"{REPO}/chart"


def _render_helm_template(values=None, template=None, namespace="default"):
    cmd = ["helm", "template", "test-release", CHART_DIR, "--namespace", namespace]
    if values:
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(values, f)
            values_file = f.name
        cmd.extend(["--values", values_file])
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result
        finally:
            os.unlink(values_file)
    elif template:
        cmd.extend(["--show-only", template])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result
    else:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result


def _get_helm_chart_yaml():
    chart_yaml_path = Path(CHART_DIR) / "Chart.yaml"
    if not chart_yaml_path.exists():
        return None
    with open(chart_yaml_path) as f:
        return yaml.safe_load(f)


def _get_values_yaml():
    values_path = Path(CHART_DIR) / "values.yaml"
    with open(values_path) as f:
        return yaml.safe_load(f)


def _get_helpers_yaml():
    helpers_path = Path(CHART_DIR) / "templates" / "_helpers.yaml"
    with open(helpers_path) as f:
        return f.read()


def _get_pod_template_file():
    template_path = Path(CHART_DIR) / "files" / "pod-template-file.kubernetes-helm-yaml"
    with open(template_path) as f:
        return f.read()


def _get_worker_k8s_sa_template():
    template_path = Path(CHART_DIR) / "templates" / "workers" / "worker-kubernetes-serviceaccount.yaml"
    if template_path.exists():
        with open(template_path) as f:
            return f.read()
    return None


def _get_notes_txt():
    notes_path = Path(CHART_DIR) / "templates" / "NOTES.txt"
    with open(notes_path) as f:
        return f.read()


# =============================================================================
# Fail-to-pass tests (test the fix)
# =============================================================================

def test_worker_kubernetes_serviceaccount_template_exists():
    template = _get_worker_k8s_sa_template()
    assert template is not None, (
        "worker-kubernetes-serviceaccount.yaml template does not exist. "
        "This file is required for the workers.kubernetes.serviceAccount feature."
    )


def test_worker_kubernetes_serviceaccount_helper_exists():
    helpers = _get_helpers_yaml()
    assert 'define \"worker.kubernetes.serviceAccountName\"' in helpers, (
        "worker.kubernetes.serviceAccountName helper is not defined in _helpers.yaml. "
        "This helper is required to generate names for kubernetes worker service accounts."
    )


def test_serviceaccountnamegen_helper_exists():
    helpers = _get_helpers_yaml()
    assert 'define \"_serviceAccountNameGen\"' in helpers, (
        "_serviceAccountNameGen helper is not defined in _helpers.yaml. "
        "This helper centralizes service account name generation logic."
    )


def test_helpers_supports_subkey():
    helpers = _get_helpers_yaml()
    assert '.subKey' in helpers, (
        "_serviceAccountName helper does not support subKey parameter. "
        "The helper must check for .subKey to handle nested sections like workers.kubernetes."
    )


def test_pod_template_uses_conditional_serviceaccount():
    template = _get_pod_template_file()
    assert '.Values.workers.kubernetes.serviceAccount.create' in template, (
        "pod-template-file.kubernetes-helm-yaml does not check workers.kubernetes.serviceAccount.create. "
        "It must conditionally use worker.kubernetes.serviceAccountName when this is set."
    )
    assert 'worker.kubernetes.serviceAccountName' in template, (
        "pod-template-file.kubernetes-helm-yaml does not use worker.kubernetes.serviceAccountName helper."
    )


def test_notes_deprecation_warnings_exist():
    notes = _get_notes_txt()
    deprecation_fields = [
        "workers.serviceAccount.automountServiceAccountToken",
        "workers.serviceAccount.create",
        "workers.serviceAccount.name",
        "workers.serviceAccount.annotations"
    ]
    for field in deprecation_fields:
        assert field in notes, (
            f"NOTES.txt missing deprecation warning for {field}. "
            "Users need to be warned about the deprecated serviceAccount fields."
        )


def test_values_has_celery_serviceaccount_section():
    values = _get_values_yaml()
    assert 'workers' in values, "values.yaml missing workers section"
    assert 'celery' in values['workers'], "values.yaml missing workers.celery section"
    assert 'serviceAccount' in values['workers']['celery'], (
        "values.yaml missing workers.celery.serviceAccount section"
    )
    sa = values['workers']['celery']['serviceAccount']
    expected_fields = ['automountServiceAccountToken', 'create', 'name', 'annotations']
    for field in expected_fields:
        assert field in sa, f"workers.celery.serviceAccount missing {field} field"


def test_values_has_kubernetes_serviceaccount_section():
    values = _get_values_yaml()
    assert 'workers' in values, "values.yaml missing workers section"
    assert 'kubernetes' in values['workers'], "values.yaml missing workers.kubernetes section"
    assert 'serviceAccount' in values['workers']['kubernetes'], (
        "values.yaml missing workers.kubernetes.serviceAccount section"
    )
    sa = values['workers']['kubernetes']['serviceAccount']
    expected_fields = ['automountServiceAccountToken', 'create', 'name', 'annotations']
    for field in expected_fields:
        assert field in sa, f"workers.kubernetes.serviceAccount missing {field} field"


def test_schema_has_celery_serviceaccount():
    schema_path = Path(CHART_DIR) / "values.schema.json"
    with open(schema_path) as f:
        schema = yaml.safe_load(f)
    workers = schema.get('properties', {}).get('workers', {})
    celery = workers.get('properties', {}).get('celery', {})
    sa = celery.get('properties', {}).get('serviceAccount', {})
    assert sa, "values.schema.json missing workers.celery.serviceAccount definition"
    assert 'properties' in sa, "serviceAccount schema missing properties"
    expected_props = ['automountServiceAccountToken', 'create', 'name', 'annotations']
    for prop in expected_props:
        assert prop in sa['properties'], f"serviceAccount schema missing {prop} property"


def test_schema_has_kubernetes_serviceaccount():
    schema_path = Path(CHART_DIR) / "values.schema.json"
    with open(schema_path) as f:
        schema = yaml.safe_load(f)
    workers = schema.get('properties', {}).get('workers', {})
    kubernetes = workers.get('properties', {}).get('kubernetes', {})
    sa = kubernetes.get('properties', {}).get('serviceAccount', {})
    assert sa, "values.schema.json missing workers.kubernetes.serviceAccount definition"
    assert 'properties' in sa, "serviceAccount schema missing properties"
    expected_props = ['automountServiceAccountToken', 'create', 'name', 'annotations']
    for prop in expected_props:
        assert prop in sa['properties'], f"serviceAccount schema missing {prop} property"


def test_newsfragment_exists():
    newsfrag_path = Path(CHART_DIR) / "newsfragments" / "64730.significant.rst"
    assert newsfrag_path.exists(), (
        "Newsfragment chart/newsfragments/64730.significant.rst does not exist. "
        "This documents the breaking change for users."
    )
    content = newsfrag_path.read_text()
    assert "workers.serviceAccount" in content, "Newsfragment should mention deprecated workers.serviceAccount"
    assert "workers.celery.serviceAccount" in content, "Newsfragment should mention new workers.celery.serviceAccount"
    assert "workers.kubernetes.serviceAccount" in content, "Newsfragment should mention new workers.kubernetes.serviceAccount"


# =============================================================================
# Pass-to-pass tests (existing repo tests)
# =============================================================================

def test_helm_lint():
    result = subprocess.run(
        ["helm", "lint", CHART_DIR],
        capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, f"Helm lint failed:\n{result.stdout}\n{result.stderr}"


def test_helm_template_basic():
    result = subprocess.run(
        ["helm", "template", "test-release", CHART_DIR],
        capture_output=True, text=True, timeout=120
    )
    assert result.returncode == 0, f"Helm template failed:\n{result.stderr}"
    output = result.stdout
    assert "apiVersion:" in output, "Template output missing Kubernetes resources"


def test_values_yaml_valid():
    values = _get_values_yaml()
    assert values is not None, "values.yaml is not valid YAML"
    assert 'workers' in values, "values.yaml missing workers section"


def test_schema_json_valid():
    schema_path = Path(CHART_DIR) / "values.schema.json"
    with open(schema_path) as f:
        schema = yaml.safe_load(f)
    assert schema is not None, "values.schema.json is not valid JSON"
    assert 'properties' in schema, "Schema missing expected fields"


def test_helpers_yaml_valid():
    helpers = _get_helpers_yaml()
    assert 'define \"airflow.serviceAccountName\"' in helpers, "Missing airflow.serviceAccountName helper"
    assert 'define \"_serviceAccountName\"' in helpers, "Missing _serviceAccountName helper"
    assert 'define \"worker.serviceAccountName\"' in helpers, "Missing worker.serviceAccountName helper"


# =============================================================================
# Pass-to-pass tests - CI/CD commands for modified templates
# =============================================================================

def test_repo_helm_lint_with_kubernetes_executor():
    import tempfile
    values = {
        "executor": "KubernetesExecutor",
        "workers": {"kubernetes": {"nodeSelector": {"diskType": "ssd"}}}
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(values, f)
        values_file = f.name
    try:
        result = subprocess.run(
            ["helm", "lint", CHART_DIR, "--values", values_file],
            capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0, f"Helm lint with KubernetesExecutor failed:\n{result.stdout}\n{result.stderr}"
    finally:
        os.unlink(values_file)


def test_repo_helm_template_with_kubernetes_executor():
    import tempfile
    values = {
        "executor": "KubernetesExecutor",
        "workers": {"kubernetes": {"terminationGracePeriodSeconds": 60}}
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(values, f)
        values_file = f.name
    try:
        result = subprocess.run(
            ["helm", "template", "test-release", CHART_DIR, "--values", values_file],
            capture_output=True, text=True, timeout=120
        )
        assert result.returncode == 0, f"Helm template with KubernetesExecutor failed:\n{result.stderr}"
        assert "pod-template-file" in result.stdout or "ConfigMap" in result.stdout, \
            "Pod template file configmap not found in output"
    finally:
        os.unlink(values_file)


def test_repo_helm_template_with_celery_executor():
    import tempfile
    values = {
        "executor": "CeleryExecutor",
        "workers": {"celery": {"replicas": 2}}
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(values, f)
        values_file = f.name
    try:
        result = subprocess.run(
            ["helm", "template", "test-release", CHART_DIR, "--values", values_file],
            capture_output=True, text=True, timeout=120
        )
        assert result.returncode == 0, f"Helm template with CeleryExecutor failed:\n{result.stderr}"
        assert "worker" in result.stdout.lower(), "Worker not found in output"
    finally:
        os.unlink(values_file)


def test_repo_helm_package():
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["helm", "package", CHART_DIR, "--destination", tmpdir],
            capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0, f"Helm package failed:\n{result.stderr}"
        result = subprocess.run(["ls", "-1", tmpdir], capture_output=True, text=True)
        assert ".tgz" in result.stdout, "No .tgz package was created"


def test_repo_helm_show_values():
    result = subprocess.run(
        ["helm", "show", "values", CHART_DIR],
        capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, f"Helm show values failed:\n{result.stderr}"
    assert "workers:" in result.stdout, "values.yaml missing workers section"


def test_repo_helm_template_with_deprecated_serviceaccount():
    import tempfile
    values = {
        "executor": "KubernetesExecutor",
        "workers": {"serviceAccount": {"create": True, "name": "deprecated-sa"}}
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(values, f)
        values_file = f.name
    try:
        result = subprocess.run(
            ["helm", "template", "test-release", CHART_DIR, "--values", values_file],
            capture_output=True, text=True, timeout=120
        )
        assert result.returncode == 0, f"Helm template with deprecated SA failed:\n{result.stderr}"
        assert "deprecated-sa" in result.stdout, "Deprecated service account name not used"
    finally:
        os.unlink(values_file)


def test_repo_values_schema_validation():
    """Validate values.yaml against schema using repo's helm-tests approach."""
    import json
    values_path = Path(CHART_DIR) / "values.yaml"
    with open(values_path) as f:
        values = yaml.safe_load(f)
    schema_path = Path(CHART_DIR) / "values.schema.json"
    with open(schema_path) as f:
        schema = json.load(f)
    # Basic validation - just check that required sections exist
    assert 'properties' in schema, "Schema missing properties"
    workers = schema.get('properties', {}).get('workers', {})
    assert 'properties' in workers, "Schema missing workers.properties"


def test_repo_helm_lint_strict():
    result = subprocess.run(
        ["helm", "lint", CHART_DIR, "--strict"],
        capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, f"Helm strict lint failed:\n{result.stdout}\n{result.stderr}"


# =============================================================================
# Functional behavior tests
# =============================================================================

def test_helm_render_with_kubernetes_executor_and_sa():
    values = {
        "executor": "KubernetesExecutor",
        "workers": {
            "kubernetes": {
                "serviceAccount": {
                    "create": True,
                    "name": "test-k8s-sa",
                    "automountServiceAccountToken": False,
                    "annotations": {"test": "annotation"}
                }
            }
        }
    }
    result = _render_helm_template(values=values)
    assert result.returncode == 0, f"Helm template with k8s executor and SA failed: {result.stderr}"
    assert "test-k8s-sa" in result.stdout, "Custom service account name not found in rendered output"


def test_helm_render_with_celery_executor():
    values = {
        "executor": "CeleryExecutor",
        "workers": {
            "celery": {
                "serviceAccount": {"create": True, "name": "test-celery-sa"}
            }
        }
    }
    result = _render_helm_template(values=values)
    assert result.returncode == 0, f"Helm template with Celery executor and SA failed: {result.stderr}"
    assert "test-celery-sa" in result.stdout, "Custom celery service account name not found in rendered output"


def test_deprecated_serviceaccount_fallback():
    values = {
        "executor": "KubernetesExecutor",
        "workers": {
            "serviceAccount": {
                "create": True,
                "name": "deprecated-sa",
                "automountServiceAccountToken": True,
                "annotations": {"deprecated": "true"}
            }
        }
    }
    result = _render_helm_template(values=values)
    assert result.returncode == 0, f"Helm template with deprecated SA failed: {result.stderr}"
    assert "deprecated-sa" in result.stdout, "Deprecated service account name not used"
