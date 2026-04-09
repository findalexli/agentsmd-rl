"""Test outputs for Airflow Helm chart workers.celery.hpa feature."""

import subprocess
import sys
import jmespath
import pytest
import yaml

REPO = "/workspace/airflow"
CHART_PATH = f"{REPO}/chart"


def render_chart(values, show_only=None):
    """Render Helm chart with given values and return parsed documents."""
    cmd = ["helm", "template", "release-name", CHART_PATH, "--values", "-"]
    if show_only:
        for path in show_only:
            cmd.extend(["--show-only", path])

    proc = subprocess.run(
        cmd,
        input=yaml.dump({"values": values}),
        capture_output=True,
        text=True,
        timeout=60,
    )

    if proc.returncode != 0:
        raise RuntimeError(f"Helm template failed: {proc.stderr}")

    # Parse multi-document YAML output
    docs = list(yaml.safe_load_all(proc.stdout))
    return [d for d in docs if d is not None]


# =============================================================================
# FAIL-TO-PASS TESTS - These should fail on base commit, pass with fix
# =============================================================================


@pytest.mark.parametrize("executor", ["CeleryExecutor", "CeleryKubernetesExecutor"])
def test_new_celery_hpa_config_path_exists(executor):
    """F2P: workers.celery.hpa.enabled should create HPA resource."""
    docs = render_chart(
        values={
            "executor": executor,
            "workers": {"celery": {"hpa": {"enabled": True}}},
        },
        show_only=["templates/workers/worker-hpa.yaml"],
    )

    assert len(docs) >= 1, "HPA should be created with workers.celery.hpa.enabled"
    assert jmespath.search("kind", docs[0]) == "HorizontalPodAutoscaler"


@pytest.mark.parametrize("executor", ["CeleryExecutor", "CeleryKubernetesExecutor"])
def test_celery_hpa_min_max_replicas(executor):
    """F2P: workers.celery.hpa.min/maxReplicaCount should configure replicas."""
    docs = render_chart(
        values={
            "executor": executor,
            "workers": {
                "celery": {
                    "hpa": {
                        "enabled": True,
                        "minReplicaCount": 2,
                        "maxReplicaCount": 10,
                    }
                }
            },
        },
        show_only=["templates/workers/worker-hpa.yaml"],
    )

    assert len(docs) >= 1, "HPA should be created"
    assert jmespath.search("spec.minReplicas", docs[0]) == 2
    assert jmespath.search("spec.maxReplicas", docs[0]) == 10


@pytest.mark.parametrize("executor", ["CeleryExecutor", "CeleryKubernetesExecutor"])
def test_celery_hpa_custom_metrics(executor):
    """F2P: workers.celery.hpa.metrics should configure custom metrics."""
    docs = render_chart(
        values={
            "executor": executor,
            "workers": {
                "celery": {
                    "hpa": {
                        "enabled": True,
                        "metrics": [
                            {
                                "type": "Resource",
                                "resource": {
                                    "name": "memory",
                                    "target": {"type": "Utilization", "averageUtilization": 75},
                                },
                            }
                        ],
                    }
                }
            },
        },
        show_only=["templates/workers/worker-hpa.yaml"],
    )

    assert len(docs) >= 1, "HPA should be created"
    metrics = jmespath.search("spec.metrics", docs[0])
    assert metrics is not None
    assert len(metrics) == 1
    assert metrics[0]["type"] == "Resource"
    assert metrics[0]["resource"]["name"] == "memory"


@pytest.mark.parametrize("executor", ["CeleryExecutor", "CeleryKubernetesExecutor"])
def test_celery_hpa_default_metrics(executor):
    """F2P: workers.celery.hpa with default metrics (CPU 80%)."""
    docs = render_chart(
        values={
            "executor": executor,
            "workers": {"celery": {"hpa": {"enabled": True}}},
        },
        show_only=["templates/workers/worker-hpa.yaml"],
    )

    assert len(docs) >= 1, "HPA should be created"
    metrics = jmespath.search("spec.metrics", docs[0])
    assert metrics == [
        {
            "type": "Resource",
            "resource": {"name": "cpu", "target": {"type": "Utilization", "averageUtilization": 80}},
        }
    ]


