"""
Tests for apache/airflow#64871: Add workers.celery.hpa configuration to Helm chart

This PR adds:
1. Schema definition for workers.celery.hpa in values.schema.json
2. Deprecation warnings in NOTES.txt when using workers.hpa.*
3. Documentation in values.yaml for the new config path

The HPA merge logic (workers.celery overriding workers) already exists.
"""

import json
import subprocess
import tempfile
import os
import yaml
import re

REPO = "/workspace/airflow"
CHART_PATH = os.path.join(REPO, "chart")


def run_helm_template(values: dict = None, show_only: str = None, extra_args: list = None) -> tuple:
    """Render Helm template with optional values override."""
    cmd = ["helm", "template", "test-release", CHART_PATH]

    if values:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(values, f)
            values_file = f.name
        cmd.extend(["-f", values_file])

    if show_only:
        cmd.extend(["--show-only", show_only])

    if extra_args:
        cmd.extend(extra_args)

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=CHART_PATH)

    if values:
        os.unlink(values_file)

    return result.stdout, result.stderr, result.returncode


def run_helm_install_dry_run(values: dict = None, name: str = "test-release") -> tuple:
    """Run helm install --dry-run to trigger NOTES.txt output."""
    cmd = [
        "helm", "install", name, CHART_PATH,
        "--dry-run",
        "--no-hooks"
    ]

    if values:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(values, f)
            values_file = f.name
        cmd.extend(["-f", values_file])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=CHART_PATH)
        os.unlink(values_file)
    else:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=CHART_PATH)

    return result.stdout, result.stderr, result.returncode


def parse_yaml_documents(yaml_str: str) -> list:
    """Parse multiple YAML documents from a string."""
    docs = []
    for doc in yaml.safe_load_all(yaml_str):
        if doc is not None:
            docs.append(doc)
    return docs


# ==============================================================================
# FAIL-TO-PASS TESTS
# These tests fail on the base commit and pass after the fix is applied
# ==============================================================================

def test_values_schema_has_celery_hpa():
    """
    Test that workers.celery.hpa configuration is valid and creates HPA.

    fail_to_pass: Before fix, workers.celery.hpa has no schema and no template.
    Verifies by rendering helm template with celery HPA enabled and checking HPA object.
    Also checks schema for metrics and behavior fields (behavior_in_tests).
    """
    values = {
        "executor": "CeleryExecutor",
        "workers": {
            "celery": {
                "hpa": {
                    "enabled": True,
                    "minReplicaCount": 3,
                    "maxReplicaCount": 10
                }
            }
        }
    }

    stdout, stderr, returncode = run_helm_template(
        values=values,
        show_only="templates/workers/worker-hpa.yaml"
    )

    assert returncode == 0, f"Helm template failed: {stderr}"

    docs = parse_yaml_documents(stdout)

    # HPA should be created with the celery.hpa config
    hpa_found = False
    for doc in docs:
        if doc and doc.get("kind") == "HorizontalPodAutoscaler":
            hpa_found = True
            spec = doc.get("spec", {})
            assert spec.get("minReplicas") == 3, f"Expected minReplicas=3, got {spec.get('minReplicas')}"
            assert spec.get("maxReplicas") == 10, f"Expected maxReplicas=10, got {spec.get('maxReplicas')}"
            break

    assert hpa_found, "HorizontalPodAutoscaler should be created with workers.celery.hpa config"

    # Also verify the schema has required fields (behavior_in_tests: metrics and behavior)
    schema_path = os.path.join(CHART_PATH, "values.schema.json")
    with open(schema_path, 'r') as f:
        schema = json.load(f)

    celery_hpa = schema.get("properties", {}).get("workers", {}).get("properties", {}).get("celery", {}).get("properties", {}).get("hpa", {})

    assert celery_hpa, "Schema should define workers.celery.hpa"

    hpa_props = celery_hpa.get("properties", {})
    assert "enabled" in hpa_props, "celery.hpa should have enabled property"
    assert "minReplicaCount" in hpa_props, "celery.hpa should have minReplicaCount property"
    assert "maxReplicaCount" in hpa_props, "celery.hpa should have maxReplicaCount property"

    # behavior_in_tests: check for metrics and behavior fields
    assert "metrics" in hpa_props, "celery.hpa schema should have metrics property"
    assert "behavior" in hpa_props, "celery.hpa schema should have behavior property"


