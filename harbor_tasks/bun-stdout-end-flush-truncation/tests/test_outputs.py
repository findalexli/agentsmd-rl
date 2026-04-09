"""
Task: bun-stdout-end-flush-truncation
Repo: oven-sh/bun @ ba05a72939569c1a371a513c3bd64a2cab6a60ee

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
TARGET = f"{REPO}/src/js/builtins/ProcessObjectInternals.ts"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Node.js helper module: extracts _final from the TS source file, polyfills
# bun-specific globals ($isPromise etc.), and exposes the function for testing.
# Cannot run ProcessObjectInternals.ts directly because it requires bun's
# TypeScript preprocessor ($ intrinsics, internal require paths).
_HELPER_JS = r"""
const fs = require('fs');
const source = fs.readFileSync(process.env.BUN_TARGET, 'utf8');

// Find the _final assignment
const match = source.match(/_final\s*=\s*(?:async\s+)?function\s*\((\w+)\)\s*\{/);
if (!match) {
    module.exports = { found: false };
} else {
    const cbArg = match[1];
    const matchPos = source.indexOf(match[0]);
    const braceStart = matchPos + match[0].length - 1;
    let depth = 1, pos = braceStart + 1;
    while (depth > 0 && pos < source.length) {
        if (source[pos] === '{') depth++;
        else if (source[pos] === '}') depth--;
        pos++;
    }
    const body = source.substring(braceStart + 1, pos - 1);

    // Polyfill bun JSC intrinsics
    globalThis.$isPromise = (x) => x != null && typeof x === 'object' && typeof x.then === 'function';
    globalThis.$isCallable = (x) => typeof x === 'function';
    globalThis.$isObject = (x) => x != null && typeof x === 'object';

    // Find closure variables referenced as this[VAR] in the body
    const thisVarMatch = body.match(/this\[(\w+)\]/);
    const closureVar = thisVarMatch ? thisVarMatch[1] : null;
    const sinkKey = Symbol('sinkKey');

    let _final;
    try {
        if (closureVar) {
            // Wrap so the closure variable resolves to our sinkKey symbol
            _final = eval('(function(' + closureVar + ') { return function(' + cbArg + ') {' + body + '}; })')(sinkKey);
        } else {
            _final = eval('(function(' + cbArg + ') {' + body + '})');
        }
    } catch(e) {
        _final = null;
    }

    function makeContext(sinkObj) {
        if (closureVar) return { [sinkKey]: sinkObj };
        return {};
    }

    module.exports = { found: true, _final, makeContext, sinkKey, body, cbArg };
}
"""

_helper_written = False


def _ensure_helper():
    global _helper_written
    if not _helper_written:
        Path("/tmp/bun_final_helper.js").write_text(_HELPER_JS)
        _helper_written = True


def _run_node_test(script: str, timeout: int = 15) -> str:
    """Write a Node.js test script and run it. Returns first stdout line."""
    _ensure_helper()
    Path("/tmp/bun_test_run.js").write_text(script)
    r = subprocess.run(
        ["node", "/tmp/bun_test_run.js"],
        capture_output=True, text=True, timeout=timeout,
        env={"PATH": "/usr/local/bin:/usr/bin:/bin", "BUN_TARGET": TARGET},
    )
    lines = r.stdout.strip().split("\n")
    first = lines[0] if lines and lines[0] else ""
    if not first:
        return f"NO_OUTPUT: {r.stderr[:300]}"
    return first


def _get_final_body():
    """Extract _final function body from ProcessObjectInternals.ts using Python regex."""
    source = Path(TARGET).read_text()
    match = re.search(r'_final\s*=\s*(?:async\s+)?function\s*\(\w+\)\s*\{', source)
    if not match:
        return None
    start = match.end() - 1  # position of opening {
    depth = 1
    pos = start + 1
    while depth > 0 and pos < len(source):
        if source[pos] == '{':
            depth += 1
        elif source[pos] == '}':
            depth -= 1
        pos += 1
    return source[start + 1:pos - 1]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_final_sync_flush():
    """_final calls sink.flush() synchronously and invokes cb(null)."""
    result = _run_node_test(r"""
const h = require('/tmp/bun_final_helper.js');
if (!h.found || !h._final) { console.log('NO_FINAL'); process.exit(0); }
let flushed = false;
const sink = { flush() { flushed = true; return undefined; } };
const ctx = h.makeContext(sink);
let cbResult = 'NOT_CALLED';
try {
    h._final.call(ctx, (err) => {
        cbResult = (err === null || err === undefined) ? 'OK' : 'ERR:' + err;
    });
} catch(e) { cbResult = 'THROW:' + e.message; }
setTimeout(() => {
    console.log(flushed && cbResult === 'OK' ? 'PASS' : 'FAIL:flush=' + flushed + ',cb=' + cbResult);
}, 200);
""")
    assert result == "PASS", f"Sync flush: {result}"


# [pr_diff] fail_to_pass
def test_final_async_flush():
    """_final waits for async flush Promise before calling cb(null)."""
    result = _run_node_test(r"""
const h = require('/tmp/bun_final_helper.js');
if (!h.found || !h._final) { console.log('NO_FINAL'); process.exit(0); }
let resolveFlush;
const flushPromise = new Promise(r => { resolveFlush = r; });
let cbCalled = false, cbBeforeResolve = false;
const ctx = h.makeContext({ flush() { return flushPromise; } });
try {
    h._final.call(ctx, (err) => { cbCalled = true; });
} catch(e) { console.log('FAIL:THROW:' + e.message); process.exit(0); }

setTimeout(() => {
    if (cbCalled) cbBeforeResolve = true;
    resolveFlush();
    setTimeout(() => {
        console.log(!cbBeforeResolve && cbCalled ? 'PASS' : 'FAIL:before=' + cbBeforeResolve + ',called=' + cbCalled);
    }, 200);
}, 50);
""")
    assert result == "PASS", f"Async flush: {result}"


# [pr_diff] fail_to_pass
def test_final_error_propagation():
    """_final propagates flush() errors to cb(err) without crashing."""
    result = _run_node_test(r"""
const h = require('/tmp/bun_final_helper.js');
if (!h.found || !h._final) { console.log('NO_FINAL'); process.exit(0); }
let cbErr = 'NOT_CALLED', uncaught = false;
process.on('uncaughtException', () => { uncaught = true; });
const ctx = h.makeContext({ flush() { throw new Error('pipe_broken'); } });
try {
    h._final.call(ctx, (err) => { cbErr = err ? err.message : 'null'; });
} catch(e) { cbErr = 'THROW:' + e.message; }
setTimeout(() => {
    console.log(cbErr === 'pipe_broken' && !uncaught ? 'PASS' : 'FAIL:cb=' + cbErr + ',uncaught=' + uncaught);
}, 200);
""")
    assert result == "PASS", f"Error propagation: {result}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_existing_stream_setup():
    """Existing _destroy, _isStdio, and destroySoon must be preserved."""
    source = Path(TARGET).read_text()
    assert "_destroy" in source, "_destroy missing from ProcessObjectInternals.ts"
    assert "_isStdio" in source, "_isStdio missing from ProcessObjectInternals.ts"
    assert "destroySoon" in source, "destroySoon missing from ProcessObjectInternals.ts"

# ---------------------------------------------------------------------------
# Pass-to-pass (repo_ci) — actual CI/CD checks from the repo
# ---------------------------------------------------------------------------

# [repo_ci] pass_to_pass — oxlint on target file (from package.json "lint")
def test_repo_oxlint():
    """Repo's oxlint passes on ProcessObjectInternals.ts (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "oxlint", TARGET],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Allow warnings (0 warnings is ideal, but codebase has existing warnings)
    # Only fail if there are errors (errors would indicate new issues introduced)
    assert "0 errors" in r.stdout or r.returncode == 0, \
        f"oxlint found errors:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass — prettier format check (from package.json "fmt")
def test_repo_prettier():
    """Repo's prettier format check passes on ProcessObjectInternals.ts (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", TARGET],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, \
        f"prettier format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_ci) — structural CI checks
# ---------------------------------------------------------------------------

# [repo_ci] pass_to_pass — structural check for kWriteStreamFastPath import
def test_kwritestreamfastpath_import():
    """kWriteStreamFastPath import must exist (required for _final implementation)."""
    source = Path(TARGET).read_text()
    assert "kWriteStreamFastPath" in source, \
        "kWriteStreamFastPath not found in ProcessObjectInternals.ts (required for stream fast path)"


# [repo_ci] pass_to_pass — require("internal/fs/streams") usage
def test_internal_fs_streams_require():
    """ProcessObjectInternals must require internal/fs/streams module."""
    source = Path(TARGET).read_text()
    assert 'require("internal/fs/streams")' in source or "require('internal/fs/streams')" in source, \
        "internal/fs/streams require not found in ProcessObjectInternals.ts"


# [repo_ci] pass_to_pass — getStdioWriteStream function exists
def test_getstdiowritestream_function():
    """getStdioWriteStream function must exist in ProcessObjectInternals."""
    source = Path(TARGET).read_text()
    assert "export function getStdioWriteStream(" in source, \
        "getStdioWriteStream export not found in ProcessObjectInternals.ts"


# [repo_ci] pass_to_pass — stream setup with fd and _type properties
def test_stream_properties():
    """Stream setup must include required properties (fd, _type, _isStdio)."""
    source = Path(TARGET).read_text()
    # These are existing properties that should be set on the stream
    assert "stream._isStdio = true" in source, "stream._isStdio assignment missing"
    assert "stream.fd = fd" in source, "stream.fd assignment missing"
    assert "stream._type" in source, "stream._type assignment missing"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from src/js/CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — src/js/CLAUDE.md:56 @ ba05a72939569c1a371a513c3bd64a2cab6a60ee
def test_no_dot_call_apply():
    """_final must use .$call/.$apply, never .call/.apply (src/js/CLAUDE.md:56)."""
    # Structural check because: bun TS preprocessor converts $-prefixed calls at build time
    body = _get_final_body()
    assert body is not None, "_final hook not found in ProcessObjectInternals.ts"
    # Strip comments before checking
    lines = [l for l in body.split("\n") if not l.strip().startswith("//")]
    code = "\n".join(lines)
    assert not re.search(r'(?<!\$)\.call\s*\(', code), \
        "Uses .call() instead of .$call() — violates src/js/CLAUDE.md:56"
    assert not re.search(r'(?<!\$)\.apply\s*\(', code), \
        "Uses .apply() instead of .$apply() — violates src/js/CLAUDE.md:56"


# [agent_config] pass_to_pass — src/js/CLAUDE.md:103 @ ba05a72939569c1a371a513c3bd64a2cab6a60ee
def test_string_literal_require():
    """All require() calls must use string literals (src/js/CLAUDE.md:103)."""
    source = Path(TARGET).read_text()
    requires = re.findall(r'require\s*\(([^)]+)\)', source)
    assert len(requires) > 0, "No require() calls found in source"
    for arg in requires:
        stripped = arg.strip()
        assert stripped.startswith('"') or stripped.startswith("'"), \
            f"Non-literal require({arg}) — violates src/js/CLAUDE.md:103"


# [agent_config] fail_to_pass — src/js/CLAUDE.md:105 @ ba05a72939569c1a371a513c3bd64a2cab6a60ee
def test_jsc_intrinsics_used():
    """_final must use $isPromise, not instanceof Promise (src/js/CLAUDE.md:105)."""
    # Structural check because: $isPromise is a JSC intrinsic only available in bun runtime
    body = _get_final_body()
    assert body is not None, "_final hook not found in ProcessObjectInternals.ts"
    lines = [l for l in body.split("\n") if not l.strip().startswith("//")]
    code = "\n".join(lines)
    assert "instanceof Promise" not in code, \
        "Uses 'instanceof Promise' instead of $isPromise — violates src/js/CLAUDE.md:105"
    assert "$isPromise" in code, \
        "Must use $isPromise intrinsic for Promise detection — violates src/js/CLAUDE.md:105"
