#!/usr/bin/env python3
"""
Behavioral tests for workers.celery.volumeClaimTemplates Helm chart changes.

Tests verify actual behavior via subprocess calls (helm template rendering,
schema validation) and structured data parsing (YAML, JSON, Python AST)
rather than text grepping source files.
"""

import ast
import json
import os
import subprocess

import pytest
import yaml

REPO = "/workspace/airflow"
CHART_DIR = os.path.join(REPO, "chart")
HELM_TESTS_DIR = os.path.join(REPO, "helm-tests")


# --- Helpers ---


def _helm_template(extra_sets=None, show_only=None):
    """Run helm template and return the CompletedProcess."""
    cmd = ["helm", "template", "test-release", ".", "--set", "executor=CeleryExecutor"]
    if extra_sets:
        for s in extra_sets:
            cmd.extend(["--set", s])
    if show_only:
        for s in show_only:
            cmd.extend(["--show-only", s])
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=60, cwd=CHART_DIR
    )


def _parse_yaml_stream(stdout):
    """Parse multi-doc YAML from helm template output into list of dicts."""
    return [d for d in yaml.safe_load_all(stdout) if d is not None]


def _load_values():
    """Load and return parsed values.yaml."""
    with open(os.path.join(CHART_DIR, "values.yaml")) as f:
        return yaml.safe_load(f)


def _load_schema():
    """Load and return parsed values.schema.json."""
    with open(os.path.join(CHART_DIR, "values.schema.json")) as f:
        return json.load(f)


def _has_vct_deprecation_warning(stdout):
    """Check if stdout contains a volumeClaimTemplates-specific deprecation warning."""
    lines = stdout.split("\n")
    for i, line in enumerate(lines):
        if "DEPRECATION WARNING" in line:
            context = "\n".join(lines[max(0, i - 1) : i + 6])
            if "volumeClaimTemplates" in context:
                return True
    return False


# Test value sets using unique names (NOT from gold fix) to avoid cheating
CELERY_VCT_SETS = [
    "workers.celery.volumeClaimTemplates[0].metadata.name=behav-test-vol",
    "workers.celery.volumeClaimTemplates[0].spec.storageClassName=behav-storage",
    "workers.celery.volumeClaimTemplates[0].spec.accessModes[0]=ReadWriteOnce",
    "workers.celery.volumeClaimTemplates[0].spec.resources.requests.storage=5Gi",
]

LEGACY_VCT_SETS = [
    "workers.volumeClaimTemplates[0].metadata.name=legacy-test-vol",
    "workers.volumeClaimTemplates[0].spec.storageClassName=legacy-storage",
    "workers.volumeClaimTemplates[0].spec.accessModes[0]=ReadWriteOnce",
    "workers.volumeClaimTemplates[0].spec.resources.requests.storage=3Gi",
]


# --- F2P Tests: Must fail on NOP, pass on GOLD ---


class TestValuesYaml:
    """Tests for values.yaml behavioral changes."""

    def test_celery_volume_claim_templates_exists(self):
        """Verify workers.celery.volumeClaimTemplates exists and defaults to []."""
        values = _load_values()
        celery_vct = values["workers"]["celery"]["volumeClaimTemplates"]
        assert celery_vct == [], (
            "workers.celery.volumeClaimTemplates should default to empty list"
        )

    def test_legacy_volume_claim_templates_deprecated_comment(self):
        """Verify using legacy VCT triggers a deprecation signal in rendered output."""
        r = _helm_template(extra_sets=LEGACY_VCT_SETS)
        assert r.returncode == 0, f"helm template failed: {r.stderr}"
        assert _has_vct_deprecation_warning(r.stdout), (
            "No deprecation warning rendered when legacy workers.volumeClaimTemplates is used"
        )

    def test_celery_section_has_examples(self):
        """Verify helm template renders volume claims from the new celery path."""
        r = _helm_template(
            extra_sets=CELERY_VCT_SETS,
            show_only=["templates/workers/worker-deployment.yaml"],
        )
        assert r.returncode == 0, f"helm template failed: {r.stderr}"
        docs = _parse_yaml_stream(r.stdout)
        found = False
        for doc in docs:
            vcts = doc.get("spec", {}).get("volumeClaimTemplates", [])
            for vct in vcts:
                if vct.get("metadata", {}).get("name") == "behav-test-vol":
                    assert vct["spec"]["storageClassName"] == "behav-storage"
                    assert vct["spec"]["resources"]["requests"]["storage"] == "5Gi"
                    found = True
        assert found, "Volume claim from celery path not rendered in worker deployment"


