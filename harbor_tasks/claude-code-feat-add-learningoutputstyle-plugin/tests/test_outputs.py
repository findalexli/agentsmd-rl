"""
Task: Add learning-output-style Plugin
Repo: anthropics/claude-code @ ae411f846195b38c8bec88914dd06132e00eadf8
PR:   10826

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import os
from pathlib import Path

REPO = "/workspace/claude-code"
PLUGIN_DIR = f"{REPO}/plugins/learning-output-style"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_plugin_json_valid():
    """Plugin manifest exists and is valid JSON with required fields."""
    path = Path(f"{PLUGIN_DIR}/.claude-plugin/plugin.json")
    assert path.exists(), f"plugin.json not found at {path}"

    content = path.read_text()
    manifest = json.loads(content)

    assert manifest.get("name") == "learning-output-style", "Plugin name incorrect"
    assert manifest.get("version") == "1.0.0", "Plugin version incorrect"
    assert "description" in manifest, "Plugin description missing"
    assert "Learning" in manifest.get("description", ""), "Description should mention Learning"
    assert "author" in manifest, "Plugin author missing"
    assert manifest["author"].get("name"), "Author name missing"


def test_hooks_json_valid():
    """Hooks configuration exists and has valid SessionStart hook."""
    path = Path(f"{PLUGIN_DIR}/hooks/hooks.json")
    assert path.exists(), f"hooks.json not found at {path}"

    content = path.read_text()
    config = json.loads(content)

    assert "hooks" in config, "hooks field missing"
    assert "SessionStart" in config["hooks"], "SessionStart hook not configured"

    hooks = config["hooks"]["SessionStart"]
    assert len(hooks) > 0, "SessionStart hooks array empty"

    hook_def = hooks[0]
    assert "hooks" in hook_def, "Nested hooks field missing"
    assert len(hook_def["hooks"]) > 0, "Hook command not defined"

    cmd_hook = hook_def["hooks"][0]
    assert cmd_hook.get("type") == "command", "Hook type should be 'command'"
    assert "command" in cmd_hook, "Hook command missing"
    assert "session-start.sh" in cmd_hook["command"], "Command should reference session-start.sh"


def test_session_start_executable():
    """Session-start hook script is executable and outputs valid JSON."""
    script_path = Path(f"{PLUGIN_DIR}/hooks-handlers/session-start.sh")
    assert script_path.exists(), f"session-start.sh not found at {script_path}"

    # Check executable permission
    assert os.access(script_path, os.X_OK), "session-start.sh is not executable"

    # Run the script and verify output
    result = subprocess.run(
        [str(script_path)],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"

    # Verify output is valid JSON
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Script output is not valid JSON: {e}")

    # Verify required structure
    assert "hookSpecificOutput" in output, "hookSpecificOutput field missing"
    assert output["hookSpecificOutput"].get("hookEventName") == "SessionStart", \
        "hookEventName should be SessionStart"
    assert "additionalContext" in output["hookSpecificOutput"], "additionalContext missing"

    content = output["hookSpecificOutput"]["additionalContext"]
    assert "learning" in content.lower(), "additionalContext should mention learning"
    assert "Insight" in content, "additionalContext should mention Insight formatting"


def test_readme_exists():
    """README.md exists and contains required documentation."""
    path = Path(f"{PLUGIN_DIR}/README.md")
    assert path.exists(), f"README.md not found at {path}"

    content = path.read_text()
    assert "# Learning Style Plugin" in content, "README title incorrect"
    assert "SessionStart" in content, "README should mention SessionStart hook"
    assert "What it does" in content, "README should have 'What it does' section"
    assert "How it works" in content, "README should have 'How it works' section"


def test_gitignore_updated():
    """.gitignore exists at root and ignores .DS_Store."""
    path = Path(f"{REPO}/.gitignore")
    assert path.exists(), ".gitignore not found at root"

    content = path.read_text()
    assert ".DS_Store" in content, ".gitignore should ignore .DS_Store"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural verification
# ---------------------------------------------------------------------------

def test_plugin_directory_structure():
    """Plugin directory structure matches expected layout."""
    dirs_to_check = [
        f"{PLUGIN_DIR}/.claude-plugin",
        f"{PLUGIN_DIR}/hooks",
        f"{PLUGIN_DIR}/hooks-handlers",
    ]
    for d in dirs_to_check:
        assert Path(d).is_dir(), f"Directory missing: {d}"


def test_session_start_has_shebang():
    """Session-start script has proper shebang line."""
    path = Path(f"{PLUGIN_DIR}/hooks-handlers/session-start.sh")
    content = path.read_text()
    assert content.startswith("#!/bin/bash"), "Script should start with bash shebang"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI-style validation
# ---------------------------------------------------------------------------

def test_repo_all_plugin_json_valid():
    """All plugin.json files in the repo are valid JSON (pass_to_pass)."""
    cmd = """for f in /workspace/claude-code/plugins/*/.claude-plugin/plugin.json; do python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$f" || exit 1; done"""
    r = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Plugin JSON validation failed:\n{r.stderr[-500:]}"


def test_repo_all_hooks_json_valid():
    """All hooks.json files in the repo are valid JSON (pass_to_pass)."""
    cmd = """for f in /workspace/claude-code/plugins/*/hooks/hooks.json; do python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$f" || exit 1; done"""
    r = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Hooks JSON validation failed:\n{r.stderr[-500:]}"


