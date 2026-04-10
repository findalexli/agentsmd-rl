#!/usr/bin/env python3
"""
Test outputs for Airflow Helm chart extraContainers refactoring.
"""

import json
import subprocess
from pathlib import Path

import jmespath
import pytest
import yaml

REPO = Path("/workspace/airflow")
CHART_DIR = REPO / "chart"
HELM_TESTS_DIR = REPO / "helm-tests"


def render_chart(values, show_only, chart_dir=None):
    if chart_dir is None:
        chart_dir = CHART_DIR
    show_args = []
    for path in show_only:
        show_args.extend(["-s", path])
    import tempfile
    import os as os_module
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(values, f)
        values_file = f.name
    try:
        cmd = ["helm", "template", "test-release", str(chart_dir), "--namespace", "default", "-f", values_file] + show_args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            raise RuntimeError(f"helm template failed: {result.stderr}")
        docs = list(yaml.safe_load_all(result.stdout))
        return [d for d in docs if d is not None]
    finally:
        os_module.unlink(values_file)


def get_pod_template_containers(docs):
    assert len(docs) > 0, "No documents rendered"
    configmap = docs[0]
    pod_template_yaml = configmap.get("data", {}).get("pod_template_file.yaml", "")
    assert pod_template_yaml, "pod_template_file.yaml not found in ConfigMap"
    pod_template = yaml.safe_load(pod_template_yaml)
    containers = pod_template.get("spec", {}).get("containers", [])
    return containers[1:] if len(containers) > 1 else []


class TestKubernetesExtraContainers:
    def test_k8s_new_path(self):
        docs = render_chart(
            values={"executor": "KubernetesExecutor", "workers": {"kubernetes": {"extraContainers": [{"name": "sidecar", "image": "test:1.0"}]}}},
            show_only=["templates/configmaps/configmap.yaml"],
        )
        containers = get_pod_template_containers(docs)
        assert containers == [{"name": "sidecar", "image": "test:1.0"}]

    def test_deprecated_still_works(self):
        docs = render_chart(
            values={"executor": "KubernetesExecutor", "workers": {"extraContainers": [{"name": "legacy", "image": "legacy:1.0"}]}},
            show_only=["templates/configmaps/configmap.yaml"],
        )
        containers = get_pod_template_containers(docs)
        assert containers == [{"name": "legacy", "image": "legacy:1.0"}]

    def test_new_takes_precedence(self):
        docs = render_chart(
            values={"executor": "KubernetesExecutor", "workers": {"extraContainers": [{"name": "old", "image": "old:1.0"}], "kubernetes": {"extraContainers": [{"name": "new", "image": "new:1.0"}]}}},
            show_only=["templates/configmaps/configmap.yaml"],
        )
        containers = get_pod_template_containers(docs)
        assert containers == [{"name": "new", "image": "new:1.0"}]


class TestCeleryExtraContainers:
    def test_celery_new_path(self):
        docs = render_chart(
            values={"executor": "CeleryExecutor", "workers": {"celery": {"extraContainers": [{"name": "celery-sidecar", "image": "celery:1.0"}]}}},
            show_only=["templates/workers/worker-deployment.yaml"],
        )
        containers = jmespath.search("spec.template.spec.containers[2:]", docs[0])
        assert containers == [{"name": "celery-sidecar", "image": "celery:1.0"}]

    def test_deprecated_celery_works(self):
        docs = render_chart(
            values={"executor": "CeleryExecutor", "workers": {"extraContainers": [{"name": "legacy", "image": "legacy:1.0"}]}},
            show_only=["templates/workers/worker-deployment.yaml"],
        )
        containers = jmespath.search("spec.template.spec.containers[2:]", docs[0])
        assert containers == [{"name": "legacy", "image": "legacy:1.0"}]

    def test_celery_new_takes_precedence(self):
        docs = render_chart(
            values={"executor": "CeleryExecutor", "workers": {"extraContainers": [{"name": "old", "image": "old:1.0"}], "celery": {"extraContainers": [{"name": "new", "image": "new:1.0"}]}}},
            show_only=["templates/workers/worker-deployment.yaml"],
        )
        containers = jmespath.search("spec.template.spec.containers[2:]", docs[0])
        assert containers == [{"name": "new", "image": "new:1.0"}]


class TestValuesSchema:
    def test_celery_extra_containers_in_schema(self):
        schema_path = CHART_DIR / "values.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)
        celery_props = schema.get("properties", {}).get("workers", {}).get("properties", {}).get("celery", {}).get("properties", {})
        assert "extraContainers" in celery_props
        assert celery_props["extraContainers"].get("type") == "array"

    def test_kubernetes_extra_containers_in_schema(self):
        schema_path = CHART_DIR / "values.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)
        k8s_props = schema.get("properties", {}).get("workers", {}).get("properties", {}).get("kubernetes", {}).get("properties", {})
        assert "extraContainers" in k8s_props
        assert k8s_props["extraContainers"].get("type") == "array"

    def test_deprecated_description_updated(self):
        schema_path = CHART_DIR / "values.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)
        workers_props = schema.get("properties", {}).get("workers", {}).get("properties", {})
        desc = workers_props.get("extraContainers", {}).get("description", "")
        assert "deprecated" in desc.lower()


