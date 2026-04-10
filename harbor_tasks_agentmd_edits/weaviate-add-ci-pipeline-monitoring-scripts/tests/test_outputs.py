"""
Task: weaviate-add-ci-pipeline-monitoring-scripts
Repo: weaviate/weaviate @ 57d1e03321fd1648889b5c3fae5261cf5a7a0217
PR:   10542

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import stat
import subprocess
from pathlib import Path

REPO = "/workspace/weaviate"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_shell_syntax():
    """All shell scripts in .claude/scripts/ must parse without errors."""
    scripts_dir = Path(REPO) / ".claude" / "scripts"
    assert scripts_dir.is_dir(), ".claude/scripts/ directory must exist"
    sh_files = list(scripts_dir.glob("*.sh"))
    assert len(sh_files) >= 2, f"Expected at least 2 scripts, found {len(sh_files)}"
    for script in sh_files:
        r = subprocess.run(
            ["bash", "-n", str(script)],
            capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0, f"Syntax error in {script.name}: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_monitor_pr_script_exists_and_executable():
    """monitor_pr.sh must exist, be executable, and accept PR env var."""
    script = Path(REPO) / ".claude" / "scripts" / "monitor_pr.sh"
    assert script.exists(), "monitor_pr.sh must exist at .claude/scripts/monitor_pr.sh"
    assert script.stat().st_mode & stat.S_IXUSR, "monitor_pr.sh must be executable"
    content = script.read_text()
    # Must accept PR as env variable
    assert "PR=" in content or "PR}" in content or "${PR" in content, \
        "monitor_pr.sh must accept PR number via PR env variable"
    # Must use gh pr checks
    assert "gh pr checks" in content, \
        "monitor_pr.sh must use 'gh pr checks' to poll CI status"
    # Must report pass/fail counts
    assert "PASS" in content and "FAIL" in content, \
        "monitor_pr.sh must report pass and fail counts"


# [pr_diff] fail_to_pass
def test_monitor_pr_exits_on_missing_pr():
    """monitor_pr.sh should exit with error when no PR number provided."""
    script = Path(REPO) / ".claude" / "scripts" / "monitor_pr.sh"
    assert script.exists(), "monitor_pr.sh must exist"
    # Run without PR env var — script should exit quickly with non-zero
    env = dict(os.environ)
    env.pop("PR", None)
    r = subprocess.run(
        ["bash", str(script)],
        capture_output=True, text=True, timeout=10,
        env=env,
    )
    assert r.returncode != 0, \
        "monitor_pr.sh should exit non-zero when PR is not set"
    assert "usage" in r.stdout.lower() or "usage" in r.stderr.lower() or "PR=" in r.stdout or "PR=" in r.stderr, \
        "monitor_pr.sh should print usage when PR is missing"


# [pr_diff] fail_to_pass
def test_monitor_docker_script_exists_and_executable():
    """monitor_docker.sh must exist, be executable, and validate args."""
    script = Path(REPO) / ".claude" / "scripts" / "monitor_docker.sh"
    assert script.exists(), "monitor_docker.sh must exist at .claude/scripts/monitor_docker.sh"
    assert script.stat().st_mode & stat.S_IXUSR, "monitor_docker.sh must be executable"
    content = script.read_text()
    # Must accept run_id as argument
    assert "RUN_ID" in content or "run_id" in content.lower(), \
        "monitor_docker.sh must accept a run ID"
    # Must use gh run view or gh api
    assert "gh run view" in content or "gh api" in content, \
        "monitor_docker.sh must use GitHub CLI to check run status"


# [pr_diff] fail_to_pass
def test_monitor_docker_exits_on_missing_arg():
    """monitor_docker.sh should exit with error when no run ID provided."""
    script = Path(REPO) / ".claude" / "scripts" / "monitor_docker.sh"
    assert script.exists(), "monitor_docker.sh must exist"
    r = subprocess.run(
        ["bash", str(script)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode != 0, \
        "monitor_docker.sh should exit non-zero when no run ID is provided"


# [pr_diff] fail_to_pass
def test_gitignore_allows_claude_scripts():
    """.gitignore must allow .claude/scripts/ to be tracked."""
    gitignore = Path(REPO) / ".gitignore"
    content = gitignore.read_text()
    # Must have a negation pattern for .claude/scripts/
    assert "!.claude/scripts" in content, \
        ".gitignore must contain '!.claude/scripts/' to allow tracking scripts"


# ---------------------------------------------------------------------------
# Config-edit (pr_diff) — CLAUDE.md documentation update
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_claude_md_has_ci_monitoring_section():
    """CLAUDE.md must have a CI / Pipeline Monitoring section."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()
    content_lower = content.lower()
    assert "ci" in content_lower and "monitor" in content_lower, \
        "CLAUDE.md must document CI monitoring"
    assert "monitor_pr" in content or "monitor_pr.sh" in content, \
        "CLAUDE.md must reference the PR monitoring script"
    assert "monitor_docker" in content or "monitor_docker.sh" in content, \
        "CLAUDE.md must reference the Docker monitoring script"


# [pr_diff] fail_to_pass
def test_claude_md_documents_script_usage():
    """CLAUDE.md must document how to use the monitoring scripts."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()
    # Must show PR usage pattern
    assert "PR=" in content or "PR =" in content, \
        "CLAUDE.md must document the PR= env var usage for monitor_pr.sh"
    # Must mention gh pr checks or rerun
    assert "rerun" in content.lower() or "re-run" in content.lower() or "gh run rerun" in content, \
        "CLAUDE.md must document how to re-run failed jobs"
    # Must mention .claude/scripts/ as the script location
    assert ".claude/scripts" in content, \
        "CLAUDE.md must reference .claude/scripts/ directory"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI checks that should pass on base commit
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_go_build():
    """Repo's Go code compiles successfully (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/weaviate && GOTOOLCHAIN=auto go build ./..."],
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"Go build failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_linter_error_groups():
    """Repo's error groups custom linter passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/weaviate && ./tools/linter_error_groups.sh"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Error groups linter failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_linter_go_routines():
    """Repo's go routines custom linter passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/weaviate && ./tools/linter_go_routines.sh"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Go routines linter failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_linter_waitgroups():
    """Repo's waitgroups custom linter passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/weaviate && ./tools/linter_waitgroups_done.sh"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Waitgroups linter failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ci_scripts_syntax():
    """All CI shell scripts have valid syntax (pass_to_pass)."""
    scripts = [
        "ci/push_docker.sh",
        "ci/generate_docker_report.sh",
        "tools/linter_error_groups.sh",
        "tools/linter_go_routines.sh",
        "tools/linter_waitgroups_done.sh",
        "tools/gen-code-from-swagger.sh",
    ]
    for script in scripts:
        script_path = Path(REPO) / script
        if script_path.exists():
            r = subprocess.run(
                ["bash", "-n", str(script_path)],
                capture_output=True, text=True, timeout=10,
            )
            assert r.returncode == 0, f"Syntax error in {script}: {r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_claude_md_preserves_existing_sections():
    """CLAUDE.md must still contain the original sections."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()
    # Key existing sections that must be preserved
    assert "## Build & Run" in content, "CLAUDE.md must preserve Build & Run section"
    assert "## Testing" in content, "CLAUDE.md must preserve Testing section"
    assert "## Architecture" in content, "CLAUDE.md must preserve Architecture section"
    assert "## Code Conventions" in content, "CLAUDE.md must preserve Code Conventions section"
