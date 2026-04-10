"""
Task: playwright-daemon-workspace-scope
Repo: playwright @ 08752e9a9be05e5d11173977c8651cf105c1aace
PR:   microsoft/playwright#39144

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import shutil
import tempfile
from pathlib import Path
import re

REPO = "/workspace/playwright"
COMMANDS_TS = f"{REPO}/packages/playwright/src/mcp/terminal/commands.ts"
PROGRAM_TS = f"{REPO}/packages/playwright/src/mcp/terminal/program.ts"
SKILL_MD = f"{REPO}/packages/playwright/src/skill/SKILL.md"
SESSION_MGMT_MD = f"{REPO}/packages/playwright/src/skill/references/session-management.md"


def _extract_command_names() -> list[str]:
    """Use node to parse command names from commands.ts."""
    result = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf-8');
const names = [...content.matchAll(/name:\\s*'([^']+)'/g)].map(m => m[1]);
console.log(JSON.stringify(names));
""", COMMANDS_TS],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Node script failed: {result.stderr}"
    return json.loads(result.stdout.strip())


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_commands_ts_valid_structure():
    """commands.ts exports a commandsArray with valid command declarations."""
    result = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf-8');
const hasArray = content.includes('commandsArray');
const commandCount = (content.match(/declareCommand\\(/g) || []).length;
console.log(JSON.stringify({ hasArray, commandCount }));
""", COMMANDS_TS],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Node script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["hasArray"], "commandsArray not found in commands.ts"
    assert data["commandCount"] >= 20, f"Expected 20+ commands, got {data['commandCount']}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD tests from the repository
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_mcp_cli_parsing():
    """MCP CLI parsing tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", f"cd {REPO} && npm ci 2>/dev/null | tail -3 && npm run build 2>/dev/null | tail -3 && npx playwright install chromium 2>/dev/null | tail -3 && npx playwright test --config=tests/mcp/playwright.config.ts --project=chromium cli-parsing.spec.ts --forbid-only 2>&1 | tail -20"],
        capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"MCP CLI parsing tests failed:\n{r.stdout[-1000:]}"
    assert "passed" in r.stdout or "passed" in r.stderr, "No tests passed in output"


# [repo_tests] pass_to_pass
def test_repo_mcp_cli_help():
    """MCP CLI help tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", f"cd {REPO} && npm ci 2>/dev/null | tail -3 && npm run build 2>/dev/null | tail -3 && npx playwright install chromium 2>/dev/null | tail -3 && npx playwright test --config=tests/mcp/playwright.config.ts --project=chromium cli-help.spec.ts --forbid-only 2>&1 | tail -20"],
        capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"MCP CLI help tests failed:\n{r.stdout[-1000:]}"
    assert "passed" in r.stdout or "passed" in r.stderr, "No tests passed in output"


# [repo_tests] pass_to_pass
def test_repo_build():
    """Repo builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", f"cd {REPO} && npm ci 2>/dev/null | tail -3 && npm run build 2>&1 | tail -30"],
        capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"
    assert "EXIT:0" in r.stdout or "Writing" in r.stdout or "help.json" in r.stdout, f"Build may have failed:\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_check_deps():
    """Repo dependency checks pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", f"cd {REPO} && npm ci 2>/dev/null | tail -3 && npm run check-deps 2>&1"],
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"Check deps failed:\n{r.stderr[-500:]}"
    assert "Checking DEPS" in r.stdout, f"DEPS check did not run properly:\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_eslint_on_modified_files():
    """ESLint passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", f"cd {REPO} && npm ci 2>/dev/null | tail -3 && npm run eslint -- --max-warnings=0 packages/playwright/src/mcp/terminal/commands.ts packages/playwright/src/mcp/terminal/program.ts 2>&1"],
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"ESLint failed on modified files:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_session_kill_all_command_registered():
    """kill-all must be renamed to session-kill-all in the command registry."""
    names = _extract_command_names()
    assert "session-kill-all" in names, \
        f"'session-kill-all' not found in registered commands: {names}"
    assert "kill-all" not in names, \
        f"Old 'kill-all' command still registered: {names}"


# [pr_diff] fail_to_pass
def test_install_replaces_install_skills():
    """install-skills must be replaced by 'install' (workspace init) command."""
    names = _extract_command_names()
    assert "install" in names, \
        f"'install' command not found in registered commands: {names}"
    assert "install-skills" not in names, \
        f"Old 'install-skills' command still registered: {names}"
    assert "install-browser" in names, \
        f"'install-browser' command missing: {names}"


# [pr_diff] fail_to_pass
def test_find_workspace_dir_function():
    """findWorkspaceDir walks up directories looking for .playwright marker."""
    # Create a temporary directory structure with .playwright marker
    tmp = tempfile.mkdtemp(prefix="pw-ws-test-")
    try:
        project = Path(tmp) / "project"
        deep = project / "sub" / "deep"
        deep.mkdir(parents=True)
        (project / ".playwright").mkdir()

        # Read program.ts and extract function info using Python regex
        content = Path(PROGRAM_TS).read_text()

        # Extract findWorkspaceDir function body using Python regex
        fn_match = re.search(
            r'function findWorkspaceDir\([^)]*\):\s*\w+(?:\s*\|\s*\w+)?\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\n\}',
            content
        )
        assert fn_match, "findWorkspaceDir function not found in program.ts"
        fn_body = fn_match.group(1)

        # Parse the function body and find the marker name
        marker_match = re.search(r'["\'](\.playwright)["\']', fn_body)
        marker = marker_match.group(1) if marker_match else ".playwright"

        # Write Node.js script to a file to avoid escaping issues
        script_file = Path(tmp) / "test_script.js"
        script_content = f"""
const fs = require('fs');
const path = require('path');

function findWorkspaceDir(startDir) {{
  let dir = startDir;
  const marker = "{marker}";
  for (let i = 0; i < 10; i++) {{
    if (fs.existsSync(path.join(dir, marker)))
      return dir;
    const parentDir = path.dirname(dir);
    if (parentDir === dir)
      break;
    dir = parentDir;
  }}
  return undefined;
}}

const result1 = findWorkspaceDir("{deep}");
const result2 = findWorkspaceDir("/tmp");

console.log(JSON.stringify({{
    deep_result: result1,
    expected_project: "{project}",
    tmp_result: result2
}}));
"""
        script_file.write_text(script_content)

        # Execute the script file
        result = subprocess.run(
            ["node", str(script_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, \
            f"findWorkspaceDir extraction/execution failed: {result.stderr}"
        data = json.loads(result.stdout.strip())
        assert data["deep_result"] == str(project), \
            f"findWorkspaceDir({deep}) returned {data['deep_result']}, expected {project}"
        # JavaScript JSON.stringify omits undefined values, so tmp_result won't exist in output
        assert "tmp_result" not in data or data.get("tmp_result") is None, \
            f"findWorkspaceDir(/tmp) should return undefined, got {data.get('tmp_result')}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# [pr_diff] fail_to_pass
def test_config_default_path_updated():
    """Default config path must be .playwright/cli.config.json, not playwright-cli.json."""
    result = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf-8');
const hasNewPath = content.includes(".playwright") &&
    content.includes("cli.config.json");
const hasOldDefault = /existsSync\\(['"]playwright-cli\\.json['"]\\)/.test(content);
console.log(JSON.stringify({ hasNewPath, hasOldDefault }));
""", PROGRAM_TS],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Node script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["hasNewPath"], \
        "program.ts must reference .playwright/cli.config.json as default config path"
    assert not data["hasOldDefault"], \
        "program.ts still references old playwright-cli.json as default config"


# [pr_diff] fail_to_pass
def test_workspace_hash_replaces_installation_hash():
    """ClientInfo uses workspaceDirHash instead of installationDirHash."""
    result = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf-8');

// Check type definition for ClientInfo
const typeMatch = content.match(/type ClientInfo = \\{{([^}]+)\\}}/s);
const interfaceMatch = content.match(/interface ClientInfo \\{{([^}]+)\\}}/s);
const definition = typeMatch ? typeMatch[1] : (interfaceMatch ? interfaceMatch[1] : content);

const hasWorkspaceHash = definition.includes('workspaceDirHash');
const hasInstallationHash = definition.includes('installationDirHash');

// Also check function usage
const usesWorkspaceHash = /workspaceDirHash/.test(content);
const usesInstallationHash = /installationDirHash/.test(content);

console.log(JSON.stringify({
    hasWorkspaceHash,
    hasInstallationHash,
    usesWorkspaceHash,
    usesInstallationHash
}));
""", PROGRAM_TS],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Node script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["hasWorkspaceHash"], \
        "ClientInfo type must define workspaceDirHash field"
    assert not data["hasInstallationHash"], \
        "ClientInfo type still has old installationDirHash field"
    assert data["usesWorkspaceHash"], \
        "program.ts must use workspaceDirHash in code"
    assert not data["usesInstallationHash"], \
        "program.ts still references old installationDirHash"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — config/skill file update tests
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/playwright-mcp-dev/SKILL.md:29-30
def test_skill_md_session_kill_all():
    """SKILL.md must reference session-kill-all, not kill-all."""
    content = Path(SKILL_MD).read_text()
    assert "session-kill-all" in content, \
        "SKILL.md must document the session-kill-all command"
    # Remove all occurrences of new name, then check old name not present
    stripped = content.replace("session-kill-all", "")
    assert "kill-all" not in stripped, \
        "SKILL.md still references the old kill-all command name"


# [agent_config] fail_to_pass — .claude/skills/playwright-mcp-dev/SKILL.md:45
def test_skill_md_delete_data_in_config_section():
    """SKILL.md Configuration section must document the delete-data command."""
    content = Path(SKILL_MD).read_text()
    config_start = content.find("### Configuration")
    sessions_start = content.find("### Sessions")
    assert config_start != -1, "SKILL.md must have a Configuration section"
    assert sessions_start != -1, "SKILL.md must have a Sessions section"
    config_section = content[config_start:sessions_start]
    assert "delete-data" in config_section, \
        "SKILL.md Configuration section must document the delete-data command"
    assert "close" in config_section and "stop the default" not in config_section, \
        "SKILL.md close should not use old inline comment style"


# [agent_config] fail_to_pass — .claude/skills/playwright-mcp-dev/SKILL.md:29-30
def test_session_management_md_kill_all_renamed():
    """session-management.md must use session-kill-all everywhere."""
    content = Path(SESSION_MGMT_MD).read_text()
    assert "session-kill-all" in content, \
        "session-management.md must reference session-kill-all"
    stripped = content.replace("session-kill-all", "")
    assert "kill-all" not in stripped, \
        "session-management.md still references old kill-all command"


# [agent_config] fail_to_pass — .claude/skills/playwright-mcp-dev/SKILL.md:29-30
def test_session_management_md_config_path():
    """session-management.md must reference .playwright/ config path, not playwright-cli.json."""
    content = Path(SESSION_MGMT_MD).read_text()
    assert ".playwright/" in content, \
        "session-management.md must reference .playwright/ directory for config"
    assert "playwright-cli.json" not in content, \
        "session-management.md still references old playwright-cli.json config path"
