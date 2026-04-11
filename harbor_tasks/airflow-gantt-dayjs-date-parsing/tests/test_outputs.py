#!/usr/bin/env python3
"""Test outputs for Airflow Helm Chart extraInitContainers changes.

This module tests the Helm chart rendering for:
- workers.celery.extraInitContainers
- workers.kubernetes.extraInitContainers

The tests verify that the pod template file and worker deployments
correctly include extra init containers as configured.
"""

import subprocess
import sys
from pathlib import Path

# REPO path inside Docker container
REPO = "/workspace/airflow"


def test_helm_tests_pod_template_extra_init_containers():
    """Helm test: pod template file supports extraInitContainers (pass_to_pass).

    Tests that workers.kubernetes.extraInitContainers renders correctly
    in the pod template file for KubernetesExecutor.
    """
    # Run with patched helm_template_generator to skip K8s schema validation (requires network)
    test_code = """
import sys
sys.path.insert(0, 'helm-tests/tests')

# Patch the validate_k8s_object function to skip network-based validation
import chart_utils.helm_template_generator as htg
htg.validate_k8s_object = lambda instance, kubernetes_version: None

import pytest
exit(pytest.main([
    'helm-tests/tests/helm_tests/airflow_aux/test_pod_template_file.py::TestPodTemplateFile::test_should_add_extra_init_containers',
    '-v', '--tb=short'
]))
"""
    r = subprocess.run(
        ["python", "-c", test_code],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Pod template extraInitContainers test failed:\n{r.stdout}\n{r.stderr}"


def test_helm_tests_pod_template_extra_init_containers_templating():
    """Helm test: pod template extraInitContainers supports templating (pass_to_pass).

    Tests that extraInitContainers names are properly templated with Helm values.
    """
    test_code = """
import sys
sys.path.insert(0, 'helm-tests/tests')
import chart_utils.helm_template_generator as htg
htg.validate_k8s_object = lambda instance, kubernetes_version: None

import pytest
exit(pytest.main([
    'helm-tests/tests/helm_tests/airflow_aux/test_pod_template_file.py::TestPodTemplateFile::test_should_template_extra_init_containers',
    '-v', '--tb=short'
]))
"""
    r = subprocess.run(
        ["python", "-c", test_code],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Pod template extraInitContainers templating test failed:\n{r.stdout}\n{r.stderr}"


def test_helm_tests_worker_deployment_extra_init_containers():
    """Helm test: worker deployment supports extraInitContainers (pass_to_pass).

    Tests that workers.kubernetes.extraInitContainers and workers.celery.extraInitContainers
    render correctly in the worker deployment template.
    """
    test_code = """
import sys
sys.path.insert(0, 'helm-tests/tests')
import chart_utils.helm_template_generator as htg
htg.validate_k8s_object = lambda instance, kubernetes_version: None

import pytest
exit(pytest.main([
    'helm-tests/tests/helm_tests/airflow_core/test_worker.py::TestWorker::test_should_add_extra_init_containers',
    '-v', '--tb=short'
]))
"""
    r = subprocess.run(
        ["python", "-c", test_code],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Worker deployment extraInitContainers test failed:\n{r.stdout}\n{r.stderr}"


def test_helm_tests_worker_deployment_extra_init_containers_templating():
    """Helm test: worker deployment extraInitContainers supports templating (pass_to_pass).

    Tests that extraInitContainers names are properly templated with Helm values.
    """
    test_code = """
import sys
sys.path.insert(0, 'helm-tests/tests')
import chart_utils.helm_template_generator as htg
htg.validate_k8s_object = lambda instance, kubernetes_version: None

import pytest
exit(pytest.main([
    'helm-tests/tests/helm_tests/airflow_core/test_worker.py::TestWorker::test_should_template_extra_init_containers',
    '-v', '--tb=short'
]))
"""
    r = subprocess.run(
        ["python", "-c", test_code],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Worker deployment extraInitContainers templating test failed:\n{r.stdout}\n{r.stderr}"


def test_helm_tests_worker_sets_deployment_extra_init_containers():
    """Helm test: worker sets deployment supports extraInitContainers (pass_to_pass).

    Tests that workers.celery.sets[].extraInitContainers renders correctly
    for custom worker sets.
    """
    test_code = """
import sys
sys.path.insert(0, 'helm-tests/tests')
import chart_utils.helm_template_generator as htg
htg.validate_k8s_object = lambda instance, kubernetes_version: None

import pytest
exit(pytest.main([
    'helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py::TestWorkerSets::test_overwrite_extra_init_containers',
    '-v', '--tb=short'
]))
"""
    r = subprocess.run(
        ["python", "-c", test_code],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Worker sets extraInitContainers test failed:\n{r.stdout}\n{r.stderr}"


def test_helm_chart_schema_valid():
    """Helm chart: values.schema.json is valid JSON (pass_to_pass).

    Validates that the Helm chart's JSON schema is syntactically valid.
    """
    r = subprocess.run(
        [
            "python", "-c",
            "import json; json.load(open('chart/values.schema.json'))"
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Helm chart schema validation failed:\n{r.stderr}"


def test_helm_chart_render_basic():
    """Helm chart: basic rendering works (pass_to_pass).

    Validates that the Helm chart can be rendered without errors.
    """
    r = subprocess.run(
        [
            "helm", "template", "test-release", "chart",
            "--namespace", "default"
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Helm chart basic rendering failed:\n{r.stderr}"


if __name__ == "__main__":
    import subprocess
    import sys

    # Run all tests
    tests = [
        test_helm_tests_pod_template_extra_init_containers,
        test_helm_tests_pod_template_extra_init_containers_templating,
        test_helm_tests_worker_deployment_extra_init_containers,
        test_helm_tests_worker_deployment_extra_init_containers_templating,
        test_helm_tests_worker_sets_deployment_extra_init_containers,
        test_helm_chart_schema_valid,
        test_helm_chart_render_basic,
    ]

    failed = []
    passed = []

    for test in tests:
        try:
            test()
            passed.append(test.__name__)
            print(f"PASS: {test.__name__}")
        except AssertionError as e:
            failed.append((test.__name__, str(e)))
            print(f"FAIL: {test.__name__}: {e}")
        except Exception as e:
            failed.append((test.__name__, str(e)))
            print(f"ERROR: {test.__name__}: {e}")

    # Write reward
    reward_path = Path("/logs/verifier/reward.txt")
    reward_path.parent.mkdir(parents=True, exist_ok=True)
    if failed:
        reward_path.write_text("0")
        sys.exit(1)
    else:
        reward_path.write_text("1")
        sys.exit(0)
