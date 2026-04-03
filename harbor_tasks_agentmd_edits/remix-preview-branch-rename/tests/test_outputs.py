"""
Task: remix-preview-branch-rename
Repo: remix-run/remix @ cd2350521c75da2cd228e9b988049fa074252ec7
PR:   11004

The preview branch name was changed from "preview" to "preview/main" to avoid
a git directory/file conflict with PR preview branches (preview/12345).
This must be updated in the CI workflow, the setup script, and documentation.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/remix"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified files must exist and be non-empty."""
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
def test_workflow_uses_preview_main_branch():
    """CI workflow must pass 'preview/main' to setup-installable-branch script."""
    workflow = (Path(REPO) / ".github/workflows/preview.yml").read_text()
    assert "setup-installable-branch preview/main" in workflow, \
        "Workflow must call setup-installable-branch with 'preview/main'"


# [pr_diff] fail_to_pass
def test_workflow_pushes_to_preview_main():
    """CI workflow must push to 'preview/main' branch, not bare 'preview'."""
    workflow = (Path(REPO) / ".github/workflows/preview.yml").read_text()
    # The push step should reference preview/main
    assert "origin preview/main" in workflow, \
        "Workflow must push to 'origin preview/main'"


# [pr_diff] fail_to_pass
def test_script_comments_reference_preview_main():
    """setup-installable-branch.ts JSDoc must reference preview/main branch."""
    script = (Path(REPO) / "scripts/setup-installable-branch.ts").read_text()
    # The JSDoc should mention preview/main as the default branch name
    assert 'remix#preview/main&path:packages/remix' in script, \
        "Script JSDoc should show preview/main in the install example"


# ---------------------------------------------------------------------------
# Config/doc update tests (config_edit) — fail_to_pass
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_workflow_still_handles_pr_previews():
    """PR preview branches (preview/{number}) must still work."""
    workflow = (Path(REPO) / ".github/workflows/preview.yml").read_text()
    # The PR preview branch format should still be present
    assert "preview/" in workflow, "Workflow must still reference preview/ branches"
    # PR-specific logic should remain
    assert "pull_request" in workflow, "Workflow must still handle pull_request events"


# [static] pass_to_pass
def test_workflow_retains_cleanup_step():
    """Workflow must still have a cleanup step for closed PRs."""
    workflow = (Path(REPO) / ".github/workflows/preview.yml").read_text()
    assert "Cleanup preview branch" in workflow or "cleanup" in workflow.lower(), \
        "Workflow must retain the branch cleanup step"
