"""
Task: mlflow-fix-poll-sh-session-id-polling
Repo: mlflow/mlflow @ e226b6470db43c522bf00ca5e5a4cd7f51f83e5b
PR:   21888

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import shutil
import subprocess
from pathlib import Path

REPO = "/workspace/mlflow"


def _run_poll_with_mock(
    session_id="test-sess-abc123", repo="mlflow/mlflow", pr="999"
):
    """Create a mock gh binary and run poll.sh, returning (CompletedProcess, call_log_str)."""
    mock_dir = Path(REPO) / "_eval_mock_bin"
    mock_dir.mkdir(exist_ok=True)
    log_file = Path(REPO) / "_eval_gh_calls.log"
    log_file.unlink(missing_ok=True)

    mock_gh = mock_dir / "gh"
    mock_gh.write_text(
        "#!/usr/bin/env bash\n"
        f'echo "$*" >> {log_file}\n'
        'if [[ "$1" == "agent-task" && "$2" == "view" ]]; then\n'
        '  echo \'{"state": "completed"}\'\n'
        "  exit 0\n"
        "fi\n"
        'if [[ "$1" == "pr" ]]; then\n'
        '  echo "false"\n'
        "  exit 0\n"
        "fi\n"
        "exit 1\n"
    )
    mock_gh.chmod(0o755)

    try:
        env = dict(os.environ)
        env["PATH"] = str(mock_dir) + ":" + env.get("PATH", "")
        r = subprocess.run(
            ["bash", ".claude/skills/copilot/poll.sh", session_id, repo, pr],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        calls = log_file.read_text() if log_file.exists() else ""
        return r, calls
    finally:
        shutil.rmtree(mock_dir, ignore_errors=True)
        log_file.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_bash_syntax():
    """poll.sh must be valid bash syntax."""
    r = subprocess.run(
        ["bash", "-n", ".claude/skills/copilot/poll.sh"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, f"Syntax error in poll.sh: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_poll_session_id_polling():
    """poll.sh must accept session_id as $1 and call 'gh agent-task view' with it."""
    r, calls = _run_poll_with_mock()
    assert r.returncode == 0, (
        f"poll.sh failed (rc={r.returncode}):\nstdout: {r.stdout}\nstderr: {r.stderr}"
    )
    assert "agent-task view" in calls, (
        f"Expected 'gh agent-task view' call, got:\n{calls}"
    )
    assert "test-sess-abc123" in calls, (
        f"Session ID not passed to gh:\n{calls}"
    )


# [pr_diff] fail_to_pass
def test_poll_no_timeline_api():
    """poll.sh must NOT use the old timeline API to check for completion."""
    r, calls = _run_poll_with_mock(
        session_id="sess-xyz-789", repo="owner/repo", pr="42"
    )
    assert r.returncode == 0, (
        f"poll.sh failed — may still be using timeline API:\n{r.stderr}"
    )
    assert "timeline" not in calls.lower(), (
        f"poll.sh still calls timeline API:\n{calls}"
    )


# ---------------------------------------------------------------------------
# Config/doc update tests (pr_diff) — SKILL.md changes
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_skill_md_allows_agent_task_view():
    """SKILL.md allowed-tools must include 'gh agent-task view'."""
    skill = Path(REPO) / ".claude" / "skills" / "copilot" / "SKILL.md"
    content = skill.read_text()
    assert "agent-task view" in content, (
        "SKILL.md missing 'agent-task view' in allowed-tools"
    )


# [pr_diff] fail_to_pass
def test_skill_md_documents_session_id():
    """SKILL.md must document extracting the session ID for poll.sh."""
    skill = Path(REPO) / ".claude" / "skills" / "copilot" / "SKILL.md"
    content = skill.read_text()
    assert "session_id" in content or "session_url" in content, (
        "SKILL.md should document session ID extraction"
    )
    # Must show the new 3-arg calling convention
    assert "poll.sh" in content, "SKILL.md should reference poll.sh"
