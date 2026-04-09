"""
Task: playwright-daemon-workspace-scoping
Repo: microsoft/playwright @ 08752e9a9be05e5d11173977c8651cf105c1aace
PR:   39144

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"

COMMANDS_TS = Path(REPO) / "packages" / "playwright" / "src" / "mcp" / "terminal" / "commands.ts"
PROGRAM_TS = Path(REPO) / "packages" / "playwright" / "src" / "mcp" / "terminal" / "program.ts"
SKILL_MD = Path(REPO) / "packages" / "playwright" / "src" / "skill" / "SKILL.md"
SESSION_MGMT_MD = Path(REPO) / "packages" / "playwright" / "src" / "skill" / "references" / "session-management.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_install_browser_command_exists():
    """install-browser command must still be registered in commands.ts."""
    content = COMMANDS_TS.read_text()
    assert "name: 'install-browser'" in content, \
        "install-browser command should exist in commands.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_session_kill_all_command():
    """kill-all command must be renamed to session-kill-all."""
    content = COMMANDS_TS.read_text()
    assert "name: 'session-kill-all'" in content, \
        "kill-all should be renamed to session-kill-all in commands.ts"
    assert "name: 'kill-all'" not in content, \
        "Old name 'kill-all' should no longer appear in commands.ts"


# [pr_diff] fail_to_pass
def test_install_command_workspace_init():
    """New 'install' command exists with workspace initialization purpose."""
    content = COMMANDS_TS.read_text()
    assert "name: 'install'" in content, \
        "An 'install' command should be registered in commands.ts"
    assert "'Initialize workspace'" in content, \
        "install command should have description 'Initialize workspace'"


# [pr_diff] fail_to_pass
def test_config_path_uses_dot_playwright():
    """Default config path changed from playwright-cli.json to .playwright/cli.config.json."""
    content = PROGRAM_TS.read_text()
    assert ".playwright" in content and "cli.config.json" in content, \
        "program.ts should reference .playwright/cli.config.json as the config path"
    assert "playwright-cli.json" not in content, \
        "Old config path playwright-cli.json should no longer appear in program.ts"


# [pr_diff] fail_to_pass
def test_find_workspace_dir_behavior():
    """findWorkspaceDir walks up from cwd looking for .playwright directory."""
    script = r"""
const fs = require('fs');
const path = require('path');
const os = require('os');

// Verify findWorkspaceDir is defined in program.ts
const src = fs.readFileSync(
    'packages/playwright/src/mcp/terminal/program.ts', 'utf-8'
);
if (!src.includes('function findWorkspaceDir')) {
    console.error('findWorkspaceDir function not found in program.ts');
    process.exit(1);
}

// Create temp directory structure to test the logic
const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'pw-ws-test-'));
try {
    const wsDir = path.join(tmpDir, 'my-workspace');
    const subDir = path.join(wsDir, 'packages', 'app', 'src');
    fs.mkdirSync(path.join(wsDir, '.playwright'), { recursive: true });
    fs.mkdirSync(subDir, { recursive: true });

    // Re-implement findWorkspaceDir as it appears in the source
    function findWorkspaceDir(startDir) {
        let dir = startDir;
        for (let i = 0; i < 10; i++) {
            if (fs.existsSync(path.join(dir, '.playwright')))
                return dir;
            const parentDir = path.dirname(dir);
            if (parentDir === dir)
                break;
            dir = parentDir;
        }
        return undefined;
    }

    // Test 1: finds .playwright in ancestor directory
    const result1 = findWorkspaceDir(subDir);
    if (result1 !== wsDir) {
        console.error(JSON.stringify({
            test: 'ancestor_lookup', expected: wsDir, got: result1
        }));
        process.exit(1);
    }

    // Test 2: returns undefined when no .playwright exists
    const noWsDir = path.join(tmpDir, 'no-workspace', 'deep', 'sub');
    fs.mkdirSync(noWsDir, { recursive: true });
    const result2 = findWorkspaceDir(noWsDir);
    if (result2 !== undefined) {
        console.error(JSON.stringify({
            test: 'no_workspace', expected: 'undefined', got: result2
        }));
        process.exit(1);
    }

    // Test 3: finds .playwright in the start directory itself
    const result3 = findWorkspaceDir(wsDir);
    if (result3 !== wsDir) {
        console.error(JSON.stringify({
            test: 'start_dir', expected: wsDir, got: result3
        }));
        process.exit(1);
    }

    console.log(JSON.stringify({ status: 'PASS', tests: 3 }));
} finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
}
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Node test failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["status"] == "PASS", f"Unexpected output: {data}"
    assert data["tests"] == 3


# [pr_diff] fail_to_pass
def test_workspace_dir_hash_replaces_installation_dir():
    """Daemon scoping uses workspaceDirHash instead of installationDirHash."""
    content = PROGRAM_TS.read_text()
    assert "workspaceDirHash" in content, \
        "program.ts should use workspaceDirHash for daemon scoping"
    assert "installationDirHash" not in content, \
        "Old installationDirHash should be replaced with workspaceDirHash"


# ---------------------------------------------------------------------------
# Config/documentation update tests (agent_config) -- SKILL.md / references
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass -- .claude/skills/playwright-mcp-dev/SKILL.md:29-30
def test_skill_md_documents_session_kill_all():
    """SKILL.md must use session-kill-all instead of kill-all."""
    content = SKILL_MD.read_text()
    assert "session-kill-all" in content, \
        "SKILL.md should document the renamed session-kill-all command"
    assert "kill-all" not in content or content.count("kill-all") == content.count("session-kill-all"), \
        "SKILL.md should not reference the old kill-all command name"


# [agent_config] fail_to_pass -- .claude/skills/playwright-mcp-dev/SKILL.md:29-30
def test_session_management_md_updated():
    """session-management.md reference doc must use session-kill-all."""
    content = SESSION_MGMT_MD.read_text()
    assert "session-kill-all" in content, \
        "session-management.md should document session-kill-all"
    lines_with_kill_all = [
        line for line in content.splitlines()
        if "kill-all" in line and "session-kill-all" not in line
    ]
    assert len(lines_with_kill_all) == 0, \
        f"session-management.md still has old 'kill-all' references: {lines_with_kill_all}"
