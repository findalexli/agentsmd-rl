"""
Tests for airflow-helm-workers-affinity task.

This task verifies that the Helm chart supports separate affinity configurations
for Kubernetes executor workers (workers.kubernetes.affinity) and Celery workers
(workers.celery.affinity), with proper precedence handling.
"""

import json
import os
import subprocess
import tempfile
import yaml

REPO = "/workspace/airflow"
CHART_DIR = os.path.join(REPO, "chart")


def helm_template(values: dict, show_only: str = None) -> list:
    """
    Render Helm chart templates with given values.
    Returns list of parsed YAML documents.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(values, f)
        values_file = f.name

    try:
        cmd = ["helm", "template", "test-release", CHART_DIR, "-f", values_file]
        if show_only:
            cmd.extend(["--show-only", show_only])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO
        )

        if result.returncode != 0:
            raise RuntimeError(f"Helm template failed: {result.stderr}")

        # Parse all YAML documents from output
        docs = []
        for doc in yaml.safe_load_all(result.stdout):
            if doc is not None:
                docs.append(doc)
        return docs
    finally:
        os.unlink(values_file)


def get_pod_template_from_configmap(docs: list) -> dict:
    """
    Extract the pod_template_file.yaml from the ConfigMap.
    The pod template is stored as a string in configmap.data['pod_template_file.yaml'].
    """
    for doc in docs:
        if doc.get("kind") == "ConfigMap" and "config" in doc.get("metadata", {}).get("name", ""):
            data = doc.get("data", {})
            pod_template_str = data.get("pod_template_file.yaml", "")
            if pod_template_str:
                # Parse the embedded YAML
                pod_templates = list(yaml.safe_load_all(pod_template_str))
                for pt in pod_templates:
                    if pt and pt.get("kind") == "Pod":
                        return pt
    return {}


def test_kubernetes_affinity_precedence_over_workers_affinity():
    """
    Test that workers.kubernetes.affinity takes precedence over workers.affinity
    in the pod-template-file (fail_to_pass).

    When both workers.affinity and workers.kubernetes.affinity are set,
    workers.kubernetes.affinity should be used for Kubernetes executor pods.
    """
    # Set workers.affinity with one label selector and workers.kubernetes.affinity with different one
    values = {
        "executor": "KubernetesExecutor",
        "workers": {
            "affinity": {
                "nodeAffinity": {
                    "requiredDuringSchedulingIgnoredDuringExecution": {
                        "nodeSelectorTerms": [{
                            "matchExpressions": [{
                                "key": "should-not-be-used",
                                "operator": "In",
                                "values": ["false"]
                            }]
                        }]
                    }
                }
            },
            "kubernetes": {
                "affinity": {
                    "nodeAffinity": {
                        "requiredDuringSchedulingIgnoredDuringExecution": {
                            "nodeSelectorTerms": [{
                                "matchExpressions": [{
                                    "key": "kubernetes-specific-key",
                                    "operator": "In",
                                    "values": ["true"]
                                }]
                            }]
                        }
                    }
                }
            }
        }
    }

    docs = helm_template(values, show_only="templates/configmaps/configmap.yaml")
    pod_template = get_pod_template_from_configmap(docs)

    assert pod_template, "Could not extract pod template from ConfigMap"

    affinity = pod_template.get("spec", {}).get("affinity", {})

    # The kubernetes-specific affinity should be used
    node_affinity = affinity.get("nodeAffinity", {})
    required = node_affinity.get("requiredDuringSchedulingIgnoredDuringExecution", {})
    node_selector_terms = required.get("nodeSelectorTerms", [])

    assert len(node_selector_terms) > 0, "Expected nodeSelectorTerms in affinity"

    match_expressions = node_selector_terms[0].get("matchExpressions", [])
    assert len(match_expressions) > 0, "Expected matchExpressions"

    # Verify that kubernetes-specific-key is used, not should-not-be-used
    key_used = match_expressions[0].get("key")
    assert key_used == "kubernetes-specific-key", \
        f"Expected kubernetes-specific-key but got {key_used}. " \
        "workers.kubernetes.affinity should take precedence over workers.affinity"


def test_kubernetes_affinity_standalone():
    """
    Test that workers.kubernetes.affinity works when set alone (fail_to_pass).

    Setting only workers.kubernetes.affinity (without workers.affinity) should
    result in that affinity being applied to the pod template.
    """
    values = {
        "executor": "KubernetesExecutor",
        "workers": {
            "kubernetes": {
                "affinity": {
                    "podAntiAffinity": {
                        "preferredDuringSchedulingIgnoredDuringExecution": [{
                            "weight": 100,
                            "podAffinityTerm": {
                                "topologyKey": "kubernetes.io/hostname",
                                "labelSelector": {
                                    "matchLabels": {
                                        "component": "k8s-worker"
                                    }
                                }
                            }
                        }]
                    }
                }
            }
        }
    }

    docs = helm_template(values, show_only="templates/configmaps/configmap.yaml")
    pod_template = get_pod_template_from_configmap(docs)

    assert pod_template, "Could not extract pod template from ConfigMap"

    affinity = pod_template.get("spec", {}).get("affinity", {})

    # Check that podAntiAffinity is set correctly
    pod_anti_affinity = affinity.get("podAntiAffinity", {})
    preferred = pod_anti_affinity.get("preferredDuringSchedulingIgnoredDuringExecution", [])

    assert len(preferred) > 0, \
        "Expected preferredDuringSchedulingIgnoredDuringExecution in podAntiAffinity. " \
        "workers.kubernetes.affinity should be applied to pod template."

    # Verify the label selector
    label_selector = preferred[0].get("podAffinityTerm", {}).get("labelSelector", {})
    match_labels = label_selector.get("matchLabels", {})
    assert match_labels.get("component") == "k8s-worker", \
        f"Expected component: k8s-worker but got {match_labels}"


def test_workers_affinity_backwards_compatibility():
    """
    Test that workers.affinity still works for backwards compatibility (pass_to_pass).

    When only workers.affinity is set (not workers.kubernetes.affinity),
    it should still be applied to the pod template.
    """
    values = {
        "executor": "KubernetesExecutor",
        "workers": {
            "affinity": {
                "nodeAffinity": {
                    "requiredDuringSchedulingIgnoredDuringExecution": {
                        "nodeSelectorTerms": [{
                            "matchExpressions": [{
                                "key": "legacy-affinity-key",
                                "operator": "In",
                                "values": ["works"]
                            }]
                        }]
                    }
                }
            }
        }
    }

    docs = helm_template(values, show_only="templates/configmaps/configmap.yaml")
    pod_template = get_pod_template_from_configmap(docs)

    assert pod_template, "Could not extract pod template from ConfigMap"

    affinity = pod_template.get("spec", {}).get("affinity", {})

    node_affinity = affinity.get("nodeAffinity", {})
    required = node_affinity.get("requiredDuringSchedulingIgnoredDuringExecution", {})
    node_selector_terms = required.get("nodeSelectorTerms", [])

    assert len(node_selector_terms) > 0, "Expected nodeSelectorTerms for legacy affinity"

    match_expressions = node_selector_terms[0].get("matchExpressions", [])
    key_used = match_expressions[0].get("key")
    assert key_used == "legacy-affinity-key", \
        f"Expected legacy-affinity-key but got {key_used}"


def test_helm_lint():
    """
    Test that the Helm chart passes linting (pass_to_pass).
    """
    result = subprocess.run(
        ["helm", "lint", CHART_DIR],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )

    assert result.returncode == 0, f"Helm lint failed:\n{result.stdout}\n{result.stderr}"


def test_values_schema_has_kubernetes_affinity():
    """
    Test that values.schema.json defines workers.kubernetes.affinity (fail_to_pass).
    """
    schema_path = os.path.join(CHART_DIR, "values.schema.json")

    with open(schema_path, 'r') as f:
        schema = json.load(f)

    # Navigate to workers.kubernetes.affinity in schema
    workers = schema.get("properties", {}).get("workers", {})
    workers_props = workers.get("properties", {})
    kubernetes = workers_props.get("kubernetes", {})
    kubernetes_props = kubernetes.get("properties", {})

    assert "affinity" in kubernetes_props, \
        "Expected 'affinity' property in workers.kubernetes schema definition"

    affinity_def = kubernetes_props["affinity"]
    assert affinity_def.get("type") == "object", \
        f"Expected affinity to be object type, got {affinity_def.get('type')}"


def test_values_yaml_has_kubernetes_affinity_default():
    """
    Test that values.yaml has workers.kubernetes.affinity default (fail_to_pass).
    """
    values_path = os.path.join(CHART_DIR, "values.yaml")

    with open(values_path, 'r') as f:
        values = yaml.safe_load(f)

    workers = values.get("workers", {})
    kubernetes = workers.get("kubernetes", {})

    assert "affinity" in kubernetes, \
        "Expected 'affinity' key in workers.kubernetes values"


def test_deprecation_warning_in_notes_template():
    """
    Test that NOTES.txt template includes deprecation warning for workers.affinity (fail_to_pass).

    Since NOTES.txt is only rendered during helm install (not helm template),
    we check the template file directly for the deprecation warning logic.
    """
    notes_path = os.path.join(CHART_DIR, "templates", "NOTES.txt")

    with open(notes_path, 'r') as f:
        notes_content = f.read()

    # Check that the template has the deprecation warning for workers.affinity
    assert "workers.affinity" in notes_content, \
        "Expected NOTES.txt to reference workers.affinity deprecation"

    assert "DEPRECATION WARNING" in notes_content, \
        "Expected DEPRECATION WARNING text in NOTES.txt"

    # Check that it mentions the new affinity options
    assert "workers.celery.affinity" in notes_content or "workers.kubernetes.affinity" in notes_content, \
        "Expected warning to mention the new affinity options"

    # Verify the conditional check for empty workers.affinity
    assert "if not (empty .Values.workers.affinity)" in notes_content, \
        "Expected conditional check for workers.affinity in NOTES.txt"


def test_repo_helm_template_renders():
    """
    Helm chart templates render without errors (pass_to_pass).

    Verifies the chart can be rendered with helm template command.
    """
    result = subprocess.run(
        ["helm", "template", "test", CHART_DIR],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )

    assert result.returncode == 0, f"Helm template failed:\n{result.stderr[-500:]}"
    # Verify some output was generated
    assert len(result.stdout) > 1000, "Expected substantial template output"


def test_repo_helm_template_kubernetes_executor():
    """
    Helm chart templates render with KubernetesExecutor (pass_to_pass).

    Verifies the chart can be rendered for KubernetesExecutor configuration.
    """
    result = subprocess.run(
        ["helm", "template", "test", CHART_DIR, "--set", "executor=KubernetesExecutor"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )

    assert result.returncode == 0, f"Helm template with KubernetesExecutor failed:\n{result.stderr[-500:]}"
    # Verify pod template file is included in output for KubernetesExecutor
    assert "pod_template_file.yaml" in result.stdout, \
        "Expected pod_template_file.yaml in KubernetesExecutor template output"


def test_repo_values_schema_valid_json():
    """
    values.schema.json is valid JSON (pass_to_pass).

    Validates JSON syntax of the values schema file.
    """
    schema_path = os.path.join(CHART_DIR, "values.schema.json")

    result = subprocess.run(
        ["python", "-m", "json.tool", schema_path],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    assert result.returncode == 0, f"values.schema.json is not valid JSON:\n{result.stderr[-500:]}"


def test_repo_values_yaml_valid_syntax():
    """
    values.yaml has valid YAML syntax (pass_to_pass).

    Validates YAML syntax of the values file.
    """
    values_path = os.path.join(CHART_DIR, "values.yaml")

    result = subprocess.run(
        ["python", "-c", f"import yaml; yaml.safe_load(open('{values_path}'))"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    assert result.returncode == 0, f"values.yaml has invalid YAML syntax:\n{result.stderr[-500:]}"


def test_repo_chart_yaml_valid():
    """
    Chart.yaml is valid and readable by helm (pass_to_pass).

    Verifies Chart.yaml can be parsed with helm show chart.
    """
    result = subprocess.run(
        ["helm", "show", "chart", CHART_DIR],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    assert result.returncode == 0, f"helm show chart failed:\n{result.stderr[-500:]}"
    # Verify basic chart metadata is present
    assert "name: airflow" in result.stdout, "Expected chart name in output"
    assert "version:" in result.stdout, "Expected chart version in output"
