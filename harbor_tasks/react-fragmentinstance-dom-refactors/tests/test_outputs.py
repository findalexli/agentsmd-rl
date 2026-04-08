"""
Task: react-fragmentinstance-dom-refactors
Repo: facebook/react @ 78f5c504b732aec0eb12514bc2cf3f27a8143dd2

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
TARGET = "packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js"


def _run_node(code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Execute a Node.js script in the repo directory."""
    script = Path(REPO) / "_eval_test_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# Shared JS: parse file with @babel/parser, provide AST helpers
_SETUP = """\
const {parse} = require('@babel/parser');
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');
const ast = parse(src, {sourceType: 'module', plugins: ['flow', 'jsx']});

function walk(node, fn, seen) {
    if (!node || typeof node !== 'object') return;
    if (!seen) seen = new Set();
    if (seen.has(node)) return;
    seen.add(node);
    if (fn(node) === false) return;
    for (const k of Object.keys(node)) {
        if (k === 'start' || k === 'end' || k === 'loc') continue;
        const v = node[k];
        if (Array.isArray(v)) { for (const c of v) walk(c, fn, seen); }
        else if (v && typeof v === 'object' && v.type) walk(v, fn, seen);
    }
}

function findFuncDecl(name) {
    let r = null;
    walk(ast, n => {
        if (n.type === 'FunctionDeclaration' && n.id && n.id.name === name) {
            r = n; return false;
        }
    });
    return r;
}

function findProtoMethod(name) {
    let r = null;
    walk(ast, n => {
        if (n.type === 'AssignmentExpression' &&
            n.left.type === 'MemberExpression' &&
            n.left.property.name === name &&
            n.left.object.type === 'MemberExpression' &&
            n.left.object.property.name === 'prototype' &&
            n.right.type === 'FunctionExpression') {
            r = n.right; return false;
        }
    });
    return r;
}

function txt(n) { return src.slice(n.start, n.end); }
""" % TARGET


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_valid():
    """ReactFiberConfigDOM.js parses without syntax errors via @babel/parser."""
    r = _run_node(_SETUP + """
console.log('PARSE_OK');
""")
    assert r.returncode == 0, f"Parse failed: {r.stderr}"
    assert "PARSE_OK" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — AST-verified via Node.js subprocess
# ---------------------------------------------------------------------------

