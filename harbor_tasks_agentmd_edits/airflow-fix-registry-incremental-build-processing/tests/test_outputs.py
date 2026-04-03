"""
Task: airflow-fix-registry-incremental-build-processing
Repo: apache/airflow @ af239855e76fbf076fe226ee5fb044ab4965cef5
PR:   63769

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/airflow"


# ---------------------------------------------------------------------------
# Helpers (same schema as upstream test helpers)
# ---------------------------------------------------------------------------

def _provider(provider_id: str, name: str, last_updated: str) -> dict:
    return {
        "id": provider_id,
        "name": name,
        "package_name": f"apache-airflow-providers-{provider_id}",
        "description": f"{name} provider",
        "lifecycle": "production",
        "logo": None,
        "version": "1.0.0",
        "versions": ["1.0.0"],
        "airflow_versions": ["3.0+"],
        "pypi_downloads": {"weekly": 0, "monthly": 0, "total": 0},
        "module_counts": {"operator": 1},
        "categories": [],
        "connection_types": [],
        "requires_python": ">=3.10",
        "dependencies": [],
        "optional_extras": {},
        "dependents": [],
        "related_providers": [],
        "docs_url": "https://example.invalid/docs",
        "source_url": "https://example.invalid/source",
        "pypi_url": "https://example.invalid/pypi",
        "first_released": "",
        "last_updated": last_updated,
    }


def _module(module_id: str, provider_id: str) -> dict:
    return {
        "id": module_id,
        "name": "ExampleOperator",
        "type": "operator",
        "import_path": f"airflow.providers.{provider_id}.operators.example.ExampleOperator",
        "module_path": f"airflow.providers.{provider_id}.operators.example",
        "short_description": "Example operator",
        "docs_url": "https://example.invalid/docs",
        "source_url": "https://example.invalid/source",
        "category": "test",
        "provider_id": provider_id,
        "provider_name": provider_id.capitalize(),
    }


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files parse without errors."""
    files = [
        "dev/breeze/src/airflow_breeze/commands/registry_commands.py",
        "dev/registry/merge_registry_data.py",
        "dev/registry/extract_connections.py",
    ]
    for f in files:
        path = Path(REPO) / f
        assert path.exists(), f"{f} does not exist"
        r = subprocess.run(
            [sys.executable, "-m", "py_compile", str(path)],
            capture_output=True, timeout=10,
        )
        assert r.returncode == 0, f"{f} has syntax errors: {r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_provider_flag_forwarded_to_all_scripts():
    """extract_data() must forward --provider flag to extract_parameters and extract_connections."""
    src = (Path(REPO) / "dev/breeze/src/airflow_breeze/commands/registry_commands.py").read_text()

    # Find lines in the command construction that invoke each extraction script
    script_names = ["extract_metadata.py", "extract_parameters.py", "extract_connections.py"]
    for script in script_names:
        # Find the line(s) that reference this script in the command string
        matching_lines = [
            line for line in src.splitlines()
            if script in line and "python" in line.lower() and "dev/registry/" in line
        ]
        assert len(matching_lines) >= 1, f"No command line found invoking {script}"

        for line in matching_lines:
            # Each script invocation must include provider flag (variable or inline)
            assert "provider_flag" in line or "--provider" in line, (
                f"{script} invocation does not include provider flag: {line.strip()}"
            )


# [pr_diff] fail_to_pass

    sys.path.insert(0, str(Path(REPO) / "dev" / "registry"))
    from merge_registry_data import merge

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        output_dir = tmp / "output"
        output_dir.mkdir()

        # Existing data: two providers with modules
        (tmp / "existing_providers.json").write_text(json.dumps({
            "providers": [
                _provider("amazon", "Amazon", "2024-01-01"),
                _provider("google", "Google", "2024-02-01"),
            ]
        }))
        (tmp / "existing_modules.json").write_text(json.dumps({
            "modules": [
                _module("amazon-s3-op", "amazon"),
                _module("google-bq-op", "google"),
            ]
        }))
        # Incremental update for amazon only
        (tmp / "new_providers.json").write_text(json.dumps({
            "providers": [_provider("amazon", "Amazon", "2025-01-01")]
        }))
        # new_modules file does NOT exist (incremental --provider skips modules.json)
        missing_modules = tmp / "nonexistent_modules.json"

        # This must not raise FileNotFoundError
        merge(
            tmp / "existing_providers.json",
            tmp / "existing_modules.json",
            tmp / "new_providers.json",
            missing_modules,
            output_dir,
        )

        # Verify output files written
        assert (output_dir / "providers.json").exists(), "providers.json not written"
        assert (output_dir / "modules.json").exists(), "modules.json not written"

        # Verify google's modules preserved (not affected by amazon update)
        result = json.loads((output_dir / "modules.json").read_text())
        modules = result["modules"]
        assert any(m["id"] == "google-bq-op" for m in modules), \
            "Existing modules for non-updated providers should be preserved"

        # Amazon modules should be removed (no new modules provided to replace them)
        assert not any(m["provider_id"] == "amazon" for m in modules), \
            "Old amazon modules should be removed when no new modules replace them"


# ---------------------------------------------------------------------------
# Config file update checks (config_edit) — fail_to_pass
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must mention the exclusion behavior for incremental builds
    assert "exclude" in content_lower or "non-target" in content_lower, \
        "AGENTS.md should describe S3 sync exclusion of non-target providers"
    assert "api/providers" in agents_md, \
        "AGENTS.md should mention the api/providers/ subtree being excluded"


# [config_edit] fail_to_pass

    # Must document that sync is selective (not a simple full sync)
    assert "selective" in content_lower or "exclude" in content_lower, \
        "README.md should describe the selective S3 sync behavior"
    # Must reference the api/providers subtree
    assert "api/providers" in readme, \
        "README.md should mention the api/providers/ subtree"


# [config_edit] fail_to_pass

    # Must document the known limitation about Eleventy generating empty stubs
    # Note: "eleventy" alone is insufficient — it already appears in the base README
    assert "known limitation" in content_lower, \
        "README.md should document the known Eleventy pagination limitation"
    assert "fallback" in content_lower or "empty fallback" in content_lower \
        or "connection_types" in readme, \
        "README.md should mention that Eleventy emits empty/fallback JSON for non-target providers"
