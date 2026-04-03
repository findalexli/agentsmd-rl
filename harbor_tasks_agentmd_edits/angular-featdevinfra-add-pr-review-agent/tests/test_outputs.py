"""
Task: angular-featdevinfra-add-pr-review-agent
Repo: angular @ 5e21431ba34d82c189dc4a7536f49dcfbc5bda4d
PR:   angular/angular#67666

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
from pathlib import Path

REPO = "/workspace/angular"
SKILL_DIR = Path(REPO) / ".agent" / "skills" / "pr_review"
SCRIPTS_DIR = SKILL_DIR / "scripts"


# ---------------------------------------------------------------------------
# Config edit tests (fail_to_pass) — SKILL.md and reference docs
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Code behavior tests (fail_to_pass) — bash scripts
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_review_scripts_exist_and_validate_args():
    """All 5 review scripts exist, are executable, and reject missing args."""
    expected_scripts = [
        "determine_review_type.sh",
        "get_pr_comments.sh",
        "post_inline_comment.sh",
        "reply_pr_comment.sh",
        "submit_pr_review.sh",
    ]
    for script_name in expected_scripts:
        script_path = SCRIPTS_DIR / script_name
        assert script_path.exists(), f"Script {script_name} should exist"
        assert os.access(str(script_path), os.X_OK), (
            f"Script {script_name} should be executable"
        )
        # Run with no args — should exit non-zero with usage message
        result = subprocess.run(
            ["bash", str(script_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode != 0, (
            f"{script_name} should exit non-zero when called with no arguments"
        )
        assert "usage" in result.stdout.lower() or "usage" in result.stderr.lower(), (
            f"{script_name} should print usage info when called with no arguments"
        )


# [pr_diff] fail_to_pass
def test_post_inline_comment_stages_to_local_file():
    """post_inline_comment.sh stages comments to a local JSON file rather than posting directly."""
    script_path = SCRIPTS_DIR / "post_inline_comment.sh"
    content = script_path.read_text()
    # The script should stage comments locally (JSON file), not post directly
    assert "json" in content.lower() or "stage" in content.lower() or "tmp" in content.lower(), (
        "post_inline_comment.sh should stage comments to a local file"
    )
    assert "jq" in content, (
        "post_inline_comment.sh should use jq to build JSON"
    )
    # Must mention that comments are not posted until submit is called
    assert "submit" in content.lower(), (
        "post_inline_comment.sh should reference submit_pr_review.sh for publishing"
    )


# [pr_diff] fail_to_pass
def test_submit_review_supports_event_types():
    """submit_pr_review.sh handles COMMENT, APPROVE, and REQUEST_CHANGES event types."""
    script_path = SCRIPTS_DIR / "submit_pr_review.sh"
    content = script_path.read_text()
    assert "COMMENT" in content, (
        "submit_pr_review.sh should support COMMENT event type"
    )
    assert "APPROVE" in content, (
        "submit_pr_review.sh should support APPROVE event type"
    )
    assert "REQUEST_CHANGES" in content, (
        "submit_pr_review.sh should support REQUEST_CHANGES event type"
    )
    # Should use the GitHub Reviews API
    assert "reviews" in content.lower() or "review" in content.lower(), (
        "submit_pr_review.sh should use the GitHub Pull Request Reviews API"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — existing skills preserved
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_skills_preserved():
    """Existing agent skills remain accessible under .agent/skills/."""
    skills_dir = Path(REPO) / ".agent" / "skills"
    expected_skills = [
        "adev-writing-guide",
        "reference-compiler-cli",
        "reference-core",
        "reference-signal-forms",
    ]
    for skill_name in expected_skills:
        skill_path = skills_dir / skill_name
        assert skill_path.exists(), (
            f"Existing skill '{skill_name}' should still be accessible "
            f"under .agent/skills/"
        )
        # Each existing skill should have a SKILL.md
        skill_md = skill_path / "SKILL.md"
        assert skill_md.exists(), (
            f"Existing skill '{skill_name}' should have a SKILL.md file"
        )