def test_empty_array_early_return():
    """indexOfEventListener returns -1 immediately when the listener array is empty."""
    r = _run_node(_SETUP + r"""
const func = findFuncDecl('indexOfEventListener');
if (!func) { console.error('indexOfEventListener not found'); process.exit(1); }

const body = func.body.body;
const first = body[0];
if (!first || first.type !== 'IfStatement') {
    console.error('FAIL: first statement must be an if-guard for empty array, got ' +
        (first ? first.type : 'undefined'));
    process.exit(1);
}

const testSrc = txt(first.test);
if (!/\.length\s*===\s*0/.test(testSrc)) {
    console.error('FAIL: if-guard must check .length === 0, got: ' + testSrc);
    process.exit(1);
}

// Consequent must contain return -1
const stmts = first.consequent.type === 'BlockStatement'
    ? first.consequent.body : [first.consequent];
const hasReturnNeg1 = stmts.some(s =>
    s.type === 'ReturnStatement' && txt(s).includes('-1')
);
if (!hasReturnNeg1) {
    console.error('FAIL: if-guard must return -1');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_normalized_options_cached_before_loop():
    """normalizeListenerOptions(optionsOrUseCapture) is called once, before the loop."""
    r = _run_node(_SETUP + r"""
const func = findFuncDecl('indexOfEventListener');
if (!func) { console.error('indexOfEventListener not found'); process.exit(1); }

const body = func.body.body;

// Find a VariableDeclaration that caches normalizeListenerOptions(optionsOrUseCapture)
let cacheIdx = -1;
let forIdx = -1;
for (let i = 0; i < body.length; i++) {
    const stmt = body[i];
    if (stmt.type === 'VariableDeclaration') {
        const t = txt(stmt);
        if (t.includes('normalizeListenerOptions') && t.includes('optionsOrUseCapture')) {
            cacheIdx = i;
        }
    }
    if (stmt.type === 'ForStatement' && forIdx === -1) {
        forIdx = i;
    }
}

if (cacheIdx === -1) {
    console.error('FAIL: no cached normalizeListenerOptions(optionsOrUseCapture) before loop');
    process.exit(1);
}
if (forIdx === -1) {
    console.error('FAIL: for-loop not found');
    process.exit(1);
}
if (cacheIdx >= forIdx) {
    console.error('FAIL: cache declaration must come before the for loop');
    process.exit(1);
}

// normalizeListenerOptions(optionsOrUseCapture) must NOT appear inside the loop body
const loopSrc = txt(body[forIdx]);
if (/normalizeListenerOptions\s*\(\s*optionsOrUseCapture\s*\)/.test(loopSrc)) {
    console.error('FAIL: normalizeListenerOptions(optionsOrUseCapture) still called inside loop');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_blur_early_exit_when_active_not_in_parent():
    """blur() checks whether activeElement is inside the fragment's parent before traversal."""
    r = _run_node(_SETUP + r"""
const func = findProtoMethod('blur');
if (!func) { console.error('FragmentInstance.prototype.blur not found'); process.exit(1); }

const funcSrc = txt(func);

const containsIdx = funcSrc.indexOf('.contains(');
const traverseIdx = funcSrc.indexOf('traverseFragmentInstance');

if (containsIdx === -1) {
    console.error('FAIL: blur() must call .contains() to guard traversal');
    process.exit(1);
}
if (traverseIdx === -1) {
    console.error('FAIL: traverseFragmentInstance call not found');
    process.exit(1);
}
if (containsIdx > traverseIdx) {
    console.error('FAIL: .contains() guard must appear before traverseFragmentInstance call');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_active_element_passed_to_traversal_callback():
    """blur() passes pre-fetched activeElement to traverseFragmentInstance."""
    r = _run_node(_SETUP + r"""
const func = findProtoMethod('blur');
if (!func) { console.error('FragmentInstance.prototype.blur not found'); process.exit(1); }

// Find the traverseFragmentInstance CallExpression via AST walk
let callNode = null;
walk(func, n => {
    if (n.type === 'CallExpression' &&
        n.callee.type === 'Identifier' &&
        n.callee.name === 'traverseFragmentInstance') {
        callNode = n; return false;
    }
});

if (!callNode) {
    console.error('FAIL: traverseFragmentInstance call not found in blur()');
    process.exit(1);
}

if (callNode.arguments.length < 3) {
    console.error('FAIL: traverseFragmentInstance must receive 3 args (fiber, callback, activeElement), got ' +
        callNode.arguments.length);
    process.exit(1);
}

const thirdArg = txt(callNode.arguments[2]);
if (!thirdArg.includes('activeElement')) {
    console.error('FAIL: third arg must be activeElement, got: ' + thirdArg);
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_text_nodes_skipped_in_blur_traversal():
    """blurActiveElementWithinFragment skips HostText nodes (can't be focused)."""
    r = _run_node(_SETUP + r"""
const func = findFuncDecl('blurActiveElementWithinFragment');
if (!func) {
    console.error('FAIL: blurActiveElementWithinFragment function not found');
    process.exit(1);
}

const funcSrc = txt(func);
if (!funcSrc.includes('HostText')) {
    console.error('FAIL: must check child.tag === HostText to skip text nodes');
    process.exit(1);
}

// Function must accept at least 2 params (child, activeElement)
if (func.params.length < 2) {
    console.error('FAIL: must accept activeElement parameter (got ' + func.params.length + ' params)');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_redundant_first_instance_removed():
    """compareDocumentPosition no longer declares a redundant firstInstance variable."""
    r = _run_node(_SETUP + r"""
const func = findProtoMethod('compareDocumentPosition');
if (!func) {
    console.error('FAIL: compareDocumentPosition not found');
    process.exit(1);
}

const funcSrc = txt(func);
if (/\b(const|let|var)\s+firstInstance\b/.test(funcSrc)) {
    console.error('FAIL: redundant firstInstance variable must be removed');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout
