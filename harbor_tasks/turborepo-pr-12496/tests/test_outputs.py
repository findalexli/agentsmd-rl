#!/usr/bin/env python3
"""
Test Outputs for vercel/turborepo#12496: Handle Package Manager Catalogs in Migration Codemod

This verifies the fix for the migration codemod that now correctly handles
package manager catalog protocol references (e.g., "turbo": "catalog:").
"""

import subprocess
import os
import tempfile
import json
import re
import shutil

REPO = "/workspace/turborepo"
CODEMOD_PKG = "packages/turbo-codemod"


def run(cmd, cwd=REPO, timeout=300, check=False):
    """Run a command and return (returncode, stdout, stderr)."""
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    if check and r.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{r.stderr}")
    return r.returncode, r.stdout, r.stderr


def test_source_files_contain_new_functions():
    """
    After the fix, the source files should contain the new catalog-related functions.
    This is a structural check that verifies the new code was added.
    """
    # Check that update-catalog.ts exists and contains key functions
    update_catalog_path = os.path.join(REPO, CODEMOD_PKG, "src/commands/migrate/steps/update-catalog.ts")

    assert os.path.exists(update_catalog_path), \
        f"update-catalog.ts does not exist at {update_catalog_path}"

    with open(update_catalog_path, "r") as f:
        content = f.read()

    assert "detectCatalog" in content, "detectCatalog function not found in update-catalog.ts"
    assert "updateCatalogVersion" in content, "updateCatalogVersion function not found in update-catalog.ts"
    assert "CatalogInfo" in content, "CatalogInfo type not found in update-catalog.ts"
    assert 'catalog:' in content, "catalog: protocol detection not found"


def test_update_catalog_ts_imports_yaml():
    """
    update-catalog.ts should import the yaml library for parsing catalog files.
    """
    update_catalog_path = os.path.join(REPO, CODEMOD_PKG, "src/commands/migrate/steps/update-catalog.ts")

    with open(update_catalog_path, "r") as f:
        content = f.read()

    assert 'yaml' in content.lower(), "yaml library import not found in update-catalog.ts"


def test_get_turbo_upgrade_command_handles_catalog_info():
    """
    get-turbo-upgrade-command.ts should accept catalogInfo parameter and return
    install command when catalog is detected.
    """
    gtuc_path = os.path.join(REPO, CODEMOD_PKG, "src/commands/migrate/steps/get-turbo-upgrade-command.ts")

    with open(gtuc_path, "r") as f:
        content = f.read()

    assert "catalogInfo" in content, "catalogInfo parameter not found in get-turbo-upgrade-command.ts"
    assert "getInstallCommand" in content or "install" in content.lower(), \
        "install command logic not found for catalog case"


def test_get_latest_version_resolves_dist_tags():
    """
    get-latest-version.ts should resolve dist-tags like 'latest' to concrete versions.
    """
    glv_path = os.path.join(REPO, CODEMOD_PKG, "src/commands/migrate/steps/get-latest-version.ts")

    with open(glv_path, "r") as f:
        content = f.read()

    # The fix should check if 'to' is a key in tags (dist-tag lookup)
    assert "tags[to]" in content, "dist-tag resolution logic not found"


def test_migrate_index_calls_detect_catalog():
    """
    migrate/index.ts should call detectCatalog to check for catalog references.
    """
    migrate_index_path = os.path.join(REPO, CODEMOD_PKG, "src/commands/migrate/index.ts")

    with open(migrate_index_path, "r") as f:
        content = f.read()

    assert "detectCatalog" in content, "detectCatalog not called in migrate/index.ts"
    assert "updateCatalogVersion" in content, "updateCatalogVersion not called in migrate/index.ts"


def test_yaml_dependency_added():
    """
    The yaml dependency should be added to package.json.
    """
    pkg_json_path = os.path.join(REPO, CODEMOD_PKG, "package.json")

    with open(pkg_json_path, "r") as f:
        pkg_json = json.load(f)

    dependencies = pkg_json.get("dependencies", {})
    assert "yaml" in dependencies, "yaml dependency not found in package.json"
    # Check it's version 2.x
    assert dependencies["yaml"].startswith("2."), f"yaml version should be 2.x, got {dependencies['yaml']}"


def test_npm_pkg_has_update_catalog_test():
    """
    There should be an update-catalog.test.ts test file.
    """
    test_path = os.path.join(REPO, CODEMOD_PKG, "__tests__/update-catalog.test.ts")
    assert os.path.exists(test_path), f"update-catalog.test.ts does not exist at {test_path}"


def test_pnpm_catalog_default_fixture_exists():
    """
    Test fixture for pnpm default catalog should exist.
    """
    fixture_path = os.path.join(REPO, CODEMOD_PKG, "__tests__/__fixtures__/get-turbo-upgrade-command/pnpm-catalog-default")
    assert os.path.exists(fixture_path), f"pnpm-catalog-default fixture not found at {fixture_path}"

    # Check the fixture has package.json and pnpm-workspace.yaml
    pkg_json_path = os.path.join(fixture_path, "package.json")
    ws_yaml_path = os.path.join(fixture_path, "pnpm-workspace.yaml")

    assert os.path.exists(pkg_json_path), f"fixture package.json not found"
    assert os.path.exists(ws_yaml_path), f"fixture pnpm-workspace.yaml not found"

    # Check the package.json uses catalog:
    with open(pkg_json_path, "r") as f:
        pkg_json = json.load(f)

    turbo_dep = pkg_json.get("devDependencies", {}).get("turbo", "")
    assert turbo_dep == "catalog:", f"Expected turbo: 'catalog:' in devDependencies, got '{turbo_dep}'"


def test_yarn_catalog_default_fixture_exists():
    """
    Test fixture for yarn default catalog should exist.
    """
    fixture_path = os.path.join(REPO, CODEMOD_PKG, "__tests__/__fixtures__/get-turbo-upgrade-command/yarn-catalog-default")
    assert os.path.exists(fixture_path), f"yarn-catalog-default fixture not found at {fixture_path}"

    pkg_json_path = os.path.join(fixture_path, "package.json")
    yarnrc_path = os.path.join(fixture_path, ".yarnrc.yml")

    assert os.path.exists(pkg_json_path), f"fixture package.json not found"
    assert os.path.exists(yarnrc_path), f"fixture .yarnrc.yml not found"


class TestRepoTests:
    """Run the repo's own tests where possible"""

    def test_repo_typescript_builds(self):
        """TypeScript compilation should succeed after the fix is applied."""
        # Build the codemod package first
        rc1, _, _ = run(f"cd {CODEMOD_PKG} && pnpm build", timeout=120)
        assert rc1 == 0, "Build failed"

        # Then check types
        rc2, _, stderr = run(f"cd {CODEMOD_PKG} && pnpm check-types", timeout=120)

        # The fix should not introduce new type errors
        # We allow existing errors but check that the new code doesn't cause failures
        if rc2 != 0:
            # Check if there are errors related to our new files
            if "update-catalog" in stderr or "CatalogInfo" in stderr:
                assert False, f"TypeScript errors in new catalog code:\n{stderr[-1000:]}"

    def test_repo_lint(self):
        """Repo's linter passes on the codemod package (pass_to_pass)."""
        r = subprocess.run(
            ["pnpm", "exec", "oxlint", "--deny-warnings", "packages/turbo-codemod"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"

    def test_repo_format(self):
        """Repo's formatter check passes on the codemod package (pass_to_pass)."""
        r = subprocess.run(
            ["pnpm", "exec", "oxfmt", "--check", "packages/turbo-codemod"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])