class TestValuesSchema:
    """Tests for values.schema.json behavioral changes."""

    def test_celery_volume_claim_templates_in_schema(self):
        """Verify workers.celery.volumeClaimTemplates is defined as array in schema."""
        schema = _load_schema()
        celery_props = (
            schema["properties"]["workers"]["properties"]["celery"]["properties"]
        )
        assert "volumeClaimTemplates" in celery_props
        assert celery_props["volumeClaimTemplates"]["type"] == "array"

    def test_celery_volume_claim_templates_has_examples(self):
        """Verify schema provides at least 2 examples for the new field."""
        schema = _load_schema()
        vct = (
            schema["properties"]["workers"]["properties"]["celery"]["properties"][
                "volumeClaimTemplates"
            ]
        )
        examples = vct.get("examples", [])
        assert len(examples) >= 2, f"Expected >= 2 examples, got {len(examples)}"

    def test_legacy_volume_claim_templates_deprecated_in_schema(self):
        """Verify legacy field schema description mentions deprecation and new path."""
        schema = _load_schema()
        legacy_desc = (
            schema["properties"]["workers"]["properties"]["volumeClaimTemplates"][
                "description"
            ]
        )
        assert "deprecated" in legacy_desc.lower()
        assert "workers.celery.volumeClaimTemplates" in legacy_desc


class TestNotesTxt:
    """Tests for NOTES.txt rendered output behavior."""

    def test_deprecation_warning_in_notes(self):
        """Verify rendered chart shows deprecation warning when legacy VCT is used."""
        r = _helm_template(extra_sets=LEGACY_VCT_SETS)
        assert r.returncode == 0, f"helm template failed: {r.stderr}"
        assert _has_vct_deprecation_warning(r.stdout), (
            "VCT deprecation warning not rendered when legacy path is used"
        )

    def test_deprecation_warning_conditional(self):
        """Verify deprecation warning only appears when legacy VCT is set."""
        # Without legacy VCT: no VCT deprecation warning
        r_no_legacy = _helm_template()
        assert r_no_legacy.returncode == 0
        assert not _has_vct_deprecation_warning(r_no_legacy.stdout), (
            "VCT deprecation warning should not appear when legacy field is empty"
        )

        # With legacy VCT: warning appears
        r_with_legacy = _helm_template(extra_sets=LEGACY_VCT_SETS)
        assert r_with_legacy.returncode == 0
        assert _has_vct_deprecation_warning(r_with_legacy.stdout), (
            "VCT deprecation warning should appear when legacy field is used"
        )


class TestHelmTests:
    """Tests for helm test file structure via Python AST parsing."""

    def _parse_test_worker(self):
        path = os.path.join(
            HELM_TESTS_DIR,
            "tests",
            "helm_tests",
            "airflow_core",
            "test_worker.py",
        )
        with open(path) as f:
            return ast.parse(f.read())

    def _parse_test_worker_sets(self):
        path = os.path.join(
            HELM_TESTS_DIR,
            "tests",
            "helm_tests",
            "airflow_core",
            "test_worker_sets.py",
        )
        with open(path) as f:
            return ast.parse(f.read())

    def _find_parametrized_vct_function(self, tree):
        """Find a VCT-related function with a parametrize decorator."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if "volume_claim_template" in node.name.lower():
                    for deco in node.decorator_list:
                        deco_dump = ast.dump(deco)
                        if "parametrize" in deco_dump:
                            return node, deco
        return None, None

    def _get_parametrize_list_elements(self, deco):
        """Extract list elements from a parametrize decorator's second arg."""
        if not isinstance(deco, ast.Call):
            return []
        for arg in deco.args:
            if isinstance(arg, ast.List):
                return arg.elts
        return []

    def _dict_top_keys(self, node):
        """Get top-level string keys of an AST Dict node."""
        if not isinstance(node, ast.Dict):
            return []
        return [k.value for k in node.keys if isinstance(k, ast.Constant)]

    def test_test_file_has_parametrized_tests(self):
        """Verify test_worker.py has parametrized volume claim template tests."""
        tree = self._parse_test_worker()
        func, _ = self._find_parametrized_vct_function(tree)
        assert func is not None, (
            "No parametrized volume claim template test found in test_worker.py"
        )

    def test_test_file_checks_celery_path(self):
        """Verify parametrized test includes the celery.volumeClaimTemplates path."""
        tree = self._parse_test_worker()
        _, deco = self._find_parametrized_vct_function(tree)
        assert deco is not None, "No parametrized VCT test found"

        elements = self._get_parametrize_list_elements(deco)
        found = False
        for elt in elements:
            if isinstance(elt, ast.Dict):
                keys = self._dict_top_keys(elt)
                if "celery" in keys:
                    idx = keys.index("celery")
                    val = elt.values[idx]
                    if isinstance(val, ast.Dict):
                        sub_keys = self._dict_top_keys(val)
                        if "volumeClaimTemplates" in sub_keys:
                            found = True
        assert found, (
            "Parametrized test does not include a celery.volumeClaimTemplates case"
        )

    def test_test_file_checks_legacy_path(self):
        """Verify parametrized test includes the legacy volumeClaimTemplates path."""
        tree = self._parse_test_worker()
        _, deco = self._find_parametrized_vct_function(tree)
        assert deco is not None, "No parametrized VCT test found"

        elements = self._get_parametrize_list_elements(deco)
        found = False
        for elt in elements:
            if isinstance(elt, ast.Dict):
                keys = self._dict_top_keys(elt)
                # Legacy case: has volumeClaimTemplates but NOT celery at top level
                if "volumeClaimTemplates" in keys and "celery" not in keys:
                    found = True
        assert found, (
            "Parametrized test does not include a legacy volumeClaimTemplates case"
        )

    def test_worker_sets_test_updated(self):
        """Verify test_worker_sets.py exercises the celery VCT path."""
        tree = self._parse_test_worker_sets()
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                keys = self._dict_top_keys(node)
                if "celery" in keys:
                    idx = keys.index("celery")
                    val = node.values[idx]
                    if isinstance(val, ast.Dict):
                        sub_keys = self._dict_top_keys(val)
                        if "volumeClaimTemplates" in sub_keys:
                            found = True
        assert found, (
            "test_worker_sets.py does not exercise workers.celery.volumeClaimTemplates"
        )


