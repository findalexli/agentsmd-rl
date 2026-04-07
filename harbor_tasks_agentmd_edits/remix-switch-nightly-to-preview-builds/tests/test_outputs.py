"""
Task: remix-switch-nightly-to-preview-builds
Repo: remix-run/remix @ 721dac4c6704d5b3e8428887af21accdcb3b23ea
PR:   remix-run/remix#11003

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/remix"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structural checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript and YAML files must parse without errors."""
    script_path = Path(f"{REPO}/scripts/setup-installable-branch.ts")
    assert script_path.exists(), "setup-installable-branch.ts must exist"
    content = script_path.read_text()
    # Basic TypeScript parse: balanced braces, no stray characters
    assert content.count("{") == content.count("}"), "Unbalanced braces in script"
    assert "parseArgs" in content, "Script must contain parseArgs call"

    preview_wf = Path(f"{REPO}/.github/workflows/preview.yml")
    assert preview_wf.exists(), "preview.yml must exist"
    yaml_content = preview_wf.read_text()
    # Basic YAML sanity: key lines are present
    assert "name:" in yaml_content, "YAML must have a name field"
    assert "jobs:" in yaml_content, "YAML must have jobs section"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavior tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_setup_script_requires_positional_arg():
    """setup-installable-branch.ts must require a branch name as positional argument."""
    script = Path(f"{REPO}/scripts/setup-installable-branch.ts").read_text()
    # The fixed version should not have a default fallback to 'nightly'
    # On base commit: positionals[0] || values.branch || 'nightly'
    # On fix: positionals[0] with explicit check
    assert "positionals[0]" in script, "Script must read branch from positionals[0]"
    # Must have an error when no arg provided (not a silent default)
    assert "must provide" in script.lower() or "must supply" in script.lower() or \
           "you must" in script.lower() or "required" in script.lower(), \
        "Script must throw error when no branch name is provided"
    # Must NOT have 'nightly' as a default value in the branch assignment
    lines = script.split("\n")
    for i, line in enumerate(lines):
        if "installableBranch" in line and "positionals" not in line and \
           "let " not in line and "const " not in line and "comment" not in line.lower():
            # This line should not have 'nightly' as default
            assert "nightly" not in line.lower(), \
                "installableBranch should not default to 'nightly'"


# [pr_diff] fail_to_pass
def test_nightly_workflow_removed():
    """The nightly.yml workflow file must be deleted."""
    nightly_yml = Path(f"{REPO}/.github/workflows/nightly.yml")
    assert not nightly_yml.exists(), \
        "nightly.yml should be deleted — builds now happen in preview.yml"


# [pr_diff] fail_to_pass
def test_preview_workflow_continuous_build():
    """preview.yml must trigger on push to main (continuous builds, not nightly)."""
    preview_yml = Path(f"{REPO}/.github/workflows/preview.yml").read_text()
    # Must have push trigger for main branch
    assert "push:" in preview_yml, "preview.yml must have push trigger"
    assert "main" in preview_yml, "preview.yml must reference main branch"
    # Must have workflow_dispatch for manual/experimental builds
    assert "workflow_dispatch" in preview_yml, \
        "preview.yml must support workflow_dispatch for experimental builds"
    # Must have separate checkout steps per event type
    assert "Checkout (push)" in preview_yml, \
        "preview.yml must have dedicated checkout step for push events"
    assert "Checkout (pull_request)" in preview_yml, \
        "preview.yml must have dedicated checkout step for PR events"
    # Must NOT be named "PR Preview" anymore
    assert "PR Preview" not in preview_yml, \
        "Workflow name should be updated from 'PR Preview'"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_readme_documents_preview_install():
    """README.md must document the preview branch install command, not nightly."""
    readme = Path(f"{REPO}/README.md").read_text()
    # Must reference preview branch install
    assert "remix-run/remix#preview" in readme, \
        "README must show install command using #preview branch"
    assert "preview&path:packages/remix" in readme, \
        "README must show correct preview install path"
    # Must NOT reference nightly branch
    assert "remix-run/remix#nightly" not in readme, \
        "README should no longer reference #nightly branch"
    # Must mention continuous or preview builds (not just nightly)
    lower = readme.lower()
    nightly_mentions = lower.count("nightly")
    # At most one "nightly" mention allowed (in historical context), not in install commands
    assert nightly_mentions == 0 or ("every night" not in lower and "nightly branch" not in lower), \
        "README should not describe nightly branch builds"


# [pr_diff] fail_to_pass
def test_contributing_documents_preview_builds():
    """CONTRIBUTING.md must have Preview builds section with preview branch info."""
    contributing = Path(f"{REPO}/CONTRIBUTING.md").read_text()
    # Must have Preview builds section
    lower = contributing.lower()
    assert "preview build" in lower or "preview branch" in lower, \
        "CONTRIBUTING.md must have section about preview builds"
    # Must reference preview workflow
    assert "preview" in lower and "workflow" in lower, \
        "CONTRIBUTING.md must reference the preview workflow"
    # Must show preview install command
    assert "remix-run/remix#preview" in contributing, \
        "CONTRIBUTING.md must show preview install command"
    # Must NOT reference nightly install
    assert "remix-run/remix#nightly" not in contributing, \
        "CONTRIBUTING.md should no longer reference #nightly install"
    # Must NOT have "Nightly Builds" as a section header
    assert "## Nightly Builds" not in contributing, \
        "CONTRIBUTING.md should not have 'Nightly Builds' section header"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub / regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_setup_script_no_overwrite_protection():
    """Script should not have branch overwrite protection (preview is force-pushed)."""
    script = Path(f"{REPO}/scripts/setup-installable-branch.ts").read_text()
    # The fixed version should NOT check for existing branches
    assert "allowedOverwrites" not in script, \
        "Script should not have allowedOverwrites branch protection"
    # Should NOT have git branch -r check for overwrite protection
    assert "git branch -r" not in script or "remoteBranches" not in script, \
        "Script should not check remote branches for overwrite protection"
