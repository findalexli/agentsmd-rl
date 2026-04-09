"""
Task: analog-v19-template-package-files
Repo: analogjs/analog @ 3f475f278250ab3c2b5da22f03d9e2b7ccbf6000
PR:   1756

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

import pytest

REPO = "/workspace/analog"
CREATE_ANALOG_DIR = f"{REPO}/packages/create-analog"
PACKAGE_JSON = f"{CREATE_ANALOG_DIR}/package.json"


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------

def test_package_json_valid():
    """package.json must be valid JSON."""
    with open(PACKAGE_JSON) as f:
        data = json.load(f)
    assert isinstance(data, dict), "package.json should be a JSON object"
    assert "files" in data, "package.json should have 'files' array"
    assert isinstance(data["files"], list), "files should be a list"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

def test_template_angular_v19_in_files():
    """template-angular-v19 must be in package.json files array."""
    with open(PACKAGE_JSON) as f:
        data = json.load(f)

    files = data.get("files", [])
    assert "template-angular-v19" in files, \
        f"template-angular-v19 missing from files array. Current files: {files}"


def test_template_angular_v19_exists():
    """template-angular-v19 directory must exist in the filesystem."""
    template_dir = Path(f"{CREATE_ANALOG_DIR}/template-angular-v19")
    assert template_dir.exists(), \
        f"template-angular-v19 directory does not exist at {template_dir}"
    assert template_dir.is_dir(), \
        f"template-angular-v19 is not a directory"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# -----------------------------------------------------------------------------

def test_other_templates_still_present():
    """Other template entries should not be removed from files array."""
    with open(PACKAGE_JSON) as f:
        data = json.load(f)

    files = data.get("files", [])
    other_templates = [
        "template-angular-v16",
        "template-angular-v17",
        "template-angular-v18",
        "template-blog",
        "template-latest",
        "template-minimal",
    ]

    missing = [t for t in other_templates if t not in files]
    assert not missing, f"Other templates were incorrectly removed: {missing}"


def test_template_files_non_empty():
    """template-angular-v19 directory must contain actual template files."""
    template_dir = Path(f"{CREATE_ANALOG_DIR}/template-angular-v19")

    # Directory should exist (fail fast if not)
    if not template_dir.exists():
        pytest.skip("template-angular-v19 directory does not exist")

    # Get all files recursively (excluding empty directories)
    files = [f for f in template_dir.rglob("*") if f.is_file()]
    assert len(files) > 0, "template-angular-v19 directory is empty (no template files)"