class TestNewsfragment:
    """Tests for the newsfragment file."""

    def test_newsfragment_exists(self):
        """Verify the newsfragment file exists."""
        path = os.path.join(CHART_DIR, "newsfragments", "62048.significant.rst")
        assert os.path.exists(path), f"Newsfragment file not found: {path}"

    def test_newsfragment_content(self):
        """Verify newsfragment documents the deprecation with both field paths."""
        path = os.path.join(CHART_DIR, "newsfragments", "62048.significant.rst")
        with open(path) as f:
            content = f.read()
        content_lower = content.lower()
        assert "deprecated" in content_lower, (
            "Newsfragment should indicate deprecation"
        )
        assert "workers.volumeClaimTemplates" in content, (
            "Newsfragment should mention the deprecated field"
        )
        assert "workers.celery.volumeClaimTemplates" in content, (
            "Newsfragment should mention the new field"
        )


# --- P2P Tests: Must pass on both NOP and GOLD ---


class TestHelmChartValidation:
    """Tests to validate the Helm chart structure (pass_to_pass)."""

    def test_values_yaml_is_valid_yaml(self):
        """Verify values.yaml is valid YAML that can be parsed."""
        values = _load_values()
        assert isinstance(values, dict), "values.yaml should parse to a dictionary"

    def test_values_schema_is_valid_json(self):
        """Verify values.schema.json is valid JSON that can be parsed."""
        schema = _load_schema()
        assert isinstance(schema, dict), (
            "values.schema.json should parse to a dictionary"
        )

    def test_schema_has_required_definitions(self):
        """Verify the schema has the required definitions for volume claim templates."""
        schema = _load_schema()
        definitions = schema.get("definitions", {})
        assert "io.k8s.api.core.v1.PersistentVolumeClaimTemplate" in definitions


class TestRepoCICommands:
    """Tests that run actual CI commands from the repo (pass_to_pass)."""

    def test_repo_helm_lint(self):
        """Helm lint passes on the chart (pass_to_pass)."""
        r = subprocess.run(
            ["helm", "lint", "."],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=CHART_DIR,
        )
        assert r.returncode == 0, f"Helm lint failed:\n{r.stdout}\n{r.stderr}"

    def test_repo_helm_template_celery(self):
        """Helm template renders with CeleryExecutor (pass_to_pass)."""
        r = subprocess.run(
            ["helm", "template", ".", "--set", "executor=CeleryExecutor"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=CHART_DIR,
        )
        assert r.returncode == 0, f"Helm template failed:\n{r.stderr[-500:]}"
        assert "worker" in r.stdout.lower(), (
            "Worker deployment not found in rendered templates"
        )

    def test_repo_values_schema_validation(self):
        """Default values.yaml validates against schema.json (pass_to_pass)."""
        r = subprocess.run(
            [
                "python3",
                "-c",
                "import json, yaml; from jsonschema import validate; "
                "schema=json.load(open('values.schema.json')); "
                "values=yaml.safe_load(open('values.yaml')); "
                "validate(instance=values, schema=schema); "
                "print('Schema validation passed')",
            ],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=CHART_DIR,
        )
        assert r.returncode == 0, f"Schema validation failed:\n{r.stderr[-500:]}"

    def test_repo_chart_yaml_valid(self):
        """Chart.yaml is valid and contains required fields (pass_to_pass)."""
        r = subprocess.run(
            [
                "python3",
                "-c",
                "import yaml; "
                "chart=yaml.safe_load(open('Chart.yaml')); "
                "assert 'apiVersion' in chart, 'Missing apiVersion'; "
                "assert 'name' in chart, 'Missing name'; "
                "assert 'version' in chart, 'Missing version'; "
                "print('Chart.yaml is valid')",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=CHART_DIR,
        )
        assert r.returncode == 0, f"Chart.yaml validation failed:\n{r.stderr[-500:]}"

    def test_repo_helm_template_with_celery_volume_claim(self):
        """Helm template renders with celery.volumeClaimTemplates (pass_to_pass)."""
        r = _helm_template(extra_sets=CELERY_VCT_SETS)
        assert r.returncode == 0, (
            f"Helm template with volumeClaimTemplates failed:\n{r.stderr[-500:]}"
        )
        assert "behav-test-vol" in r.stdout or "volumeClaimTemplates" in r.stdout, (
            "Volume claim template not rendered in output"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