class TestValuesYaml:
    def test_celery_extra_containers_default_empty(self):
        values_path = CHART_DIR / "values.yaml"
        with open(values_path) as f:
            values = yaml.safe_load(f)
        celery_extra = values.get("workers", {}).get("celery", {}).get("extraContainers", "NOT_FOUND")
        assert celery_extra == []

    def test_kubernetes_extra_containers_default_empty(self):
        values_path = CHART_DIR / "values.yaml"
        with open(values_path) as f:
            values = yaml.safe_load(f)
        k8s_extra = values.get("workers", {}).get("kubernetes", {}).get("extraContainers", "NOT_FOUND")
        assert k8s_extra == []




class TestRepoHelmTests:
    '''Pass-to-pass tests that run the repo's actual Helm tests.

    These tests run a curated subset of the Airflow repo's helm tests that cover
    the modified code paths (extraContainers for workers). They validate that
    the existing tests pass on the base commit (pre-fix state).
    '''

    def _setup_helm_tests(self):
        '''Ensure repo exists at expected location and setup Python path.'''
        assert REPO.exists(), f'Repo not found at {REPO}. Ensure repo is mounted.'
        assert HELM_TESTS_DIR.exists(), f'Helm tests not found at {HELM_TESTS_DIR}'
        # Install required dependencies for helm tests
        subprocess.run(
            ['pip', 'install', '-q', 'jmespath', 'jsonschema', 'pyyaml'],
            capture_output=True, timeout=60, check=False
        )

    def test_repo_helm_pod_template_tests(self):
        '''Run repo's pod-template-file tests for extraContainers (pass_to_pass).'''
        self._setup_helm_tests()
        env = {
            'PYTHONPATH': f'{HELM_TESTS_DIR}/tests:{HELM_TESTS_DIR}/tests/chart_utils',
            'HELM_TEST_KUBERNETES_VERSION': '1.30.13',
            'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
        }
        r = subprocess.run(
            [
                '/usr/local/bin/python3', '-m', 'pytest',
                'tests/helm_tests/airflow_aux/test_pod_template_file.py',
                '-v', '-k', 'extra_containers',
                '--tb=short'
            ],
            capture_output=True, text=True, timeout=120, cwd=HELM_TESTS_DIR, env=env
        )
        assert r.returncode == 0, f'Pod template tests failed: {r.stderr[-1000:]}'

    def test_repo_helm_worker_tests(self):
        '''Run repo's worker tests for extraContainers (pass_to_pass).'''
        self._setup_helm_tests()
        env = {
            'PYTHONPATH': f'{HELM_TESTS_DIR}/tests:{HELM_TESTS_DIR}/tests/chart_utils',
            'HELM_TEST_KUBERNETES_VERSION': '1.30.13',
            'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
        }
        r = subprocess.run(
            [
                '/usr/local/bin/python3', '-m', 'pytest',
                'tests/helm_tests/airflow_core/test_worker.py',
                '-v', '-k', 'extra_containers',
                '--tb=short'
            ],
            capture_output=True, text=True, timeout=120, cwd=HELM_TESTS_DIR, env=env
        )
        assert r.returncode == 0, f'Worker tests failed: {r.stderr[-1000:]}'

    def test_repo_helm_worker_sets_tests(self):
        '''Run repo's worker sets tests for extraContainers (pass_to_pass).'''
        self._setup_helm_tests()
        env = {
            'PYTHONPATH': f'{HELM_TESTS_DIR}/tests:{HELM_TESTS_DIR}/tests/chart_utils',
            'HELM_TEST_KUBERNETES_VERSION': '1.30.13',
            'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
        }
        r = subprocess.run(
            [
                '/usr/local/bin/python3', '-m', 'pytest',
                'tests/helm_tests/airflow_core/test_worker_sets.py',
                '-v', '-k', 'extra_containers',
                '--tb=short'
            ],
            capture_output=True, text=True, timeout=120, cwd=HELM_TESTS_DIR, env=env
        )
        assert r.returncode == 0, f'Worker sets tests failed: {r.stderr[-1000:]}'

    def test_repo_helm_lint(self):
        '''Helm lint passes on the chart (pass_to_pass).'''
        assert REPO.exists(), f'Repo not found at {REPO}'
        r = subprocess.run(
            ['helm', 'lint', '.'],
            capture_output=True, text=True, timeout=60, cwd=CHART_DIR
        )
        assert r.returncode == 0, f'Helm lint failed: {r.stderr[-500:]}'

    def test_repo_helm_template_basic(self):
        '''Helm template renders successfully with default values (pass_to_pass).'''
        assert REPO.exists(), f'Repo not found at {REPO}'
        r = subprocess.run(
            ['helm', 'template', 'test-release', '.', '--namespace', 'default'],
            capture_output=True, text=True, timeout=60, cwd=CHART_DIR
        )
        assert r.returncode == 0, f'Helm template failed: {r.stderr[-500:]}'

    def test_repo_values_schema_valid_json(self):
        '''values.schema.json is valid JSON (pass_to_pass).'''
        schema_path = CHART_DIR / 'values.schema.json'
        assert schema_path.exists(), f'Schema file not found at {schema_path}'
        r = subprocess.run(
            ['python', '-c', f'import json; json.load(open("{schema_path}")); print("OK")'],
            capture_output=True, text=True, timeout=30
        )
        assert r.returncode == 0 and 'OK' in r.stdout, f'Schema validation failed: {r.stderr}'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
