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
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
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
        docs = list(yaml.safe_load_all(result.stdout))
        return [d for d in docs if d is not None]
    finally:
        if values:
            os.unlink(values_file)


def get_doc_by_kind(docs, kind):
    for doc in docs:
        if doc.get("kind") == kind:
            return doc
    return None


def jmespath_search(path, doc):
    parts = path.split(".")
    current = doc
    for part in parts:
        if current is None:
            return None
        if part.startswith("[") and part.endswith("]"):
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
    for doc in docs:
        if doc.get("kind") == "ConfigMap":
            data = doc.get("data", {})
            for key, value in data.items():
                try:
                    pod = yaml.safe_load(value)
                    if pod and pod.get("kind") == "Pod":
                        return pod
                except:
                    pass
    return None


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


def test_workers_celery_affinity_deployment():
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
    statefulset_doc = get_doc_by_kind(docs, "StatefulSet")
    assert statefulset_doc is not None
    spec_affinity = jmespath_search("spec.template.spec.affinity", statefulset_doc)
    assert spec_affinity is not None, "StatefulSet should have affinity set"
    assert spec_affinity.get("nodeAffinity", {}).get("requiredDuringSchedulingIgnoredDuringExecution", {}).get("nodeSelectorTerms", [{}])[0].get("matchExpressions", [{}])[0].get("key") == "foo-bar-key"


def test_kubernetes_affinity_precedence():
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
    assert spec_affinity == new_affinity, f"New affinity should take precedence: {spec_affinity}"


def test_backward_compatibility_old_affinity():
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
    assert spec_affinity == affinity_values


def test_schema_has_new_affinity_fields():
    schema_path = os.path.join(CHART_DIR, "values.schema.json")
    with open(schema_path) as f:
        schema = json.load(f)
    celery_props = jmespath_search("properties.workers.properties.celery.properties", schema)
    assert celery_props is not None, "workers.celery properties should exist"
    assert "affinity" in celery_props, "workers.celery.affinity should be defined in schema"
    kubernetes_props = jmespath_search("properties.workers.properties.kubernetes.properties", schema)
    assert kubernetes_props is not None, "workers.kubernetes properties should exist"
    assert "affinity" in kubernetes_props


def test_schema_deprecation_description():
    schema_path = os.path.join(CHART_DIR, "values.schema.json")
    with open(schema_path) as f:
        schema = json.load(f)
    workers_affinity_desc = jmespath_search("properties.workers.properties.affinity.description", schema)
    assert workers_affinity_desc is not None
    assert "deprecated" in workers_affinity_desc.lower()


def test_notes_deprecation_warning():
    notes_path = os.path.join(CHART_DIR, "templates/NOTES.txt")
    with open(notes_path) as f:
        notes = f.read()
    assert "workers.affinity" in notes
    assert "deprecated" in notes.lower() or "renamed" in notes.lower()


def test_values_yaml_has_new_fields():
    values_path = os.path.join(CHART_DIR, "values.yaml")
    with open(values_path) as f:
        values = yaml.safe_load(f)
    celery_affinity = jmespath_search("workers.celery.affinity", values)
    assert celery_affinity is not None
    assert isinstance(celery_affinity, dict)
    kubernetes_affinity = jmespath_search("workers.kubernetes.affinity", values)
    assert kubernetes_affinity is not None
    assert isinstance(kubernetes_affinity, dict)


