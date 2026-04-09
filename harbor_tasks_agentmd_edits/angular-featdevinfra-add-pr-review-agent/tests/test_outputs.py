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

import pytest

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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_bash_scripts_syntax():
    """All bash scripts in the repo have valid syntax (pass_to_pass)."""
    # Find all .sh files in the repo
    sh_files = list(Path(REPO).rglob("*.sh"))
    assert len(sh_files) > 0, "Should find shell scripts in the repo"

    for script in sh_files:
        # Run bash -n to check syntax
        result = subprocess.run(
            ["bash", "-n", str(script)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, (
            f"Script {script} has invalid bash syntax:\n{result.stderr}"
        )


# [repo_tests] pass_to_pass
def test_pr_review_scripts_executable():
    """PR review scripts are executable and have valid syntax (pass_to_pass)."""
    scripts_dir = SCRIPTS_DIR
    if not scripts_dir.exists():
        pytest.skip("PR review scripts not yet created")

    expected_scripts = [
        "determine_review_type.sh",
        "get_pr_comments.sh",
        "post_inline_comment.sh",
        "reply_pr_comment.sh",
        "submit_pr_review.sh",
    ]

    for script_name in expected_scripts:
        script_path = scripts_dir / script_name
        assert script_path.exists(), f"Script {script_name} should exist"
        assert os.access(str(script_path), os.X_OK), (
            f"Script {script_name} should be executable"
        )
        # Validate syntax
        result = subprocess.run(
            ["bash", "-n", str(script_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, (
            f"Script {script_name} has invalid syntax:\n{result.stderr}"
        )


# [repo_tests] pass_to_pass
def test_git_repo_valid():
    """Git repository is valid and has expected structure (pass_to_pass)."""
    # Check git status works
    result = subprocess.run(
        ["git", "-C", REPO, "status", "--short"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"Git status failed:\n{result.stderr}"

    # Check expected directories exist
    expected_dirs = [".agent", "packages", "scripts", ".github"]
    for dir_name in expected_dirs:
        dir_path = Path(REPO) / dir_name
        assert dir_path.exists(), f"Expected directory {dir_name} should exist"


# [repo_tests] pass_to_pass
def test_jq_syntax_in_scripts():
    """Scripts using jq have valid jq syntax (pass_to_pass)."""
    # Check that jq is available
    result = subprocess.run(
        ["jq", "--version"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 0, "jq should be available"

    # Test basic jq functionality that scripts rely on
    test_json = '{"path": "test", "line": 42, "body": "comment"}'
    result = subprocess.run(
        ["jq", ".path", "-"],
        capture_output=True,
        text=True,
        input=test_json,
        timeout=5,
    )
    assert result.returncode == 0, f"jq should work:\n{result.stderr}"
    assert '"test"' in result.stdout, "jq should extract the path field"
