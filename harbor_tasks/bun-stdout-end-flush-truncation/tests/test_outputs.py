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

# Node.js script that extracts the _final function body and closure variables
# from ProcessObjectInternals.ts so we can eval and test it in isolation.
_EXTRACT_JS = r"""
const fs = require('fs');
const source = fs.readFileSync(process.argv[2], 'utf8');
let idx = source.indexOf('._final');
if (idx < 0) idx = source.indexOf('["_final"]');
if (idx < 0) { console.log(JSON.stringify({found:false})); process.exit(0); }
const m = source.substring(idx).match(/_final['"]*\]?\s*=\s*(?:async\s+)?function\s*\((\w+)\)/);
if (!m) { console.log(JSON.stringify({found:false})); process.exit(0); }
const cbName = m[1];
const braceStart = source.indexOf('{', idx + m.index);
if (braceStart < 0) { console.log(JSON.stringify({found:false})); process.exit(0); }
let d=1, p=braceStart+1;
while(d>0 && p<source.length){ if(source[p]==='{')d++; else if(source[p]==='}')d--; p++; }
const body = source.substring(braceStart+1, p-1);
const isAsync = /async\s+function/.test(source.substring(idx, braceStart));
const fsi = source.lastIndexOf('getStdioWriteStream', idx);
const pre = fsi>=0 ? source.substring(fsi, idx) : '';
const decls = [];
const dr = /(?:const|let|var)\s+(\w+)\s*=\s*([^;]+);/g;
let dm; while((dm=dr.exec(pre))!==null) decls.push({name:dm[1],init:dm[2].trim()});
console.log(JSON.stringify({found:true, cbName, body, isAsync, constDecls:decls}));
"""

# Common JS test harness: builds the _final function and a sink proxy
_COMMON_JS = r"""
const data = JSON.parse(require('fs').readFileSync('/tmp/bun_final_data.json','utf8'));
const { cbName, body, constDecls } = data;

globalThis.$isPromise = (x) => x!=null && typeof x==='object' && typeof x.then==='function';
globalThis.$isCallable = (x) => typeof x==='function';
globalThis.$isObject = (x) => x!=null && typeof x==='object';

let closureSetup = '';
for (const d of constDecls) {
    closureSetup += d.init.includes('require(')
        ? `var ${d.name} = Symbol('${d.name}');\n`
        : `var ${d.name} = undefined;\n`;
}

function buildFinal() {
    return eval('(' + (data.isAsync ? 'async ' : '') + 'function(' + cbName + ') {' + closureSetup + body + '})');
}

function makeProxy(sink) {
    return new Proxy({}, {
        get(t, p) {
            if (p==='constructor') return Object;
            if (p===Symbol.toPrimitive||p===Symbol.toStringTag) return undefined;
            return sink;
        }
    });
}

module.exports = { buildFinal, makeProxy, data };
"""

_extract_cache = None


