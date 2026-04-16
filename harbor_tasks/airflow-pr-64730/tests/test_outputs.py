"""
Tests for apache/airflow#64730: Add workers.celery.serviceAccount & workers.kubernetes.serviceAccount

These tests verify the new executor-specific service account configuration options.
"""

import subprocess
import yaml
import os
import pytest

REPO = "/workspace/airflow"
CHART_PATH = os.path.join(REPO, "chart")


def helm_template(set_values: list[str] = None, release_name: str = "test") -> list[dict]:
    """Render helm chart and return parsed YAML documents."""
    cmd = ["helm", "template", release_name, CHART_PATH]
    if set_values:
        for val in set_values:
            cmd.extend(["--set", val])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"helm template failed: {result.stderr}")

    # Parse all YAML documents
    docs = []
    for doc in yaml.safe_load_all(result.stdout):
        if doc:
            docs.append(doc)
    return docs


def find_resource(docs: list[dict], kind: str, name: str) -> dict | None:
    """Find a Kubernetes resource by kind and name."""
    for doc in docs:
        if doc.get("kind") == kind and doc.get("metadata", {}).get("name") == name:
            return doc
    return None


def find_resources_by_kind(docs: list[dict], kind: str) -> list[dict]:
    """Find all resources of a given kind."""
    return [doc for doc in docs if doc.get("kind") == kind]


class TestKubernetesWorkerServiceAccount:
    """Tests for workers.kubernetes.serviceAccount configuration (fail_to_pass)."""

    def test_kubernetes_service_account_create(self):
        """
        When workers.kubernetes.serviceAccount.create is true with KubernetesExecutor,
        a separate kubernetes worker service account should be created.

        This is a fail_to_pass test - before the PR, this configuration option
        does not exist and no separate kubernetes worker service account is created.
        """
        docs = helm_template([
            "executor=KubernetesExecutor",
            "workers.kubernetes.serviceAccount.create=true",
            "workers.kubernetes.serviceAccount.name=k8s-worker-sa",
        ])

        # Find the kubernetes worker service account
        sa = find_resource(docs, "ServiceAccount", "k8s-worker-sa")
        assert sa is not None, "Kubernetes worker ServiceAccount should be created"

        # Verify it has worker component label
        labels = sa.get("metadata", {}).get("labels", {})
        assert labels.get("component") == "worker", "Should have component=worker label"

    def test_kubernetes_service_account_annotations(self):
        """
        workers.kubernetes.serviceAccount.annotations should be applied to the
        kubernetes worker service account.
        """
        docs = helm_template([
            "executor=KubernetesExecutor",
            "workers.kubernetes.serviceAccount.create=true",
            "workers.kubernetes.serviceAccount.annotations.iam\\.amazonaws\\.com/role=arn:aws:iam::123456:role/test",
        ])

        # Find any service accounts with worker component
        service_accounts = find_resources_by_kind(docs, "ServiceAccount")
        worker_sas = [sa for sa in service_accounts
                      if sa.get("metadata", {}).get("labels", {}).get("component") == "worker"]

        # At least one should have the annotation
        found_annotation = False
        for sa in worker_sas:
            annotations = sa.get("metadata", {}).get("annotations", {})
            if annotations.get("iam.amazonaws.com/role") == "arn:aws:iam::123456:role/test":
                found_annotation = True
                break

        assert found_annotation, "Kubernetes worker SA should have custom annotation"

    def test_kubernetes_service_account_automount_token(self):
        """
        workers.kubernetes.serviceAccount.automountServiceAccountToken should control
        token mounting on the kubernetes worker service account.
        """
        # Test with automount disabled
        docs = helm_template([
            "executor=KubernetesExecutor",
            "workers.kubernetes.serviceAccount.create=true",
            "workers.kubernetes.serviceAccount.automountServiceAccountToken=false",
        ])

        service_accounts = find_resources_by_kind(docs, "ServiceAccount")
        worker_sas = [sa for sa in service_accounts
                      if sa.get("metadata", {}).get("labels", {}).get("component") == "worker"]

        # Find one with automount disabled
        found = False
        for sa in worker_sas:
            if sa.get("automountServiceAccountToken") == False:
                found = True
                break

        assert found, "Should find worker SA with automountServiceAccountToken=false"


