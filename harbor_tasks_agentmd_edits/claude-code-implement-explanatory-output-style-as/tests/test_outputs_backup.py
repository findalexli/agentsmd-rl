"""
Task: claude-code-implement-explanatory-output-style-as
Repo: anthropics/claude-code @ 4dc23d0275ff615ba1dccbdd76ad2b12a3ede591
PR:   10495

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/claude-code"
PLUGIN_DIR = f"{REPO}/plugins/explanatory-output-style"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_plugin_files_exist():
    """Plugin directory and all required files must exist."""
    required_files = [
        f"{PLUGIN_DIR}/.claude-plugin/plugin.json",
        f"{PLUGIN_DIR}/README.md",
        f"{PLUGIN_DIR}/hooks-handlers/session-start.sh",
        f"{PLUGIN_DIR}/hooks/hooks.json",
    ]
    for path in required_files:
        assert Path(path).exists(), f"Missing required file: {path}"


def test_session_start_outputs_valid_json():
    """Session start script must output valid JSON when executed."""
    script_path = f"{PLUGIN_DIR}/hooks-handlers/session-start.sh"
    if not Path(script_path).exists():
        raise AssertionError("session-start.sh does not exist (test_plugin_files_exist should fail)")

    result = subprocess.run(
        ["bash", script_path],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Script failed with exit code {result.returncode}: {result.stderr}"

    # Parse the JSON output
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Script output is not valid JSON: {e}\nOutput:\n{result.stdout}")

    # Validate expected structure
    assert "hookSpecificOutput" in data, "Missing 'hookSpecificOutput' key"
    assert data["hookSpecificOutput"]["hookEventName"] == "SessionStart", "Wrong hookEventName"
    assert "additionalContext" in data["hookSpecificOutput"], "Missing 'additionalContext'"


def test_session_start_has_explanatory_content():
    """Session start output must contain the explanatory mode instructions."""
    script_path = f"{PLUGIN_DIR}/hooks-handlers/session-start.sh"
    if not Path(script_path).exists():
        raise AssertionError("session-start.sh does not exist")

    result = subprocess.run(
        ["bash", script_path],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"

    data = json.loads(result.stdout)
    content = data["hookSpecificOutput"]["additionalContext"]

    # Verify key phrases from the explanatory mode instructions
    assert "explanatory" in content.lower(), "Missing 'explanatory' in content"
    assert "insight" in content.lower(), "Missing 'insight' in content"
    assert "educational" in content.lower(), "Missing 'educational' in content"
    assert "backticks" in content.lower() or "`" in content, "Missing backtick formatting reference"


def test_plugin_json_valid():
    """Plugin manifest must be valid JSON with required fields."""
    plugin_path = f"{PLUGIN_DIR}/.claude-plugin/plugin.json"
    if not Path(plugin_path).exists():
        raise AssertionError("plugin.json does not exist")

    content = Path(plugin_path).read_text()
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise AssertionError(f"plugin.json is not valid JSON: {e}")

    assert data.get("name") == "explanatory-output-style", "Wrong plugin name"
    assert "version" in data, "Missing version field"
    assert "description" in data, "Missing description field"
    assert "author" in data, "Missing author field"


def test_hooks_json_valid():
    """Hooks configuration must be valid JSON with SessionStart handler."""
    hooks_path = f"{PLUGIN_DIR}/hooks/hooks.json"
    if not Path(hooks_path).exists():
        raise AssertionError("hooks.json does not exist")

    content = Path(hooks_path).read_text()
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise AssertionError(f"hooks.json is not valid JSON: {e}")

    assert "hooks" in data, "Missing 'hooks' key"
    assert "SessionStart" in data["hooks"], "Missing SessionStart hook"

    # Verify the hook configuration points to the shell script
    session_hooks = data["hooks"]["SessionStart"]
    assert len(session_hooks) > 0, "Empty SessionStart hooks array"

    # Check that one of the hooks references our session-start.sh script
    found_command = False
    for hook_group in session_hooks:
        for hook in hook_group.get("hooks", []):
            if hook.get("type") == "command":
                cmd = hook.get("command", "")
                if "session-start.sh" in cmd:
                    found_command = True
                    break

    assert found_command, "No command hook found referencing session-start.sh"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + file quality checks
# ---------------------------------------------------------------------------

def test_shell_script_executable():
    """Session start script must be executable (has shebang and proper perms)."""
    script_path = Path(f"{PLUGIN_DIR}/hooks-handlers/session-start.sh")
    if not script_path.exists():
        # Skip if file doesn't exist (let fail_to_pass test handle it)
        return

    # Check for shebang
    content = script_path.read_text()
    assert content.startswith("#!/"), "Script missing shebang line"

    # Check that bash is used
    assert "#!/bin/bash" in content or "#!/usr/bin/env bash" in content, "Script should use bash"


def test_readme_documents_usage():
    """README must document the plugin purpose and usage."""
    readme_path = Path(f"{PLUGIN_DIR}/README.md")
    if not readme_path.exists():
        return  # Skip if missing

    content = readme_path.read_text()

    # Check for key documentation sections
    assert "# Explanatory" in content or "explanatory" in content.lower(), "Missing plugin name in README"
    assert "SessionStart" in content or "hook" in content.lower(), "Missing hook reference"
    assert "educational" in content.lower() or "insight" in content.lower(), "Missing educational content reference"
