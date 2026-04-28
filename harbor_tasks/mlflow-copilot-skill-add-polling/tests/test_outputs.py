"""
Task: mlflow-copilot-skill-add-polling
Repo: mlflow/mlflow @ 91ce5a5514917a562304c7946c9c6313b88cce40
PR:   21684

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

import yaml

REPO = "/workspace/mlflow"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Repo CI tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_bash_syntax_claude_scripts():
    """Existing .claude shell scripts pass bash syntax check (pass_to_pass)."""
    scripts = [
        Path(REPO) / ".claude" / "hooks" / "enforce-uv.sh",
        Path(REPO) / ".claude" / "statusline.sh",
    ]
    for script in scripts:
        if script.exists():
            r = subprocess.run(
                ["bash", "-n", str(script)],
                capture_output=True, text=True, timeout=10,
            )
            assert r.returncode == 0, f"bash -n failed for {script}: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_yaml_valid_skill():
    """SKILL.md frontmatter is valid YAML (pass_to_pass)."""
    skill_md = Path(REPO) / ".claude" / "skills" / "copilot" / "SKILL.md"
    r = subprocess.run(
        ["python3", "-c",
         f"import yaml; f=open('{skill_md}'); c=f.read(); "
         f"y=c.split('---')[1]; yaml.safe_load(y); print('YAML valid')"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"YAML validation failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_skill_has_name():
    """SKILL.md frontmatter has required 'name' field (pass_to_pass)."""
    skill_md = Path(REPO) / ".claude" / "skills" / "copilot" / "SKILL.md"
    r = subprocess.run(
        ["python3", "-c",
         f"import yaml; f=open('{skill_md}'); c=f.read(); "
         f"y=c.split('---')[1]; d=yaml.safe_load(y); "
         f"assert 'name' in d, 'Missing name'; print('Has name')"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"name check failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_skill_has_allowed_tools():
    """SKILL.md frontmatter has required 'allowed-tools' field (pass_to_pass)."""
    skill_md = Path(REPO) / ".claude" / "skills" / "copilot" / "SKILL.md"
    r = subprocess.run(
        ["python3", "-c",
         f"import yaml; f=open('{skill_md}'); c=f.read(); "
         f"y=c.split('---')[1]; d=yaml.safe_load(y); "
         f"assert 'allowed-tools' in d, 'Missing allowed-tools'; print('Has allowed-tools')"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"allowed-tools check failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_python_syntax_hooks():
    """.claude hooks Python files have valid syntax (pass_to_pass)."""
    hooks_dir = Path(REPO) / ".claude" / "hooks"
    py_files = ["lint.py", "validate_pr_body.py"]
    for f in py_files:
        r = subprocess.run(
            ["python3", "-m", "py_compile", str(hooks_dir / f)],
            capture_output=True, text=True, timeout=10, cwd=REPO,
        )
        assert r.returncode == 0, f"Python syntax error in {f}: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_json_valid_settings():
    """.claude/settings.json is valid JSON (pass_to_pass)."""
    settings_json = Path(REPO) / ".claude" / "settings.json"
    r = subprocess.run(
        ["python3", "-c",
         f"import json; f=open('{settings_json}'); json.load(f); print('JSON valid')"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"JSON validation failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_hooks_are_executable():
    """.claude shell hooks are executable (pass_to_pass)."""
    enforce_uv = Path(REPO) / ".claude" / "hooks" / "enforce-uv.sh"
    r = subprocess.run(
        ["test", "-x", str(enforce_uv)],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, "enforce-uv.sh must be executable"


# [repo_tests] pass_to_pass
def test_repo_statusline_is_executable():
    """.claude/statusline.sh is executable (pass_to_pass)."""
    statusline = Path(REPO) / ".claude" / "statusline.sh"
    r = subprocess.run(
        ["test", "-x", str(statusline)],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, "statusline.sh must be executable"


# [repo_tests] pass_to_pass
def test_repo_claude_structure_valid():
    """.claude directory structure is valid (pass_to_pass)."""
    required_paths = [
        ".claude/settings.json",
        ".claude/statusline.sh",
        ".claude/hooks/enforce-uv.sh",
        ".claude/hooks/lint.py",
        ".claude/hooks/validate_pr_body.py",
        ".claude/skills/copilot/SKILL.md",
    ]
    for p in required_paths:
        full_path = Path(REPO) / p
        r = subprocess.run(
            ["test", "-f", str(full_path)],
            capture_output=True, text=True, timeout=10, cwd=REPO,
        )
        assert r.returncode == 0, f"Required file missing: {p}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / YAML validity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_skill_frontmatter_valid():
    """SKILL.md has valid YAML frontmatter."""
    skill_md = Path(REPO) / ".claude" / "skills" / "copilot" / "SKILL.md"
    content = skill_md.read_text()
    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter"
    end = content.index("---", 3)
    frontmatter = content[3:end].strip()
    data = yaml.safe_load(frontmatter)
    assert "name" in data
    assert "allowed-tools" in data


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — poll.sh code tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_poll_script_exists_executable():
    """poll.sh exists and is executable."""
    poll_sh = Path(REPO) / ".claude" / "skills" / "copilot" / "poll.sh"
    assert poll_sh.exists(), "poll.sh must exist"
    assert os.access(poll_sh, os.X_OK), "poll.sh must be executable"


# [pr_diff] fail_to_pass
def test_poll_script_syntax_valid():
    """poll.sh passes bash syntax check."""
    poll_sh = Path(REPO) / ".claude" / "skills" / "copilot" / "poll.sh"
    r = subprocess.run(
        ["bash", "-n", str(poll_sh)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"bash -n failed: {r.stderr}"


# [pr_diff] fail_to_pass
def test_poll_script_requires_args():
    """poll.sh fails when invoked without required arguments."""
    poll_sh = Path(REPO) / ".claude" / "skills" / "copilot" / "poll.sh"
    r = subprocess.run(
        ["bash", str(poll_sh)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode != 0, "poll.sh should fail without arguments"


# [pr_diff] fail_to_pass
def test_poll_script_api_and_event():
    """poll.sh detects copilot_work_finished by calling the GitHub timeline API."""
    poll_sh = Path(REPO) / ".claude" / "skills" / "copilot" / "poll.sh"

    with tempfile.TemporaryDirectory() as tmpdir:
        call_log = os.path.join(tmpdir, "gh_calls.log")

        # Mock gh: logs every invocation and returns copilot_work_finished event.
        # Handles both --jq (pre-filtered output) and raw JSON approaches.
        mock_gh_script = (
            '#!/usr/bin/env bash\n'
            'echo "$@" >> "CALL_LOG_PLACEHOLDER"\n'
            'for arg in "$@"; do\n'
            '    if [[ "$arg" == "--jq" ]]; then\n'
            '        echo "2024-01-01T00:00:00Z"\n'
            '        exit 0\n'
            '    fi\n'
            'done\n'
            "echo '[{\"event\":\"copilot_work_finished\",\"created_at\":\"2024-01-01T00:00:00Z\"}]'\n"
            'exit 0\n'
        ).replace("CALL_LOG_PLACEHOLDER", call_log)

        mock_gh_path = os.path.join(tmpdir, "gh")
        with open(mock_gh_path, "w") as f:
            f.write(mock_gh_script)
        os.chmod(mock_gh_path, 0o755)

        # Mock sleep so the polling loop does not block
        mock_sleep_path = os.path.join(tmpdir, "sleep")
        with open(mock_sleep_path, "w") as f:
            f.write("#!/usr/bin/env bash\nexit 0\n")
        os.chmod(mock_sleep_path, 0o755)

        env = os.environ.copy()
        env["PATH"] = tmpdir + ":" + env.get("PATH", "")

        r = subprocess.run(
            ["bash", str(poll_sh), "mlflow/mlflow", "123"],
            capture_output=True, text=True, timeout=30, env=env,
        )
        assert r.returncode == 0, (
            f"poll.sh should exit 0 when copilot_work_finished event is detected.\n"
            f"stdout: {r.stdout}\nstderr: {r.stderr}"
        )
        # Verify the script actually invoked gh (rules out no-op stubs)
        assert os.path.exists(call_log), \
            "poll.sh must call gh to query the GitHub API"
        log_content = open(call_log).read()
        assert len(log_content.strip()) > 0, \
            "poll.sh must invoke gh with arguments"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — SKILL.md config update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_allows_poll_tool():
    """SKILL.md allowed-tools includes poll.sh."""
    skill_md = Path(REPO) / ".claude" / "skills" / "copilot" / "SKILL.md"
    content = skill_md.read_text()
    end = content.index("---", 3)
    frontmatter = content[3:end].strip()
    data = yaml.safe_load(frontmatter)
    tools = data.get("allowed-tools", [])
    assert any("poll.sh" in t for t in tools), \
        f"allowed-tools must include poll.sh, got: {tools}"


# [pr_diff] fail_to_pass
def test_skill_polling_docs():
    """SKILL.md has a polling for completion section with usage instructions."""
    skill_md = Path(REPO) / ".claude" / "skills" / "copilot" / "SKILL.md"
    content = skill_md.read_text()
    content_lower = content.lower()
    assert "polling" in content_lower, \
        "SKILL.md must have a polling section"
    assert "poll.sh" in content, \
        "SKILL.md must reference poll.sh in the polling section"

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

def test_ci_lint_check_uv_lock_changes():
    """pass_to_pass | CI job 'lint' → step 'Check uv.lock changes'"""
    r = subprocess.run(
        ["bash", "-lc", 'files=$(gh pr view "${PR_NUMBER}" --repo "${REPO}" --json files --jq \'.files[].path\')\nif echo "$files" | grep -q \'^uv.lock$\' && echo "$files" | grep -q \'^pyproject.toml$\'; then\n  echo \'::warning file=pyproject.toml,line=1,col=1::[Non-blocking]\' \\\n       \'Ignore if you did not intend to upgrade package versions.\' \\\n       \'`uv lock` does not automatically upgrade package versions\' \\\n       \'when relaxing version constraints (e.g., bumping max version).\' \\\n       \'Use `uv lock --upgrade-package <package>` to upgrade.\'\nfi'], cwd=REPO,
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

def test_ci_build_build_ui():
    """pass_to_pass | CI job 'build' → step 'Build UI'"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn && yarn build'], cwd=os.path.join(REPO, 'mlflow/server/js'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build UI' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_tests_run_fs2db_pytest_tests():
    """pass_to_pass | CI job 'unit-tests' → step 'Run fs2db pytest tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run pytest tests/store/fs2db'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run fs2db pytest tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_external_links_run_external_links_checker():
    """pass_to_pass | CI job 'check-external-links' → step 'Run external links checker'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run check-links'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run external links checker' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")