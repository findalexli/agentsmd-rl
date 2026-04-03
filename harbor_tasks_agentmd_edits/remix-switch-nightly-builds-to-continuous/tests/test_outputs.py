"""
Task: remix-switch-nightly-builds-to-continuous
Repo: remix-run/remix @ 721dac4c6704d5b3e8428887af21accdcb3b23ea
PR:   11003

Switch nightly builds (cron-scheduled to a `nightly` branch) to continuous
preview builds (push-triggered to a `preview` branch).  The CI workflow,
build script, and documentation must all be updated consistently.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/remix"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Key modified files must exist and be non-empty."""
    files = [
        ".github/workflows/preview.yml",
        "CONTRIBUTING.md",
        "README.md",
        "scripts/setup-installable-branch.ts",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        assert p.stat().st_size > 0, f"{f} must be non-empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_nightly_workflow_removed():
    """The old nightly.yml workflow must be deleted."""
    p = Path(REPO) / ".github/workflows/nightly.yml"
    assert not p.exists(), "nightly.yml should be removed — its functionality moves to preview.yml"


# [pr_diff] fail_to_pass
def test_preview_workflow_has_push_trigger():
    """preview.yml must trigger on pushes to main (continuous builds)."""
    workflow = (Path(REPO) / ".github/workflows/preview.yml").read_text()
    assert "push:" in workflow, "Workflow must have a push trigger"
    # The push trigger should target main
    assert "main" in workflow, "Push trigger should target the main branch"


# [pr_diff] fail_to_pass
def test_preview_workflow_builds_on_push():
    """preview.yml must build and push a preview branch on push-to-main events."""
    workflow = (Path(REPO) / ".github/workflows/preview.yml").read_text()
    # Should reference building/pushing for push events
    assert "setup-installable-branch preview" in workflow, \
        "Workflow must call setup-installable-branch with 'preview' for push events"
    # Should force-push the preview branch
    assert re.search(r"git push.*origin preview", workflow), \
        "Workflow must push to origin preview branch"


# [pr_diff] fail_to_pass
def test_script_requires_branch_name():
    """setup-installable-branch.ts must require a positional branch name argument."""
    script = (Path(REPO) / "scripts/setup-installable-branch.ts").read_text()
    # The old script had a fallback: positionals[0] || values.branch || 'nightly'
    # The new script requires a positional arg and throws if missing
    assert "|| 'nightly'" not in script, \
        "Script must not default to 'nightly' branch name"
    # Should error when no argument given
    assert "if (!installableBranch)" in script or "must provide" in script.lower() or \
        "Error:" in script, \
        "Script should throw an error when no branch name is provided"


# [pr_diff] fail_to_pass
def test_script_removes_overwrite_protection():
    """setup-installable-branch.ts must remove the nightly-specific overwrite protection."""
    script = (Path(REPO) / "scripts/setup-installable-branch.ts").read_text()
    # Old script had allowedOverwrites = ['nightly'] check
    assert "allowedOverwrites" not in script, \
        "The allowedOverwrites branch-protection logic should be removed"
    assert "remoteBranches" not in script or "git branch -r" not in script, \
        "The remote branch check should be removed"


# [pr_diff] fail_to_pass
def test_script_comments_reference_preview():
    """setup-installable-branch.ts JSDoc must reference preview branch, not nightly."""
    script = (Path(REPO) / "scripts/setup-installable-branch.ts").read_text()
    # JSDoc should now say 'preview' not 'nightly'
    assert 'remix#preview&path:packages/remix' in script, \
        "Script JSDoc should show preview in the install example"
    assert '(usually `nightly`)' not in script, \
        "Script JSDoc should not reference nightly as the default"


# ---------------------------------------------------------------------------
# Config/doc update tests (config_edit) — fail_to_pass
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_preview_workflow_retains_pr_previews():
    """PR preview branches (preview/{number}) must still be supported."""
    workflow = (Path(REPO) / ".github/workflows/preview.yml").read_text()
    assert "pull_request" in workflow, "Workflow must still handle pull_request events"
    assert "preview/" in workflow, "Workflow must still reference preview/ branches for PRs"


# [static] pass_to_pass
def test_preview_workflow_retains_cleanup():
    """Workflow must still clean up PR preview branches when PRs close."""
    workflow = (Path(REPO) / ".github/workflows/preview.yml").read_text()
    assert "closed" in workflow, "Workflow must still handle closed PR events"
    assert "cleanup" in workflow.lower() or "Cleanup" in workflow, \
        "Workflow must retain the branch cleanup step"
