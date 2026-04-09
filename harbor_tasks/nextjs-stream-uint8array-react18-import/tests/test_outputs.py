"""
Task: nextjs-stream-uint8array-react18-import
Repo: vercel/next.js @ 9cb2048439b8b95b6e6460d17d94d9cb1823fbef
PR:   92263

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/next.js"
STREAM_OPS = Path(REPO) / "packages/next/src/server/app-render/stream-ops.ts"
STREAM_OPS_NODE = Path(REPO) / "packages/next/src/server/app-render/stream-ops.node.ts"
STREAM_OPS_WEB = Path(REPO) / "packages/next/src/server/app-render/stream-ops.web.ts"
SERIALIZED_ERRORS = Path(REPO) / "packages/next/src/server/dev/serialized-errors.ts"
HELPER = Path(REPO) / "packages/next/src/server/stream-utils/node-web-streams-helper.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_stream_ops_no_uint8array_export():
    """stream-ops.ts must NOT re-export streamToUint8Array (it pulls in react-dom)."""
    # Use node to parse the file and check for the export
    code = """
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const lines = content.split('\\n');
const exports = lines.filter(l =>
    l.match(/export\\b/) && l.includes('streamToUint8Array') && !l.trim().startsWith('//')
);
if (exports.length > 0) {
    console.error('FOUND forbidden export:', exports[0].trim());
    process.exit(1);
}
console.log('OK');
"""
    r = subprocess.run(
        ["node", "-e", code, str(STREAM_OPS)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, (
        f"stream-ops.ts still exports streamToUint8Array: {r.stderr.strip()}"
    )


# [pr_diff] fail_to_pass
def test_serialized_errors_imports_from_helper():
    """serialized-errors.ts must import streamToUint8Array from node-web-streams-helper, not stream-ops."""
    code = """
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const lines = content.split('\\n');

// Find the import line for streamToUint8Array
const importLine = lines.find(l =>
    l.includes('streamToUint8Array') &&
    l.match(/import\\b/) &&
    !l.trim().startsWith('//')
);

if (!importLine) {
    console.error('ERROR: no import of streamToUint8Array found');
    process.exit(1);
}

// It must NOT import from stream-ops
if (importLine.includes('stream-ops')) {
    console.error('ERROR: imports from stream-ops:', importLine.trim());
    process.exit(1);
}

// It must import from node-web-streams-helper
if (!importLine.includes('node-web-streams-helper')) {
    console.error('ERROR: imports from unexpected location:', importLine.trim());
    process.exit(1);
}

console.log('OK');
"""
    r = subprocess.run(
        ["node", "-e", code, str(SERIALIZED_ERRORS)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, (
        f"serialized-errors.ts has wrong import path: {r.stderr.strip()}"
    )


# [pr_diff] fail_to_pass
def test_helper_has_anystream_signature():
    """node-web-streams-helper.ts must export streamToUint8Array accepting AnyStream (not just ReadableStream)."""
    content = HELPER.read_text()

    # Find the exported streamToUint8Array function signature
    # After the fix, signature is: export async function streamToUint8Array(stream: AnyStream)
    # Before the fix, it was: export async function streamToUint8Array(stream: ReadableStream<Uint8Array>)
    pattern = r"export\s+async\s+function\s+streamToUint8Array\s*\([^)]*AnyStream[^)]*\)"
    assert re.search(pattern, content), (
        "streamToUint8Array in node-web-streams-helper.ts must accept AnyStream, "
        "not just ReadableStream<Uint8Array>"
    )


# [pr_diff] fail_to_pass
def test_stream_ops_node_no_uint8array_function():
    """stream-ops.node.ts must NOT define streamToUint8Array (moved to helper)."""
    content = STREAM_OPS_NODE.read_text()
    # Check for function definition (not just any mention like a comment)
    fn_pattern = r"export\s+async\s+function\s+streamToUint8Array"
    assert not re.search(fn_pattern, content), (
        "stream-ops.node.ts still defines streamToUint8Array — it should be in node-web-streams-helper.ts"
    )


# [pr_diff] fail_to_pass
def test_stream_ops_web_no_uint8array_function():
    """stream-ops.web.ts must NOT define or import streamToUint8Array."""
    content = STREAM_OPS_WEB.read_text()
    # Check for function definition
    fn_def = re.search(r"export\s+async\s+function\s+streamToUint8Array", content)
    # Check for named import of streamToUint8Array from helper
    named_import = re.search(
        r"streamToUint8Array\s+as\s+\w+|import\s*\{[^}]*streamToUint8Array[^}]*\}.*from.*node-web-streams-helper",
        content,
    )
    assert not fn_def, "stream-ops.web.ts still defines streamToUint8Array"
    assert not named_import, "stream-ops.web.ts still imports streamToUint8Array from helper"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_helper_still_exports_stream_to_buffer():
    """node-web-streams-helper.ts must still export streamToBuffer (regression check)."""
    content = HELPER.read_text()
    assert re.search(r"export\s+async\s+function\s+streamToBuffer", content), (
        "streamToBuffer export was accidentally removed from node-web-streams-helper.ts"
    )


# [static] pass_to_pass
def test_not_stub():
    """streamToUint8Array in node-web-streams-helper.ts must have real logic (not a stub)."""
    content = HELPER.read_text()
    # Extract the body of streamToUint8Array — find its function and count meaningful lines
    match = re.search(
        r"export\s+async\s+function\s+streamToUint8Array\s*\([^)]*\)[^{]*\{(.*?)^\}",
        content,
        re.DOTALL | re.MULTILINE,
    )
    assert match, "streamToUint8Array function not found in node-web-streams-helper.ts"
    body = match.group(1)
    meaningful = [l for l in body.split("\n") if l.strip() and not l.strip().startswith("//")]
    assert len(meaningful) >= 3, (
        f"streamToUint8Array body has only {len(meaningful)} lines — likely a stub"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md / dce-edge SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:396 @ 9cb2048439b8
def test_dce_safe_require_in_helper():
    """node-web-streams-helper.ts must use DCE-safe if/else branching for require('node:stream')."""
    # AGENTS.md line 396: "Keep require() behind compile-time if/else branches for DCE"
    # The streamToUint8Array function (or its helpers) must use if/else branching
    # with process.env.TURBOPACK / process.env.__NEXT_BUNDLER for require('node:stream')
    code = """
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');

// Find the region after streamToUint8Array is defined in the unified function
// The DCE pattern requires if/else branching on process.env.TURBOPACK or similar
const hasTurbopackBranch = content.includes("process.env.TURBOPACK") &&
    content.includes("require('node:stream')");
const hasBundlerBranch = content.includes("process.env.__NEXT_BUNDLER");

if (!hasTurbopackBranch || !hasBundlerBranch) {
    console.error('ERROR: Missing DCE-safe if/else require branching');
    console.error('  TURBOPACK branch:', hasTurbopackBranch);
    console.error('  __NEXT_BUNDLER branch:', hasBundlerBranch);
    process.exit(1);
}

console.log('OK');
"""
    r = subprocess.run(
        ["node", "-e", code, str(HELPER)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, (
        f"node-web-streams-helper.ts missing DCE-safe require pattern: {r.stderr.strip()}"
    )
