"""
Task: react-devtools-prerendering-pageshow
Repo: facebook/react @ 4b568a8dbb4cb84b0067f353b9c0bec1ddb61d8e
PR:   facebook/react#35958

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"
PROXY = Path(REPO) / "packages/react-devtools-extensions/src/contentScripts/proxy.js"
FLOW_DOM = Path(REPO) / "flow-typed/environments/dom.js"

# Shared Node.js snippet: extract a function body by brace matching.
_EXTRACT_FN = r"""
function extractFn(code, name) {
    const pat = 'function ' + name + '(';
    const idx = code.indexOf(pat);
    if (idx === -1) return null;
    let bs = code.indexOf('{', idx);
    let depth = 0;
    for (let i = bs; i < code.length; i++) {
        if (code[i] === '{') depth++;
        else if (code[i] === '}') { depth--; if (depth === 0) return code.substring(bs + 1, i); }
    }
    return null;
}
"""


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    script = Path(REPO) / "_eval_tmp.js"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file integrity checks
# ---------------------------------------------------------------------------


def test_proxy_js_exists_and_nontrivial():
    """proxy.js must exist and contain core extension functions."""
    assert PROXY.exists(), f"proxy.js not found at {PROXY}"
    content = PROXY.read_text()
    assert "function injectProxy" in content, "injectProxy function missing from proxy.js"
    assert "connectPort" in content, "connectPort function missing from proxy.js"
    assert len(content) > 500, "proxy.js is suspiciously small — likely truncated or stubbed"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix verification
# ---------------------------------------------------------------------------


def test_handle_pageshow_defers_when_prerendering():
    """When document.prerendering is true, handlePageShow defers injection via prerenderingchange."""
    r = _run_node(_EXTRACT_FN + r"""
const fs = require('fs');
const code = fs.readFileSync('packages/react-devtools-extensions/src/contentScripts/proxy.js', 'utf8');

const body = extractFn(code, 'handlePageShow');
if (!body) { console.log(JSON.stringify({error: 'handlePageShow not found'})); process.exit(0); }

let injectCalls = 0;
let events = [];
const injectProxy = () => { injectCalls++; };
const document = {
    prerendering: true,
    addEventListener: (evt, fn, opts) => { events.push({evt, once: opts?.once}); },
};

try {
    const fn = new Function('document', 'injectProxy', body);
    fn(document, injectProxy);
} catch(e) {
    console.log(JSON.stringify({error: e.message})); process.exit(0);
}

console.log(JSON.stringify({injectCalls, events}));
""")
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "error" not in data, f"Execution error: {data.get('error')}"
    # injectProxy must NOT be called when prerendering
    assert data["injectCalls"] == 0, (
        f"injectProxy was called {data['injectCalls']} time(s) when prerendering=true, expected 0"
    )
    # prerenderingchange listener must be registered
    pc = [e for e in data["events"] if e["evt"] == "prerenderingchange"]
    assert len(pc) >= 1, "No prerenderingchange listener was registered"
    assert pc[0]["once"] is True, (
        f"prerenderingchange listener missing once:true, got opts={pc[0]}"
    )


def test_handle_pageshow_injects_when_not_prerendering():
    """When document.prerendering is false, handlePageShow calls injectProxy directly."""
    r = _run_node(_EXTRACT_FN + r"""
const fs = require('fs');
const code = fs.readFileSync('packages/react-devtools-extensions/src/contentScripts/proxy.js', 'utf8');

const body = extractFn(code, 'handlePageShow');
if (!body) { console.log(JSON.stringify({error: 'handlePageShow not found'})); process.exit(0); }

let injectCalls = 0;
const injectProxy = () => { injectCalls++; };
const document = {
    prerendering: false,
    addEventListener: () => {},
};

try {
    const fn = new Function('document', 'injectProxy', body);
    fn(document, injectProxy);
} catch(e) {
    console.log(JSON.stringify({error: e.message})); process.exit(0);
}

console.log(JSON.stringify({injectCalls}));
""")
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "error" not in data, f"Execution error: {data.get('error')}"
    assert data["injectCalls"] >= 1, (
        f"injectProxy was not called when prerendering=false, expected >= 1 call"
    )


def test_pageshow_listener_uses_handle_pageshow():
    """The pageshow event listener must be registered with handlePageShow, not injectProxy."""
    r = _run_node(r"""
const fs = require('fs');
const code = fs.readFileSync('packages/react-devtools-extensions/src/contentScripts/proxy.js', 'utf8');

const match = code.match(/addEventListener\s*\(\s*['"]pageshow['"]\s*,\s*(\w+)\s*\)/);
if (!match) { console.log('MISSING'); process.exit(0); }
console.log(match[1]);
""")
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    handler = r.stdout.strip()
    assert handler == "handlePageShow", (
        f"pageshow listener uses '{handler}', expected 'handlePageShow'"
    )


def test_inject_proxy_no_target_parameter():
    """injectProxy must have no parameters (old {target} destructuring removed)."""
    r = _run_node(r"""
const fs = require('fs');
const code = fs.readFileSync('packages/react-devtools-extensions/src/contentScripts/proxy.js', 'utf8');

// Extract function signature (up to closing paren of parameter list)
function extractSig(code, name) {
    const pat = 'function ' + name + '(';
    const idx = code.indexOf(pat);
    if (idx === -1) return null;
    let ps = code.indexOf('(', idx);
    let depth = 0;
    for (let i = ps; i < code.length; i++) {
        if (code[i] === '(') depth++;
        else if (code[i] === ')') { depth--; if (depth === 0) return code.substring(idx, i + 1); }
    }
    return null;
}

const sig = extractSig(code, 'injectProxy');
if (!sig) { console.log('MISSING'); process.exit(0); }

// Strip Flow type annotation: {target}: {target: any} -> {target}
const cleaned = sig.replace(/\{target\}\s*:\s*\{target:\s*any\}/g, '{target}');

const paramMatch = cleaned.match(/function\s+injectProxy\s*\(([^)]*)\)/);
if (!paramMatch) { console.log('MISSING'); process.exit(0); }

const params = paramMatch[1].trim();
console.log(params.length === 0 ? '0' : params);
""")
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    result = r.stdout.strip()
    assert result == "0", f"injectProxy has parameters: '{result}', expected none"


def test_flow_prerendering_type_declared():
    """flow-typed/environments/dom.js must declare prerendering: boolean on Document."""
    assert FLOW_DOM.exists(), f"Flow DOM type definitions not found at {FLOW_DOM}"
    content = FLOW_DOM.read_text()
    assert re.search(r"\bprerendering\s*:\s*boolean\b", content), (
        "prerendering: boolean not found in flow-typed/environments/dom.js"
    )
