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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual CI commands that validate existing plugins
# ---------------------------------------------------------------------------

# Existing plugin paths for pass-to-pass testing
EXISTING_PLUGIN_DIR = f"{REPO}/plugins/security-guidance"
AGENT_SDK_DEV_DIR = f"{REPO}/plugins/agent-sdk-dev"
FEATURE_DEV_DIR = f"{REPO}/plugins/feature-dev"
PR_REVIEW_DIR = f"{REPO}/plugins/pr-review-toolkit"


def test_repo_security_guidance_plugin_json_valid():
    """Security-guidance plugin manifest JSON is syntactically valid (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", f"import json; json.load(open('{EXISTING_PLUGIN_DIR}/.claude-plugin/plugin.json'))"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"plugin.json is not valid JSON: {result.stderr}"


def test_repo_security_guidance_hooks_json_valid():
    """Security-guidance hooks configuration JSON is syntactically valid (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", f"import json; json.load(open('{EXISTING_PLUGIN_DIR}/hooks/hooks.json'))"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"hooks.json is not valid JSON: {result.stderr}"


def test_repo_security_guidance_hook_script_valid_python():
    """Security-guidance hook script has valid Python syntax (pass_to_pass)."""
    script_path = f"{EXISTING_PLUGIN_DIR}/hooks/security_reminder_hook.py"
    result = subprocess.run(
        ["python3", "-m", "py_compile", script_path],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"security_reminder_hook.py has Python syntax errors: {result.stderr}"


def test_repo_all_plugin_jsons_valid():
    """All plugin.json files across plugins are syntactically valid JSON (pass_to_pass)."""
    # Use raw string to avoid escape sequence warnings
    cmd = (
        r"find " + REPO + r"/plugins -name 'plugin.json' -exec python3 -c "
        r"'import json; json.load(open(\"{}\"))' \;"
    )
    result = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Plugin JSON validation failed: {result.stderr}"


def test_repo_all_hooks_jsons_valid():
    """All hooks.json files across plugins are syntactically valid JSON (pass_to_pass)."""
    # Use raw string to avoid escape sequence warnings
    cmd = (
        r"find " + REPO + r"/plugins -name 'hooks.json' -exec python3 -c "
        r"'import json; json.load(open(\"{}\"))' \;"
    )
    result = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Hooks JSON validation failed: {result.stderr}"


def test_repo_agent_sdk_dev_plugin_json_valid():
    """Agent-sdk-dev plugin manifest JSON is syntactically valid (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", f"import json; json.load(open('{AGENT_SDK_DEV_DIR}/.claude-plugin/plugin.json'))"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"agent-sdk-dev plugin.json is not valid JSON: {result.stderr}"


def test_repo_feature_dev_plugin_json_valid():
    """Feature-dev plugin manifest JSON is syntactically valid (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", f"import json; json.load(open('{FEATURE_DEV_DIR}/.claude-plugin/plugin.json'))"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"feature-dev plugin.json is not valid JSON: {result.stderr}"


def test_repo_pr_review_plugin_json_valid():
    """PR-review-toolkit plugin manifest JSON is syntactically valid (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", f"import json; json.load(open('{PR_REVIEW_DIR}/.claude-plugin/plugin.json'))"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"pr-review-toolkit plugin.json is not valid JSON: {result.stderr}"


def test_repo_examples_hook_valid_python():
    """Examples hook (bash_command_validator_example.py) has valid Python syntax (pass_to_pass)."""
    script_path = f"{REPO}/examples/hooks/bash_command_validator_example.py"
    result = subprocess.run(
        ["python3", "-m", "py_compile", script_path],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"bash_command_validator_example.py has Python syntax errors: {result.stderr}"


def test_repo_marketplace_json_valid():
    """Plugin marketplace.json is syntactically valid JSON (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", f"import json; json.load(open('{REPO}/.claude-plugin/marketplace.json'))"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"marketplace.json is not valid JSON: {result.stderr}"


def test_repo_devcontainer_json_valid():
    """Devcontainer configuration JSON is syntactically valid (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-c", f"import json; json.load(open('{REPO}/.devcontainer/devcontainer.json'))"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"devcontainer.json is not valid JSON: {result.stderr}"


def test_repo_devcontainer_script_valid_bash():
    """Devcontainer init script has valid bash syntax (pass_to_pass)."""
    script_path = f"{REPO}/.devcontainer/init-firewall.sh"
    result = subprocess.run(
        ["bash", "-n", script_path],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"init-firewall.sh has bash syntax errors: {result.stderr}"


# ---------------------------------------------------------------------------
# Additional Pass-to-pass (repo_tests) — Plugin README structure validation
# ---------------------------------------------------------------------------

def test_repo_plugins_readme_exists():
    """Plugins README.md exists (pass_to_pass)."""
    result = subprocess.run(
        ["test", "-f", f"{REPO}/plugins/README.md"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert result.returncode == 0, "plugins/README.md does not exist"


def test_repo_plugins_readme_has_plugin_structure_docs():
    """Plugins README documents the plugin structure (pass_to_pass)."""
    result = subprocess.run(
        ["grep", "-q", "plugin.json", f"{REPO}/plugins/README.md"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert result.returncode == 0, "plugins/README.md does not document plugin.json structure"


def test_repo_code_review_readme_exists():
    """Code-review plugin README exists (pass_to_pass)."""
    result = subprocess.run(
        ["test", "-f", f"{REPO}/plugins/code-review/README.md"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert result.returncode == 0, "code-review README.md does not exist"


def test_repo_commit_commands_readme_exists():
    """Commit-commands plugin README exists (pass_to_pass)."""
    result = subprocess.run(
        ["test", "-f", f"{REPO}/plugins/commit-commands/README.md"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert result.returncode == 0, "commit-commands README.md does not exist"
