"""
Tests for apache/airflow#64932: Add workers.celery.extraContainers & workers.kubernetes.extraContainers

These tests verify that:
1. workers.kubernetes.extraContainers adds containers to pod template (f2p)
2. workers.celery.extraContainers is defined in values schema (f2p)
3. Deprecated workers.extraContainers still works (p2p)
4. Helm template renders without errors (p2p)
"""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml

REPO = Path("/workspace/airflow")
CHART_DIR = REPO / "chart"


def render_chart(
    values: dict,
    show_only: list[str] | None = None,
    chart_dir: str | Path | None = None,
) -> list[dict]:
    """Render helm chart with given values and return parsed YAML docs."""
    if chart_dir is None:
        chart_dir = CHART_DIR

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(values, f)
        values_file = f.name

    cmd = [
        "helm", "template", "release-name", str(chart_dir),
        "--values", values_file,
        "--kube-version", "1.30.0",
    ]
    if show_only:
        for template in show_only:
            cmd.extend(["--show-only", template])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    os.unlink(values_file)

    if result.returncode != 0:
        raise RuntimeError(f"Helm template failed: {result.stderr}")

    docs = list(yaml.safe_load_all(result.stdout))
    return [d for d in docs if d is not None]


@pytest.fixture(scope="module")
def chart_with_pod_template():
    """
    Create a temporary chart directory with pod-template-file copied to templates/.
    This mimics the test setup in the original helm tests.
    """
    tmp_dir = tempfile.mkdtemp()
    temp_chart_dir = Path(tmp_dir) / "chart"

    # Copy the entire chart directory
    shutil.copytree(CHART_DIR, temp_chart_dir)

    # Copy pod-template-file to templates so it can be rendered
    shutil.copyfile(
        temp_chart_dir / "files" / "pod-template-file.kubernetes-helm-yaml",
        temp_chart_dir / "templates" / "pod-template-file.yaml",
    )

    yield temp_chart_dir

    # Cleanup
    shutil.rmtree(tmp_dir)


class TestKubernetesExtraContainers:
    """Test workers.kubernetes.extraContainers functionality (fail_to_pass)."""

    def test_kubernetes_extra_containers_in_pod_template(self, chart_with_pod_template):
        """
        workers.kubernetes.extraContainers should add containers to pod-template-file.

        Before the fix: workers.kubernetes.extraContainers is not recognized,
        so no extra containers appear in the pod template.

        After the fix: workers.kubernetes.extraContainers is recognized and
        extra containers are added to the pod template.
        """
        values = {
            "workers": {
                "kubernetes": {
                    "extraContainers": [
                        {
                            "name": "k8s-sidecar",
                            "image": "busybox:1.36",
                        }
                    ]
                }
            }
        }

        docs = render_chart(
            values,
            show_only=["templates/pod-template-file.yaml"],
            chart_dir=chart_with_pod_template,
        )
        assert len(docs) > 0, "No pod template rendered"

        pod = docs[0]
        containers = pod.get("spec", {}).get("containers", [])

        # Find our sidecar container
        sidecar_names = [c["name"] for c in containers if c.get("name") == "k8s-sidecar"]
        assert "k8s-sidecar" in sidecar_names, (
            f"Expected 'k8s-sidecar' in containers, got: {[c['name'] for c in containers]}"
        )

    def test_kubernetes_extra_containers_with_varied_config(self, chart_with_pod_template):
        """Test workers.kubernetes.extraContainers with different container configs."""
        values = {
            "workers": {
                "kubernetes": {
                    "extraContainers": [
                        {
                            "name": "log-collector",
                            "image": "fluent/fluentd:v1.16",
                            "volumeMounts": [{"name": "logs", "mountPath": "/var/log"}],
                        }
                    ]
                }
            }
        }

        docs = render_chart(
            values,
            show_only=["templates/pod-template-file.yaml"],
            chart_dir=chart_with_pod_template,
        )
        pod = docs[0]
        containers = pod.get("spec", {}).get("containers", [])

        log_collector = next((c for c in containers if c.get("name") == "log-collector"), None)
        assert log_collector is not None, "log-collector container not found"
        assert log_collector["image"] == "fluent/fluentd:v1.16"


