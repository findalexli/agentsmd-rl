"""
Task: react-devtools-extension-types
Repo: facebook/react @ 9c0323e2cf9be543d6eaa44419598622603f

Add Flow type annotations to React DevTools browser extension files,
replacing untyped `chrome` global with proper ExtensionAPI interface.

All checks must pass for reward = 1. Any failure = reward 0.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — type definitions and annotations
# ---------------------------------------------------------------------------


def test_flow_interfaces_and_chrome_typed():
    """ExtensionRuntimePort and ExtensionAPI interfaces are fully defined with chrome typed as ExtensionAPI."""
    r = _run_node("""
const fs = require('fs');
const types = fs.readFileSync('scripts/flow/react-devtools.js', 'utf8');

// ExtensionRuntimePort must exist with all required members
const portMatch = types.match(/interface\\s+ExtensionRuntimePort\\s*\\{([\\s\\S]*?)\\n\\}/);
if (!portMatch) throw new Error('ExtensionRuntimePort interface not found');

const portBody = portMatch[1];
['disconnect()', 'postMessage(', 'onMessage', 'onDisconnect', 'name:'].forEach(m => {
    if (!portBody.includes(m)) throw new Error('ExtensionRuntimePort missing: ' + m);
});

// ExtensionAPI must exist with required properties
const apiMatch = types.match(/interface\\s+ExtensionAPI\\s*\\{([\\s\\S]*?)\\n\\}/);
if (!apiMatch) throw new Error('ExtensionAPI interface not found');

const apiBody = apiMatch[1];
['runtime:', 'tabs:', 'devtools:'].forEach(p => {
    if (!apiBody.includes(p)) throw new Error('ExtensionAPI missing: ' + p);
});

// chrome must be typed as ExtensionAPI, not any
if (!types.includes('declare const chrome: ExtensionAPI')) {
    throw new Error('chrome must be typed as ExtensionAPI');
}
if (types.match(/declare\\s+const\\s+chrome\\s*:\\s*any/)) {
    throw new Error('chrome should not be typed as any');
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Interface validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_background_script_typed():
    """Background index.js has @flow, typed parameters, and uses ExtensionRuntimePort."""
    r = _run_node("""
const fs = require('fs');
const bg = fs.readFileSync(
    'packages/react-devtools-extensions/src/background/index.js', 'utf8');

// Must have @flow annotation
if (!bg.includes('@flow')) throw new Error('Missing @flow annotation');

// Must use ExtensionRuntimePort type
if (!bg.includes('ExtensionRuntimePort')) throw new Error('Missing ExtensionRuntimePort');

// registerTab must have tabId: number
if (!/registerTab\\s*\\(\\s*tabId\\s*:\\s*number/.test(bg)) {
    throw new Error('registerTab missing tabId: number');
}

// registerExtensionPort must have typed port param
if (!/registerExtensionPort\\s*\\(\\s*port\\s*:\\s*ExtensionRuntimePort/.test(bg)) {
    throw new Error('registerExtensionPort missing typed port param');
}

// registerProxyPort must have typed port param
if (!/registerProxyPort\\s*\\(\\s*port\\s*:\\s*ExtensionRuntimePort/.test(bg)) {
    throw new Error('registerProxyPort missing typed port param');
}

// connectExtensionAndProxyPorts must have typed nullable port params
if (!/maybeExtensionPort\\s*:\\s*ExtensionRuntimePort/.test(bg)) {
    throw new Error('connectExtensionAndProxyPorts missing typed extension port');
}
if (!/maybeProxyPort\\s*:\\s*ExtensionRuntimePort/.test(bg)) {
    throw new Error('connectExtensionAndProxyPorts missing typed proxy port');
}

// ports object must be typed
if (!bg.includes('[tabId: string]:')) {
    throw new Error('ports object not properly typed');
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Background type check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_main_uses_shared_types():
    """Main index.js uses shared ExtensionRuntimePort and local ExtensionPort typedef is removed."""
    r = _run_node("""
const fs = require('fs');
const main = fs.readFileSync(
    'packages/react-devtools-extensions/src/main/index.js', 'utf8');

// Must reference shared ExtensionRuntimePort
if (!main.includes('ExtensionRuntimePort')) {
    throw new Error('main/index.js should reference ExtensionRuntimePort');
}

// Local ExtensionPort typedef must be removed
if (main.includes('type ExtensionPort = {')) {
    throw new Error('Local ExtensionPort typedef should be removed');
}

// port variable should use ExtensionRuntimePort
if (!/let\\s+port\\s*:\\s*ExtensionRuntimePort/.test(main)) {
    throw new Error('port variable should be typed as ExtensionRuntimePort');
}

// Old ExtensionEvent local type should be removed (replaced by shared type)
if (main.includes('type ExtensionEvent = {')) {
    throw new Error('Local ExtensionEvent typedef should be removed');
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Main script type check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — files exist and parse correctly
# ---------------------------------------------------------------------------


def test_modified_files_parse():
    """Modified JS files parse as valid Flow-enabled JavaScript via babel."""
    r = _run_node("""
const parser = require('@babel/parser');
const fs = require('fs');

const files = [
    'scripts/flow/react-devtools.js',
    'packages/react-devtools-extensions/src/background/index.js',
    'packages/react-devtools-extensions/src/main/index.js',
];

for (const file of files) {
    const code = fs.readFileSync(file, 'utf8');
    try {
        parser.parse(code, { sourceType: 'module', plugins: ['flow', 'jsx'] });
    } catch (e) {
        throw new Error('Parse error in ' + file + ': ' + e.message);
    }
}

console.log('PASS');
""", timeout=60)
    assert r.returncode == 0, f"File parsing failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_modified_files_exist():
    """All modified files exist and are non-empty."""
    for f in [
        "scripts/flow/react-devtools.js",
        "packages/react-devtools-extensions/src/background/index.js",
        "packages/react-devtools-extensions/src/main/index.js",
    ]:
        text = Path(f"{REPO}/{f}").read_text()
        assert len(text) > 0, f"{f} is empty"
