"""
Task: nextjs-dev-restart-distdir-deletion
Repo: vercel/next.js @ cb0d88f6e3e340216d478e0ba0c201ec23f7c15c
PR:   92135

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = Path("/workspace/next.js")
START_SERVER = REPO / "packages/next/src/server/lib/start-server.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Node.js validation script in the repo directory."""
    script = REPO / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", "--no-warnings", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=str(REPO),
        )
    finally:
        script.unlink(missing_ok=True)


def _node_result(code: str) -> dict:
    """Run a Node.js script that outputs JSON and parse the result."""
    r = _run_node(code)
    assert r.returncode == 0, f"Node.js failed: {r.stderr}"
    return json.loads(r.stdout.strip().split('\n')[-1])


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_remove_event_handler():
    """Watchpack 'remove' handler exists and triggers process exit on directory deletion."""
    fp = json.dumps(str(START_SERVER))
    data = _node_result(
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync({fp}, 'utf8');\n"
        r"""
const removePat = /wp\.on\(\s*'remove'/;
const hasRemoveHandler = removePat.test(src);
const hasRestartExit = src.includes('RESTART_EXIT_CODE');
// Verify the remove handler references a path list guard (e.g., dirWatchPaths)
const removeRegion = src.substring(src.indexOf("wp.on('remove'"));
const hasPathGuard = /includes\(/.test(removeRegion.substring(0, 400));
console.log(JSON.stringify({ok: hasRemoveHandler && hasRestartExit && hasPathGuard}));
"""
    )
    assert data['ok'], (
        "start-server.ts missing Watchpack 'remove' handler with "
        "RESTART_EXIT_CODE and path inclusion guard"
    )


# [pr_diff] fail_to_pass
def test_missing_option_in_watchpack():
    """Watchpack watch call includes 'missing' option for directory deletion detection."""
    fp = json.dumps(str(START_SERVER))
    data = _node_result(
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync({fp}, 'utf8');\n"
        r"""
// Find wp.watch({...}) calls and check for 'missing' option
const watchPat = /wp\.watch\(\s*\{([^}]+)\}/g;
let match;
let hasMissing = false;
while ((match = watchPat.exec(src)) !== null) {
    if (match[1].includes('missing')) hasMissing = true;
}
console.log(JSON.stringify({ok: hasMissing}));
"""
    )
    assert data['ok'], (
        "Watchpack wp.watch() missing 'missing' option — "
        "needed to detect directory deletion"
    )


# [pr_diff] fail_to_pass
def test_distdir_ancestor_walking():
    """Absolute distDir is computed and ancestor directories are collected for watching."""
    fp = json.dumps(str(START_SERVER))
    data = _node_result(
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync({fp}, 'utf8');\n"
        r"""
// Check that an absolute distDir is computed from dir + distDir
const hasAbsPath = /path\.join\(dir,\s*distDir\)/.test(src);
// Check that there's a while/for loop walking parent directories via path.dirname
const hasAncestorWalk = /path\.dirname\(/.test(src) && /while|for/.test(src);
// Check that ancestor paths are pushed into a collection
const hasPush = /\.push\(/.test(src);
console.log(JSON.stringify({
    ok: hasAbsPath && hasAncestorWalk && hasPush
}));
"""
    )
    assert data['ok'], (
        "start-server.ts missing distDir ancestor walking logic: "
        "absolute distDir computation, ancestor loop with path.dirname, "
        "or path collection"
    )


# [pr_diff] fail_to_pass
def test_change_handler_guards_config_files():
    """Change handler only responds to config file changes, not directory changes."""
    fp = json.dumps(str(START_SERVER))
    data = _node_result(
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync({fp}, 'utf8');\n"
        r"""
// Find the change handler and check it guards with a file list check
const changeIdx = src.indexOf("wp.on('change'");
if (changeIdx === -1) {
    console.log(JSON.stringify({ok: false, error: 'no change handler'}));
    process.exit(0);
}
const region = src.substring(changeIdx, changeIdx + 500);
// Must have a guard checking if filename is in the config file list
const hasGuard = /\.includes\(filename\)/.test(region) || /\.indexOf\(filename\)/.test(region);
console.log(JSON.stringify({ok: hasGuard}));
"""
    )
    assert data['ok'], (
        "Change handler missing config file guard — should only respond "
        "to config file changes, not directory change events"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — syntax / anti-stub checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_syntax_valid():
    """start-server.ts has balanced braces and no obvious syntax issues."""
    src = START_SERVER.read_text()
    open_braces = src.count('{')
    close_braces = src.count('}')
    assert open_braces == close_braces, (
        f"Unbalanced braces in start-server.ts: {open_braces} open vs {close_braces} close"
    )
    assert len(src) > 10000, "start-server.ts is suspiciously short — check file integrity"


# [static] pass_to_pass
def test_restart_exit_code_in_remove():
    """Remove handler uses RESTART_EXIT_CODE (not a hardcoded magic number)."""
    src = START_SERVER.read_text()
    remove_idx = src.find("wp.on('remove'")
    if remove_idx == -1:
        return  # No remove handler on base commit; nothing to validate
    region = src[remove_idx:remove_idx + 400]
    assert 'RESTART_EXIT_CODE' in region, (
        "Remove handler should call process.exit(RESTART_EXIT_CODE)"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:300
def test_dev_only_code_guard():
    """File watching with directory deletion detection is inside the if (isDev) guard."""
    src = START_SERVER.read_text()
    remove_idx = src.find("wp.on('remove'")
    if remove_idx == -1:
        return  # No remove handler on base commit; nothing to validate
    isdev_idx = src.find('if (isDev)')
    assert isdev_idx != -1, "if (isDev) block not found"
    assert remove_idx > isdev_idx, (
        "wp.on('remove') must be inside the if (isDev) block — "
        "directory deletion watching is dev-server-only behavior"
    )
