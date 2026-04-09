"""
Test outputs for airflow-chart-celery-volumeclaim task.

This task requires adding `workers.celery.volumeClaimTemplates` to the Airflow Helm chart
with backward compatibility for the deprecated `workers.volumeClaimTemplates`.
"""

import json
import subprocess
import yaml
from pathlib import Path

REPO = Path("/workspace/airflow")
CHART = REPO / "chart"
VALUES_YAML = CHART / "values.yaml"
VALUES_SCHEMA = CHART / "values.schema.json"
NOTES_TXT = CHART / "templates" / "NOTES.txt"


class TestValuesYaml:
    """Tests for values.yaml changes."""

    def test_celery_volumeclaimtemplates_exists(self):
        """Verify workers.celery.volumeClaimTemplates field exists."""
        with open(VALUES_YAML) as f:
            values = yaml.safe_load(f)

        assert "workers" in values, "workers section missing"
        assert "celery" in values["workers"], "workers.celery section missing"
        assert "volumeClaimTemplates" in values["workers"]["celery"], \
            "workers.celery.volumeClaimTemplates field missing"
        assert values["workers"]["celery"]["volumeClaimTemplates"] == [], \
            "Default value should be empty list"

    def test_deprecated_field_has_comment(self):
        """Verify deprecated workers.volumeClaimTemplates has deprecation comment."""
        with open(VALUES_YAML) as f:
            content = f.read()

        # Find the workers.volumeClaimTemplates section
        assert "# (deprecated, use `workers.celery.volumeClaimTemplates` instead)" in content, \
            "Deprecation comment not found in values.yaml"


class TestValuesSchema:
    """Tests for values.schema.json changes."""

    def test_schema_is_valid_json(self):
        """Verify schema.json is valid JSON."""
        with open(VALUES_SCHEMA) as f:
            schema = json.load(f)
        assert schema is not None

    def test_celery_volumeclaimtemplates_in_schema(self):
        """Verify workers.celery.volumeClaimTemplates is in schema."""
        with open(VALUES_SCHEMA) as f:
            schema = json.load(f)

        celery = schema["properties"]["workers"]["properties"]["celery"]["properties"]
        assert "volumeClaimTemplates" in celery, \
            "workers.celery.volumeClaimTemplates not in schema"

        vct = celery["volumeClaimTemplates"]
        assert vct["type"] == "array", "Type should be array"
        assert "description" in vct, "Description required"
        assert "examples" in vct, "Examples should be provided"

    def test_deprecated_description_updated(self):
        """Verify old workers.volumeClaimTemplates description mentions deprecation."""
        with open(VALUES_SCHEMA) as f:
            schema = json.load(f)

        workers_vct = schema["properties"]["workers"]["properties"]["volumeClaimTemplates"]
        desc = workers_vct.get("description", "")
        assert "deprecated" in desc.lower(), \
            "Old field description should mention deprecation"
        assert "workers.celery.volumeClaimTemplates" in desc, \
            "Should reference new field location"

    def test_schema_examples_are_valid(self):
        """Verify the schema examples for new field are valid."""
        with open(VALUES_SCHEMA) as f:
            schema = json.load(f)

        celery = schema["properties"]["workers"]["properties"]["celery"]["properties"]
        vct = celery["volumeClaimTemplates"]
        examples = vct.get("examples", [])

        assert len(examples) >= 2, "Should have at least 2 examples"

        for ex in examples:
            assert "name" in ex, "Example missing name"
            assert "storageClassName" in ex, "Example missing storageClassName"
            assert "accessModes" in ex, "Example missing accessModes"
            assert "resources" in ex, "Example missing resources"


class TestNotesTxt:
    """Tests for NOTES.txt changes."""

    def test_deprecation_warning_exists(self):
        """Verify NOTES.txt has deprecation warning for old field."""
        with open(NOTES_TXT) as f:
            content = f.read()

        assert "workers.volumeClaimTemplates has been renamed" in content, \
            "Deprecation warning not found"
        assert "workers.celery.volumeClaimTemplates" in content, \
            "New field location not mentioned in warning"


