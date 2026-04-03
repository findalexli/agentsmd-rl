"""
Task: remix-release-rename-transitive-deps
Repo: remix-run/remix @ 130fbdc7b808a2d313363458dabc00caf036f482
PR:   11000

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/remix"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must exist and be non-empty."""
    files = [
        "scripts/release-pr.ts",
        "scripts/utils/release-pr.ts",
        "scripts/utils/changes.ts",
        "scripts/utils/packages.ts",
        "scripts/publish.ts",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        content = p.read_text()
        assert len(content) > 100, f"{f} must have substantial content"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests: renaming
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_release_pr_script_renamed():
    """Main PR script must be at scripts/release-pr.ts (not changes-version-pr.ts)."""
    new_path = Path(REPO) / "scripts" / "release-pr.ts"
    old_path = Path(REPO) / "scripts" / "changes-version-pr.ts"
    assert new_path.exists(), "scripts/release-pr.ts must exist"
    assert not old_path.exists(), "scripts/changes-version-pr.ts should be removed"


# [pr_diff] fail_to_pass
def test_release_pr_utils_renamed():
    """Utility module must be at scripts/utils/release-pr.ts (not version-pr.ts)."""
    new_path = Path(REPO) / "scripts" / "utils" / "release-pr.ts"
    old_path = Path(REPO) / "scripts" / "utils" / "version-pr.ts"
    assert new_path.exists(), "scripts/utils/release-pr.ts must exist"
    assert not old_path.exists(), "scripts/utils/version-pr.ts should be removed"


# [pr_diff] fail_to_pass
def test_pr_title_is_release():
    """The release-pr.ts script must use 'Release' as the PR title, not 'Version Packages'."""
    content = (Path(REPO) / "scripts" / "release-pr.ts").read_text()
    # Must contain the new title assignment
    assert re.search(r"""prTitle\s*=\s*['"]Release['"]""", content), \
        "release-pr.ts must set prTitle = 'Release'"
    # Must NOT contain old title
    assert "Version Packages" not in content, \
        "release-pr.ts must not reference 'Version Packages'"


# [pr_diff] fail_to_pass
def test_commit_message_subject():
    """generateCommitMessage must use 'Release' as the commit subject."""
    content = (Path(REPO) / "scripts" / "utils" / "changes.ts").read_text()
    assert re.search(r"""let\s+subject\s*=\s*['"]Release['"]""", content), \
        "changes.ts must set subject = 'Release'"


# [pr_diff] fail_to_pass
def test_dependency_bumps_in_package_release():
    """PackageRelease interface must include dependencyBumps field."""
    content = (Path(REPO) / "scripts" / "utils" / "changes.ts").read_text()
    assert "dependencyBumps" in content, \
        "changes.ts must define dependencyBumps in PackageRelease"
    assert "DependencyBump" in content, \
        "changes.ts must define DependencyBump interface"


# [pr_diff] fail_to_pass
def test_get_transitive_dependents_exists():
    """packages.ts must export getTransitiveDependents function."""
    content = (Path(REPO) / "scripts" / "utils" / "packages.ts").read_text()
    assert "export function getTransitiveDependents" in content, \
        "packages.ts must export getTransitiveDependents"
    assert "export function buildReverseDependencyGraph" in content, \
        "packages.ts must export buildReverseDependencyGraph"
    assert "export function getGitHubReleaseUrl" in content, \
        "packages.ts must export getGitHubReleaseUrl"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — config/docs update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — workflow file and PR branch name
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_workflow_references_consistent():
    """Workflow YAML and scripts must reference consistent naming."""
    workflow = Path(REPO) / ".github" / "workflows" / "release-pr.yaml"
    if workflow.exists():
        content = workflow.read_text()
        assert "release-pr" in content or "Release" in content, \
            "Workflow file must use updated naming"

    # release-pr.ts must import from utils/release-pr.ts
    script = Path(REPO) / "scripts" / "release-pr.ts"
    if script.exists():
        content = script.read_text()
        assert "release-pr" in content, \
            "release-pr.ts must import from ./utils/release-pr"

    # publish.ts must reference "Release" PR
    publish = Path(REPO) / "scripts" / "publish.ts"
    content = publish.read_text()
    assert "Version Packages" not in content, \
        "publish.ts must not reference old 'Version Packages' naming"
