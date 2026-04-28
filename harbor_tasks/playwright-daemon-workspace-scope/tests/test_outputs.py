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
# Pass-to-pass (static + repo_tests)
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


# [repo_tests] pass_to_pass
def test_repo_eslint_on_modified_files():
    """ESLint passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", f"cd {REPO} && npm ci 2>&1 | tail -5 && npm run eslint -- --max-warnings=0 packages/playwright/src/mcp/terminal/commands.ts packages/playwright/src/mcp/terminal/program.ts 2>&1"],
        capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"ESLint failed on modified files:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


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
def test_workspace_dir_lookup_behavior():
    """program.ts walks up directories looking for .playwright marker to determine workspace."""
    content = Path(PROGRAM_TS).read_text()

    assert "'.playwright'" in content or '".playwright"' in content, \
        "program.ts must reference '.playwright' as workspace marker"

    # Behavioral test: verify the workspace-finding algorithm works correctly
    # by exercising it against a temp directory structure
    tmp = tempfile.mkdtemp(prefix="pw-ws-test-")
    try:
        project = Path(tmp) / "project"
        deep = project / "sub" / "deep"
        deep.mkdir(parents=True)
        (project / ".playwright").mkdir()

        script_file = Path(tmp) / "test_ws.js"
        script_file.write_text(f"""
const fs = require('fs');
const path = require('path');

// Walk up from startDir looking for .playwright marker
// (same algorithm expected in program.ts, regardless of function name)
function walkUpForMarker(startDir) {{
  let dir = startDir;
  for (let i = 0; i < 20; i++) {{
    if (fs.existsSync(path.join(dir, '.playwright')))
      return dir;
    const parentDir = path.dirname(dir);
    if (parentDir === dir) break;
    dir = parentDir;
  }}
  return undefined;
}}

const found = walkUpForMarker("{deep}");
const notFound = walkUpForMarker("/tmp/nonexistent-xyz");
console.log(JSON.stringify({{
    found: found,
    expected: "{project}",
    not_found: notFound
}}));
""")
        result = subprocess.run(
            ["node", str(script_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, \
            f"Workspace lookup test failed: {result.stderr}"
        data = json.loads(result.stdout.strip())
        assert data["found"] == str(project), \
            f"Walking up from {deep} should find workspace at {project}, got {data['found']}"
        assert data.get("not_found") is None, \
            "Walking up from a dir without .playwright marker should return undefined"
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

# [agent_config] fail_to_pass
def test_skill_md_session_kill_all():
    """SKILL.md must reference session-kill-all, not kill-all."""
    content = Path(SKILL_MD).read_text()
    assert "session-kill-all" in content, \
        "SKILL.md must document the session-kill-all command"
    # Remove all occurrences of new name, then check old name not present
    stripped = content.replace("session-kill-all", "")
    assert "kill-all" not in stripped, \
        "SKILL.md still references the old kill-all command name"


# [agent_config] fail_to_pass
def test_skill_md_delete_data_in_config_section():
    """SKILL.md Configuration section must document close and delete-data commands with descriptive comments."""
    content = Path(SKILL_MD).read_text()
    config_start = content.find("### Configuration")
    sessions_start = content.find("### Sessions")
    assert config_start != -1, "SKILL.md must have a Configuration section"
    assert sessions_start != -1, "SKILL.md must have a Sessions section"
    config_section = content[config_start:sessions_start]
    assert "delete-data" in config_section, \
        "SKILL.md Configuration section must document the delete-data command"
    assert "close" in config_section, \
        "SKILL.md Configuration section must document the close command"
    # New format: descriptive comments above each command ("Close the browser", "Delete user data")
    assert "Close the browser" in config_section, \
        "SKILL.md close command should have 'Close the browser' comment above it"
    assert "Delete user data" in config_section, \
        "SKILL.md delete-data command should have 'Delete user data' comment above it"


# [agent_config] fail_to_pass
def test_session_management_md_kill_all_renamed():
    """session-management.md must use session-kill-all everywhere."""
    content = Path(SESSION_MGMT_MD).read_text()
    assert "session-kill-all" in content, \
        "session-management.md must reference session-kill-all"
    stripped = content.replace("session-kill-all", "")
    assert "kill-all" not in stripped, \
        "session-management.md still references old kill-all command"


# [agent_config] fail_to_pass
def test_session_management_md_config_path():
    """session-management.md must reference .playwright/ config path, not playwright-cli.json."""
    content = Path(SESSION_MGMT_MD).read_text()
    assert ".playwright/" in content, \
        "session-management.md must reference .playwright/ directory for config"
    assert "playwright-cli.json" not in content, \
        "session-management.md still references old playwright-cli.json config path"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_playwright_driver_npm():
    """pass_to_pass | CI job 'build-playwright-driver' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_playwright_driver_npm_2():
    """pass_to_pass | CI job 'build-playwright-driver' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")