def test_repo_shellcheck_passes():
    """All shell scripts in plugins pass shellcheck (pass_to_pass)."""
    cmd = "apt-get update -qq && apt-get install -y -qq shellcheck >/dev/null 2>&1 && find /workspace/claude-code/plugins -name '*.sh' -type f -exec shellcheck {} +"
    r = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Shellcheck failed:\n{r.stderr[-500:]}"


def test_repo_explanatory_hook_runs():
    """Existing explanatory plugin session-start hook executes successfully (pass_to_pass)."""
    cmd = "apt-get update -qq && apt-get install -y -qq jq >/dev/null 2>&1 && export CLAUDE_PLUGIN_ROOT=/workspace/claude-code/plugins/explanatory-output-style && timeout 30 /workspace/claude-code/plugins/explanatory-output-style/hooks-handlers/session-start.sh >/dev/null 2>&1"
    r = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Explanatory hook failed to run:\n{r.stderr[-500:]}"


def test_repo_python_syntax_valid():
    """All Python files in the repo have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "find /workspace/claude-code -name '*.py' -type f -exec python3 -m py_compile {} +"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax validation failed:\n{r.stderr[-500:]}"


def test_repo_security_hook_imports():
    """Security guidance hook can be imported without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import importlib.util; "
         "spec = importlib.util.spec_from_file_location('hook', '/workspace/claude-code/plugins/security-guidance/hooks/security_reminder_hook.py'); "
         "module = importlib.util.module_from_spec(spec); "
         "spec.loader.exec_module(module)"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Security hook import failed:\n{r.stderr[-500:]}"


def test_repo_all_plugins_have_valid_name():
    """All plugins have plugin.json with required 'name' field (pass_to_pass)."""
    cmd = """for f in /workspace/claude-code/plugins/*/.claude-plugin/plugin.json; do if ! python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d.get("name"), "missing name"' "$f" 2>/dev/null; then echo "Invalid plugin.json: $f"; exit 1; fi; done"""
    r = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Plugin missing name field:\n{r.stderr[-500:]}"


def test_repo_all_hooks_json_have_hooks_field():
    """All hooks.json files have required 'hooks' wrapper field (pass_to_pass)."""
    cmd = """for f in /workspace/claude-code/plugins/*/hooks/hooks.json; do if ! python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert "hooks" in d, "missing hooks field"' "$f" 2>/dev/null; then echo "Invalid hooks.json (no hooks field): $f"; exit 1; fi; done"""
    r = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"hooks.json missing hooks field:\n{r.stderr[-500:]}"


def test_repo_all_shell_scripts_executable():
    """All shell scripts in plugins hooks-handlers are executable (pass_to_pass)."""
    cmd = """for f in /workspace/claude-code/plugins/*/hooks-handlers/*.sh; do if [ -f "$f" ] && [ ! -x "$f" ]; then echo "Not executable: $f"; exit 1; fi; done"""
    r = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Shell script not executable:\n{r.stderr[-500:]}"


def test_repo_all_plugins_have_claude_plugin_dir():
    """All plugins have .claude-plugin directory with plugin.json (pass_to_pass)."""
    cmd = """for d in /workspace/claude-code/plugins/*/; do if [ ! -d "${d}.claude-plugin" ]; then echo "Missing .claude-plugin dir: $d"; exit 1; fi; done"""
    r = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Plugin missing .claude-plugin dir:\n{r.stderr[-500:]}"


def test_repo_all_plugin_json_required_fields():
    """All plugin.json files have required fields: name, version, description, author.name (pass_to_pass)."""
    cmd = """for f in /workspace/claude-code/plugins/*/.claude-plugin/plugin.json; do python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d.get("name"), "missing name"; assert d.get("version"), "missing version"; assert d.get("description"), "missing description"; assert d.get("author",{}).get("name"), "missing author name"' "$f" 2>/dev/null || { echo "Invalid plugin.json (missing required fields): $f"; exit 1; }; done"""
    r = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Plugin manifest missing required fields:\n{r.stderr[-500:]}"


def test_repo_security_hook_runs():
    """Security guidance hook can run without errors when given valid input (pass_to_pass)."""
    # The hook may exit 0 (no warning) or 2 (warning triggered) - both are valid
    r = subprocess.run(
        ["bash", "-c",
         "echo '{\"tool_name\": \"Edit\", \"tool_input\": {\"file_path\": \"test.py\", \"new_string\": \"print(1)\"}, \"session_id\": \"test\"}' | "
         "ENABLE_SECURITY_REMINDER=1 timeout 10 python3 /workspace/claude-code/plugins/security-guidance/hooks/security_reminder_hook.py"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    # Exit code 0 = no warning needed, 2 = warning shown (both valid for hook)
    assert r.returncode in [0, 2], f"Security hook failed with exit {r.returncode}:\n{r.stderr[-500:]}"
