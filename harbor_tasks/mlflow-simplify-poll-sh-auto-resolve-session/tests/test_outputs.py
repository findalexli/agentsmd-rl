"""
Task: mlflow-simplify-poll-sh-auto-resolve-session
Repo: mlflow/mlflow @ cd2cea0d7acf7d47f4fbd8f94e7da0844a89e76a
PR:   21901

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "/workspace/mlflow"


# ---------------------------------------------------------------------------
# Helper: mock gh CLI for behavioral tests
# ---------------------------------------------------------------------------

def _setup_mock_gh(tmpdir, target_repo, target_pr):
    """Create a mock gh CLI returning realistic JSON and supporting --jq via jq.

    Returns the path to the call log file.
    """
    call_log = os.path.join(tmpdir, "gh_calls.log")
    mock_gh = os.path.join(tmpdir, "gh")

    # Write JSON response files that match the gh agent-task schema
    list_json = json.dumps([{
        "id": "mock-session-abc",
        "repository": target_repo,
        "pullRequestNumber": target_pr,
        "createdAt": "2024-01-01T00:00:00Z",
    }])
    Path(os.path.join(tmpdir, "resp_list.json")).write_text(list_json)
    Path(os.path.join(tmpdir, "resp_view.json")).write_text('{"state":"completed"}')
    Path(os.path.join(tmpdir, "resp_pr.json")).write_text('{"isDraft":false}')

    with open(mock_gh, "w") as f:
        f.write(
            '#!/usr/bin/env bash\n'
            'echo "$*" >> "' + call_log + '"\n'
            '\n'
            'jq_filter=""\n'
            'prev=""\n'
            'for arg in "$@"; do\n'
            '    if [[ "$prev" == "--jq" ]]; then\n'
            '        jq_filter="$arg"\n'
            '    fi\n'
            '    prev="$arg"\n'
            'done\n'
            '\n'
            'case "$1 $2" in\n'
            '  "agent-task list")  json_file="' + tmpdir + '/resp_list.json" ;;\n'
            '  "agent-task view")  json_file="' + tmpdir + '/resp_view.json" ;;\n'
            '  "pr view")          json_file="' + tmpdir + '/resp_pr.json" ;;\n'
            '  "pr ready")         exit 0 ;;\n'
            '  *)                  echo "mock-ok"; exit 0 ;;\n'
            'esac\n'
            '\n'
            'if [[ -n "$jq_filter" ]]; then\n'
            '    jq -r "$jq_filter" "$json_file"\n'
            'else\n'
            '    cat "$json_file"\n'
            'fi\n'
        )
    os.chmod(mock_gh, 0o755)
    return call_log


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


# [static] pass_to_pass
def test_skill_yaml_frontmatter():
    """SKILL.md must have valid YAML frontmatter with required fields (pass_to_pass)."""
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "pyyaml"],
        capture_output=True, timeout=60,
    )
    import yaml
    content = (Path(REPO) / ".claude/skills/copilot/SKILL.md").read_text()
    assert content.startswith("---"), "SKILL.md missing YAML frontmatter start"
    parts = content.split("---", 2)
    assert len(parts) >= 3, "SKILL.md frontmatter not properly closed"
    frontmatter = parts[1]
    data = yaml.safe_load(frontmatter)
    assert isinstance(data, dict), "SKILL.md frontmatter is not a valid YAML mapping"
    assert "name" in data, "SKILL.md missing 'name' field"
    assert "description" in data, "SKILL.md missing 'description' field"
    assert "allowed-tools" in data, "SKILL.md missing 'allowed-tools' field"
    assert isinstance(data["allowed-tools"], list), "SKILL.md 'allowed-tools' is not a list"


# ---------------------------------------------------------------------------
# Pass-to-pass gates — repo CI/CD tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_copilot_skill_ruff():
    """Copilot skill passes ruff linting (pass_to_pass)."""
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


# [repo_tests] pass_to_pass
def test_poll_sh_shellcheck():
    """poll.sh passes shellcheck linting (pass_to_pass)."""
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "shellcheck-py"],
        capture_output=True, timeout=60,
    )
    poll_sh = Path(REPO) / ".claude/skills/copilot/poll.sh"
    r = subprocess.run(
        ["shellcheck", str(poll_sh)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"shellcheck failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [static] pass_to_pass
def test_poll_retains_core_loop():
    """poll.sh must still have the polling loop and mark-ready logic."""
    content = (Path(REPO) / ".claude/skills/copilot/poll.sh").read_text()
    assert "while true" in content, "Polling loop removed"
    assert "gh agent-task view" in content, "Session status check removed"
    assert "gh pr ready" in content, "Mark-ready-for-review logic removed"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using mock gh CLI
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_poll_two_arg_interface():
    """poll.sh must accept exactly 2 args (repo, pr_number) and run to completion."""
    poll_sh = Path(REPO) / ".claude/skills/copilot/poll.sh"

    with tempfile.TemporaryDirectory() as tmpdir:
        call_log = _setup_mock_gh(tmpdir, "testowner/testrepo", 99)
        env = os.environ.copy()
        env["PATH"] = f"{tmpdir}:{env.get('PATH', '')}"

        r = subprocess.run(
            ["bash", str(poll_sh), "testowner/testrepo", "99"],
            capture_output=True, text=True, timeout=30, env=env,
        )
        # Base code (3-arg interface) crashes with "unbound variable" for $3
        assert "unbound variable" not in r.stderr, \
            f"poll.sh requires more than 2 arguments: {r.stderr}"
        assert r.returncode == 0, \
            f"poll.sh should succeed with 2 args, exit {r.returncode}: {r.stderr}"
        # Verify the script ran its main logic (not a no-op stub)
        assert Path(call_log).exists() and Path(call_log).read_text().strip(), \
            "poll.sh did not execute any gh commands with 2 args"


# [pr_diff] fail_to_pass
def test_poll_auto_resolves_session():
    """poll.sh must use 'gh agent-task list' to auto-resolve the session ID."""
    poll_sh = Path(REPO) / ".claude/skills/copilot/poll.sh"

    with tempfile.TemporaryDirectory() as tmpdir:
        call_log = _setup_mock_gh(tmpdir, "testowner/testrepo", 99)
        env = os.environ.copy()
        env["PATH"] = f"{tmpdir}:{env.get('PATH', '')}"

        subprocess.run(
            ["bash", str(poll_sh), "testowner/testrepo", "99"],
            capture_output=True, text=True, timeout=30, env=env,
        )

        assert Path(call_log).exists(), "poll.sh did not invoke gh at all"
        calls = Path(call_log).read_text()
        # Must call gh agent-task list to discover the session
        assert "agent-task list" in calls, \
            f"poll.sh did not call 'gh agent-task list' to resolve session. Calls:\n{calls}"
        # The resolved session ID must actually be used in the polling view call
        view_lines = [l for l in calls.splitlines() if "agent-task view" in l]
        assert any("mock-session-abc" in l for l in view_lines), \
            f"Auto-resolved session ID not used in polling. View calls: {view_lines}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_allowed_tools_has_agent_task_list():
    """SKILL.md allowed-tools must permit 'gh agent-task list' commands."""
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "pyyaml"],
        capture_output=True, timeout=60,
    )
    import yaml

    content = (Path(REPO) / ".claude/skills/copilot/SKILL.md").read_text()
    parts = content.split("---", 2)
    assert len(parts) >= 3, "SKILL.md frontmatter not properly delimited"
    data = yaml.safe_load(parts[1])
    assert isinstance(data, dict), "SKILL.md frontmatter is not valid YAML"

    allowed_tools = data.get("allowed-tools", [])
    has_list_perm = any("agent-task list" in str(tool) for tool in allowed_tools)
    assert has_list_perm, \
        f"SKILL.md allowed-tools must permit 'gh agent-task list'. Found: {allowed_tools}"


# [pr_diff] fail_to_pass
def test_skill_polling_simplified():
    """SKILL.md polling section must show 2-arg usage without session_url extraction."""
    content = (Path(REPO) / ".claude/skills/copilot/SKILL.md").read_text()

    # Locate the polling section
    polling_match = re.search(r'(?i)##\s+.*polling', content)
    assert polling_match, "SKILL.md must have a polling section"
    polling_section = content[polling_match.start():]

    # Bound to next top-level section
    next_heading = re.search(r'\n## ', polling_section[4:])
    if next_heading:
        polling_section = polling_section[:next_heading.start() + 4]

    # Extract code blocks from polling section
    code_blocks = re.findall(r'```(?:\w*)\n(.*?)```', polling_section, re.DOTALL)
    all_code = "\n".join(code_blocks)

    # Must not contain session_url extraction boilerplate
    assert "session_url" not in all_code, \
        "Polling code still contains session_url extraction boilerplate"

    # poll.sh must be referenced with exactly 2 positional args (not 3)
    poll_lines = [
        line.strip() for line in all_code.splitlines()
        if "poll.sh" in line and not line.strip().startswith("#")
    ]
    assert len(poll_lines) > 0, "Polling section must show poll.sh usage"
    for line in poll_lines:
        parts = line.split()
        sh_idx = next(i for i, p in enumerate(parts) if "poll.sh" in p)
        args = [a for a in parts[sh_idx + 1:] if not a.startswith("-")]
        assert len(args) == 2, \
            f"poll.sh should be invoked with 2 args, found {len(args)}: {line}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_lint_run_pre_commit():
    """pass_to_pass | CI job 'lint' → step 'Run pre-commit'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --no-sync pre-commit run --all-files'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run pre-commit' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_test_clint():
    """pass_to_pass | CI job 'lint' → step 'Test clint'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --no-sync pytest dev/clint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test clint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_check_function_signatures():
    """pass_to_pass | CI job 'lint' → step 'Check function signatures'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --no-project dev/check_function_signatures.py'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check function signatures' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_check_whitespace_only_changes():
    """pass_to_pass | CI job 'lint' → step 'Check whitespace-only changes'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --no-project dev/check_whitespace_only.py \\\n  --repo $REPO \\\n  --pr $PR_NUMBER'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check whitespace-only changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_check_uv_lock_changes():
    """pass_to_pass | CI job 'lint' → step 'Check uv.lock changes'"""
    r = subprocess.run(
        ["bash", "-lc", 'files=$(gh pr view "${PR_NUMBER}" --repo "${REPO}" --json files --jq \'.files[].path\')\nif echo "$files" | grep -q \'^uv.lock$\' && echo "$files" | grep -q \'^pyproject.toml$\'; then\n  echo \'::warning file=pyproject.toml,line=1,col=1::[Non-blocking]\' \\\n       \'Run `uv lock --upgrade-package <package>` if this PR should update package versions.\' \\\n       \'`uv lock` alone won\'"\'"\'t bump them.\'\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check uv.lock changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_check_unused_media():
    """pass_to_pass | CI job 'lint' → step 'Check unused media'"""
    r = subprocess.run(
        ["bash", "-lc", 'dev/find-unused-media.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check unused media' failed (returncode={r.returncode}):\n"
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

def test_ci_build_build_distribution_files():
    """pass_to_pass | CI job 'build' → step 'Build distribution files'"""
    r = subprocess.run(
        ["bash", "-lc", '# if workflow_dispatch is triggered, use the specified ref\nif [ "$EVENT_NAME" == "workflow_dispatch" ]; then\n  SHA_OPT="--sha $(git rev-parse HEAD)"\nelse\n  SHA_OPT=""\nfi\n\npython dev/build.py --package-type "$MATRIX_TYPE" $SHA_OPT\n\n# List distribution files and check their file sizes\nls -lh dist\n\n# Set step outputs\nsdist_path=$(find dist -type f -name "*.tar.gz")\nwheel_path=$(find dist -type f -name "*.whl")\nwheel_name=$(basename $wheel_path)\nwheel_size=$(stat -c %s $wheel_path)\necho "sdist-path=${sdist_path}" >> $GITHUB_OUTPUT\necho "wheel-path=${wheel_path}" >> $GITHUB_OUTPUT\necho "wheel-name=${wheel_name}" >> $GITHUB_OUTPUT\necho "wheel-size=${wheel_size}" >> $GITHUB_OUTPUT'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build distribution files' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_run_twine_check():
    """pass_to_pass | CI job 'build' → step 'Run twine check'"""
    r = subprocess.run(
        ["bash", "-lc", 'twine check --strict $WHEEL_PATH'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run twine check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_test_installation_from_tarball():
    """pass_to_pass | CI job 'build' → step 'Test installation from tarball'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -c "import mlflow; print(mlflow.__version__)" && python -c "from mlflow import *"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test installation from tarball' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_test_installation_from_github():
    """pass_to_pass | CI job 'build' → step 'Test installation from GitHub'"""
    r = subprocess.run(
        ["bash", "-lc", 'if [ "$MATRIX_TYPE" == "skinny" ]; then\n  URL="git+https://github.com/${REPO}.git@${REF}#subdirectory=libs/skinny"\nelif [ "$MATRIX_TYPE" == "tracing" ]; then\n  URL="git+https://github.com/${REPO}.git@${REF}#subdirectory=libs/tracing"\nelse\n  URL="git+https://github.com/${REPO}.git@${REF}"\nfi\n\nuv run --isolated --no-project --with $URL python -I -c \'import mlflow; print(mlflow.__version__)\''], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test installation from GitHub' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")