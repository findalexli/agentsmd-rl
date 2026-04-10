"""
Task: uv-ci-snapshot-apply-script
Repo: astral-sh/uv @ dd0d76cd83821e22a7054de21eb73051eb23274d
PR:   #18424

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import tomllib
from pathlib import Path

import yaml

REPO = "/workspace/uv"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """CI workflow YAML must parse without errors."""
    workflow = Path(REPO) / ".github" / "workflows" / "test.yml"
    content = workflow.read_text()
    data = yaml.safe_load(content)
    assert isinstance(data, dict), "Workflow YAML should parse to a dict"
    assert "jobs" in data, "Workflow YAML should have a jobs key"


# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's Python scripts pass ruff linting (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check", "scripts/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's Python scripts are properly formatted (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "format", "--diff", "scripts/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_shellcheck_scripts():
    """Repo's shell scripts pass shellcheck (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "shellcheck-py", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Find shell scripts and run shellcheck
    r = subprocess.run(
        ["bash", "-c", f"find {REPO}/scripts -name '*.sh' -type f | head -20 | xargs shellcheck --shell bash --severity warning"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"shellcheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_validate_pyproject():
    """Repo's pyproject.toml is valid (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "validate-pyproject", "packaging", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["validate-pyproject", f"{REPO}/pyproject.toml"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"validate-pyproject failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typos():
    """Repo has no typos (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "typos", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["typos"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"typos check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — CI workflow changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_workflow_sets_insta_env_vars():
    """CI test jobs must set INSTA_UPDATE and INSTA_PENDING_DIR env vars."""
    workflow = Path(REPO) / ".github" / "workflows" / "test.yml"
    data = yaml.safe_load(workflow.read_text())
    jobs = data["jobs"]

    for job_key in ["cargo-test-linux", "cargo-test-windows"]:
        job = jobs[job_key]
        steps = job["steps"]
        nextest_steps = [
            s for s in steps
            if isinstance(s.get("run", ""), str) and "nextest" in s.get("run", "")
        ]
        assert len(nextest_steps) > 0, f"No nextest step found in {job_key}"
        env = nextest_steps[0].get("env", {})
        assert env.get("INSTA_UPDATE") == "new", \
            f"{job_key}: INSTA_UPDATE should be 'new', got {env.get('INSTA_UPDATE')}"
        assert "INSTA_PENDING_DIR" in env, \
            f"{job_key}: INSTA_PENDING_DIR env var should be set"


# [pr_diff] fail_to_pass
def test_workflow_uploads_pending_snapshots():
    """CI test jobs must upload pending snapshot artifacts on failure."""
    workflow = Path(REPO) / ".github" / "workflows" / "test.yml"
    data = yaml.safe_load(workflow.read_text())
    jobs = data["jobs"]

    platforms_with_upload = set()
    for job_key, job in jobs.items():
        if not job_key.startswith("cargo-test"):
            continue
        steps = job["steps"]
        for step in steps:
            uses = step.get("uses", "")
            if "upload-artifact" in uses:
                with_block = step.get("with", {})
                name = str(with_block.get("name", ""))
                if "pending-snapshots" in name:
                    condition = step.get("if", "")
                    assert "failure()" in condition, \
                        f"Upload step in {job_key} should only run on failure"
                    platforms_with_upload.add(job_key)

    assert "cargo-test-linux" in platforms_with_upload, \
        "Linux test job should upload pending snapshots"
    assert "cargo-test-windows" in platforms_with_upload, \
        "Windows test job should upload pending snapshots"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — script behavior
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_script_rejects_invalid_action():
    """The apply-ci-snapshots script must reject invalid action arguments."""
    script = Path(REPO) / "scripts" / "apply-ci-snapshots.sh"
    assert script.exists(), "scripts/apply-ci-snapshots.sh should exist"

    # Use a shell command to create mock binaries and run the test
    cmd = f"""
    tmpbin=$(mktemp -d)
    for cmd in gh cargo-insta git; do
        echo '#!/bin/sh' > "$tmpbin/$cmd"
        echo 'exit 0' >> "$tmpbin/$cmd"
        chmod +x "$tmpbin/$cmd"
    done
    export PATH="$tmpbin:$PATH"
    bash '{script}' 12345 badaction 2>&1
    """
    r = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode != 0, "Script should exit non-zero for invalid action"
    combined = r.stdout + r.stderr
    assert "accept" in combined, \
        "Error message should mention valid actions"
    assert "review" in combined, \
        "Error message should mention 'review' as valid action"


# [pr_diff] fail_to_pass
def test_script_detects_missing_tools():
    """The apply-ci-snapshots script must detect missing required tools."""
    script = Path(REPO) / "scripts" / "apply-ci-snapshots.sh"
    assert script.exists(), "scripts/apply-ci-snapshots.sh should exist"

    # Use a minimal PATH that has bash but not gh, cargo-insta, or git
    minimal_path = "/bin:/usr/bin"
    r = subprocess.run(
        ["bash", str(script), "12345"],
        capture_output=True, text=True, timeout=10,
        env={"PATH": minimal_path, "HOME": "/tmp"},
    )
    assert r.returncode != 0, "Script should exit non-zero when tools are missing"
    combined = r.stdout + r.stderr
    assert "required" in combined.lower() or "not found" in combined.lower(), \
        "Error message should indicate a tool is missing/required"


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config edit (config_edit) — CONTRIBUTING.md update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
