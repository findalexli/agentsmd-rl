"""
Task: playwright-kill-all-daemon-command
Repo: microsoft/playwright @ 8710e613f8297cebe33c4f6a745999ab4e4907aa
PR:   39116

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

import pytest

REPO = "/workspace/playwright"


# ---------------------------------------------------------------------------
# Build fixture — compiles TypeScript once per test session
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def build():
    """Build the TypeScript project so compiled JS is available."""
    result = subprocess.run(
        ["node", "utils/build/build.js"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"
    return result


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles(build):
    """TypeScript project builds without errors after changes."""
    # The build fixture already asserts success; verify the CLI entry point exists
    cli_js = Path(REPO) / "packages" / "playwright" / "lib" / "mcp" / "terminal" / "cli.js"
    assert cli_js.exists(), f"Compiled CLI entry point not found at {cli_js}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_kill_all_cli_output(build):
    """Running kill-all with no daemons prints 'No daemon processes found.'"""
    result = subprocess.run(
        ["node", "packages/playwright/lib/mcp/terminal/cli.js", "kill-all"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"CLI exited with {result.returncode}:\n{result.stderr}"
    assert "No daemon processes found" in result.stdout, \
        f"Expected 'No daemon processes found' in output, got:\n{result.stdout}"


# [pr_diff] fail_to_pass
def test_kill_all_command_registered(build):
    """kill-all is registered in the commands map."""
    script = (
        "const cmds = require('./packages/playwright/lib/mcp/terminal/commands.js');"
        "const names = Object.keys(cmds.commands);"
        "console.log(JSON.stringify(names));"
    )
    result = subprocess.run(
        ["node", "-e", script],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Failed to load commands:\n{result.stderr}"
    names = json.loads(result.stdout.strip())
    assert "kill-all" in names, f"kill-all not in commands: {names}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — SKILL.md and references must be updated
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/playwright-mcp-dev/SKILL.md:29-30
def test_skill_md_documents_kill_all():
    """SKILL.md must document the kill-all command in the Sessions section."""
    skill_md = Path(REPO) / "packages" / "playwright" / "src" / "skill" / "SKILL.md"
    content = skill_md.read_text()
    assert "kill-all" in content, \
        "SKILL.md should document the kill-all command"
    assert "daemon" in content.lower() or "zombie" in content.lower(), \
        "SKILL.md kill-all entry should mention daemon or zombie processes"


# [agent_config] fail_to_pass — .claude/skills/playwright-mcp-dev/SKILL.md:29-30
def test_session_management_documents_kill_all():
    """session-management.md reference must document the kill-all command."""
    ref_md = (
        Path(REPO) / "packages" / "playwright" / "src"
        / "skill" / "references" / "session-management.md"
    )
    content = ref_md.read_text()
    assert "kill-all" in content, \
        "session-management.md should document the kill-all command"
    assert "daemon" in content.lower() or "zombie" in content.lower() or "unresponsive" in content.lower(), \
        "session-management.md kill-all entry should explain its purpose"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — existing commands preserved
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_session_commands_preserved():
    """Existing session management commands must still be documented in SKILL.md."""
    skill_md = Path(REPO) / "packages" / "playwright" / "src" / "skill" / "SKILL.md"
    content = skill_md.read_text()
    for cmd in ["session-list", "session-stop", "session-restart",
                "session-stop-all", "session-delete"]:
        assert cmd in content, f"Existing command '{cmd}' should still be in SKILL.md"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — npm run build
def test_repo_build():
    """Repo's build command passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — eslint on playwright-core
def test_repo_eslint_playwright_core():
    """Repo's ESLint on playwright-core passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "eslint", "--", "packages/playwright-core/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — eslint on terminal source files (modified code)
def test_repo_eslint_terminal():
    """Repo's ESLint on modified terminal source files passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "eslint", "--", "packages/playwright/src/mcp/terminal/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — build generates valid CLI entry point
def test_repo_build_generates_cli():
    """Build generates playable CLI that can show help (pass_to_pass)."""
    # First build the project
    r1 = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r1.returncode == 0, f"Build failed:\n{r1.stderr[-500:]}"
    # Then verify CLI can run
    cli_js = Path(REPO) / "packages" / "playwright" / "lib" / "mcp" / "terminal" / "cli.js"
    assert cli_js.exists(), f"Compiled CLI entry point not found at {cli_js}"
    r2 = subprocess.run(
        ["node", str(cli_js), "--help"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r2.returncode == 0, f"CLI --help failed:\n{r2.stderr[-500:]}"
    assert "session-list" in r2.stdout, f"CLI help should mention session-list:\n{r2.stdout[:500]}"


# [repo_tests] pass_to_pass — lint-packages workspace check
def test_repo_lint_packages():
    """Repo's workspace package consistency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"lint-packages failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — build generates help.json for CLI
def test_repo_build_generates_help():
    """Build generates CLI help.json file (pass_to_pass)."""
    # First build the project
    r1 = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r1.returncode == 0, f"Build failed:\n{r1.stderr[-500:]}"
    # Verify help.json was generated
    help_json = Path(REPO) / "packages" / "playwright" / "lib" / "mcp" / "terminal" / "help.json"
    assert help_json.exists(), f"Generated CLI help.json not found at {help_json}"
    # Verify it's valid JSON
    content = help_json.read_text()
    help_data = json.loads(content)
    assert "commands" in help_data or "sections" in help_data, f"help.json should contain commands or sections"
