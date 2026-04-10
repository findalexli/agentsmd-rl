"""Tests for workers.celery.serviceAccount & workers.kubernetes.serviceAccount feature."""

import os
import re
import subprocess
import yaml
from pathlib import Path

REPO = "/workspace/airflow"
CHART_DIR = f"{REPO}/chart"


def _render_helm_template(values=None, template=None, namespace="default"):
    """Render Helm template with given values."""
    cmd = ["helm", "template", "test-release", CHART_DIR, "--namespace", namespace]

    if values:
        # Create temporary values file
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
    """Load Chart.yaml."""
    chart_yaml_path = Path(CHART_DIR) / "Chart.yaml"
    if not chart_yaml_path.exists():
        return None
    with open(chart_yaml_path) as f:
        return yaml.safe_load(f)


def _get_values_yaml():
    """Load values.yaml."""
    values_path = Path(CHART_DIR) / "values.yaml"
    with open(values_path) as f:
        return yaml.safe_load(f)


def _get_helpers_yaml():
    """Load _helpers.yaml."""
    helpers_path = Path(CHART_DIR) / "templates" / "_helpers.yaml"
    with open(helpers_path) as f:
        return f.read()


def _get_pod_template_file():
    """Load pod-template-file.kubernetes-helm-yaml."""
    template_path = Path(CHART_DIR) / "files" / "pod-template-file.kubernetes-helm-yaml"
    with open(template_path) as f:
        return f.read()


def _get_worker_k8s_sa_template():
    """Load worker-kubernetes-serviceaccount.yaml if it exists."""
    template_path = Path(CHART_DIR) / "templates" / "workers" / "worker-kubernetes-serviceaccount.yaml"
    if template_path.exists():
        with open(template_path) as f:
            return f.read()
    return None


def _get_notes_txt():
    """Load NOTES.txt."""
    notes_path = Path(CHART_DIR) / "templates" / "NOTES.txt"
    with open(notes_path) as f:
        return f.read()


# =============================================================================
# Fail-to-pass tests (test the fix)
# =============================================================================

def test_worker_kubernetes_serviceaccount_template_exists():
    """FAIL-TO-PASS: worker-kubernetes-serviceaccount.yaml template must exist."""
    template = _get_worker_k8s_sa_template()
    assert template is not None, (
        "worker-kubernetes-serviceaccount.yaml template does not exist. "
        "This file is required for the workers.kubernetes.serviceAccount feature."
    )


def test_worker_kubernetes_serviceaccount_helper_exists():
    """FAIL-TO-PASS: worker.kubernetes.serviceAccountName helper must exist."""
    helpers = _get_helpers_yaml()
    assert 'define "worker.kubernetes.serviceAccountName"' in helpers, (
        "worker.kubernetes.serviceAccountName helper is not defined in _helpers.yaml. "
        "This helper is required to generate names for kubernetes worker service accounts."
    )


def test_serviceaccountnamegen_helper_exists():
    """FAIL-TO-PASS: _serviceAccountNameGen helper must exist for refactored logic."""
    helpers = _get_helpers_yaml()
    assert 'define "_serviceAccountNameGen"' in helpers, (
        "_serviceAccountNameGen helper is not defined in _helpers.yaml. "
        "This helper centralizes service account name generation logic."
    )


def test_helpers_supports_subkey():
    """FAIL-TO-PASS: _serviceAccountName helper must support subKey parameter."""
    helpers = _get_helpers_yaml()
    # Check that the helper has been updated to support subKey
    assert '.subKey' in helpers, (
        "_serviceAccountName helper does not support subKey parameter. "
        "The helper must check for .subKey to handle nested sections like workers.kubernetes."
    )


def test_pod_template_uses_conditional_serviceaccount():
    """FAIL-TO-PASS: pod-template-file must conditionally use kubernetes service account."""
    template = _get_pod_template_file()

    # Should have conditional logic for kubernetes service account
    assert '.Values.workers.kubernetes.serviceAccount.create' in template, (
        "pod-template-file.kubernetes-helm-yaml does not check workers.kubernetes.serviceAccount.create. "
        "It must conditionally use worker.kubernetes.serviceAccountName when this is set."
    )

    # Should reference the new helper
    assert 'worker.kubernetes.serviceAccountName' in template, (
        "pod-template-file.kubernetes-helm-yaml does not use worker.kubernetes.serviceAccountName helper."
    )


