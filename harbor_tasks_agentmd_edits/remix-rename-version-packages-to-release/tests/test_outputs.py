"""
Task: remix-rename-version-packages-to-release
Repo: remix-run/remix @ 130fbdc7b808a2d313363458dabc00caf036f482
PR:   11000

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/remix"


def _run_ts(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a temp .ts file in the repo and run it with node."""
    script_path = Path(REPO) / "_eval_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings", str(script_path)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Core TypeScript utility files must parse without syntax errors."""
    # These files exist on both base and fixed commits
    files_to_check = [
        "scripts/utils/changes.ts",
        "scripts/utils/packages.ts",
        "scripts/publish.ts",
    ]
    for f in files_to_check:
        fpath = Path(REPO) / f
        assert fpath.exists(), f"{f} does not exist"
        content = fpath.read_text()
        # Basic TS syntax check: file should be non-empty and not contain obvious errors
        assert len(content) > 100, f"{f} is suspiciously short ({len(content)} chars)"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression (repo_tests)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's linter passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "lint"], capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "typecheck"], capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_changes_validate():
    """Change files validation passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "changes:validate"], capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Changes validation failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_format_check():
    """Prettier format check passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "format:check"], capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_scripts_tsc():
    """Scripts directory TypeScript compilation passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"], capture_output=True, text=True, timeout=600, cwd=f"{REPO}/scripts",
    )
    assert r.returncode == 0, f"Scripts TypeScript check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_release_pr_script_renamed():
    """The script must be renamed from changes-version-pr.ts to release-pr.ts."""
    assert (Path(REPO) / "scripts" / "release-pr.ts").exists(), \
        "scripts/release-pr.ts must exist"
    assert not (Path(REPO) / "scripts" / "changes-version-pr.ts").exists(), \
        "scripts/changes-version-pr.ts should be removed (renamed)"


# [pr_diff] fail_to_pass
def test_release_pr_utils_renamed():
    """The util must be renamed from version-pr.ts to release-pr.ts."""
    assert (Path(REPO) / "scripts" / "utils" / "release-pr.ts").exists(), \
        "scripts/utils/release-pr.ts must exist"
    assert not (Path(REPO) / "scripts" / "utils" / "version-pr.ts").exists(), \
        "scripts/utils/version-pr.ts should be removed (renamed)"


# [pr_diff] fail_to_pass
def test_commit_message_subject():
    """generateCommitMessage must use 'Release' not 'Version Packages'."""
    content = (Path(REPO) / "scripts" / "utils" / "changes.ts").read_text()
    assert "let subject = 'Release'" in content, \
        "generateCommitMessage should use 'Release' as commit subject"
    assert "Version Packages" not in content, \
        "changes.ts should not reference 'Version Packages'"


# [pr_diff] fail_to_pass
def test_release_pr_title_and_branch():
    """The release PR script must use 'Release' title and 'release-pr/main' branch."""
    content = (Path(REPO) / "scripts" / "release-pr.ts").read_text()
    assert "'Release'" in content or '"Release"' in content, \
        "PR title should be 'Release'"
    assert "release-pr/main" in content, \
        "PR branch should be 'release-pr/main'"
    assert "Version Packages" not in content, \
        "release-pr.ts should not reference 'Version Packages'"


