"""
Task: playwright-chorecli-scope-daemon-by-workspace
Repo: playwright @ 08752e9a9be05e5d11173977c8651cf105c1aace
PR:   microsoft/playwright#39144

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/playwright"

COMMANDS_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/commands.ts"
PROGRAM_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/program.ts"
SKILL_MD = Path(REPO) / "packages/playwright/src/skill/SKILL.md"
SESSION_MGMT_MD = Path(REPO) / "packages/playwright/src/skill/references/session-management.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_node_ready = False


def _ensure_node():
    """Install Node.js once if not already present."""
    global _node_ready
    if _node_ready:
        return
    r = subprocess.run(["node", "--version"], capture_output=True, text=True)
    if r.returncode == 0:
        _node_ready = True
        return
    subprocess.run(
        ["bash", "-c",
         "apt-get update -qq && apt-get install -y -qq nodejs >/dev/null 2>&1"],
        capture_output=True, text=True, timeout=120, check=True,
    )
    _node_ready = True


def _run_node(code: str, cwd: str = REPO, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in a temp file."""
    _ensure_node()
    script = Path(cwd) / "_eval_tmp.js"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=cwd,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Behavioral fail_to_pass tests — execute code via Node.js subprocess
# ---------------------------------------------------------------------------

def test_find_workspace_dir_resolves_marker():
    """findWorkspaceDir walks up and returns the dir containing .playwright marker."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = os.path.join(tmpdir, "project")
        deep = os.path.join(workspace, "a", "b", "c")
        os.makedirs(deep)
        os.makedirs(os.path.join(workspace, ".playwright"))

        program_path = json.dumps(str(PROGRAM_TS))
        deep_path = json.dumps(deep)
        ws_path = json.dumps(workspace)

        r = _run_node(f"""
const fs = require('fs');
const path = require('path');

const src = fs.readFileSync({program_path}, 'utf8');

// Locate the findWorkspaceDir function
const fnIdx = src.indexOf('function findWorkspaceDir');
if (fnIdx === -1) {{
    console.error('FAIL: findWorkspaceDir function not found in program.ts');
    process.exit(1);
}}

// Extract its body via brace-matching
let depth = 0, started = false, end = fnIdx;
for (let i = fnIdx; i < src.length; i++) {{
    if (src[i] === '{{') {{ depth++; started = true; }}
    if (src[i] === '}}') depth--;
    if (started && depth === 0) {{ end = i + 1; break; }}
}}

// Strip TypeScript type annotations to get valid JS
let fnCode = src.slice(fnIdx, end);
fnCode = fnCode.replace(/:\\s*string(\\s*\\|\\s*undefined)?/g, '');

eval(fnCode);

// Test: nested dir should resolve to workspace root containing .playwright
const result = findWorkspaceDir({deep_path});
if (result !== {ws_path}) {{
    console.error('FAIL: expected ' + {ws_path} + ', got ' + result);
    process.exit(1);
}}

// Test: dir without .playwright marker should return undefined
const noResult = findWorkspaceDir('/tmp');
if (noResult !== undefined) {{
    console.error('FAIL: expected undefined for /tmp, got ' + noResult);
    process.exit(1);
}}

console.log('PASS');
""")
    assert r.returncode == 0, \
        f"findWorkspaceDir behavioral test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


def test_command_declarations_via_node():
    """Node.js parses commands.ts: session-kill-all + install exist, old names gone."""
    cmds_path = json.dumps(str(COMMANDS_TS))

    r = _run_node(f"""
const fs = require('fs');
const src = fs.readFileSync({cmds_path}, 'utf8');

const names = [...src.matchAll(/name:\\s*['"]([^'"]+)['"]/g)].map(m => m[1]);
const errors = [];

if (!names.includes('session-kill-all'))
    errors.push('Missing session-kill-all command');
if (names.includes('kill-all'))
    errors.push('Old kill-all command still present');
if (!names.includes('install'))
    errors.push('Missing install command');
if (names.includes('install-skills'))
    errors.push('Old install-skills command still present');

if (errors.length > 0) {{
    errors.forEach(e => console.error('FAIL: ' + e));
    process.exit(1);
}}

