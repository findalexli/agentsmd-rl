"""
Task: analog-v19-template-package-files
Repo: analogjs/analog @ 3f475f278250ab3c2b5da22f03d9e2b7ccbf6000
PR:   1756

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import tarfile
import tempfile
from pathlib import Path

import pytest

REPO = "/workspace/analog"
CREATE_ANALOG_DIR = f"{REPO}/packages/create-analog"
PACKAGE_JSON = f"{CREATE_ANALOG_DIR}/package.json"


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------

def test_package_json_valid():
    """package.json must be valid JSON with a files array."""
    with open(PACKAGE_JSON) as f:
        data = json.load(f)
    assert isinstance(data, dict), "package.json should be a JSON object"
    assert "files" in data, "package.json should have 'files' array"
    assert isinstance(data["files"], list), "files should be a list"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

def test_template_angular_v19_in_files():
    """template-angular-v19 must be listed in package.json files array."""
    with open(PACKAGE_JSON) as f:
        data = json.load(f)

    files = data.get("files", [])
    assert "template-angular-v19" in files, \
        f"template-angular-v19 missing from files array. Current files: {files}"


def test_template_angular_v19_in_npm_pack():
    """
    template-angular-v19 must be included in npm pack tarball.
    This is the behavioral test that verifies the fix actually works.
    """
    # First check that template-angular-v19 is in package.json files array
    with open(PACKAGE_JSON) as f:
        data = json.load(f)
    files = data.get("files", [])
    if "template-angular-v19" not in files:
        pytest.skip("template-angular-v19 not in package.json files array (fix not applied)")

    # Run npm pack to create a tarball and check it includes the template
    result = subprocess.run(
        ["npm", "pack", "--dry-run", "--json"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=CREATE_ANALOG_DIR,
    )

    # If npm pack fails, try alternative approach with actual pack
    if result.returncode != 0 or not result.stdout.strip():
        # Fallback: create actual tarball and inspect it
        with tempfile.TemporaryDirectory() as tmpdir:
            pack_result = subprocess.run(
                ["npm", "pack", "--pack-destination", tmpdir],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=CREATE_ANALOG_DIR,
            )
            assert pack_result.returncode == 0, \
                f"npm pack failed: {pack_result.stderr}"

            # Find the created tarball
            tarballs = list(Path(tmpdir).glob("*.tgz"))
            assert len(tarballs) > 0, "npm pack did not create a tarball"

            # Check tarball contains template-angular-v19
            with tarfile.open(tarballs[0], "r:gz") as tar:
                members = tar.getnames()
                template_in_tarball = any(
                    "template-angular-v19" in m for m in members
                )
                assert template_in_tarball, \
                    f"template-angular-v19 not found in npm pack tarball. Members: {members[:20]}..."
    else:
        # Parse JSON output from dry-run
        try:
            pack_data = json.loads(result.stdout)
            if isinstance(pack_data, list) and len(pack_data) > 0:
                files_in_pack = pack_data[0].get("files", [])
                files_list = [f.get("path", "") for f in files_in_pack]
            else:
                files_list = []
        except json.JSONDecodeError:
            files_list = []

        template_in_pack = any(
            "template-angular-v19" in f for f in files_list
        )
        assert template_in_pack, \
            f"template-angular-v19 not found in npm pack output. Files: {files_list[:20]}..."


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


def test_npm_pack_includes_all_templates():
    """
    Repo test: npm pack should include all template directories.
    This is a pass-to-pass gate to ensure we don't break packaging.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        pack_result = subprocess.run(
            ["npm", "pack", "--pack-destination", tmpdir],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=CREATE_ANALOG_DIR,
        )
        assert pack_result.returncode == 0, \
            f"npm pack failed: {pack_result.stderr}"

        # Find the created tarball
        tarballs = list(Path(tmpdir).glob("*.tgz"))
        assert len(tarballs) > 0, "npm pack did not create a tarball"

        # Check tarball contains all expected templates
        with tarfile.open(tarballs[0], "r:gz") as tar:
            members = tar.getnames()
            expected_templates = [
                "template-angular-v16",
                "template-angular-v17",
                "template-angular-v18",
                "template-blog",
                "template-latest",
                "template-minimal",
            ]
            missing = []
            for template in expected_templates:
                if not any(template in m for m in members):
                    missing.append(template)
            assert not missing, f"Templates missing from npm pack: {missing}"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# -----------------------------------------------------------------------------