# [pr_diff] fail_to_pass
def test_package_utils_new_functions():
    """packages.ts must export getPackageShortName, getGitTag, getGitHubReleaseUrl."""
    result = _run_ts("""
import { getPackageShortName, getGitTag, getGitHubReleaseUrl } from './scripts/utils/packages.ts'

let out = {
    scoped: getPackageShortName('@remix-run/headers'),
    unscoped: getPackageShortName('remix'),
    scopedAlt: getPackageShortName('@remix-run/fetch-router'),
    tag1: getGitTag('@remix-run/headers', '0.11.0'),
    tag2: getGitTag('remix', '3.0.0'),
    url: getGitHubReleaseUrl('@remix-run/headers', '0.11.0'),
}
console.log(JSON.stringify(out))
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["scoped"] == "headers", f"Expected 'headers', got {data['scoped']}"
    assert data["unscoped"] == "remix", f"Expected 'remix', got {data['unscoped']}"
    assert data["scopedAlt"] == "fetch-router", f"Expected 'fetch-router', got {data['scopedAlt']}"
    assert data["tag1"] == "headers@0.11.0", f"Expected 'headers@0.11.0', got {data['tag1']}"
    assert data["tag2"] == "remix@3.0.0", f"Expected 'remix@3.0.0', got {data['tag2']}"
    assert "headers@0.11.0" in data["url"], f"URL should contain tag: {data['url']}"
    assert "github.com/remix-run/remix" in data["url"], f"URL should point to remix repo: {data['url']}"


# [pr_diff] fail_to_pass
def test_dependency_bumps_in_changelog():
    """changes.ts must include DependencyBump interface and dependencyBumps on PackageRelease."""
    content = (Path(REPO) / "scripts" / "utils" / "changes.ts").read_text()
    assert "interface DependencyBump" in content or "export interface DependencyBump" in content, \
        "DependencyBump interface must be defined"
    assert "dependencyBumps" in content, \
        "PackageRelease must have dependencyBumps field"
    assert "getTransitiveDependents" in content, \
        "changes.ts must import/use getTransitiveDependents"


# [pr_diff] fail_to_pass
def test_workflow_yaml_updated():
    """The workflow YAML must be renamed and reference release-pr.ts."""
    assert (Path(REPO) / ".github" / "workflows" / "release-pr.yaml").exists(), \
        "release-pr.yaml workflow must exist"
    assert not (Path(REPO) / ".github" / "workflows" / "changes-version-pr.yaml").exists(), \
        "changes-version-pr.yaml should be removed"
    content = (Path(REPO) / ".github" / "workflows" / "release-pr.yaml").read_text()
    assert "release-pr.ts" in content, "Workflow should run release-pr.ts"
    assert '"Release"' in content or "'Release'" in content, \
        "Workflow name should reference 'Release'"


# ---------------------------------------------------------------------------
# Config/documentation update tests (agentmd-edit)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:58 @ 130fbdc7b808a2d313363458dabc00caf036f482
def test_agents_md_references_release_pr():
    """AGENTS.md must reference 'release-pr' workflow and 'Release' PR naming."""
    content = (Path(REPO) / "AGENTS.md").read_text()
    assert "release-pr" in content, \
        "AGENTS.md must reference the release-pr workflow/script"
    assert "release-pr.yaml" in content or "release-pr.ts" in content, \
        "AGENTS.md must link to the renamed file(s)"
    assert "changes-version-pr" not in content, \
        "AGENTS.md must not reference the old changes-version-pr name"
    assert "Version Packages" not in content, \
        "AGENTS.md must not reference 'Version Packages'"


# [pr_diff] fail_to_pass
def test_contributing_md_references_release_pr():
    """CONTRIBUTING.md must reference 'release-pr' workflow and 'Release' PR naming."""
    content = (Path(REPO) / "CONTRIBUTING.md").read_text()
    assert "release-pr" in content, \
        "CONTRIBUTING.md must reference the release-pr workflow"
    assert "changes-version-pr" not in content, \
        "CONTRIBUTING.md must not reference the old changes-version-pr name"
    assert "Version Packages" not in content, \
        "CONTRIBUTING.md must not reference 'Version Packages'"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - cleanup
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_publish_script_no_old_refs():
    """publish.ts should reference 'Release' PR, not 'Version Packages' PR."""
    content = (Path(REPO) / "scripts" / "publish.ts").read_text()
    assert "Version Packages" not in content, \
        "publish.ts should not reference 'Version Packages'"
