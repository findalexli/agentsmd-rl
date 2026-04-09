"""Tests for workers.celery.affinity and workers.kubernetes.affinity feature."""

import json
import os
import subprocess
import tempfile
import pytest
import yaml

REPO = "/workspace/airflow"
CHART_DIR = os.path.join(REPO, "chart")


def helm_template(values=None, show_only=None, chart_dir=None):
    """Run helm template and return parsed documents."""
    if chart_dir is None:
        chart_dir = CHART_DIR

    cmd = ["helm", "template", "test-release", chart_dir]

    if values:
        # Create temporary values file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(values, f)
            values_file = f.name
        cmd.extend(["-f", values_file])

    if show_only:
        for path in show_only:
            cmd.extend(["--show-only", path])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            raise RuntimeError(f"helm template failed: {result.stderr}")

        # Parse YAML documents
        docs = list(yaml.safe_load_all(result.stdout))
        return [d for d in docs if d is not None]
    finally:
        if values:
            os.unlink(values_file)


def get_doc_by_kind(docs, kind):
    """Get document by Kubernetes kind."""
    for doc in docs:
        if doc.get("kind") == kind:
            return doc
    return None


def jmespath_search(path, doc):
    """Simple JMESPath-like search for nested dict access."""
    parts = path.split(".")
    current = doc
    for part in parts:
        if current is None:
            return None
        if part.startswith("[") and part.endswith("]"):
            # Array index
            idx = int(part[1:-1])
            if isinstance(current, list) and idx < len(current):
                current = current[idx]
            else:
                return None
        elif isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def extract_pod_template_from_configmap(docs):
    """Extract the pod template from the ConfigMap data."""
    for doc in docs:
        if doc.get("kind") == "ConfigMap":
            data = doc.get("data", {})
            for key, value in data.items():
                # Try to parse as YAML pod template
                try:
                    pod = yaml.safe_load(value)
                    if pod and pod.get("kind") == "Pod":
                        return pod
                except:
                    pass
    return None


# Test 1: Fail-to-pass test - workers.kubernetes.affinity should be used for pod-template-file
@pytest.mark.parametrize("affinity_values", [
    {
        "nodeAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": {
                "nodeSelectorTerms": [
                    {
                        "matchExpressions": [
                            {"key": "foo", "operator": "In", "values": ["true"]},
                        ]
                    }
                ]
            }
        }
    },
    {
        "podAffinity": {
            "preferredDuringSchedulingIgnoredDuringExecution": [
                {
                    "podAffinityTerm": {
                        "topologyKey": "foo",
                        "labelSelector": {"matchLabels": {"tier": "airflow"}},
                    },
                    "weight": 1,
                }
            ]
        }
    },
])
def test_workers_kubernetes_affinity_pod_template(affinity_values):
    """
    Test that workers.kubernetes.affinity is correctly applied to pod-template-file.
    This is a fail-to-pass test - without the fix, this should not work.
    """
    values = {
        "executor": "KubernetesExecutor",
        "workers": {
            "kubernetes": {
                "affinity": affinity_values,
            },
        },
    }

    docs = helm_template(
        values=values,
        show_only=["templates/configmaps/configmap.yaml"],
    )

    pod_doc = extract_pod_template_from_configmap(docs)
    assert pod_doc is not None, "Pod template should be found in ConfigMap"

    spec_affinity = jmespath_search("spec.affinity", pod_doc)
    assert spec_affinity is not None, "Pod should have affinity set"
    assert spec_affinity == affinity_values, f"Affinity should match input: {spec_affinity} != {affinity_values}"