def test_notes_deprecation_warnings_exist():
    """FAIL-TO-PASS: NOTES.txt must include deprecation warnings for old serviceAccount fields."""
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
    """FAIL-TO-PASS: values.yaml must have workers.celery.serviceAccount section."""
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
    """FAIL-TO-PASS: values.yaml must have workers.kubernetes.serviceAccount section."""
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
    """FAIL-TO-PASS: values.schema.json must have workers.celery.serviceAccount schema."""
    schema_path = Path(CHART_DIR) / "values.schema.json"
    with open(schema_path) as f:
        schema = yaml.safe_load(f)

    # Navigate to workers.celery.serviceAccount
    workers = schema.get('properties', {}).get('workers', {})
    celery = workers.get('properties', {}).get('celery', {})
    sa = celery.get('properties', {}).get('serviceAccount', {})

    assert sa, "values.schema.json missing workers.celery.serviceAccount definition"
    assert 'properties' in sa, "serviceAccount schema missing properties"

    expected_props = ['automountServiceAccountToken', 'create', 'name', 'annotations']
    for prop in expected_props:
        assert prop in sa['properties'], f"serviceAccount schema missing {prop} property"


def test_schema_has_kubernetes_serviceaccount():
    """FAIL-TO-PASS: values.schema.json must have workers.kubernetes.serviceAccount schema."""
    schema_path = Path(CHART_DIR) / "values.schema.json"
    with open(schema_path) as f:
        schema = yaml.safe_load(f)

    # Navigate to workers.kubernetes.serviceAccount
    workers = schema.get('properties', {}).get('workers', {})
    kubernetes = workers.get('properties', {}).get('kubernetes', {})
    sa = kubernetes.get('properties', {}).get('serviceAccount', {})

    assert sa, "values.schema.json missing workers.kubernetes.serviceAccount definition"
    assert 'properties' in sa, "serviceAccount schema missing properties"

    expected_props = ['automountServiceAccountToken', 'create', 'name', 'annotations']
    for prop in expected_props:
        assert prop in sa['properties'], f"serviceAccount schema missing {prop} property"