def test_celery_hpa_behavior_config():
    """F2P: workers.celery.hpa.behavior should configure scaling behavior."""
    expected_behavior = {
        "scaleDown": {
            "stabilizationWindowSeconds": 300,
            "policies": [{"type": "Percent", "value": 100, "periodSeconds": 15}],
        }
    }
    docs = render_chart(
        values={
            "executor": "CeleryExecutor",
            "workers": {
                "celery": {
                    "hpa": {
                        "enabled": True,
                        "behavior": expected_behavior,
                    }
                }
            },
        },
        show_only=["templates/workers/worker-hpa.yaml"],
    )

    assert len(docs) >= 1, "HPA should be created"
    assert jmespath.search("spec.behavior", docs[0]) == expected_behavior


def test_worker_sets_celery_hpa_override():
    """F2P: Worker sets should support celery.hpa configuration override."""
    docs = render_chart(
        values={
            "workers": {
                "celery": {
                    "enableDefault": False,
                    "sets": [{"name": "test", "hpa": {"enabled": True, "minReplicaCount": 15}}],
                }
            },
        },
        show_only=["templates/workers/worker-hpa.yaml"],
    )

    assert len(docs) == 1, "HPA should be created for worker set"
    assert jmespath.search("spec.minReplicas", docs[0]) == 15


# =============================================================================
# PASS-TO-PASS TESTS - These test existing repo tests that should always pass
# =============================================================================


def test_old_hpa_path_still_works():
    """P2P: Old workers.hpa.enabled should still create HPA (backward compatibility)."""
    docs = render_chart(
        values={
            "executor": "CeleryExecutor",
            "workers": {"hpa": {"enabled": True}},
        },
        show_only=["templates/workers/worker-hpa.yaml"],
    )

    assert len(docs) >= 1, "HPA should be created with old workers.hpa.enabled"
    assert jmespath.search("kind", docs[0]) == "HorizontalPodAutoscaler"


def test_hpa_disabled_by_default():
    """P2P: HPA should be disabled by default (no docs rendered)."""
    docs = render_chart(
        values={},
        show_only=["templates/workers/worker-hpa.yaml"],
    )

    assert len(docs) == 0, "HPA should not be created by default"


def test_hpa_not_created_for_non_celery_executor():
    """P2P: HPA should not be created for non-Celery executors."""
    docs = render_chart(
        values={
            "executor": "KubernetesExecutor",
            "workers": {"celery": {"hpa": {"enabled": True}}},
        },
        show_only=["templates/workers/worker-hpa.yaml"],
    )

    assert len(docs) == 0, "HPA should not be created for KubernetesExecutor"


@pytest.mark.parametrize(
    "persistence_config,expected_kind",
    [
        ({"celery": {"hpa": {"enabled": True}, "persistence": {"enabled": True}}}, "StatefulSet"),
        ({"celery": {"hpa": {"enabled": True}, "persistence": {"enabled": False}}}, "Deployment"),
    ],
)
def test_hpa_scale_target_ref(persistence_config, expected_kind):
    """P2P: HPA scaleTargetRef should match persistence config."""
    docs = render_chart(
        values={
            "executor": "CeleryExecutor",
            "workers": persistence_config,
        },
        show_only=["templates/workers/worker-hpa.yaml"],
    )

    assert len(docs) >= 1, "HPA should be created"
    target_kind = jmespath.search("spec.scaleTargetRef.kind", docs[0])
    assert target_kind == expected_kind