# Test 2: Fail-to-pass test - workers.celery.affinity should be used for worker StatefulSet
def test_workers_celery_affinity_deployment():
    """
    Test that workers.celery.affinity is correctly applied to worker StatefulSet.
    This is a fail-to-pass test - without the fix, this should not work.
    """
    # Use a simpler affinity that won't have type issues with Helm
    affinity_values = {
        "nodeAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": {
                "nodeSelectorTerms": [
                    {
                        "matchExpressions": [
                            {"key": "foo-bar-key", "operator": "Exists"},
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
                "affinity": affinity_values,
            },
        },
    }

    docs = helm_template(
        values=values,
        show_only=["templates/workers/worker-deployment.yaml"],
    )

    # Celery worker is a StatefulSet, not a Deployment
    statefulset_doc = get_doc_by_kind(docs, "StatefulSet")
    assert statefulset_doc is not None, f"StatefulSet document should be generated, got: {[d.get('kind') for d in docs if d]}"

    spec_affinity = jmespath_search("spec.template.spec.affinity", statefulset_doc)
    assert spec_affinity is not None, "StatefulSet should have affinity set"
    # Compare the actual content
    assert spec_affinity.get("nodeAffinity", {}).get("requiredDuringSchedulingIgnoredDuringExecution", {}).get("nodeSelectorTerms", [{}])[0].get("matchExpressions", [{}])[0].get("key") == "foo-bar-key", f"Affinity not correctly set: {spec_affinity}"


# Test 3: Fail-to-pass test - precedence test - workers.kubernetes.affinity should take precedence over workers.affinity
def test_kubernetes_affinity_precedence():
    """
    Test that workers.kubernetes.affinity takes precedence over workers.affinity.
    When both are set, workers.kubernetes.affinity should be used.
    """
    old_affinity = {
        "podAffinity": {
            "preferredDuringSchedulingIgnoredDuringExecution": [
                {
                    "podAffinityTerm": {
                        "topologyKey": "old-key",
                        "labelSelector": {"matchLabels": {"tier": "old"}},
                    },
                    "weight": 1,
                }
            ]
        }
    }

    new_affinity = {
        "nodeAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": {
                "nodeSelectorTerms": [
                    {
                        "matchExpressions": [
                            {"key": "new-key", "operator": "In", "values": ["true"]},
                        ]
                    }
                ]
            }
        }
    }

    values = {
        "executor": "KubernetesExecutor",
        "workers": {
            "affinity": old_affinity,
            "kubernetes": {
                "affinity": new_affinity,
            },
        },
    }

    docs = helm_template(
        values=values,
        show_only=["templates/configmaps/configmap.yaml"],
    )

    pod_doc = extract_pod_template_from_configmap(docs)
    assert pod_doc is not None, "Pod template should be found in ConfigMap"

    spec_affinity = jmespath_search("spec.affinity", pod_doc)
    assert spec_affinity is not None, "Pod should have affinity set"
    assert spec_affinity == new_affinity, f"New affinity should take precedence over old: got {spec_affinity}"


# Test 4: Backward compatibility - workers.affinity should still work
def test_backward_compatibility_old_affinity():
    """
    Test that the old workers.affinity still works for backward compatibility.
    """
    affinity_values = {
        "nodeAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": {
                "nodeSelectorTerms": [
                    {
                        "matchExpressions": [
                            {"key": "foo", "operator": "In", "values": ["true"]},
                        ]
                    }
                ]
            }
        }
    }

    values = {
        "executor": "KubernetesExecutor",
        "workers": {
            "affinity": affinity_values,
        },
    }

    docs = helm_template(
        values=values,
        show_only=["templates/configmaps/configmap.yaml"],
    )

    pod_doc = extract_pod_template_from_configmap(docs)
    assert pod_doc is not None, "Pod template should be found in ConfigMap"

    spec_affinity = jmespath_search("spec.affinity", pod_doc)
    assert spec_affinity is not None, "Pod should have affinity set"
    assert spec_affinity == affinity_values, f"Old affinity should still work: {spec_affinity} != {affinity_values}"


# Test 5: Verify schema changes - values.schema.json should have new fields
def test_schema_has_new_affinity_fields():
    """
    Test that values.schema.json has the new affinity fields defined.
    """
    schema_path = os.path.join(CHART_DIR, "values.schema.json")
    with open(schema_path) as f:
        schema = json.load(f)

    # Check workers.celery.affinity exists
    celery_props = jmespath_search("properties.workers.properties.celery.properties", schema)
    assert celery_props is not None, "workers.celery properties should exist"
    assert "affinity" in celery_props, "workers.celery.affinity should be defined in schema"

    # Check workers.kubernetes.affinity exists
    kubernetes_props = jmespath_search("properties.workers.properties.kubernetes.properties", schema)
    assert kubernetes_props is not None, "workers.kubernetes properties should exist"
    assert "affinity" in kubernetes_props, "workers.kubernetes.affinity should be defined in schema"


# Test 6: Verify schema description mentions deprecation
def test_schema_deprecation_description():
    """
    Test that the deprecated workers.affinity field has deprecation note in schema.
    """
    schema_path = os.path.join(CHART_DIR, "values.schema.json")
    with open(schema_path) as f:
        schema = json.load(f)

    workers_affinity_desc = jmespath_search("properties.workers.properties.affinity.description", schema)
    assert workers_affinity_desc is not None, "workers.affinity description should exist"
    assert "deprecated" in workers_affinity_desc.lower(), "workers.affinity description should mention deprecation"