// install command description must mention workspace
const m = src.match(/name:\\s*['"]install['"][\\s\\S]*?description:\\s*['"]([^'"]+)['"]/);
if (!m || !/workspace/i.test(m[1])) {{
    console.error('FAIL: install command description should mention workspace');
    process.exit(1);
}}

console.log('PASS');
""")
    assert r.returncode == 0, \
        f"Command declarations test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


def test_daemon_socket_uses_workspace_hash():
    """daemonSocketPath uses workspaceDirHash, not installationDirHash."""
    prog_path = json.dumps(str(PROGRAM_TS))

    r = _run_node(f"""
const fs = require('fs');
const src = fs.readFileSync({prog_path}, 'utf8');

const match = src.match(/function\\s+daemonSocketPath[\\s\\S]*?\\{{[\\s\\S]*?\\}}/);
if (!match) {{
    console.error('FAIL: daemonSocketPath function not found');
    process.exit(1);
}}

const fn = match[0];
if (fn.includes('installationDirHash')) {{
    console.error('FAIL: daemonSocketPath still uses installationDirHash');
    process.exit(1);
}}
if (!fn.includes('workspaceDirHash')) {{
    console.error('FAIL: daemonSocketPath does not use workspaceDirHash');
    process.exit(1);
}}

console.log('PASS');
""")
    assert r.returncode == 0, \
        f"Daemon socket hash test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Structural fail_to_pass tests — verify code changes via string analysis
# ---------------------------------------------------------------------------

def test_workspace_scoping_replaces_installation_dir():
    """program.ts uses workspaceDirHash instead of installationDirHash."""
    src = PROGRAM_TS.read_text()
    assert "workspaceDirHash" in src, \
        "program.ts must use workspaceDirHash for workspace-scoped daemon isolation"
    assert "installationDirHash" not in src, \
        "program.ts must not reference old installationDirHash"


def test_config_path_updated():
    """Default config file path is .playwright/cli.config.json, not playwright-cli.json."""
    src = PROGRAM_TS.read_text()
    assert "cli.config.json" in src, \
        "program.ts must reference cli.config.json as the config file name"
    assert "playwright-cli.json" not in src, \
        "program.ts must not reference old playwright-cli.json config path"


def test_install_creates_playwright_dir():
    """The install function in program.ts creates a .playwright directory."""
    src = PROGRAM_TS.read_text()
    fn_match = re.search(r"(?:async\s+)?function\s+install\s*\(", src)
    assert fn_match, "program.ts must define an install() function"
    fn_region = src[fn_match.start():fn_match.start() + 800]
    assert ".playwright" in fn_region, \
        "install() function must create .playwright workspace marker directory"
    assert "mkdir" in fn_region, \
        "install() must use mkdir to create the .playwright directory"


def test_session_kill_all_in_switch():
    """program.ts switch/case routes 'session-kill-all' command."""
    src = PROGRAM_TS.read_text()
    assert re.search(r"case\s+['\"]session-kill-all['\"]", src), \
        "program.ts must have case 'session-kill-all' in the command switch"
    assert not re.search(r"case\s+['\"]kill-all['\"]", src), \
        "program.ts must not have old case 'kill-all' in the command switch"


# ---------------------------------------------------------------------------
# Documentation fail_to_pass tests (agent_config)
# ---------------------------------------------------------------------------

def test_skill_md_session_kill_all():
    """SKILL.md documents session-kill-all command (not kill-all)."""
    content = SKILL_MD.read_text()
    assert "session-kill-all" in content, \
        "SKILL.md must reference session-kill-all command"
    stripped = content.replace("session-kill-all", "")
    assert "kill-all" not in stripped, \
        "SKILL.md must not reference old 'kill-all' command"


def test_session_mgmt_md_kill_all_renamed():
    """session-management.md uses session-kill-all everywhere."""
    content = SESSION_MGMT_MD.read_text()
    assert "session-kill-all" in content, \
        "session-management.md must reference session-kill-all"
    stripped = content.replace("session-kill-all", "")
    assert "kill-all" not in stripped, \
        "session-management.md must not reference old 'kill-all' command"


def test_session_mgmt_md_config_path():
    """session-management.md no longer references playwright-cli.json."""
    content = SESSION_MGMT_MD.read_text()
    assert "playwright-cli.json" not in content, \
        "session-management.md must not reference old playwright-cli.json config path"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

def test_commands_ts_has_install_browser():
    """install-browser command must still exist for browser installation."""
    src = COMMANDS_TS.read_text()
    names = re.findall(r"name:\s*['\"]([^'\"]+)['\"]", src)
    assert "install-browser" in names, \
        "commands.ts must still have 'install-browser' command"


def test_skill_md_has_session_list():
    """SKILL.md still documents session-list command."""
    content = SKILL_MD.read_text()
    assert "session-list" in content, \
        "SKILL.md must still document session-list command"