def test_deprecation_warning_in_notes_template():
    """
    Test that using workers.hpa.enabled triggers a deprecation warning in NOTES.

    fail_to_pass: Before fix, no deprecation warnings exist.
    Verifies by running helm install --dry-run with workers.hpa.enabled and
    checking that the output mentions the deprecation of workers.hpa and
    recommends workers.celery.hpa instead.
    """
    values = {
        "executor": "CeleryExecutor",
        "workers": {
            "hpa": {
                "enabled": True,
                "minReplicaCount": 2,
                "maxReplicaCount": 5
            }
        }
    }

    stdout, stderr, returncode = run_helm_install_dry_run(values=values)

    # dry-run fail returns non-zero, but output is still produced
    # Check that output contains warning about workers.hpa
    combined = stdout + stderr

    # Should mention the old path (workers.hpa) and new path (workers.celery.hpa)
    # We check for presence of both paths in a warning context
    assert "workers.hpa" in combined and "workers.celery.hpa" in combined, \
        "NOTES should warn about workers.hpa deprecation and recommend workers.celery.hpa"


def test_deprecation_warning_for_min_replica():
    """
    Test that using workers.hpa.minReplicaCount triggers a deprecation warning.

    fail_to_pass: Before fix, no deprecation warnings exist for minReplicaCount.
    Verifies by running helm install --dry-run with workers.hpa.minReplicaCount set
    and checking the output mentions the deprecation.
    """
    values = {
        "executor": "CeleryExecutor",
        "workers": {
            "hpa": {
                "enabled": True,
                "minReplicaCount": 2
            }
        }
    }

    stdout, stderr, returncode = run_helm_install_dry_run(values=values)

    combined = stdout + stderr

    # Should warn about the deprecated minReplicaCount config in workers.hpa
    # and recommend the workers.celery.hpa path
    assert "workers.hpa" in combined and "workers.celery.hpa" in combined, \
        "NOTES should warn about workers.hpa.minReplicaCount deprecation"


def test_values_yaml_has_celery_hpa_section():
    """
    Test that workers.celery.hpa renders correctly with values.yaml documentation.

    fail_to_pass: Before fix, workers.celery.hpa section doesn't exist in values.yaml.
    Verifies by rendering template with celery.hpa config and checking the output.
    """
    values = {
        "executor": "CeleryExecutor",
        "workers": {
            "celery": {
                "hpa": {
                    "enabled": True,
                    "minReplicaCount": 4,
                    "maxReplicaCount": 20
                }
            }
        }
    }

    stdout, stderr, returncode = run_helm_template(
        values=values,
        show_only="templates/workers/worker-hpa.yaml"
    )

    assert returncode == 0, f"Helm template failed: {stderr}"

    docs = parse_yaml_documents(stdout)

    # Should produce a valid HPA with the celery config values
    hpa_found = False
    for doc in docs:
        if doc and doc.get("kind") == "HorizontalPodAutoscaler":
            hpa_found = True
            spec = doc.get("spec", {})
            assert spec.get("minReplicas") == 4, f"Expected minReplicas=4 from celery.hpa, got {spec.get('minReplicas')}"
            assert spec.get("maxReplicas") == 20, f"Expected maxReplicas=20 from celery.hpa, got {spec.get('maxReplicas')}"
            break

    assert hpa_found, "HPA should be created using workers.celery.hpa values"


# ==============================================================================
# PASS-TO-PASS TESTS
# These tests pass on both the base commit and after the fix
# ==============================================================================

def test_helm_template_renders():
    """
    Test that helm template renders without errors with default values.

    pass_to_pass: Basic chart rendering should work on both commits.
    """
    values = {
        "executor": "CeleryExecutor"
    }

    stdout, stderr, returncode = run_helm_template(values=values)

    assert returncode == 0, f"Helm template failed: {stderr}"
    assert len(stdout) > 0, "Template output should not be empty"

    # Parse all documents to verify valid YAML
    docs = parse_yaml_documents(stdout)
    assert len(docs) > 0, "Should render at least one Kubernetes resource"


def test_base_hpa_config_creates_hpa():
    """
    Test that workers.hpa configuration creates HPA (backward compatibility).

    pass_to_pass: Base HPA config should work on both commits.
    """
    values = {
        "executor": "CeleryExecutor",
        "workers": {
            "hpa": {
                "enabled": True,
                "minReplicaCount": 3,
                "maxReplicaCount": 12
            }
        }
    }

    stdout, stderr, returncode = run_helm_template(
        values=values,
        show_only="templates/workers/worker-hpa.yaml"
    )

    assert returncode == 0, f"Helm template failed: {stderr}"

    docs = parse_yaml_documents(stdout)

    # HPA should be created with the base config
    hpa_found = False
    for doc in docs:
        if doc and doc.get("kind") == "HorizontalPodAutoscaler":
            hpa_found = True
            spec = doc.get("spec", {})
            assert spec.get("minReplicas") == 3, f"Expected minReplicas=3, got {spec.get('minReplicas')}"
            assert spec.get("maxReplicas") == 12, f"Expected maxReplicas=12, got {spec.get('maxReplicas')}"

    assert hpa_found, "HPA resource should be created with workers.hpa config"