# Test 7: Verify NOTES.txt has deprecation warning
def test_notes_deprecation_warning():
    """
    Test that NOTES.txt contains deprecation warning for workers.affinity.
    """
    notes_path = os.path.join(CHART_DIR, "templates/NOTES.txt")
    with open(notes_path) as f:
        notes = f.read()

    assert "workers.affinity" in notes, "NOTES.txt should mention workers.affinity"
    assert "deprecated" in notes.lower() or "renamed" in notes.lower(), "NOTES.txt should warn about deprecation"


# Test 8: Verify values.yaml has new affinity fields
def test_values_yaml_has_new_fields():
    """
    Test that values.yaml has the new affinity fields defined.
    """
    values_path = os.path.join(CHART_DIR, "values.yaml")
    with open(values_path) as f:
        values = yaml.safe_load(f)

    # Check workers.celery.affinity exists
    celery_affinity = jmespath_search("workers.celery.affinity", values)
    assert celery_affinity is not None, "workers.celery.affinity should exist"
    assert isinstance(celery_affinity, dict), "workers.celery.affinity should be a dict"

    # Check workers.kubernetes.affinity exists
    kubernetes_affinity = jmespath_search("workers.kubernetes.affinity", values)
    assert kubernetes_affinity is not None, "workers.kubernetes.affinity should exist"
    assert isinstance(kubernetes_affinity, dict), "workers.kubernetes.affinity should be a dict"


# Test 9: Pass-to-pass test - Helm lint should pass
def test_helm_lint():
    """
    Pass-to-pass test: Helm lint should pass on the chart.
    """
    result = subprocess.run(
        ["helm", "lint", CHART_DIR],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Helm lint failed:\n{result.stdout}\n{result.stderr}"


# Test 10: Pass-to-pass test - Helm template with default values should work
def test_helm_template_default_values():
    """
    Pass-to-pass test: Helm template should work with default values.
    """
    result = subprocess.run(
        ["helm", "template", "test-release", CHART_DIR],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Helm template failed:\n{result.stderr}"
    # Should produce non-empty output
    assert result.stdout.strip(), "Helm template should produce output"


# Test 11: Pass-to-pass test - Helm lint strict mode (repo CI check)
def test_helm_lint_strict():
    """
    Pass-to-pass test: Helm lint strict mode passes (repo CI check).
    Verifies chart follows Helm best practices.
    """
    result = subprocess.run(
        ["helm", "lint", CHART_DIR, "--strict"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Helm lint strict failed:\n{result.stdout}\n{result.stderr}"


# Test 12: Pass-to-pass test - Helm template with values.yaml (repo CI check)
def test_helm_template_with_values():
    """
    Pass-to-pass test: Helm template with explicit values.yaml passes (repo CI check).
    Verifies all templates render correctly with default configuration.
    """
    values_path = os.path.join(CHART_DIR, "values.yaml")
    result = subprocess.run(
        ["helm", "template", "test-release", CHART_DIR, "-f", values_path],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Helm template with values.yaml failed:\n{result.stderr}"
    assert result.stdout.strip(), "Helm template should produce non-empty output"


# Test 13: Pass-to-pass test - Helm template validation with KubernetesExecutor (repo CI check)
def test_helm_template_kubernetes_executor():
    """
    Pass-to-pass test: Helm template with KubernetesExecutor passes (repo CI check).
    Verifies pod-template-file renders correctly for the modified executor path.
    """
    values = {"executor": "KubernetesExecutor"}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(values, f)
        values_file = f.name

    try:
        result = subprocess.run(
            ["helm", "template", "test-release", CHART_DIR, "-f", values_file],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"Helm template with KubernetesExecutor failed:\n{result.stderr}"
    finally:
        os.unlink(values_file)


# Test 14: Pass-to-pass test - Helm template validation with CeleryExecutor (repo CI check)
def test_helm_template_celery_executor():
    """
    Pass-to-pass test: Helm template with CeleryExecutor passes (repo CI check).
    Verifies worker StatefulSet renders correctly for the modified Celery path.
    """
    values = {"executor": "CeleryExecutor"}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(values, f)
        values_file = f.name

    try:
        result = subprocess.run(
            ["helm", "template", "test-release", CHART_DIR, "-f", values_file],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"Helm template with CeleryExecutor failed:\n{result.stderr}"
    finally:
        os.unlink(values_file)