class TestHelmRender:
    """Tests for Helm chart rendering with new values."""

    def _render_chart(self, values):
        """Helper to render helm chart with given values."""
        import tempfile

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(values, f)
            values_file = f.name

        try:
            result = subprocess.run(
                [
                    "helm", "template", "test", ".",
                    "--values", values_file,
                    "--show-only", "templates/workers/worker-deployment.yaml"
                ],
                cwd=CHART,
                capture_output=True,
                text=True,
                timeout=60
            )
            return result
        finally:
            import os
            os.unlink(values_file)

    def test_new_volumeclaimtemplates_location_works(self):
        """Verify new workers.celery.volumeClaimTemplates location works."""
        values = {
            "executor": "CeleryExecutor",
            "workers": {
                "celery": {
                    "volumeClaimTemplates": [
                        {
                            "metadata": {"name": "test-volume"},
                            "spec": {
                                "storageClassName": "standard",
                                "accessModes": ["ReadWriteOnce"],
                                "resources": {"requests": {"storage": "5Gi"}}
                            }
                        }
                    ]
                }
            }
        }

        result = self._render_chart(values)
        assert result.returncode == 0, f"Helm render failed: {result.stderr}"

        # Check the rendered output contains our volume
        assert "test-volume" in result.stdout, "Volume claim template not rendered"

    def test_backward_compatibility(self):
        """Verify old workers.volumeClaimTemplates still works."""
        values = {
            "executor": "CeleryExecutor",
            "workers": {
                "volumeClaimTemplates": [
                    {
                        "metadata": {"name": "legacy-volume"},
                        "spec": {
                            "storageClassName": "standard",
                            "accessModes": ["ReadWriteOnce"],
                            "resources": {"requests": {"storage": "3Gi"}}
                        }
                    }
                ]
            }
        }

        result = self._render_chart(values)
        assert result.returncode == 0, f"Helm render failed: {result.stderr}"
        assert "legacy-volume" in result.stdout, "Legacy volume claim template not rendered"

    def test_new_location_takes_precedence(self):
        """Verify new location takes precedence when both are specified."""
        values = {
            "executor": "CeleryExecutor",
            "workers": {
                "volumeClaimTemplates": [
                    {
                        "metadata": {"name": "old-volume"},
                        "spec": {
                            "storageClassName": "old-class",
                            "accessModes": ["ReadWriteOnce"],
                            "resources": {"requests": {"storage": "1Gi"}}
                        }
                    }
                ],
                "celery": {
                    "volumeClaimTemplates": [
                        {
                            "metadata": {"name": "new-volume"},
                            "spec": {
                                "storageClassName": "new-class",
                                "accessModes": ["ReadWriteOnce"],
                                "resources": {"requests": {"storage": "2Gi"}}
                            }
                        }
                    ]
                }
            }
        }

        result = self._render_chart(values)
        assert result.returncode == 0, f"Helm render failed: {result.stderr}"

        # New location should take precedence
        assert "new-volume" in result.stdout, "New volume not found"
        assert "new-class" in result.stdout, "New storage class not found"


class TestYamlStructure:
    """Tests for YAML structure and syntax."""

    def test_values_yaml_is_valid(self):
        """Verify values.yaml is valid YAML."""
        with open(VALUES_YAML) as f:
            data = yaml.safe_load(f)
        assert data is not None
        assert isinstance(data, dict)

    def test_celery_section_has_all_fields(self):
        """Verify workers.celery has expected structure."""
        with open(VALUES_YAML) as f:
            values = yaml.safe_load(f)

        celery = values["workers"]["celery"]
        expected_fields = ["enabled", "gracefulTermination", "persistence", "hostAliases",
                          "volumeClaimTemplates", "schedulerName"]

        for field in expected_fields:
            assert field in celery, f"Expected field {field} in workers.celery"


class TestCommentsAndDocumentation:
    """Tests for documentation and comments."""

    def test_new_field_has_documentation_comment(self):
        """Verify new volumeClaimTemplates has documentation comments."""
        with open(VALUES_YAML) as f:
            content = f.read()

        # Find the celery section with volumeClaimTemplates
        celery_section_start = content.find("celery:")
        celery_section = content[celery_section_start:]

        # Find the volumeClaimTemplates in that section
        vct_start = celery_section.find("volumeClaimTemplates:")
        vct_section = celery_section[vct_start-500:vct_start+100]

        assert "Additional volume claim templates" in vct_section or \
               "Requires mounting" in vct_section, \
            "Documentation comment missing for new field"


class TestRepoPassToPass:
    """Pass-to-pass tests - verify repo CI checks pass on base and after fix."""

    def test_repo_helm_lint(self):
        """Repo's Helm chart linting passes (pass_to_pass)."""
        r = subprocess.run(
            ["helm", "lint", "."],
            cwd=CHART,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert r.returncode == 0, f"Helm lint failed:\n{r.stderr}"

    def test_repo_helm_template_default(self):
        """Repo's Helm chart templates with default values (pass_to_pass)."""
        r = subprocess.run(
            ["helm", "template", "test", ".", "--values", "values.yaml"],
            cwd=CHART,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert r.returncode == 0, f"Helm template failed:\n{r.stderr[-500:]}"

    def test_repo_values_schema_valid_json(self):
        """Repo's values.schema.json is valid JSON (pass_to_pass)."""
        import json
        with open(VALUES_SCHEMA) as f:
            schema = json.load(f)
        assert schema is not None
        assert "properties" in schema
        # Verify workers property exists
        assert "workers" in schema.get("properties", {}), "workers not in schema properties"

    def test_repo_values_yaml_valid(self):
        """Repo's values.yaml is valid YAML (pass_to_pass)."""
        with open(VALUES_YAML) as f:
            values = yaml.safe_load(f)
        assert values is not None
        assert isinstance(values, dict)
        # Verify workers section exists
        assert "workers" in values, "workers section not in values"