def test_celery_hpa_merge_works():
    """
    Test that workers.celery.hpa values merge with workers.hpa values.

    pass_to_pass: The merge logic already exists in the HPA template.
    """
    values = {
        "executor": "CeleryExecutor",
        "workers": {
            "hpa": {
                "enabled": True,
                "minReplicaCount": 2,
                "maxReplicaCount": 8
            },
            "celery": {
                "hpa": {
                    "minReplicaCount": 5,
                    "maxReplicaCount": 15
                }
            }
        }
    }

    stdout, stderr, returncode = run_helm_template(
        values=values,
        show_only="templates/workers/worker-hpa.yaml"
    )

    assert returncode == 0, f"Helm template failed: {stderr}"

    docs = parse_yaml_documents(stdout)

    # The celery values should merge/override base hpa values
    for doc in docs:
        if doc and doc.get("kind") == "HorizontalPodAutoscaler":
            spec = doc.get("spec", {})
            assert spec.get("minReplicas") == 5, f"Expected minReplicas=5, got {spec.get('minReplicas')}"
            assert spec.get("maxReplicas") == 15, f"Expected maxReplicas=15, got {spec.get('maxReplicas')}"
            return

    assert False, "HPA resource should be created"


def test_values_schema_valid_json():
    """
    Test that values.schema.json is valid JSON.

    pass_to_pass: Schema should be valid JSON on both commits.
    """
    schema_path = os.path.join(CHART_PATH, "values.schema.json")

    with open(schema_path, 'r') as f:
        content = f.read()

    # Should parse without error
    schema = json.loads(content)

    assert "properties" in schema, "Schema should have properties"
    assert "workers" in schema["properties"], "Schema should define workers"


def test_hpa_disabled_by_default():
    """
    Test that HPA is disabled by default.

    pass_to_pass: Default behavior should be consistent on both commits.
    """
    values = {
        "executor": "CeleryExecutor"
    }

    stdout, stderr, returncode = run_helm_template(
        values=values,
        show_only="templates/workers/worker-hpa.yaml"
    )

    assert returncode == 0, f"Helm template failed: {stderr}"

    docs = parse_yaml_documents(stdout)

    # With HPA disabled (default), no HPA resource should be created
    for doc in docs:
        if doc and doc.get("kind") == "HorizontalPodAutoscaler":
            assert False, "HPA should not be created when disabled (default)"


def test_repo_helm_lint():
    """
    Repo's helm lint passes on the chart.

    pass_to_pass: Helm lint should pass on both base and fixed commits.
    """
    r = subprocess.run(
        ["helm", "lint", CHART_PATH],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Helm lint failed:\n{r.stderr[-500:]}"


def test_repo_chart_schema():
    """
    Repo's chart_schema.py validation passes.

    pass_to_pass: chart_schema.py should pass on both commits.
    """
    r = subprocess.run(
        ["python", f"{REPO}/scripts/ci/prek/chart_schema.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"chart_schema.py failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_values_schema_json_valid():
    """
    Repo's values.schema.json is valid JSON that can be parsed.

    pass_to_pass: values.schema.json must be valid JSON on both commits.
    """
    schema_path = os.path.join(CHART_PATH, "values.schema.json")
    with open(schema_path, 'r') as f:
        content = f.read()

    # Should parse without error
    schema = json.loads(content)

    # Must have required top-level keys
    assert "properties" in schema, "Schema must have properties"
    assert "$schema" in schema, "Schema must declare JSON Schema version"


def test_repo_helm_template_workers_hpa():
    """
    Helm template renders worker-hpa.yaml without errors when HPA is enabled.

    pass_to_pass: HPA template should render correctly on both commits.
    """
    r = subprocess.run(
        [
            "helm", "template", "test-release", CHART_PATH,
            "--show-only", "templates/workers/worker-hpa.yaml",
            "--set", "executor=CeleryExecutor",
            "--set", "workers.hpa.enabled=true",
        ],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Helm template failed:\n{r.stderr[-500:]}"

    # Parse the output to verify it's valid YAML
    docs = list(yaml.safe_load_all(r.stdout))
    hpa_found = any(doc and doc.get("kind") == "HorizontalPodAutoscaler" for doc in docs)
    assert hpa_found, "HorizontalPodAutoscaler resource should be rendered"


if __name__ == "__main__":
    import sys
    sys.exit(subprocess.call(["pytest", __file__, "-v", "--tb=short"]))