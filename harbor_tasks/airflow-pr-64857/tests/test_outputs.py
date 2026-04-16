"""
Tests for apache/airflow#64857: Add workers.celery.waitForMigrations section

This PR adds a new configuration path `workers.celery.waitForMigrations` to the
Airflow Helm chart, deprecating the old `workers.waitForMigrations` path.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path("/workspace/airflow")
CHART_DIR = REPO / "chart"


def run_helm_template(values: dict, show_only: list[str] | None = None) -> list[dict]:
    """Render Helm chart with given values and return parsed YAML documents."""
    import yaml
    import tempfile

    cmd = ["helm", "template", "release-name", str(CHART_DIR)]

    if values:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(values, f)
            values_file = f.name
        cmd.extend(["-f", values_file])

    if show_only:
        for template in show_only:
            cmd.extend(["--show-only", template])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    if result.returncode != 0:
        raise RuntimeError(f"Helm template failed: {result.stderr}")

    # Parse multi-document YAML
    docs = []
    for doc in yaml.safe_load_all(result.stdout):
        if doc:
            docs.append(doc)

    return docs


def jmespath_search(expression: str, data: dict):
    """Search data using jmespath expression."""
    import jmespath
    return jmespath.search(expression, data)


class TestCeleryWaitForMigrationsConfig:
    """Tests for the new workers.celery.waitForMigrations configuration path."""

    def test_celery_wait_for_migrations_schema_defines_enabled_field(self):
        """Schema has workers.celery.waitForMigrations.enabled with nullable type (fail_to_pass)."""
        schema_path = CHART_DIR / "values.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)

        # Navigate to workers.celery.waitForMigrations.enabled in schema
        celery = schema["properties"]["workers"]["properties"].get("celery", {})
        wfm = celery.get("properties", {}).get("waitForMigrations", {})
        enabled = wfm.get("properties", {}).get("enabled", {})

        assert enabled, "workers.celery.waitForMigrations.enabled must exist in schema"
        # Verify it's nullable (allows null for inheritance from deprecated path)
        type_val = enabled.get("type", [])
        if isinstance(type_val, list):
            assert "null" in type_val, "enabled type must include null for inheritance"
        else:
            assert type_val == "null", "enabled type must be null for inheritance"

    def test_celery_wait_for_migrations_schema_defines_env_field(self):
        """Schema has workers.celery.waitForMigrations.env as array (fail_to_pass)."""
        schema_path = CHART_DIR / "values.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)

        celery = schema["properties"]["workers"]["properties"].get("celery", {})
        wfm = celery.get("properties", {}).get("waitForMigrations", {})
        env = wfm.get("properties", {}).get("env", {})

        assert env, "workers.celery.waitForMigrations.env must exist in schema"
        assert env.get("type") == "array", "env must be an array type"

    def test_celery_wait_for_migrations_schema_defines_security_contexts(self):
        """Schema has workers.celery.waitForMigrations.securityContexts.container (fail_to_pass)."""
        schema_path = CHART_DIR / "values.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)

        celery = schema["properties"]["workers"]["properties"].get("celery", {})
        wfm = celery.get("properties", {}).get("waitForMigrations", {})
        sec_ctx = wfm.get("properties", {}).get("securityContexts", {})
        container = sec_ctx.get("properties", {}).get("container", {})

        assert container, "workers.celery.waitForMigrations.securityContexts.container must exist"

    def test_celery_wait_for_migrations_in_values_yaml(self):
        """values.yaml contains workers.celery.waitForMigrations section (fail_to_pass)."""
        import yaml

        values_path = CHART_DIR / "values.yaml"
        with open(values_path) as f:
            values = yaml.safe_load(f)

        celery = values.get("workers", {}).get("celery", {})
        wfm = celery.get("waitForMigrations", {})

        assert wfm, "workers.celery.waitForMigrations must exist in values.yaml"
        # Verify it's a dict with expected keys (not just an empty placeholder)
        assert isinstance(wfm, dict), "waitForMigrations should be a dict"

    def test_deprecation_notice_in_old_schema_path(self):
        """Old workers.waitForMigrations schema description mentions deprecation (fail_to_pass)."""
        schema_path = CHART_DIR / "values.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)

        old_wfm = schema["properties"]["workers"]["properties"].get("waitForMigrations", {})
        desc = old_wfm.get("description", "")

        # The old path's description should mention deprecation
        assert "deprecated" in desc.lower(), \
            "workers.waitForMigrations description should mention deprecation"


class TestDeprecationWarnings:
    """Tests for deprecation warnings in NOTES.txt template."""

    def _get_notes_content(self) -> str:
        """Read raw NOTES.txt template content."""
        notes_path = CHART_DIR / "templates" / "NOTES.txt"
        return notes_path.read_text()

    def test_notes_shows_deprecation_when_using_old_enabled_path(self):
        """NOTES.txt has deprecation warning for workers.waitForMigrations.enabled (fail_to_pass)."""
        content = self._get_notes_content()

        # Should have the deprecation warning text for enabled path
        # The template contains conditional blocks with DEPRECATION WARNING
        assert "DEPRECATION" in content or "deprecated" in content.lower(), \
            "NOTES.txt should have deprecation content"
        # Must mention the old and new paths for the enabled setting
        assert "workers.waitForMigrations.enabled" in content, \
            "NOTES.txt should reference workers.waitForMigrations.enabled"

    def test_notes_shows_deprecation_when_using_old_env_path(self):
        """NOTES.txt has deprecation warning for workers.waitForMigrations.env (fail_to_pass)."""
        content = self._get_notes_content()

        assert "DEPRECATION" in content or "deprecated" in content.lower(), \
            "NOTES.txt should have deprecation content"
        assert "workers.waitForMigrations.env" in content, \
            "NOTES.txt should reference workers.waitForMigrations.env"


class TestNewsfragment:
    """Tests for the changelog newsfragment."""

    def test_newsfragment_exists(self):
        """Newsfragment for PR 62054 exists (fail_to_pass)."""
        newsfragment = CHART_DIR / "newsfragments" / "62054.significant.rst"
        assert newsfragment.exists(), \
            "Newsfragment 62054.significant.rst should exist"

    def test_newsfragment_describes_config_change(self):
        """Newsfragment describes the configuration path change (fail_to_pass)."""
        newsfragment = CHART_DIR / "newsfragments" / "62054.significant.rst"
        if not newsfragment.exists():
            pytest.skip("Newsfragment doesn't exist yet")

        content = newsfragment.read_text()
        # Should mention config path change meaningfully
        assert "waitForMigrations" in content, \
            "Newsfragment should mention the config path"
        # At least one of old/new should be present
        has_old = "workers.waitForMigrations" in content
        has_new = "workers.celery.waitForMigrations" in content
        assert has_old or has_new, \
            "Newsfragment should mention at least one config path"


class TestCeleryWaitForMigrationsBehavior:
    """Tests that verify the new config path actually works (behavioral verification)."""

    def test_celery_path_controls_init_container_presence(self):
        """New workers.celery.waitForMigrations.enabled=false disables init container (fail_to_pass)."""
        docs = run_helm_template(
            values={
                "executor": "CeleryExecutor",
                "workers": {
                    "celery": {
                        "waitForMigrations": {"enabled": False}
                    }
                }
            },
            show_only=["templates/workers/worker-deployment.yaml"]
        )

        for doc in docs:
            init_containers = jmespath_search(
                "spec.template.spec.initContainers[?name=='wait-for-airflow-migrations']",
                doc
            )
            # When disabled via new path, init container should not exist
            assert not init_containers or len(init_containers) == 0, \
                "wait-for-airflow-migrations should not exist when disabled via celery path"

    def test_celery_path_accepts_env_configuration(self):
        """New workers.celery.waitForMigrations.env accepts env vars (fail_to_pass)."""
        docs = run_helm_template(
            values={
                "executor": "CeleryExecutor",
                "workers": {
                    "celery": {
                        "waitForMigrations": {
                            "env": [{"name": "TEST_VAR", "value": "test_value"}]
                        }
                    }
                }
            },
            show_only=["templates/workers/worker-deployment.yaml"]
        )

        for doc in docs:
            init_containers = jmespath_search(
                "spec.template.spec.initContainers[?name=='wait-for-airflow-migrations']",
                doc
            )
            if init_containers:
                env_vars = init_containers[0].get("env", [])
                env_names = [e.get("name") for e in env_vars]
                assert "TEST_VAR" in env_names, \
                    "TEST_VAR env should be present in init container via celery path"

    def test_new_path_takes_precedence_over_old(self):
        """New celery path takes precedence when both old and new are set (fail_to_pass)."""
        docs = run_helm_template(
            values={
                "executor": "CeleryExecutor",
                "workers": {
                    "waitForMigrations": {"enabled": True},
                    "celery": {
                        "waitForMigrations": {"enabled": False}
                    }
                }
            },
            show_only=["templates/workers/worker-deployment.yaml"]
        )

        # When both are set, the new path should take precedence (celery=false disables)
        for doc in docs:
            init_containers = jmespath_search(
                "spec.template.spec.initContainers[?name=='wait-for-airflow-migrations']",
                doc
            )
            assert not init_containers or len(init_containers) == 0, \
                "New celery path should take precedence over old path"


class TestPassToPass:
    """Regression tests - these should pass both before and after the fix."""

    def test_helm_lint_passes(self):
        """Helm lint passes on the chart (pass_to_pass)."""
        result = subprocess.run(
            ["helm", "lint", str(CHART_DIR)],
            capture_output=True,
            text=True,
            timeout=120
        )
        assert result.returncode == 0, f"Helm lint failed:\n{result.stderr}"

    def test_values_yaml_is_valid_yaml(self):
        """values.yaml is valid YAML (pass_to_pass)."""
        import yaml

        values_path = CHART_DIR / "values.yaml"
        try:
            with open(values_path) as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"values.yaml is not valid YAML: {e}")

    def test_values_schema_is_valid_json(self):
        """values.schema.json is valid JSON (pass_to_pass)."""
        schema_path = CHART_DIR / "values.schema.json"
        try:
            with open(schema_path) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"values.schema.json is not valid JSON: {e}")

    def test_old_wait_for_migrations_still_works(self):
        """Old workers.waitForMigrations config still works (pass_to_pass)."""
        try:
            docs = run_helm_template(
                values={
                    "executor": "CeleryExecutor",
                    "workers": {
                        "waitForMigrations": {
                            "enabled": False
                        }
                    }
                },
                show_only=["templates/workers/worker-deployment.yaml"]
            )
        except RuntimeError as e:
            pytest.fail(f"Old config path should still work: {e}")

        # Verify it rendered successfully
        assert len(docs) > 0, "Should render at least one document"


class TestRepoCI:
    """Tests that mirror the repo's CI checks using subprocess (pass_to_pass)."""

    def test_repo_jsonschema_validates_values(self):
        """values.yaml validates against values.schema.json (pass_to_pass)."""
        result = subprocess.run(
            [
                "python3", "-c",
                """
import json
import yaml
import jsonschema
schema = json.load(open('/workspace/airflow/chart/values.schema.json'))
values = yaml.safe_load(open('/workspace/airflow/chart/values.yaml'))
jsonschema.validate(values, schema)
print('Schema validation passed')
"""
            ],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(REPO),
        )
        assert result.returncode == 0, f"Schema validation failed:\n{result.stderr}"

    def test_repo_schema_is_valid_jsonschema(self):
        """values.schema.json is a valid JSON Schema (pass_to_pass)."""
        result = subprocess.run(
            [
                "python3", "-c",
                """
import json
import jsonschema
schema = json.load(open('/workspace/airflow/chart/values.schema.json'))
jsonschema.Draft7Validator.check_schema(schema)
print('JSON schema is valid Draft7')
"""
            ],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(REPO),
        )
        assert result.returncode == 0, f"JSON schema validation failed:\n{result.stderr}"

    def test_repo_helm_template_default_values(self):
        """Helm template renders with default values (pass_to_pass)."""
        result = subprocess.run(
            ["helm", "template", "test-release", str(CHART_DIR)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, f"Helm template failed:\n{result.stderr[-500:]}"
        # Check that we got some output
        assert "apiVersion:" in result.stdout, "Helm template should produce YAML output"

    def test_repo_helm_template_celery_executor(self):
        """Helm template renders with CeleryExecutor (pass_to_pass)."""
        result = subprocess.run(
            [
                "helm", "template", "test-release", str(CHART_DIR),
                "--set", "executor=CeleryExecutor",
                "--show-only", "templates/workers/worker-deployment.yaml"
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, f"Helm template failed:\n{result.stderr[-500:]}"
        assert "worker" in result.stdout.lower(), "Should render worker deployment"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