def test_newsfragment_exists():
    """FAIL-TO-PASS: Newsfragment must exist documenting the deprecation."""
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
    """PASS-TO-PASS: Helm chart must pass linting."""
    result = subprocess.run(
        ["helm", "lint", CHART_DIR],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Helm lint failed:\n{result.stdout}\n{result.stderr}"


def test_helm_template_basic():
    """PASS-TO-PASS: Helm chart must render templates successfully."""
    result = subprocess.run(
        ["helm", "template", "test-release", CHART_DIR],
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Helm template failed:\n{result.stderr}"

    # Should produce valid YAML output
    output = result.stdout
    assert "apiVersion:" in output, "Template output missing Kubernetes resources"


def test_values_yaml_valid():
    """PASS-TO-PASS: values.yaml must be valid YAML."""
    values = _get_values_yaml()
    assert values is not None, "values.yaml is not valid YAML"
    assert 'workers' in values, "values.yaml missing workers section"


def test_schema_json_valid():
    """PASS-TO-PASS: values.schema.json must be valid JSON."""
    schema_path = Path(CHART_DIR) / "values.schema.json"
    with open(schema_path) as f:
        schema = yaml.safe_load(f)
    assert schema is not None, "values.schema.json is not valid JSON"
    assert '$schema' in schema or 'properties' in schema, "Schema missing expected fields"


def test_helpers_yaml_valid():
    """PASS-TO-PASS: _helpers.yaml must exist and have required helpers."""
    helpers = _get_helpers_yaml()

    # Check essential helpers exist
    assert 'define "airflow.serviceAccountName"' in helpers, "Missing airflow.serviceAccountName helper"
    assert 'define "_serviceAccountName"' in helpers, "Missing _serviceAccountName helper"
    assert 'define "worker.serviceAccountName"' in helpers, "Missing worker.serviceAccountName helper"


# =============================================================================
# Pass-to-pass tests - CI/CD commands for modified templates
# =============================================================================

def test_repo_helm_lint_with_kubernetes_executor():
    """PASS-TO-PASS: Helm lint passes with KubernetesExecutor (tests pod-template-file rendering)."""
    import tempfile
    # Test with KubernetesExecutor - this renders the pod-template-file which is modified by PR
    values = {
        "executor": "KubernetesExecutor",
        "workers": {
            "kubernetes": {
                "nodeSelector": {"diskType": "ssd"}
            }
        }
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
    """PASS-TO-PASS: Helm template renders with KubernetesExecutor (tests pod-template-file)."""
    import tempfile
    # Test with KubernetesExecutor - tests pod-template-file.kubernetes-helm-yaml
    values = {
        "executor": "KubernetesExecutor",
        "workers": {
            "kubernetes": {
                "terminationGracePeriodSeconds": 60
            }
        }
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
        # Should contain pod-template-file configmap
        assert "pod-template-file" in result.stdout or "ConfigMap" in result.stdout, \
            "Pod template file configmap not found in output"
    finally:
        os.unlink(values_file)


def test_repo_helm_template_with_celery_executor():
    """PASS-TO-PASS: Helm template renders correctly with CeleryExecutor (worker-deployment.yaml)."""
    import tempfile
    # Test with CeleryExecutor - this renders worker-deployment.yaml which uses workers.celery
    values = {
        "executor": "CeleryExecutor",
        "workers": {
            "celery": {
                "replicas": 2
            }
        }
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
        # Should contain worker deployment
        assert "worker" in result.stdout.lower(), "Worker not found in output"
    finally:
        os.unlink(values_file)


def test_repo_helm_package():
    """PASS-TO-PASS: Helm chart packages successfully (CI build test)."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["helm", "package", CHART_DIR, "--destination", tmpdir],
            capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0, f"Helm package failed:\n{result.stderr}"
        # Should create a .tgz file
        result = subprocess.run(
            ["ls", "-1", tmpdir],
            capture_output=True, text=True
        )
        assert ".tgz" in result.stdout, "No .tgz package was created"


def test_repo_helm_show_values():
    """PASS-TO-PASS: Helm show values works (validates chart structure)."""
    result = subprocess.run(
        ["helm", "show", "values", CHART_DIR],
        capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, f"Helm show values failed:\n{result.stderr}"
    # Should contain workers section
    assert "workers:" in result.stdout, "values.yaml missing workers section"


def test_repo_helm_template_with_deprecated_serviceaccount():
    """PASS-TO-PASS: Helm template works with deprecated workers.serviceAccount (backward compat)."""
    import tempfile
    values = {
        "executor": "KubernetesExecutor",
        "workers": {
            "serviceAccount": {
                "create": True,
                "name": "deprecated-sa"
            }
        }
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


# =============================================================================
# Functional behavior tests
# =============================================================================


def test_helm_render_with_kubernetes_executor_and_sa():
    """Test that KubernetesExecutor with custom service account renders correctly."""
    values = {
        "executor": "KubernetesExecutor",
        "workers": {
            "kubernetes": {
                "serviceAccount": {
                    "create": True,
                    "name": "test-k8s-sa",
                    "automountServiceAccountToken": False,
                    "annotations": {
                        "test": "annotation"
                    }
                }
            }
        }
    }

    result = _render_helm_template(values=values)
    assert result.returncode == 0, f"Helm template with k8s executor and SA failed: {result.stderr}"

    output = result.stdout

    # Should contain ServiceAccount with our custom name
    assert "test-k8s-sa" in output, "Custom service account name not found in rendered output"


def test_helm_render_with_celery_executor():
    """Test that CeleryExecutor with custom service account renders correctly."""
    values = {
        "executor": "CeleryExecutor",
        "workers": {
            "celery": {
                "serviceAccount": {
                    "create": True,
                    "name": "test-celery-sa"
                }
            }
        }
    }

    result = _render_helm_template(values=values)
    assert result.returncode == 0, f"Helm template with Celery executor and SA failed: {result.stderr}"

    output = result.stdout
    assert "test-celery-sa" in output, "Custom celery service account name not found in rendered output"


def test_deprecated_serviceaccount_fallback():
    """Test that deprecated workers.serviceAccount still works as fallback."""
    values = {
        "executor": "KubernetesExecutor",
        "workers": {
            "serviceAccount": {
                "create": True,
                "name": "deprecated-sa",
                "automountServiceAccountToken": True,
                "annotations": {
                    "deprecated": "true"
                }
            }
        }
    }

    result = _render_helm_template(values=values)
    assert result.returncode == 0, f"Helm template with deprecated SA failed: {result.stderr}"

    output = result.stdout
    # Should still work with the deprecated settings
    assert "deprecated-sa" in output, "Deprecated service account name not used"