def test_helm_lint():
    result = subprocess.run(
        ["helm", "lint", CHART_DIR],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Helm lint failed: {result.stdout} {result.stderr}"


def test_helm_template_default_values():
    result = subprocess.run(
        ["helm", "template", "test-release", CHART_DIR],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Helm template failed: {result.stderr}"
    assert result.stdout.strip()


def test_helm_lint_strict():
    result = subprocess.run(
        ["helm", "lint", CHART_DIR, "--strict"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Helm lint strict failed: {result.stdout} {result.stderr}"


def test_helm_template_with_values():
    values_path = os.path.join(CHART_DIR, "values.yaml")
    result = subprocess.run(
        ["helm", "template", "test-release", CHART_DIR, "-f", values_path],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    assert result.stdout.strip()


def test_helm_template_kubernetes_executor():
    values = {"executor": "KubernetesExecutor"}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(values, f)
        values_file = f.name
    try:
        result = subprocess.run(
            ["helm", "template", "test-release", CHART_DIR, "-f", values_file],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0
    finally:
        os.unlink(values_file)


def test_helm_template_celery_executor():
    values = {"executor": "CeleryExecutor"}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(values, f)
        values_file = f.name
    try:
        result = subprocess.run(
            ["helm", "template", "test-release", CHART_DIR, "-f", values_file],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0
    finally:
        os.unlink(values_file)


def test_values_yaml_schema_validation():
    try:
        import jsonschema
    except ImportError:
        subprocess.run(["pip", "install", "-q", "jsonschema"], check=True)
        import jsonschema
    values_path = os.path.join(CHART_DIR, "values.yaml")
    with open(values_path) as f:
        values = yaml.safe_load(f)
    schema_path = os.path.join(CHART_DIR, "values.schema.json")
    with open(schema_path) as f:
        schema = json.load(f)
    try:
        jsonschema.validate(instance=values, schema=schema)
    except jsonschema.ValidationError as e:
        pytest.fail(f"Schema validation failed: {e.message}")


def test_chart_yaml_valid():
    chart_yaml_path = os.path.join(CHART_DIR, "Chart.yaml")
    with open(chart_yaml_path) as f:
        chart_yaml = yaml.safe_load(f)
    assert "apiVersion" in chart_yaml
    assert "name" in chart_yaml
    assert "version" in chart_yaml
    assert chart_yaml["apiVersion"] == "v2"
    assert chart_yaml["name"] == "airflow"


HELM_TESTS_DIR = os.path.join(REPO, "helm-tests")


def install_test_deps():
    subprocess.run(
        ["pip", "install", "-q", "jsonschema", "jmespath"],
        capture_output=True,
        check=True,
    )


def test_repo_chart_quality_schema_validation():
    install_test_deps()
    result = subprocess.run(
        [
            "python", "-m", "pytest",
            "tests/helm_tests/airflow_aux/test_chart_quality.py::TestChartQuality::test_values_validate_schema",
            "-xvs",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=HELM_TESTS_DIR,
    )
    assert result.returncode == 0, f"Failed: {result.stdout} {result.stderr}"


def test_repo_worker_affinity():
    install_test_deps()
    result = subprocess.run(
        [
            "python", "-m", "pytest",
            "tests/helm_tests/airflow_core/test_worker.py::TestWorker::test_affinity",
            "-xvs",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=HELM_TESTS_DIR,
    )
    assert result.returncode == 0, f"Failed: {result.stdout} {result.stderr}"


def test_repo_worker_default_affinity():
    install_test_deps()
    result = subprocess.run(
        [
            "python", "-m", "pytest",
            "tests/helm_tests/airflow_core/test_worker.py::TestWorker::test_should_create_default_affinity",
            "-xvs",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=HELM_TESTS_DIR,
    )
    assert result.returncode == 0, f"Failed: {result.stdout} {result.stderr}"


def test_repo_pod_template_workers_affinity():
    install_test_deps()
    result = subprocess.run(
        [
            "python", "-m", "pytest",
            "tests/helm_tests/airflow_aux/test_pod_template_file.py::TestPodTemplateFile::test_workers_affinity",
            "-xvs",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=HELM_TESTS_DIR,
    )
    assert result.returncode == 0, f"Failed: {result.stdout} {result.stderr}"


def test_repo_pod_template_global_affinity():
    install_test_deps()
    result = subprocess.run(
        [
            "python", "-m", "pytest",
            "tests/helm_tests/airflow_aux/test_pod_template_file.py::TestPodTemplateFile::test_global_affinity",
            "-xvs",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=HELM_TESTS_DIR,
    )
    assert result.returncode == 0, f"Failed: {result.stdout} {result.stderr}"


def test_repo_pod_template_affinity_overwrite():
    install_test_deps()
    result = subprocess.run(
        [
            "python", "-m", "pytest",
            "tests/helm_tests/airflow_aux/test_pod_template_file.py::TestPodTemplateFile::test_affinity_overwrite",
            "-xvs",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=HELM_TESTS_DIR,
    )
    assert result.returncode == 0, f"Failed: {result.stdout} {result.stderr}"


def test_repo_worker_affinity_overwrite():
    install_test_deps()
    result = subprocess.run(
        [
            "python", "-m", "pytest",
            "tests/helm_tests/airflow_core/test_worker.py::TestWorker::test_affinity_overwrite",
            "-xvs",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=HELM_TESTS_DIR,
    )
    assert result.returncode == 0, f"Failed: {result.stdout} {result.stderr}"