"""
Task: mlflow-simplify-poll-sh-auto-resolve-session
Repo: mlflow/mlflow @ cd2cea0d7acf7d47f4fbd8f94e7da0844a89e76a
PR:   21901

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/mlflow"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_poll_sh_syntax():
    """poll.sh must parse without bash syntax errors."""
    script = Path(REPO) / ".claude/skills/copilot/poll.sh"
    r = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Syntax error in poll.sh:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass gates — repo CI/CD tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_copilot_skill_ruff():
    """Copilot skill passes ruff linting (pass_to_pass)."""
    # Install ruff if not available
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "ruff==0.15.5"],
        capture_output=True, timeout=60,
    )
    skill_dir = Path(REPO) / ".claude/skills/copilot"
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--output-format=concise", str(skill_dir)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_copilot_files_exist():
    """Copilot skill required files exist and are non-empty (pass_to_pass)."""
    poll_sh = Path(REPO) / ".claude/skills/copilot/poll.sh"
    skill_md = Path(REPO) / ".claude/skills/copilot/SKILL.md"

    assert poll_sh.exists(), "poll.sh does not exist"
    assert skill_md.exists(), "SKILL.md does not exist"

    poll_content = poll_sh.read_text()
    skill_content = skill_md.read_text()

    assert len(poll_content) > 0, "poll.sh is empty"
    assert len(skill_content) > 0, "SKILL.md is empty"

    # Basic structure checks
    assert "#!/usr/bin/env bash" in poll_content, "poll.sh missing shebang"
    assert "set -euo pipefail" in poll_content, "poll.sh missing set options"
    assert "name: copilot" in skill_content, "SKILL.md missing name"


# [static] pass_to_pass
def test_poll_retains_core_loop():
    """poll.sh must still have the polling loop and mark-ready logic."""
    content = (Path(REPO) / ".claude/skills/copilot/poll.sh").read_text()
    assert "while true" in content, "Polling loop removed"
    assert "gh agent-task view" in content, "Session status check removed"
    assert "gh pr ready" in content, "Mark-ready-for-review logic removed"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavior tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_poll_two_arg_interface():
    """poll.sh must accept 2 args (repo, pr_number), not 3."""
    content = (Path(REPO) / ".claude/skills/copilot/poll.sh").read_text()
    # Must NOT assign session_id from $1
    assert 'session_id="$1"' not in content, \
        "poll.sh still takes session_id as first argument"
    # Must assign repo from $1
    lines = content.splitlines()
    repo_from_1 = any(
        "repo=" in line and '"$1"' in line
        for line in lines
    )
    assert repo_from_1, "poll.sh does not assign repo from $1"
    # Must assign pr_number from $2
    pr_from_2 = any(
        "pr_number=" in line and '"$2"' in line
        for line in lines
    )
    assert pr_from_2, "poll.sh does not assign pr_number from $2"


# [pr_diff] fail_to_pass
def test_poll_auto_resolves_session():
    """poll.sh must use 'gh agent-task list' to auto-resolve session ID."""
    content = (Path(REPO) / ".claude/skills/copilot/poll.sh").read_text()
    assert "gh agent-task list" in content, \
        "poll.sh does not call 'gh agent-task list' to resolve session"
    # Must filter by repository and pullRequestNumber
    assert "repository" in content, \
        "poll.sh does not filter by repository"
    assert "pullRequestNumber" in content, \
        "poll.sh does not filter by pullRequestNumber"
    # Must sort by createdAt to get latest session
    assert "sort_by" in content or "createdAt" in content, \
        "poll.sh does not sort sessions by creation time"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_allowed_tools_has_agent_task_list():
    """SKILL.md allowed-tools must include 'gh agent-task list'."""
    content = (Path(REPO) / ".claude/skills/copilot/SKILL.md").read_text()
    assert "agent-task list" in content, \
        "SKILL.md allowed-tools does not include 'gh agent-task list'"


# [pr_diff] fail_to_pass
def test_skill_polling_simplified():
    """SKILL.md polling section must not have session_url extraction boilerplate."""
    content = (Path(REPO) / ".claude/skills/copilot/SKILL.md").read_text()
    # Should NOT have the old session_url extraction pattern
    assert "session_url=" not in content and "session_url =" not in content, \
        "SKILL.md still contains session_url extraction"
    assert 'session_id="${session_url' not in content, \
        "SKILL.md still extracts session_id from URL"
    # Should show simplified 2-arg usage
    assert "poll.sh" in content, "SKILL.md must reference poll.sh"
    # Should mention automatic session resolution
    assert "automatic" in content.lower() or "auto" in content.lower(), \
        "SKILL.md should mention automatic session resolution"