class TestCeleryExtraContainersSchema:
    """Test workers.celery.extraContainers schema definition (fail_to_pass)."""

    def test_celery_extra_containers_in_schema(self):
        """
        workers.celery.extraContainers should be defined in values.schema.json.

        Before the fix: workers.celery.extraContainers is not in the schema.
        After the fix: workers.celery.extraContainers is defined with proper type.
        """
        schema_path = CHART_DIR / "values.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)

        # Navigate to workers.celery.extraContainers
        workers = schema.get("properties", {}).get("workers", {})
        workers_props = workers.get("properties", {})
        celery = workers_props.get("celery", {})
        celery_props = celery.get("properties", {})

        assert "extraContainers" in celery_props, (
            "workers.celery.extraContainers not found in schema. "
            f"Available celery properties: {list(celery_props.keys())}"
        )

        extra_containers = celery_props["extraContainers"]
        assert extra_containers.get("type") == "array", (
            f"extraContainers should be array type, got: {extra_containers.get('type')}"
        )

    def test_kubernetes_extra_containers_in_schema(self):
        """
        workers.kubernetes.extraContainers should be defined in values.schema.json.

        Before the fix: workers.kubernetes.extraContainers is not in the schema.
        After the fix: workers.kubernetes.extraContainers is defined with proper type.
        """
        schema_path = CHART_DIR / "values.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)

        workers = schema.get("properties", {}).get("workers", {})
        workers_props = workers.get("properties", {})
        kubernetes = workers_props.get("kubernetes", {})
        k8s_props = kubernetes.get("properties", {})

        assert "extraContainers" in k8s_props, (
            "workers.kubernetes.extraContainers not found in schema. "
            f"Available kubernetes properties: {list(k8s_props.keys())}"
        )

        extra_containers = k8s_props["extraContainers"]
        assert extra_containers.get("type") == "array", (
            f"extraContainers should be array type, got: {extra_containers.get('type')}"
        )


class TestDeprecatedExtraContainers:
    """Test that deprecated workers.extraContainers still works (pass_to_pass)."""

    def test_deprecated_extra_containers_still_works(self, chart_with_pod_template):
        """
        Deprecated workers.extraContainers should still add containers.
        This is a pass_to_pass test - backward compatibility.
        """
        values = {
            "workers": {
                "extraContainers": [
                    {
                        "name": "legacy-sidecar",
                        "image": "nginx:1.25",
                    }
                ]
            }
        }

        docs = render_chart(
            values,
            show_only=["templates/pod-template-file.yaml"],
            chart_dir=chart_with_pod_template,
        )
        pod = docs[0]
        containers = pod.get("spec", {}).get("containers", [])

        sidecar_names = [c["name"] for c in containers]
        assert "legacy-sidecar" in sidecar_names, (
            f"Deprecated extraContainers should still work. Got: {sidecar_names}"
        )


