"""
Task: posthog-chore-playwright-flake-verification-ci
Repo: PostHog/posthog @ e74eb42064ccff936e8b2039626646132a444c8d
PR:   51426

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/posthog"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_shell_script_syntax():
    """Verification shell script must exist and parse without bash syntax errors."""
    script = Path(REPO) / ".github" / "scripts" / "verify-playwright-new-tests-and-snapshots.sh"
    assert script.exists(), "Verification script does not exist"
    r = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Bash syntax error:\n{r.stderr}"


# [static] pass_to_pass
def test_workflow_yaml_valid():
    """CI workflow file must be valid YAML."""
    import yaml

    wf = Path(REPO) / ".github" / "workflows" / "ci-e2e-playwright.yml"
    content = wf.read_text()
    try:
        yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise AssertionError(f"Workflow YAML is invalid: {e}")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_bash_syntax_verify_script():
    """Bash syntax check for the verification script (pass_to_pass)."""
    # This script is created by the fix; syntax check validates it's well-formed bash
    script = Path(REPO) / ".github" / "scripts" / "verify-playwright-new-tests-and-snapshots.sh"
    assert script.exists(), "Verification script does not exist"
    r = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Bash syntax error:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_python_syntax_check_scripts():
    """Python syntax check for CI scripts (pass_to_pass)."""
    scripts = [
        ".github/scripts/check-idor-model-coverage.py",
        ".github/scripts/check-operator-parity.py",
    ]
    for script_path in scripts:
        full_path = Path(REPO) / script_path
        if full_path.exists():
            r = subprocess.run(
                ["python3", "-m", "py_compile", str(full_path)],
                capture_output=True, text=True, timeout=10,
            )
            assert r.returncode == 0, f"Python syntax error in {script_path}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_workflow_yaml_validates():
    """CI workflow files are valid YAML (pass_to_pass)."""
    import yaml

    workflows = [
        ".github/workflows/ci-e2e-playwright.yml",
        ".github/workflows/ci-frontend.yml",
    ]
    for wf_path in workflows:
        full_path = Path(REPO) / wf_path
        if full_path.exists():
            content = full_path.read_text()
            try:
                yaml.safe_load(content)
            except yaml.YAMLError as e:
                raise AssertionError(f"Workflow YAML {wf_path} is invalid: {e}")


# [repo_tests] pass_to_pass
def test_repo_shell_scripts_syntax():
    """Shell script syntax check for CI scripts (pass_to_pass)."""
    scripts = [
        ".github/scripts/verify-new-snapshots.sh",
        ".github/scripts/count-snapshot-changes.sh",
    ]
    for script_path in scripts:
        full_path = Path(REPO) / script_path
        if full_path.exists():
            r = subprocess.run(
                ["bash", "-n", str(full_path)],
                capture_output=True, text=True, timeout=10,
            )
            assert r.returncode == 0, f"Bash syntax error in {script_path}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_playwright_package_json():
    """Playwright package.json is valid JSON (pass_to_pass)."""
    import json

    pkg_path = Path(REPO) / "playwright" / "package.json"
    assert pkg_path.exists(), "Playwright package.json does not exist"
    r = subprocess.run(
        ["python3", "-c", f"import json; json.load(open('{pkg_path}')); print('JSON valid')"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Invalid JSON in playwright/package.json:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_verify_new_snapshots_syntax():
    """Shell script syntax check for verify-new-snapshots.sh (pass_to_pass)."""
    script = Path(REPO) / ".github" / "scripts" / "verify-new-snapshots.sh"
    assert script.exists(), "verify-new-snapshots.sh does not exist"
    r = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Bash syntax error in verify-new-snapshots.sh:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_count_snapshot_changes_syntax():
    """Shell script syntax check for count-snapshot-changes.sh (pass_to_pass)."""
    script = Path(REPO) / ".github" / "scripts" / "count-snapshot-changes.sh"
    assert script.exists(), "count-snapshot-changes.sh does not exist"
    r = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Bash syntax error in count-snapshot-changes.sh:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_trigger_vercel_preview_syntax():
    """Shell script syntax check for trigger-vercel-preview.sh (pass_to_pass)."""
    script = Path(REPO) / ".github" / "scripts" / "trigger-vercel-preview.sh"
    assert script.exists(), "trigger-vercel-preview.sh does not exist"
    r = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Bash syntax error in trigger-vercel-preview.sh:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_optimize_test_durations_syntax():
    """Python syntax check for optimize_test_durations.py (pass_to_pass)."""
    script = Path(REPO) / ".github" / "scripts" / "optimize_test_durations.py"
    assert script.exists(), "optimize_test_durations.py does not exist"
    r = subprocess.run(
        ["python3", "-m", "py_compile", str(script)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Python syntax error in optimize_test_durations.py:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_verification_script_validates_args():
    """Verification script must validate arguments and reject bad input."""
    script = Path(REPO) / ".github" / "scripts" / "verify-playwright-new-tests-and-snapshots.sh"
    assert script.exists(), "Verification script does not exist"

    # No args → should fail with usage message
    r = subprocess.run(
        ["bash", str(script)],
        capture_output=True, text=True, timeout=10,
        cwd=REPO,
    )
    assert r.returncode != 0, "Script should fail when called with no arguments"
    assert "usage" in r.stderr.lower() or "usage" in r.stdout.lower(), \
        "Script should print usage info on bad args"

    # Invalid repeat_count → should fail
    r2 = subprocess.run(
        ["bash", str(script), "HEAD", "notanumber"],
        capture_output=True, text=True, timeout=10,
        cwd=REPO,
    )
    assert r2.returncode != 0, "Script should reject non-numeric repeat_count"


# [pr_diff] fail_to_pass
def test_verification_script_detects_changed_specs():
    """Script uses git diff to find changed playwright spec files."""
    script = Path(REPO) / ".github" / "scripts" / "verify-playwright-new-tests-and-snapshots.sh"
    content = script.read_text()

    # Must use git diff to find changed spec files
    assert "git diff" in content, "Script should use git diff to detect changes"
    assert "spec.ts" in content, "Script should filter for .spec.ts files"
    assert "playwright/" in content or "playwright/**" in content, \
        "Script should scope detection to playwright directory"


# [pr_diff] fail_to_pass
def test_verification_script_repeat_each():
    """Script must run playwright with --repeat-each for flake detection."""
    script = Path(REPO) / ".github" / "scripts" / "verify-playwright-new-tests-and-snapshots.sh"
    content = script.read_text()

    assert "--repeat-each" in content, "Script must use --repeat-each flag"
    assert "--retries=0" in content or "--retries 0" in content, \
        "Script must disable retries to catch genuine flakes"
    assert "write_results" in content or "results" in content.lower(), \
        "Script should write results for CI reporting"


# [pr_diff] fail_to_pass
def test_workflow_has_verification_step():
    """CI workflow must include the flake verification step for PRs."""
    wf = Path(REPO) / ".github" / "workflows" / "ci-e2e-playwright.yml"
    content = wf.read_text()

    assert "verify-playwright-new-tests-and-snapshots" in content, \
        "Workflow must reference the verification script"
    assert "pull_request" in content, \
        "Verification should run on pull requests"


# [pr_diff] fail_to_pass
def test_workflow_reports_flake_results():
    """CI workflow must read flake verification results and include them in PR comments."""
    wf = Path(REPO) / ".github" / "workflows" / "ci-e2e-playwright.yml"
    content = wf.read_text()

    assert "flake-verification-results.json" in content, \
        "Workflow must read the flake verification results JSON"
    assert "flake" in content.lower() and "verification" in content.lower() and "failed" in content.lower(), \
        "Workflow must report flake verification failures"


# ---------------------------------------------------------------------------
# Config/doc update tests (agentmd-edit) — REQUIRED
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_references_readme():
    """SKILL.md must reference playwright/README.md instead of duplicating best practices inline."""
    skill = Path(REPO) / ".agents" / "skills" / "playwright-test" / "SKILL.md"
    content = skill.read_text()

    # Should reference the README
    assert "readme" in content.lower(), \
        "SKILL.md should reference the README for best practices"

    # Should NOT still have the old inline rules that were moved to README
    assert "css selector" not in content.lower(), \
        "SKILL.md should not duplicate CSS selector rule (moved to README)"
    assert "page object model" not in content.lower(), \
        "SKILL.md should not duplicate page object model rule (moved to README)"


# [pr_diff] fail_to_pass
def test_readme_has_best_practices():
    """playwright/README.md must have a best practices section with key rules."""
    readme = Path(REPO) / "playwright" / "README.md"
    content = readme.read_text()

    # Must have a best practices section (the old README had no such section)
    assert "best practices" in content.lower(), \
        "README should have a 'Best practices' section"

    # Must include specific rules moved from SKILL.md
    assert "getbyrole" in content.lower() or "getbytestid" in content.lower(), \
        "README should mention getByRole or getByTestId as preferred selectors"
    assert "page object model" in content.lower() or "page-models" in content.lower(), \
        "README should mention page object models"
    assert "test.step" in content.lower() or "test.step()" in content, \
        "README should mention test.step() for splitting logical steps"


# [agent_config] fail_to_pass
def test_readme_has_gotchas_section():
    """playwright/README.md must have a gotchas section covering flaky tests and selectors."""
    readme = Path(REPO) / "playwright" / "README.md"
    content = readme.read_text()

    assert "gotcha" in content.lower(), \
        "README should have a 'Gotchas' section"
    assert "flaky" in content.lower(), \
        "README gotchas should mention flaky tests"
    assert "strict mode" in content.lower() or "loose selector" in content.lower(), \
        "README gotchas should mention strict mode violations or loose selectors"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_script_not_stub():
    """Verification script must have real logic, not be a stub."""
    script = Path(REPO) / ".github" / "scripts" / "verify-playwright-new-tests-and-snapshots.sh"
    content = script.read_text()
    lines = [l for l in content.strip().splitlines() if l.strip() and not l.strip().startswith("#")]
    assert len(lines) >= 20, \
        f"Script has only {len(lines)} non-comment lines — likely a stub"
    assert "playwright test" in content, \
        "Script must actually invoke playwright test"