def test_celery_hpa_disabled_when_keda_enabled():
    """P2P: HPA should not be created when KEDA is enabled."""
    docs = render_chart(
        values={
            "executor": "CeleryExecutor",
            "workers": {
                "celery": {"keda": {"enabled": True}, "hpa": {"enabled": True}},
            },
        },
        show_only=[
            "templates/workers/worker-kedaautoscaler.yaml",
            "templates/workers/worker-hpa.yaml",
        ],
    )

    # Should only have KEDA autoscaler, not HPA
    assert len(docs) == 1
    assert jmespath.search("kind", docs[0]) == "ScaledObject"


# =============================================================================
# PASS-TO-PASS TESTS - Repo CI/CD Tests (should always pass on base and after fix)
# =============================================================================


def _install_helm_test_deps():
    """Install dependencies needed for helm tests."""
    subprocess.run(
        ["pip", "install", "jsonschema", "kubernetes", "-q"],
        capture_output=True,
        check=False,
    )


def test_repo_helm_hpa_tests():
    """Repo's Helm HPA tests pass (pass_to_pass)."""
    _install_helm_test_deps()
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "helm-tests/tests/helm_tests/other/test_hpa.py",
            "-v", "--tb=short"
        ],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
        env={**subprocess.os.environ, "PYTHONPATH": f"{REPO}/helm-tests/tests"},
    )
    assert r.returncode == 0, f"Helm HPA tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"


def test_repo_helm_worker_hpa_tests():
    """Repo's Helm Worker HPA autoscale tests pass (pass_to_pass)."""
    _install_helm_test_deps()
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "helm-tests/tests/helm_tests/airflow_core/test_worker.py::TestWorkerHPAAutoScaler",
            "-v", "--tb=short"
        ],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
        env={**subprocess.os.environ, "PYTHONPATH": f"{REPO}/helm-tests/tests"},
    )
    assert r.returncode == 0, f"Helm Worker HPA tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"


def test_repo_helm_worker_sets_hpa_tests():
    """Repo's Helm Worker Sets HPA tests pass (pass_to_pass)."""
    _install_helm_test_deps()
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py",
            "-k", "hpa",
            "-v", "--tb=short"
        ],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
        env={**subprocess.os.environ, "PYTHONPATH": f"{REPO}/helm-tests/tests"},
    )
    assert r.returncode == 0, f"Helm Worker Sets HPA tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"


def test_repo_helm_chart_quality():
    """Repo's Helm chart quality test passes (pass_to_pass)."""
    _install_helm_test_deps()
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "helm-tests/tests/helm_tests/airflow_aux/test_chart_quality.py",
            "-v", "--tb=short"
        ],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
        env={**subprocess.os.environ, "PYTHONPATH": f"{REPO}/helm-tests/tests"},
    )
    assert r.returncode == 0, f"Helm chart quality test failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"


# =============================================================================
# SCHEMA VALIDATION TESTS
# =============================================================================


def test_values_schema_has_celery_hpa_section():
    """F2P: values.schema.json should contain workers.celery.hpa definition."""
    with open(f"{CHART_PATH}/values.schema.json") as f:
        schema = json.load(f)

    # Navigate to workers.celery.hpa in schema
    celery_props = jmespath.search(
        "properties.workers.properties.celery.properties.hpa", schema
    )
    assert celery_props is not None, "Schema should define workers.celery.hpa"
    assert "properties" in celery_props
    assert "enabled" in celery_props["properties"]
    assert "minReplicaCount" in celery_props["properties"]
    assert "maxReplicaCount" in celery_props["properties"]
    assert "metrics" in celery_props["properties"]
    assert "behavior" in celery_props["properties"]


def test_old_hpa_schema_has_deprecation_note():
    """P2P: Old workers.hpa schema should have deprecation description."""
    with open(f"{CHART_PATH}/values.schema.json") as f:
        schema = json.load(f)

    hpa_desc = jmespath.search(
        "properties.workers.properties.hpa.description", schema
    )
    assert "deprecated" in hpa_desc.lower(), "Old hpa should have deprecation note"


# Need to import json here
import json


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