class TestSeparateServiceAccounts:
    """Tests for separate Celery and Kubernetes service accounts (fail_to_pass)."""

    def test_separate_celery_and_kubernetes_service_accounts(self):
        """
        With CeleryKubernetesExecutor, should be able to create DIFFERENT service
        accounts for Celery workers vs Kubernetes executor pods.

        This is the key new feature - before the PR, there was only one shared
        workers.serviceAccount. After the PR, you can have separate ones.
        """
        docs = helm_template([
            "executor=CeleryKubernetesExecutor",
            "workers.celery.serviceAccount.create=true",
            "workers.celery.serviceAccount.name=celery-worker-sa",
            "workers.kubernetes.serviceAccount.create=true",
            "workers.kubernetes.serviceAccount.name=k8s-worker-sa",
        ])

        # Find both service accounts
        celery_sa = find_resource(docs, "ServiceAccount", "celery-worker-sa")
        k8s_sa = find_resource(docs, "ServiceAccount", "k8s-worker-sa")

        assert celery_sa is not None, "Celery worker ServiceAccount should be created"
        assert k8s_sa is not None, "Kubernetes worker ServiceAccount should be created"

        # They should be different service accounts
        assert celery_sa.get("metadata", {}).get("name") != k8s_sa.get("metadata", {}).get("name"), \
            "Celery and Kubernetes worker service accounts should be different"


class TestCeleryWorkerServiceAccount:
    """Tests for workers.celery.serviceAccount configuration (pass_to_pass)."""

    def test_celery_service_account_name(self):
        """
        workers.celery.serviceAccount.name should set the service account name
        for celery workers (this works via merge on base commit).
        """
        docs = helm_template([
            "executor=CeleryExecutor",
            "workers.celery.serviceAccount.create=true",
            "workers.celery.serviceAccount.name=celery-worker-sa",
        ])

        # Find the celery worker service account
        sa = find_resource(docs, "ServiceAccount", "celery-worker-sa")
        assert sa is not None, "Celery worker ServiceAccount should be created with custom name"

    def test_celery_service_account_annotations(self):
        """
        workers.celery.serviceAccount.annotations should be applied to celery
        worker service account.
        """
        docs = helm_template([
            "executor=CeleryExecutor",
            "workers.celery.serviceAccount.create=true",
            "workers.celery.serviceAccount.annotations.custom-key=custom-value",
        ])

        service_accounts = find_resources_by_kind(docs, "ServiceAccount")

        # Find service account with custom annotation
        found = False
        for sa in service_accounts:
            annotations = sa.get("metadata", {}).get("annotations", {})
            if annotations.get("custom-key") == "custom-value":
                found = True
                break

        assert found, "Should find ServiceAccount with celery custom annotation"


class TestLegacyServiceAccount:
    """Tests for backward compatibility with workers.serviceAccount (pass_to_pass)."""

    def test_legacy_workers_service_account_still_works(self):
        """
        The legacy workers.serviceAccount configuration should still work
        for backward compatibility.
        """
        docs = helm_template([
            "executor=CeleryExecutor",
            "workers.serviceAccount.create=true",
            "workers.serviceAccount.name=legacy-worker-sa",
        ])

        # Find the worker service account
        sa = find_resource(docs, "ServiceAccount", "legacy-worker-sa")
        assert sa is not None, "Legacy workers.serviceAccount should still create SA"


class TestHelmTemplateBasics:
    """Basic helm template tests (pass_to_pass)."""

    def test_helm_template_renders(self):
        """Helm template should render without errors."""
        docs = helm_template()
        assert len(docs) > 0, "Should produce at least one resource"

    def test_helm_template_with_celery_executor(self):
        """Helm template with CeleryExecutor should render."""
        docs = helm_template(["executor=CeleryExecutor"])
        assert len(docs) > 0, "Should produce resources with CeleryExecutor"

    def test_helm_template_with_kubernetes_executor(self):
        """Helm template with KubernetesExecutor should render."""
        docs = helm_template(["executor=KubernetesExecutor"])
        assert len(docs) > 0, "Should produce resources with KubernetesExecutor"


class TestRepoCIChecks:
    """Tests that run actual repo CI commands (pass_to_pass)."""

    def test_helm_lint(self):
        """Helm lint passes on the chart (pass_to_pass)."""
        r = subprocess.run(
            ["helm", "lint", "chart/"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Helm lint failed:\n{r.stderr[-500:]}"

    def test_chart_schema_validation(self):
        """Chart schema validation passes (pass_to_pass)."""
        r = subprocess.run(
            ["python", "scripts/ci/prek/chart_schema.py"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Chart schema validation failed:\n{r.stderr[-500:]}"

    def test_helm_template_celery_kubernetes_executor(self):
        """Helm template with CeleryKubernetesExecutor renders (pass_to_pass)."""
        r = subprocess.run(
            ["helm", "template", "test", "chart/", "--set", "executor=CeleryKubernetesExecutor"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Helm template failed:\n{r.stderr[-500:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
