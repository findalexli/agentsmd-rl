"""
Test outputs for airflow-helm-worker-affinity benchmark task.

Tests that workers.kubernetes.affinity takes precedence over the deprecated
workers.affinity in the pod-template-file.

The key behavioral change is in pod-template-file.kubernetes-helm-yaml:
- Before: $affinity := or .Values.workers.affinity .Values.affinity
- After:  $affinity := or .Values.workers.kubernetes.affinity .Values.workers.affinity .Values.affinity
"""

import json
import subprocess
import tempfile
from pathlib import Path

import jmespath
import pytest
import yaml

REPO = Path("/workspace/airflow")
CHART_DIR = REPO / "chart"


def render_chart(values: dict, show_only: list[str] | None = None) -> list[dict]:
    """Render Helm chart with given values and return parsed K8s objects."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(values, f)
        values_file = f.name

    cmd = [
        "helm", "template", "release-name", str(CHART_DIR),
        "--values", values_file,
        "--kube-version", "1.30.0",
        "--namespace", "default",
    ]
    if show_only:
        for path in show_only:
            cmd.extend(["--show-only", path])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=str(CHART_DIR))
    Path(values_file).unlink()

    if result.returncode != 0:
        raise RuntimeError(f"Helm template failed: {result.stderr}")

    objects = list(yaml.safe_load_all(result.stdout))
    return [obj for obj in objects if obj is not None]


def extract_pod_template_from_configmap(configmap: dict) -> dict:
    """Extract the pod_template_file.yaml from the ConfigMap data."""
    pod_template_yaml = configmap.get("data", {}).get("pod_template_file.yaml", "")
    if not pod_template_yaml:
        raise ValueError("pod_template_file.yaml not found in ConfigMap")
    return yaml.safe_load(pod_template_yaml)


class TestKubernetesWorkerAffinityPrecedence:
    """Test workers.kubernetes.affinity takes precedence over workers.affinity (fail_to_pass).

    The bug is in pod-template-file.kubernetes-helm-yaml where the affinity
    resolution doesn't check workers.kubernetes.affinity first.
    """

    def test_kubernetes_affinity_precedence_node_affinity(self):
        """
        Test that workers.kubernetes.affinity takes precedence over workers.affinity
        when both are set with different nodeAffinity values.

        On base commit: workers.kubernetes.affinity is ignored, workers.affinity is used
        After fix: workers.kubernetes.affinity takes precedence
        """
        values = {
            "executor": "KubernetesExecutor",
            "workers": {
                "affinity": {
                    "nodeAffinity": {
                        "requiredDuringSchedulingIgnoredDuringExecution": {
                            "nodeSelectorTerms": [{
                                "matchExpressions": [{
                                    "key": "deprecated-affinity-key",
                                    "operator": "In",
                                    "values": ["deprecated-value"]
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
                                        "values": ["kubernetes-value"]
                                    }]
                                }]
                            }
                        }
                    }
                }
            }
        }

        # Render the configmap which contains the pod-template-file
        docs = render_chart(values, show_only=["templates/configmaps/configmap.yaml"])
        assert len(docs) >= 1, "Expected at least one ConfigMap document"

        configmap = docs[0]
        pod_template = extract_pod_template_from_configmap(configmap)

        affinity = jmespath.search("spec.affinity", pod_template)
        assert affinity is not None, "Affinity should be set in pod template"

        # Check that the kubernetes-specific affinity is used, NOT the deprecated one
        match_key = jmespath.search(
            "nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0].key",
            affinity
        )
        assert match_key == "kubernetes-specific-key", (
            f"Expected kubernetes-specific-key but got {match_key}. "
            "workers.kubernetes.affinity should take precedence over workers.affinity"
        )

    def test_kubernetes_affinity_precedence_pod_anti_affinity(self):
        """
        Test with podAntiAffinity instead of nodeAffinity to ensure the fix works
        for different affinity types.
        """
        values = {
            "executor": "KubernetesExecutor",
            "workers": {
                "affinity": {
                    "podAntiAffinity": {
                        "preferredDuringSchedulingIgnoredDuringExecution": [{
                            "weight": 50,
                            "podAffinityTerm": {
                                "topologyKey": "deprecated-topology",
                                "labelSelector": {
                                    "matchLabels": {"source": "deprecated"}
                                }
                            }
                        }]
                    }
                },
                "kubernetes": {
                    "affinity": {
                        "podAntiAffinity": {
                            "preferredDuringSchedulingIgnoredDuringExecution": [{
                                "weight": 100,
                                "podAffinityTerm": {
                                    "topologyKey": "kubernetes-topology",
                                    "labelSelector": {
                                        "matchLabels": {"source": "kubernetes"}
                                    }
                                }
                            }]
                        }
                    }
                }
            }
        }

        docs = render_chart(values, show_only=["templates/configmaps/configmap.yaml"])
        assert len(docs) >= 1

        configmap = docs[0]
        pod_template = extract_pod_template_from_configmap(configmap)

        affinity = jmespath.search("spec.affinity", pod_template)
        assert affinity is not None

        # Check that kubernetes-topology is used, not deprecated-topology
        topology_key = jmespath.search(
            "podAntiAffinity.preferredDuringSchedulingIgnoredDuringExecution[0].podAffinityTerm.topologyKey",
            affinity
        )
        assert topology_key == "kubernetes-topology", (
            f"Expected kubernetes-topology but got {topology_key}. "
            "workers.kubernetes.affinity should override workers.affinity"
        )


class TestNewAffinityFieldIndependent:
    """Test that workers.kubernetes.affinity works independently (fail_to_pass).

    On the broken code, workers.kubernetes.affinity is not recognized as a
    valid affinity source, so setting it alone produces no affinity in the
    pod template. After the fix, it is properly resolved.
    """

    def test_kubernetes_affinity_works_alone(self):
        """
        Test that workers.kubernetes.affinity is applied when set without
        the deprecated workers.affinity field.

        On base: workers.kubernetes.affinity is ignored, no affinity in pod template
        After fix: workers.kubernetes.affinity is picked up, affinity appears
        """
        values = {
            "executor": "KubernetesExecutor",
            "workers": {
                "kubernetes": {
                    "affinity": {
                        "nodeAffinity": {
                            "requiredDuringSchedulingIgnoredDuringExecution": {
                                "nodeSelectorTerms": [{
                                    "matchExpressions": [{
                                        "key": "standalone-k8s-key",
                                        "operator": "In",
                                        "values": ["standalone-k8s-value"]
                                    }]
                                }]
                            }
                        }
                    }
                }
            }
        }

        docs = render_chart(values, show_only=["templates/configmaps/configmap.yaml"])
        assert len(docs) >= 1

        configmap = docs[0]
        pod_template = extract_pod_template_from_configmap(configmap)

        affinity = jmespath.search("spec.affinity", pod_template)
        assert affinity is not None, (
            "Affinity should be set in pod template when workers.kubernetes.affinity is configured"
        )

        match_key = jmespath.search(
            "nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution"
            ".nodeSelectorTerms[0].matchExpressions[0].key",
            affinity
        )
        assert match_key == "standalone-k8s-key", (
            f"Expected standalone-k8s-key but got {match_key}. "
            "workers.kubernetes.affinity should be applied when used alone"
        )


class TestSchemaValidation:
    """Test that schema includes new affinity fields (fail_to_pass)."""

    def test_schema_has_kubernetes_affinity(self):
        """Test that values.schema.json includes workers.kubernetes.affinity."""
        schema_path = CHART_DIR / "values.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)

        # Navigate to workers.kubernetes.affinity in schema
        workers_props = schema.get("properties", {}).get("workers", {}).get("properties", {})
        kubernetes_props = workers_props.get("kubernetes", {}).get("properties", {})

        assert "affinity" in kubernetes_props, (
            "Schema should define workers.kubernetes.affinity property"
        )
        affinity_desc = kubernetes_props["affinity"].get("description", "")
        assert "pod-template-file" in affinity_desc.lower() or "kubernetes" in affinity_desc.lower(), (
            "workers.kubernetes.affinity should have an appropriate description"
        )

    def test_schema_has_celery_affinity(self):
        """Test that values.schema.json includes workers.celery.affinity."""
        schema_path = CHART_DIR / "values.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)

        workers_props = schema.get("properties", {}).get("workers", {}).get("properties", {})
        celery_props = workers_props.get("celery", {}).get("properties", {})

        assert "affinity" in celery_props, (
            "Schema should define workers.celery.affinity property"
        )


class TestHelmTemplateBasic:
    """Basic helm template tests (pass_to_pass)."""

    def test_helm_template_default_values(self):
        """Test that helm template works with default values."""
        docs = render_chart({})
        assert len(docs) > 0, "Helm template should produce at least one document"

    def test_helm_template_with_kubernetes_executor(self):
        """Test helm template with KubernetesExecutor renders configmap."""
        values = {"executor": "KubernetesExecutor"}
        docs = render_chart(values, show_only=["templates/configmaps/configmap.yaml"])
        assert len(docs) >= 1, "Should render configmap for KubernetesExecutor"

        # Check that pod_template_file.yaml is present
        configmap = docs[0]
        assert "pod_template_file.yaml" in configmap.get("data", {}), (
            "ConfigMap should contain pod_template_file.yaml"
        )

    def test_helm_template_with_celery_executor(self):
        """Test helm template with CeleryExecutor."""
        values = {"executor": "CeleryExecutor"}
        docs = render_chart(values, show_only=["templates/workers/worker-deployment.yaml"])
        assert len(docs) >= 1, "Should render worker deployment for CeleryExecutor"


class TestBackwardCompatibility:
    """Test backward compatibility with workers.affinity (pass_to_pass)."""

    def test_workers_affinity_still_works_alone(self):
        """Test that workers.affinity still works when used alone (without the new fields)."""
        values = {
            "executor": "KubernetesExecutor",
            "workers": {
                "affinity": {
                    "nodeAffinity": {
                        "requiredDuringSchedulingIgnoredDuringExecution": {
                            "nodeSelectorTerms": [{
                                "matchExpressions": [{
                                    "key": "legacy-key",
                                    "operator": "In",
                                    "values": ["legacy-value"]
                                }]
                            }]
                        }
                    }
                }
            }
        }

        docs = render_chart(values, show_only=["templates/configmaps/configmap.yaml"])
        assert len(docs) >= 1

        configmap = docs[0]
        pod_template = extract_pod_template_from_configmap(configmap)

        affinity = jmespath.search("spec.affinity", pod_template)
        assert affinity is not None, "Affinity should be set from workers.affinity"

        match_key = jmespath.search(
            "nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0].key",
            affinity
        )
        assert match_key == "legacy-key", "workers.affinity should still work when used alone"

    def test_celery_workers_affinity_works(self):
        """Test that workers.affinity works for Celery workers."""
        values = {
            "executor": "CeleryExecutor",
            "workers": {
                "affinity": {
                    "nodeAffinity": {
                        "requiredDuringSchedulingIgnoredDuringExecution": {
                            "nodeSelectorTerms": [{
                                "matchExpressions": [{
                                    "key": "celery-legacy-key",
                                    "operator": "In",
                                    "values": ["celery-value"]
                                }]
                            }]
                        }
                    }
                }
            }
        }

        docs = render_chart(values, show_only=["templates/workers/worker-deployment.yaml"])
        assert len(docs) >= 1

        worker_doc = docs[0]
        affinity = jmespath.search("spec.template.spec.affinity", worker_doc)
        assert affinity is not None, "Affinity should be set in worker deployment"


class TestRepoCICommands:
    """Run actual repo CI commands (pass_to_pass)."""

    def test_repo_helm_lint(self):
        """Repo's helm lint passes on the chart (pass_to_pass)."""
        r = subprocess.run(
            ["helm", "lint", ".", "-f", "values.yaml"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(CHART_DIR),
        )
        assert r.returncode == 0, f"Helm lint failed:\n{r.stdout}\n{r.stderr}"

    def test_repo_chart_schema_validation(self):
        """Repo's chart_schema.py script passes (pass_to_pass)."""
        r = subprocess.run(
            ["python3", str(REPO / "scripts" / "ci" / "prek" / "chart_schema.py")],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(CHART_DIR),
        )
        assert r.returncode == 0, f"chart_schema.py failed:\n{r.stdout}\n{r.stderr}"

    def test_repo_values_schema_valid_json(self):
        """Repo's values.schema.json is valid JSON schema (pass_to_pass)."""
        r = subprocess.run(
            [
                "python3", "-c",
                "import json; import jsonschema; "
                "schema=json.load(open('values.schema.json')); "
                "jsonschema.Draft7Validator.check_schema(schema); "
                "print('Schema is valid')"
            ],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(CHART_DIR),
        )
        assert r.returncode == 0, f"Schema validation failed:\n{r.stdout}\n{r.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