def _extract_final():
    """Extract _final function metadata from ProcessObjectInternals.ts."""
    global _extract_cache
    if _extract_cache is not None:
        return _extract_cache
    r = subprocess.run(
        ["node", "-e", _EXTRACT_JS, TARGET],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Extraction script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    Path("/tmp/bun_final_data.json").write_text(json.dumps(data))
    Path("/tmp/bun_test_common.js").write_text(_COMMON_JS)
    _extract_cache = data
    return data


def _run_node_test(name: str, script: str) -> str:
    """Write and run a Node.js test script, return first stdout line."""
    _extract_final()  # ensure extraction data + common module exist
    path = Path(f"/tmp/bun_test_{name}.js")
    path.write_text(script)
    r = subprocess.run(
        ["node", str(path)], capture_output=True, text=True, timeout=15,
    )
    lines = r.stdout.strip().split("\n")
    return lines[0] if lines and lines[0] else f"NO_OUTPUT: {r.stderr[:300]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_final_sync_flush():
    """_final calls sink.flush() synchronously and invokes cb(null)."""
    info = _extract_final()
    assert info["found"], "_final hook not found in ProcessObjectInternals.ts"

    result = _run_node_test("sync_flush", r"""
const { buildFinal, makeProxy } = require('/tmp/bun_test_common.js');
let flushCalled = false;
const sink = {
    flush() { flushCalled = true; return undefined; },
    write() { return true; }, close(){}, ref(){}, unref(){}
};
const fn = buildFinal();
let cbResult = 'NOT_CALLED';
try {
    fn.call(makeProxy(sink), (err) => {
        cbResult = (err === null || err === undefined) ? 'SUCCESS' : 'ERROR';
    });
} catch(e) { cbResult = 'EXEC_ERROR: ' + e.message; }
setTimeout(() => {
    console.log(flushCalled && cbResult === 'SUCCESS'
        ? 'PASS' : 'FAIL: flush=' + flushCalled + ' cb=' + cbResult);
}, 200);
""")
    assert result == "PASS", f"Sync flush: {result}"


# [pr_diff] fail_to_pass
def test_final_async_flush():
    """_final waits for async flush Promise before calling cb(null)."""
    info = _extract_final()
    assert info["found"], "_final hook not found in ProcessObjectInternals.ts"

    result = _run_node_test("async_flush", r"""
const { buildFinal, makeProxy } = require('/tmp/bun_test_common.js');
let resolveFlush;
const flushPromise = new Promise(r => { resolveFlush = r; });
const sink = {
    flush() { return flushPromise; },
    write() { return true; }, close(){}, ref(){}, unref(){}
};
const fn = buildFinal();
let cbResult = 'NOT_CALLED';
let cbBeforeResolve = false;
try {
    fn.call(makeProxy(sink), (err) => {
        cbResult = (err === null || err === undefined) ? 'SUCCESS' : 'ERROR';
    });
} catch(e) { cbResult = 'EXEC_ERROR: ' + e.message; }

setTimeout(() => {
    if (cbResult !== 'NOT_CALLED') cbBeforeResolve = true;
    resolveFlush();
    setTimeout(() => {
        if (!cbBeforeResolve && cbResult === 'SUCCESS') console.log('PASS');
        else if (cbBeforeResolve) console.log('FAIL: cb fired before flush Promise resolved');
        else console.log('FAIL: cb=' + cbResult);
    }, 200);
}, 50);
""")
    assert result == "PASS", f"Async flush: {result}"


# [pr_diff] fail_to_pass
def test_final_error_propagation():
    """_final propagates flush() errors to cb(err) without crashing."""
    info = _extract_final()
    assert info["found"], "_final hook not found in ProcessObjectInternals.ts"

    result = _run_node_test("error_prop", r"""
const { buildFinal, makeProxy } = require('/tmp/bun_test_common.js');
const sink = {
    flush() { throw new Error('pipe broken'); },
    write() { return true; }, close(){}, ref(){}, unref(){}
};
const fn = buildFinal();
let cbResult = 'NOT_CALLED';
let uncaught = false;
process.on('uncaughtException', () => { uncaught = true; });
try {
    fn.call(makeProxy(sink), (err) => {
        cbResult = (err && err.message === 'pipe broken') ? 'ERROR_CAUGHT' : 'WRONG: ' + String(err);
    });
} catch(e) { cbResult = 'UNCAUGHT: ' + e.message; }
setTimeout(() => {
    console.log(cbResult === 'ERROR_CAUGHT' && !uncaught
        ? 'PASS' : 'FAIL: cb=' + cbResult + ' uncaught=' + uncaught);
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
# Config-derived (agent_config) — rules from src/js/CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — src/js/CLAUDE.md:56 @ ba05a72939569c1a371a513c3bd64a2cab6a60ee
def test_no_dot_call_apply():
    """_final must use .$call/.$apply, never .call/.apply (src/js/CLAUDE.md:56)."""
    info = _extract_final()
    assert info["found"], "_final hook not found in ProcessObjectInternals.ts"
    # Strip comments before checking
    lines = [l for l in info["body"].split("\n") if not l.strip().startswith("//")]
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
    info = _extract_final()
    assert info["found"], "_final hook not found in ProcessObjectInternals.ts"
    lines = [l for l in info["body"].split("\n") if not l.strip().startswith("//")]
    code = "\n".join(lines)
    assert "instanceof Promise" not in code, \
        "Uses 'instanceof Promise' instead of $isPromise — violates src/js/CLAUDE.md:105"
    assert "$isPromise" in code, \
        "Must use $isPromise intrinsic for Promise detection — violates src/js/CLAUDE.md:105"
