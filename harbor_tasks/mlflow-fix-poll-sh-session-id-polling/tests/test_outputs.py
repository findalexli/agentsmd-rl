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


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# -----------------------------------------------------------------------------


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


# [repo_tests] pass_to_pass - ACTUAL CI COMMANDS
def test_repo_bash_syntax_poll_sh():
    """poll.sh must be valid bash syntax (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-n", ".claude/skills/copilot/poll.sh"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, f"Syntax error in poll.sh: {r.stderr}"


def test_repo_git_tracked_copilot_files():
    """Copilot skill files must be tracked by git (pass_to_pass)."""
    r = subprocess.run(
        ["git", "ls-files", ".claude/skills/copilot/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, f"git ls-files failed: {r.stderr}"
    tracked = r.stdout.strip().split("\n")
    assert ".claude/skills/copilot/poll.sh" in tracked, "poll.sh not tracked by git"
    assert ".claude/skills/copilot/SKILL.md" in tracked, "SKILL.md not tracked by git"


def test_repo_shellcheck_poll_sh():
    """poll.sh must pass shellcheck linting (pass_to_pass)."""
    # Install shellcheck if not present (CI environments often lack it)
    subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True,
        timeout=60,
    )
    subprocess.run(
        ["apt-get", "install", "-y", "-qq", "shellcheck"],
        capture_output=True,
        timeout=120,
    )
    r = subprocess.run(
        ["shellcheck", ".claude/skills/copilot/poll.sh"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"shellcheck failed:\n{r.stdout}\n{r.stderr}"


def test_repo_mlflow_typo_copilot_files():
    """Copilot skill files must pass MLflow typo check (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "dev/mlflow-typo.sh", ".claude/skills/copilot/poll.sh", ".claude/skills/copilot/SKILL.md"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"MLflow typo check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_poll_sh_permissions():
    """poll.sh must be executable (pass_to_pass)."""
    r = subprocess.run(
        ["test", "-x", ".claude/skills/copilot/poll.sh"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, "poll.sh is not executable"


def test_repo_no_trailing_whitespace():
    """Copilot skill files must not have trailing whitespace (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", 'grep -n " $" .claude/skills/copilot/poll.sh .claude/skills/copilot/SKILL.md || true'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=10,
    )
    # grep returns 0 if matches found, 1 if no matches, 2 if error
    # We want no matches (exit code 1 with our || true, it's always 0 but output will be empty if no matches)
    assert r.stdout.strip() == "", f"Trailing whitespace found:\n{r.stdout}"


def test_repo_no_tabs():
    """Copilot skill files must not contain tabs (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", 'grep -n "$\\t" .claude/skills/copilot/poll.sh .claude/skills/copilot/SKILL.md || true'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.stdout.strip() == "", f"Tab characters found:\n{r.stdout}"


# [static] pass_to_pass - FILE CONTENT CHECKS (not actual CI commands)
def test_copilot_skill_files_exist():
    """Copilot skill files must exist (poll.sh and SKILL.md)."""
    poll_sh = Path(REPO) / ".claude" / "skills" / "copilot" / "poll.sh"
    skill_md = Path(REPO) / ".claude" / "skills" / "copilot" / "SKILL.md"

    assert poll_sh.exists(), f"poll.sh not found at {poll_sh}"
    assert skill_md.exists(), f"SKILL.md not found at {skill_md}"


# [static] pass_to_pass
def test_poll_sh_executable():
    """poll.sh must be executable (has shebang and executable bit)."""
    poll_sh = Path(REPO) / ".claude" / "skills" / "copilot" / "poll.sh"

    assert poll_sh.exists(), "poll.sh not found"

    # Check shebang
    content = poll_sh.read_text()
    assert content.startswith("#!/usr/bin/env bash"), "poll.sh missing bash shebang"

    # Check executable bit (on Unix systems)
    stat = poll_sh.stat()
    assert stat.st_mode & 0o111, "poll.sh not executable"


# [static] pass_to_pass
def test_skill_md_valid_yaml_frontmatter():
    """SKILL.md must have valid YAML frontmatter structure."""
    skill_md = Path(REPO) / ".claude" / "skills" / "copilot" / "SKILL.md"

    assert skill_md.exists(), "SKILL.md not found"

    content = skill_md.read_text()

    # Must start with ---
    assert content.startswith("---"), "SKILL.md missing YAML frontmatter start"

    # Must have closing ---
    lines = content.split("\n")
    assert lines[0] == "---", "SKILL.md frontmatter must start with --- on its own line"

    # Find second ---
    found_end = False
    for line in lines[1:]:
        if line == "---":
            found_end = True
            break
        # Should have key-value pairs
        if line.strip() and not line.strip().startswith("#"):
            assert ":" in line or line.strip().startswith("-"), f"Invalid YAML line: {line}"

    assert found_end, "SKILL.md missing YAML frontmatter end (---)"


# [static] pass_to_pass
def test_skill_md_has_required_fields():
    """SKILL.md must have required fields (name, description, allowed-tools)."""
    skill_md = Path(REPO) / ".claude" / "skills" / "copilot" / "SKILL.md"

    assert skill_md.exists(), "SKILL.md not found"

    content = skill_md.read_text()

    # Extract frontmatter (between first --- and next ---)
    parts = content.split("---")
    if len(parts) >= 3:
        frontmatter = parts[1]

        assert "name:" in frontmatter, "SKILL.md missing 'name' field"
        assert "description:" in frontmatter, "SKILL.md missing 'description' field"
        assert "allowed-tools:" in frontmatter, "SKILL.md missing 'allowed-tools' field"
    else:
        raise AssertionError("SKILL.md has invalid frontmatter structure")


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# -----------------------------------------------------------------------------


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
        f"poll.sh failed - may still be using timeline API:\n{r.stderr}"
    )
    assert "timeline" not in calls.lower(), (
        f"poll.sh still calls timeline API:\n{calls}"
    )


# -----------------------------------------------------------------------------
# Config/doc update tests (pr_diff) - SKILL.md changes
# -----------------------------------------------------------------------------


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

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_lint_macos_run_pre_commit():
    """pass_to_pass | CI job 'lint-macos' → step 'Run pre-commit'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --no-sync pre-commit run --all-files'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run pre-commit' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_macos_test_clint():
    """pass_to_pass | CI job 'lint-macos' → step 'Test clint'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --no-sync pytest dev/clint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test clint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_macos_check_function_signatures():
    """pass_to_pass | CI job 'lint-macos' → step 'Check function signatures'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --no-project dev/check_function_signatures.py'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check function signatures' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_tests_run_fs2db_pytest_tests():
    """pass_to_pass | CI job 'unit-tests' → step 'Run fs2db pytest tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run pytest tests/store/fs2db'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run fs2db pytest tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build_ui():
    """pass_to_pass | CI job 'build' → step 'Build UI'"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn && yarn build'], cwd=os.path.join(REPO, 'mlflow/server/js'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build UI' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")