def test_repo_package_json_valid():
    """Repo CI: All package.json files must be valid JSON (pass_to_pass)."""
    package_json_files = [
        f"{REPO}/package.json",
        f"{CREATE_ANALOG_DIR}/package.json",
    ]

    for pkg_file in package_json_files:
        with open(pkg_file) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {pkg_file}: {e}")


def test_repo_create_analog_package_has_files_array():
    """
    Repo CI: create-analog package.json must have a files array (pass_to_pass).
    This ensures the package is properly configured for npm publishing.
    """
    with open(f"{CREATE_ANALOG_DIR}/package.json") as f:
        data = json.load(f)

    assert "files" in data, "create-analog package.json must have 'files' array"
    assert isinstance(data["files"], list), "files must be a list"
    assert len(data["files"]) > 0, "files array must not be empty"


def test_repo_all_templates_exist_on_filesystem():
    """
    Repo CI: All template directories listed in files array must exist (pass_to_pass).
    This ensures package.json files array matches the actual filesystem.
    """
    with open(f"{CREATE_ANALOG_DIR}/package.json") as f:
        data = json.load(f)

    files = data.get("files", [])
    template_entries = [f for f in files if f.startswith("template-")]

    missing_dirs = []
    for template in template_entries:
        template_dir = Path(f"{CREATE_ANALOG_DIR}/{template}")
        if not template_dir.exists() or not template_dir.is_dir():
            missing_dirs.append(template)

    assert not missing_dirs, f"Template directories in files array but missing from filesystem: {missing_dirs}"


def test_repo_templates_have_required_files():
    """
    Repo CI: All template directories must contain required files (pass_to_pass).
    This validates template structure without requiring a build.
    """
    template_dirs = [
        d for d in Path(CREATE_ANALOG_DIR).iterdir()
        if d.is_dir() and d.name.startswith("template-")
    ]

    for template_dir in template_dirs:
        # Each template should have at minimum a package.json
        required_files = ["package.json"]
        for req_file in required_files:
            file_path = template_dir / req_file
            assert file_path.exists(), f"Template {template_dir.name} missing required file: {req_file}"


def test_repo_npm_pack_dry_run_succeeds():
    """
    Repo CI: npm pack --dry-run must succeed (pass_to_pass).
    Validates package structure without creating tarball.
    """
    result = subprocess.run(
        ["npm", "pack", "--dry-run", "--json"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=CREATE_ANALOG_DIR,
    )
    # Note: npm pack --dry-run may fail if there are issues, but even
    # without --json output, a zero return code means the package is valid
    assert result.returncode == 0, f"npm pack --dry-run failed: {result.stderr}"


def test_repo_prettier_check_create_analog():
    """
    Repo CI: prettier --check must pass on create-analog files (pass_to_pass).
    This is the actual CI lint check from .github/workflows/ci.yml.
    """
    result = subprocess.run(
        ["npx", "prettier", "--check", "package.json", "index.js"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=CREATE_ANALOG_DIR,
    )
    assert result.returncode == 0, f"prettier check failed:\n{result.stderr}"


def test_repo_node_check_index_js():
    """
    Repo CI: node --check passes on create-analog index.js (pass_to_pass).
    """
    result = subprocess.run(
        ["node", "--check", "index.js"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=CREATE_ANALOG_DIR,
    )
    assert result.returncode == 0, f"node check failed:\n{result.stderr}"
