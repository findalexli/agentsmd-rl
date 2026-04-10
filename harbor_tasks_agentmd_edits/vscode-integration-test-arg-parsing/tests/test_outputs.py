"""
Task: vscode-integration-test-arg-parsing
Repo: microsoft/vscode @ 2de60eada57a6ea88a11ff72091e26b2825e84af
PR:   305837

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path
import stat

REPO = "/workspace/vscode"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified shell scripts must parse without syntax errors."""
    for script in ["scripts/test-integration.sh"]:
        r = subprocess.run(
            ["bash", "-n", script],
            cwd=REPO, capture_output=True, timeout=10,
        )
        assert r.returncode == 0, (
            f"{script} has syntax errors:\n{r.stderr.decode()}"
        )


# [repo_tests] pass_to_pass
def test_all_shell_scripts_syntax():
    """All repo shell scripts must parse without syntax errors."""
    scripts = [
        "scripts/test.sh",
        "scripts/test-integration.sh",
        "scripts/test-remote-integration.sh",
        "scripts/test-web-integration.sh",
        "scripts/test-documentation.sh",
        "scripts/code.sh",
        "scripts/code-cli.sh",
        "scripts/code-server.sh",
        "scripts/code-web.sh",
        "scripts/code-agent-host.sh",
        "scripts/code-sessions-web.sh",
        "scripts/node-electron.sh",
        "scripts/generate-definitelytyped.sh",
        ".github/workflows/check-clean-git-state.sh",
    ]
    for script in scripts:
        r = subprocess.run(
            ["bash", "-n", script],
            cwd=REPO, capture_output=True, timeout=10,
        )
        assert r.returncode == 0, (
            f"{script} has syntax errors:\n{r.stderr.decode()}"
        )


# [static] pass_to_pass
def test_shell_script_executability():
    """Shell scripts referenced in CI are executable."""
    scripts = [
        "scripts/test.sh",
        "scripts/test-integration.sh",
        "scripts/test-remote-integration.sh",
        "scripts/test-web-integration.sh",
    ]
    for script in scripts:
        path = Path(REPO, script)
        if path.exists():
            mode = path.stat().st_mode
            assert mode & stat.S_IXUSR, f"{script} should be executable"


# [repo_tests] pass_to_pass
def test_node_syntax_integration_tests():
    """Node.js can parse modified JS test files (node --check)."""
    files = [
        "test/integration/electron/testrunner.js",
    ]
    for filepath in files:
        r = subprocess.run(
            ["node", "--check", filepath],
            cwd=REPO, capture_output=True, timeout=30,
        )
        assert r.returncode == 0, (
            f"{filepath} has syntax errors:\n{r.stderr.decode()}"
        )


# [repo_tests] pass_to_pass
def test_node_syntax_css_html_tests():
    """Node.js can parse CSS and HTML server test index files."""
    files = [
        "extensions/css-language-features/server/test/index.js",
        "extensions/html-language-features/server/test/index.js",
    ]
    for filepath in files:
        r = subprocess.run(
            ["node", "--check", filepath],
            cwd=REPO, capture_output=True, timeout=30,
        )
        assert r.returncode == 0, (
            f"{filepath} has syntax errors:\n{r.stderr.decode()}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_help_shows_suite_option():
    """test-integration.sh --help must document the --suite option."""
    r = subprocess.run(
        ["bash", "scripts/test-integration.sh", "--help"],
        cwd=REPO, capture_output=True, timeout=10,
    )
    out = r.stdout.decode()
    assert r.returncode == 0, f"--help exited with {r.returncode}"
    assert "--suite" in out, "--help output should document the --suite option"
    assert "--grep" in out, "--help output should document the --grep option"


# [pr_diff] fail_to_pass
def test_help_lists_available_suites():
    """test-integration.sh --help must list known suite names."""
    r = subprocess.run(
        ["bash", "scripts/test-integration.sh", "--help"],
        cwd=REPO, capture_output=True, timeout=10,
    )
    out = r.stdout.decode()
    # Check for a representative sample of suite names
    for suite in ["api-folder", "git", "typescript", "emmet", "css", "html"]:
        assert suite in out, f"--help should list suite '{suite}'"


# [pr_diff] fail_to_pass
def test_invalid_suite_exits_error():
    """--suite with a non-existent name must exit non-zero with a validation error."""
    try:
        r = subprocess.run(
            ["bash", "scripts/test-integration.sh", "--suite", "nonexistent-suite-xyz"],
            cwd=REPO, capture_output=True, timeout=15,
            env={
                "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "HOME": "/root",
                "INTEGRATION_TEST_ELECTRON_PATH": "/bin/true",
            },
        )
    except subprocess.TimeoutExpired:
        raise AssertionError(
            "Script timed out instead of quickly rejecting invalid suite filter"
        )
    combined = r.stdout.decode() + r.stderr.decode()
    assert r.returncode != 0, (
        "Should exit non-zero for invalid suite filter"
    )
    assert "no suites match" in combined.lower(), (
        f"Should report 'no suites match' for invalid filter. Got:\n{combined}"
    )


# [pr_diff] fail_to_pass
def test_mocha_grep_in_test_runners():
    """CSS, HTML, and electron test runners must support MOCHA_GREP env var."""
    files_to_check = [
        "extensions/css-language-features/server/test/index.js",
        "extensions/html-language-features/server/test/index.js",
        "test/integration/electron/testrunner.js",
    ]
    for filepath in files_to_check:
        content = Path(REPO, filepath).read_text()
        assert "MOCHA_GREP" in content, (
            f"{filepath} must read MOCHA_GREP env var to forward grep patterns"
        )
        assert "process.env.MOCHA_GREP" in content, (
            f"{filepath} must use process.env.MOCHA_GREP"
        )


# [pr_diff] fail_to_pass
def test_should_run_suite_function():
    """test-integration.sh must define a should_run_suite function for filtering."""
    content = Path(REPO, "scripts/test-integration.sh").read_text()
    assert "should_run_suite" in content, (
        "Shell script must define should_run_suite function for suite filtering"
    )
    # Verify the function is actually called to gate suite execution
    assert content.count("should_run_suite") >= 3, (
        "should_run_suite must be called multiple times to gate different suites"
    )


# ---------------------------------------------------------------------------
# Config/documentation update tests (config_edit) — fail_to_pass
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
