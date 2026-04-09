"""
Task: mlflow-add-copilot-approve-workflow-rerun
Repo: mlflow/mlflow @ 39f35acce9e63788371bfaaa2c57cafef10a02ec
PR:   22330

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/mlflow"
APPROVE_SH = Path(REPO) / ".claude" / "skills" / "copilot" / "approve.sh"
SKILL_MD = Path(REPO) / ".claude" / "skills" / "copilot" / "SKILL.md"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_approve_sh_syntax():
    """approve.sh must exist and have valid bash syntax."""
    assert APPROVE_SH.exists(), f"{APPROVE_SH} does not exist"
    r = subprocess.run(
        ["bash", "-n", str(APPROVE_SH)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Syntax error in approve.sh:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_approve_sh_exits_on_missing_args():
    """approve.sh must fail when called without required arguments."""
    assert APPROVE_SH.exists(), f"{APPROVE_SH} does not exist"
    r = subprocess.run(
        ["bash", str(APPROVE_SH)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode != 0, (
        "approve.sh should exit nonzero when called without arguments"
    )


# [pr_diff] fail_to_pass
def test_approve_sh_rerun_not_approve_api():
    """Script must use the /rerun API endpoint, not /approve."""
    content = APPROVE_SH.read_text()
    assert "/rerun" in content, (
        "approve.sh should use the /rerun endpoint to trigger workflow reruns"
    )
    # The script should NOT use the /approve endpoint (it fails for same-repo PRs)
    lines = content.splitlines()
    api_lines = [l for l in lines if "gh api" in l and "/approve" in l]
    assert len(api_lines) == 0, (
        "approve.sh should not use the /approve API (fails for same-repo Copilot PRs)"
    )


# [pr_diff] fail_to_pass
def test_approve_sh_filters_copilot_action_required():
    """Script must filter for action_required conclusion and Copilot actor."""
    content = APPROVE_SH.read_text()
    assert "action_required" in content, (
        "approve.sh should filter for action_required workflow conclusion"
    )
    assert "Copilot" in content, (
        "approve.sh should filter for the Copilot actor"
    )


# [pr_diff] fail_to_pass
def test_approve_sh_handles_empty_results():
    """Script must handle the case where no matching workflow runs are found."""
    content = APPROVE_SH.read_text()
    # Must have a conditional that checks for empty/no matching runs
    has_empty_check = (
        '-z "$run_ids"' in content
        or '-z "${run_ids}"' in content
        or "No action_required" in content
        or "no.*workflow" in content.lower()
    )
    assert has_empty_check, (
        "approve.sh should check whether any matching runs were found "
        "and print a message when none exist"
    )
    # The empty-results path must not be an error
    assert "exit 0" in content, (
        "approve.sh should exit 0 (not error) when no matching runs are found"
    )


# ---------------------------------------------------------------------------
# Config/documentation update tests (REQUIRED for agentmd-edit)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_md_approve_in_allowed_tools():
    """SKILL.md must list approve.sh in allowed-tools frontmatter."""
    content = SKILL_MD.read_text()
    assert "approve.sh" in content, (
        "SKILL.md should reference approve.sh"
    )
    # Check it appears in the allowed-tools section (frontmatter)
    in_frontmatter = False
    in_allowed_tools = False
    found = False
    for line in content.splitlines():
        if line.strip() == "---":
            if in_frontmatter:
                break  # end of frontmatter
            in_frontmatter = True
            continue
        if in_frontmatter and "allowed-tools" in line:
            in_allowed_tools = True
        if in_allowed_tools and "approve.sh" in line:
            found = True
            break
    assert found, (
        "approve.sh must be listed in the allowed-tools section of SKILL.md frontmatter"
    )


# [pr_diff] fail_to_pass
def test_skill_md_documents_approve_workflow():
    """SKILL.md must document how to use the approve workflow script."""
    content = SKILL_MD.read_text()
    content_lower = content.lower()
    # Must have a section about approving workflows
    assert "approv" in content_lower, (
        "SKILL.md should document workflow approval"
    )
    # Must show the actual command usage
    assert "approve.sh" in content, (
        "SKILL.md should show the approve.sh command"
    )
    # Must mention both owner/repo and pr_number parameters
    has_repo_param = "<owner>" in content or "owner/repo" in content.lower() or "repo" in content
    has_pr_param = "pr_number" in content or "pr number" in content.lower()
    assert has_repo_param and has_pr_param, (
        "SKILL.md should document both repo and PR number parameters for approve.sh"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI checks that must pass on base and gold
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_bash_syntax_copilot():
    """All shell scripts in .claude/skills/copilot have valid bash syntax (pass_to_pass)."""
    skill_dir = Path(REPO) / ".claude" / "skills" / "copilot"
    for script in skill_dir.glob("*.sh"):
        r = subprocess.run(
            ["bash", "-n", str(script)],
            capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0, f"Syntax error in {script}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_claude():
    """Ruff linting passes on .claude directory (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pip", "install", "ruff==0.15.5", "-q"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        ["ruff", "check", ".claude/", "--output-format=concise"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_bash_syntax_all_claude():
    """All shell scripts in .claude have valid bash syntax (pass_to_pass)."""
    claude_dir = Path(REPO) / ".claude"
    for script in claude_dir.rglob("*.sh"):
        r = subprocess.run(
            ["bash", "-n", str(script)],
            capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0, f"Syntax error in {script}:\n{r.stderr}"