class TestHelmChartValidity:
    """Test that helm chart renders correctly (pass_to_pass)."""

    def test_chart_lint(self):
        """Helm lint should pass."""
        result = subprocess.run(
            ["helm", "lint", str(CHART_DIR)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, f"Helm lint failed:\n{result.stderr}"

    def test_default_values_render(self):
        """Chart should render with default values."""
        docs = render_chart({})
        assert len(docs) > 0, "No templates rendered with default values"

    def test_values_schema_valid_json(self):
        """values.schema.json should be valid JSON (pass_to_pass)."""
        result = subprocess.run(
            ["python3", "-c", "import json; json.load(open('values.schema.json'))"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=CHART_DIR,
        )
        assert result.returncode == 0, f"values.schema.json is not valid JSON:\n{result.stderr}"

    def test_values_yaml_conforms_to_schema(self):
        """values.yaml should conform to values.schema.json (pass_to_pass)."""
        # Install jsonschema if needed
        subprocess.run(
            ["pip", "install", "--quiet", "jsonschema"],
            capture_output=True,
            timeout=60,
        )
        validation_script = '''
import json
import yaml
import jsonschema

schema = json.load(open("values.schema.json"))
values = yaml.safe_load(open("values.yaml"))

jsonschema.Draft7Validator.check_schema(schema)
validator = jsonschema.Draft7Validator(schema)
errors = list(validator.iter_errors(values))
if errors:
    for e in errors[:5]:
        print(f"ERROR: {e.message}")
    exit(1)
'''
        result = subprocess.run(
            ["python3", "-c", validation_script],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=CHART_DIR,
        )
        assert result.returncode == 0, f"values.yaml does not conform to schema:\n{result.stdout}\n{result.stderr}"

    def test_chart_dependencies_ok(self):
        """Helm chart dependencies should be properly configured (pass_to_pass)."""
        result = subprocess.run(
            ["helm", "dependency", "list", str(CHART_DIR)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"Helm dependency list failed:\n{result.stderr}"
        # Verify postgresql dependency is marked OK
        assert "ok" in result.stdout.lower() or "missing" not in result.stdout.lower(), (
            f"Dependencies not ok:\n{result.stdout}"
        )


class TestKubernetesOverridesDeprecated:
    """Test that kubernetes.extraContainers overrides deprecated extraContainers (fail_to_pass)."""

    def test_kubernetes_takes_precedence(self, chart_with_pod_template):
        """
        When both workers.extraContainers and workers.kubernetes.extraContainers are set,
        kubernetes.extraContainers should take precedence for pod-template-file.

        Before the fix: workers.kubernetes.extraContainers is ignored.
        After the fix: workers.kubernetes.extraContainers takes precedence.
        """
        values = {
            "workers": {
                "extraContainers": [
                    {"name": "deprecated-sidecar", "image": "old:v1"}
                ],
                "kubernetes": {
                    "extraContainers": [
                        {"name": "preferred-sidecar", "image": "new:v2"}
                    ]
                }
            }
        }

        docs = render_chart(
            values,
            show_only=["templates/pod-template-file.yaml"],
            chart_dir=chart_with_pod_template,
        )
        pod = docs[0]
        containers = pod.get("spec", {}).get("containers", [])
        container_names = [c["name"] for c in containers]

        # The kubernetes-specific one should be used
        assert "preferred-sidecar" in container_names, (
            f"Expected 'preferred-sidecar' from kubernetes.extraContainers, got: {container_names}"
        )
        # The deprecated one should NOT appear (kubernetes takes precedence)
        assert "deprecated-sidecar" not in container_names, (
            "deprecated-sidecar should not appear when kubernetes.extraContainers is set"
        )


class TestValuesYamlStructure:
    """Test values.yaml has proper structure for new config paths (fail_to_pass)."""

    def test_workers_celery_extracontainers_in_values(self):
        """workers.celery.extraContainers should be defined in values.yaml."""
        values_path = CHART_DIR / "values.yaml"
        with open(values_path) as f:
            values = yaml.safe_load(f)

        workers = values.get("workers", {})
        celery = workers.get("celery", {})

        assert "extraContainers" in celery, (
            "workers.celery.extraContainers not found in values.yaml. "
            f"Available celery keys: {list(celery.keys())}"
        )

    def test_workers_kubernetes_extracontainers_in_values(self):
        """workers.kubernetes.extraContainers should be defined in values.yaml."""
        values_path = CHART_DIR / "values.yaml"
        with open(values_path) as f:
            values = yaml.safe_load(f)

        workers = values.get("workers", {})
        kubernetes = workers.get("kubernetes", {})

        assert "extraContainers" in kubernetes, (
            "workers.kubernetes.extraContainers not found in values.yaml. "
            f"Available kubernetes keys: {list(kubernetes.keys())}"
        )
