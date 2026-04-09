"""
Task: react-devtools-prerender-proxy-loop
Repo: react @ 4b568a8dbb4cb84b0067f353b9c0bec1ddb61d8e
PR:   35958

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/react"
PROXY_JS = os.path.join(REPO, "packages/react-devtools-extensions/src/contentScripts/proxy.js")
FLOW_DOM = os.path.join(REPO, "flow-typed/environments/dom.js")


def _strip_flow_types(code):
    """Strip Flow type annotations so proxy.js can be eval'd by Node.js."""
    # {target}: {target: any} → {target}
    code = re.sub(r'\{target\}\s*:\s*\{target:\s*any\}', '{target}', code)
    # Simple param type annotations: (name: any) → (name)
    code = re.sub(r'(\w+)\s*:\s*any\b', r'\1', code)
    # Variable type annotations: : IntervalID, : boolean
    code = re.sub(r':\s*IntervalID\b', '', code)
    code = re.sub(r':\s*boolean\b', '', code)
    # Generic type params: Map<number, Function>()
    code = re.sub(r'<number,\s*Function>', '', code)
    return code


def _build_test_script(prerendering_value, check_code):
    """Build a self-contained Node.js test script that loads proxy.js with mocks."""
    proxy_code = Path(PROXY_JS).read_text()
    proxy_code = _strip_flow_types(proxy_code)
    # Escape backticks and backslashes for embedding in template literal
    proxy_code_escaped = proxy_code.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

    return f"""
const vm = require('vm');

// Track registered event listeners
const windowEvents = {{}};
const docEvents = {{}};

const mockWindow = {{
    addEventListener: (name, handler) => {{
        if (!windowEvents[name]) windowEvents[name] = [];
        windowEvents[name].push(handler);
    }},
    removeEventListener: () => {{}},
    postMessage: () => {{}},
    __REACT_DEVTOOLS_PROXY_INJECTED__: undefined,
}};

const mockDocument = {{
    prerendering: {str(prerendering_value).lower()},
    addEventListener: (name, handler, opts) => {{
        if (!docEvents[name]) docEvents[name] = [];
        docEvents[name].push({{handler, opts}});
    }},
}};

Object.defineProperty(mockWindow, 'document', {{
    get: () => mockDocument,
}});

const sandbox = {{
    window: mockWindow,
    document: mockDocument,
    chrome: {{
        runtime: {{
            connect: () => ({{
                onMessage: {{ addListener: () => {{}} }},
                onDisconnect: {{ addListener: () => {{}} }},
                postMessage: () => {{}},
            }}),
            sendMessage: () => {{}},
            onMessage: {{ addListener: () => {{}} }},
        }},
    }},
    setInterval: () => 1,
    clearInterval: () => {{}},
    console: console,
    Map: Map,
    Error: Error,
}};

vm.createContext(sandbox);

// Load proxy.js in the sandboxed environment
const code = `{proxy_code_escaped}`;
vm.runInContext(code, sandbox);

// Fire pageshow event
const pageshowHandlers = windowEvents.pageshow || [];
pageshowHandlers.forEach(h => h({{target: mockDocument}}));

// Run check
{check_code}
"""


def _run_node_test(script):
    """Write script to temp file and run with Node.js."""
    fd, path = tempfile.mkstemp(suffix='.js', dir=REPO)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(script)
        r = subprocess.run(["node", path], cwd=REPO, capture_output=True, timeout=30)
    finally:
        os.unlink(path)
    return r


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_proxy_js_valid_syntax():
    """proxy.js must be valid JavaScript (after stripping Flow types)."""
    code = Path(PROXY_JS).read_text()
    code = _strip_flow_types(code)
    fd, path = tempfile.mkstemp(suffix='.js', dir=REPO)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(code)
        r = subprocess.run(
            ["node", "--check", path],
            cwd=REPO, capture_output=True, timeout=15,
        )
    finally:
        os.unlink(path)
    assert r.returncode == 0, (
        f"proxy.js has syntax errors:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_pageshow_defers_during_prerender():
    """When document.prerendering is true, pageshow must NOT inject the proxy."""
    check = """
if (sandbox.window.__REACT_DEVTOOLS_PROXY_INJECTED__) {
    console.error('FAIL: proxy was injected while page is prerendering');
    process.exit(1);
}
process.exit(0);
"""
    r = _run_node_test(_build_test_script(True, check))
    assert r.returncode == 0, (
        f"Proxy was injected during prerendering (should be deferred):\n"
        f"{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_prerenderingchange_deferred_injection():
    """During prerender, a prerenderingchange listener must be registered to defer injection."""
    check = """
const listeners = docEvents.prerenderingchange || [];
if (listeners.length === 0) {
    console.error('FAIL: no prerenderingchange listener registered during prerender');
    process.exit(1);
}
// Trigger the prerenderingchange callback and verify injection happens
const entry = listeners[0];
entry.handler();
if (!sandbox.window.__REACT_DEVTOOLS_PROXY_INJECTED__) {
    console.error('FAIL: proxy was not injected after prerenderingchange fired');
    process.exit(1);
}
process.exit(0);
"""
    r = _run_node_test(_build_test_script(True, check))
    assert r.returncode == 0, (
        f"prerenderingchange deferred injection not working:\n"
        f"{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_flow_document_prerendering():
    """Flow type for Document must include prerendering: boolean."""
    src = Path(FLOW_DOM).read_text()
    # Find the Document class declaration and check for prerendering property
    assert re.search(r'prerendering\s*:\s*boolean', src), (
        "flow-typed/environments/dom.js must declare 'prerendering: boolean' on Document"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_pageshow_injects_when_not_prerendering():
    """When document.prerendering is false, pageshow must inject the proxy normally."""
    check = """
if (!sandbox.window.__REACT_DEVTOOLS_PROXY_INJECTED__) {
    console.error('FAIL: proxy was not injected when not prerendering');
    process.exit(1);
}
process.exit(0);
"""
    r = _run_node_test(_build_test_script(False, check))
    assert r.returncode == 0, (
        f"Proxy not injected when prerendering=false:\n"
        f"{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [static] pass_to_pass
def test_pagereveal_still_registered():
    """pagereveal event must still have a handler registered (backward compat)."""
    # This test doesn't need the full sandbox — just verify the listener is registered
    check = """
const handlers = windowEvents.pagereveal || [];
if (handlers.length === 0) {
    console.error('FAIL: no pagereveal handler registered');
    process.exit(1);
}
process.exit(0);
"""
    r = _run_node_test(_build_test_script(False, check))
    assert r.returncode == 0, (
        f"pagereveal handler not registered:\n"
        f"{r.stdout.decode()}\n{r.stderr.decode()}"
    )
