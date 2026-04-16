#!/usr/bin/env python3
"""
Test outputs for @mantine/modals breaking changes fix.

F2P tests use the TypeScript compiler API (via Node.js subprocess) to verify
behavioral/structural properties of the code. P2P tests run the repo's own
test tooling (jest, eslint, prettier, tsc).
"""

import subprocess

REPO = "/workspace/mantine"
MODALS_SRC = REPO + "/packages/@mantine/modals/src"


def run_node(script, timeout=30):
    """Execute a Node.js script via subprocess and return the result."""
    return subprocess.run(
        ['node', '-e', script],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout
    )


# =============================================================================
# FAIL-TO-PASS TESTS
# =============================================================================

def test_open_context_modal_signature():
    """
    F2P: openContextModal implementation should take two arguments (modal, props).

    Uses TypeScript compiler to parse ModalsProvider.tsx and count the function's
    parameters. The buggy version takes 1 (single object); the fix takes 2.
    """
    script = """
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s/ModalsProvider.tsx', 'utf8');
const sf = ts.createSourceFile('f.tsx', src, ts.ScriptTarget.Latest, true);

let paramCount = -1;
function visit(node) {
    if (ts.isVariableDeclaration(node) && node.name.getText(sf) === 'openContextModal' && node.initializer) {
        let fn = node.initializer;
        if (ts.isCallExpression(fn) && fn.arguments.length > 0) fn = fn.arguments[0];
        if (ts.isArrowFunction(fn) || ts.isFunctionExpression(fn)) paramCount = fn.parameters.length;
    }
    if (ts.isFunctionDeclaration(node) && node.name && node.name.getText(sf) === 'openContextModal') {
        paramCount = node.parameters.length;
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (paramCount !== 2) {
    console.error('openContextModal has ' + paramCount + ' parameter(s), expected 2');
    process.exit(1);
}
""" % MODALS_SRC

    result = run_node(script)
    assert result.returncode == 0, (
        "openContextModal should take two arguments (modal, props): " + result.stderr.strip()
    )


def test_context_has_close_all():
    """
    F2P: ModalsContextProps should have closeAll, not closeAllModals.

    Uses TypeScript compiler to inspect interface member names.
    """
    script = """
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s/context.ts', 'utf8');
const sf = ts.createSourceFile('f.ts', src, ts.ScriptTarget.Latest, true);

let hasCloseAll = false, hasCloseAllModals = false;
function visit(node) {
    if (ts.isInterfaceDeclaration(node) && node.name.getText(sf) === 'ModalsContextProps') {
        for (const m of node.members) {
            const n = m.name && m.name.getText(sf);
            if (n === 'closeAll') hasCloseAll = true;
            if (n === 'closeAllModals') hasCloseAllModals = true;
        }
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (!hasCloseAll) { console.error('ModalsContextProps missing closeAll'); process.exit(1); }
if (hasCloseAllModals) { console.error('ModalsContextProps still has closeAllModals'); process.exit(1); }
""" % MODALS_SRC

    result = run_node(script)
    assert result.returncode == 0, (
        "ModalsContextProps should have closeAll, not closeAllModals: " + result.stderr.strip()
    )


def test_update_context_modal_no_modal_key():
    """
    F2P: updateContextModal should not require modalKey parameter.

    Uses TypeScript compiler to inspect the function's destructured parameters.
    """
    script = """
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s/ModalsProvider.tsx', 'utf8');
const sf = ts.createSourceFile('f.tsx', src, ts.ScriptTarget.Latest, true);

let found = false, hasModalKey = false;
function visit(node) {
    if (ts.isVariableDeclaration(node) && node.name.getText(sf) === 'updateContextModal' && node.initializer) {
        let fn = node.initializer;
        if (ts.isCallExpression(fn) && fn.arguments.length > 0) fn = fn.arguments[0];
        if (ts.isArrowFunction(fn) || ts.isFunctionExpression(fn)) {
            found = true;
            for (const p of fn.parameters) {
                if (ts.isObjectBindingPattern(p.name)) {
                    for (const el of p.name.elements) {
                        if (el.name.getText(sf) === 'modalKey') hasModalKey = true;
                    }
                }
            }
        }
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (!found) { console.error('updateContextModal function not found'); process.exit(1); }
if (hasModalKey) { console.error('updateContextModal still destructures modalKey'); process.exit(1); }
""" % MODALS_SRC

    result = run_node(script)
    assert result.returncode == 0, (
        "updateContextModal should only need modalId: " + result.stderr.strip()
    )


def test_open_context_modal_type_signature():
    """
    F2P: openContextModal type in ModalsContextProps should take two parameters.

    Uses TypeScript compiler to count the function type's parameters.
    The buggy type has 1 (single props object); the fix has 2 (modal, props).
    """
    script = """
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s/context.ts', 'utf8');
const sf = ts.createSourceFile('f.ts', src, ts.ScriptTarget.Latest, true);

let paramCount = -1;
function visit(node) {
    if (ts.isInterfaceDeclaration(node) && node.name.getText(sf) === 'ModalsContextProps') {
        for (const m of node.members) {
            if (m.name && m.name.getText(sf) === 'openContextModal' && m.type && ts.isFunctionTypeNode(m.type)) {
                paramCount = m.type.parameters.length;
            }
        }
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (paramCount !== 2) {
    console.error('openContextModal type has ' + paramCount + ' param(s), expected 2');
    process.exit(1);
}
""" % MODALS_SRC

    result = run_node(script)
    assert result.returncode == 0, (
        "openContextModal type should take two arguments: " + result.stderr.strip()
    )


def test_no_context_modal_inner_props_type():
    """
    F2P: ContextModalInnerProps type should not exist; OpenContextModal should
    be defined directly.

    Uses TypeScript compiler to scan top-level type declarations.
    """
    script = """
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s/context.ts', 'utf8');
const sf = ts.createSourceFile('f.ts', src, ts.ScriptTarget.Latest, true);

let hasCMIP = false, hasOCM = false;
function visit(node) {
    if (ts.isTypeAliasDeclaration(node) || ts.isInterfaceDeclaration(node)) {
        const n = node.name.getText(sf);
        if (n === 'ContextModalInnerProps') hasCMIP = true;
        if (n === 'OpenContextModal') hasOCM = true;
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (!hasOCM) { console.error('OpenContextModal type not found'); process.exit(1); }
if (hasCMIP) { console.error('ContextModalInnerProps should be removed'); process.exit(1); }
""" % MODALS_SRC

    result = run_node(script)
    assert result.returncode == 0, (
        "ContextModalInnerProps should be removed: " + result.stderr.strip()
    )


def test_close_context_modal_uses_close_modal():
    """
    F2P: closeContextModal should delegate to closeModal, not have its own
    implementation with modal collection lookup.

    Uses TypeScript compiler to check that no closeContextModal variable
    contains a .find() call (the buggy lookup pattern).
    """
    script = """
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s/ModalsProvider.tsx', 'utf8');
const sf = ts.createSourceFile('f.tsx', src, ts.ScriptTarget.Latest, true);

let mentioned = false, hasBuggyLookup = false;

function checkForFind(node) {
    if (ts.isPropertyAccessExpression(node) && node.name.getText(sf) === 'find') {
        hasBuggyLookup = true;
    }
    ts.forEachChild(node, checkForFind);
}

function visit(node) {
    if (ts.isVariableDeclaration(node) && node.name.getText(sf) === 'closeContextModal') {
        mentioned = true;
        if (node.initializer) checkForFind(node.initializer);
    }
    if ((ts.isPropertyAssignment(node) || ts.isShorthandPropertyAssignment(node))
        && node.name && node.name.getText(sf) === 'closeContextModal') {
        mentioned = true;
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (!mentioned) { console.error('closeContextModal not found in provider'); process.exit(1); }
if (hasBuggyLookup) { console.error('closeContextModal should not perform modal lookup via .find()'); process.exit(1); }
""" % MODALS_SRC

    result = run_node(script)
    assert result.returncode == 0, (
        "closeContextModal should delegate to closeModal: " + result.stderr.strip()
    )


def test_modals_type_simplified():
    """
    F2P: MantineModalsOverwritten type should exist for proper type augmentation.

    Uses TypeScript compiler to find the type declaration in context.ts.
    """
    script = """
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s/context.ts', 'utf8');
const sf = ts.createSourceFile('f.ts', src, ts.ScriptTarget.Latest, true);

let hasMM = false, hasMMO = false;
function visit(node) {
    if (ts.isTypeAliasDeclaration(node) || ts.isInterfaceDeclaration(node)) {
        const n = node.name.getText(sf);
        if (n === 'MantineModals') hasMM = true;
        if (n === 'MantineModalsOverwritten') hasMMO = true;
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (!hasMM) { console.error('MantineModals type not found'); process.exit(1); }
if (!hasMMO) { console.error('MantineModalsOverwritten type not found'); process.exit(1); }
""" % MODALS_SRC

    result = run_node(script)
    assert result.returncode == 0, (
        "MantineModalsOverwritten type should exist: " + result.stderr.strip()
    )


def test_open_context_modal_in_events():
    """
    F2P: Provider should convert single-arg event payload to two-arg
    openContextModal call via a wrapper function in useModalsEvents.

    Uses TypeScript compiler to check that the openContextModal property
    in useModalsEvents is an explicit property assignment (wrapper), not
    a shorthand pass-through.
    """
    script = """
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s/ModalsProvider.tsx', 'utf8');
const sf = ts.createSourceFile('f.tsx', src, ts.ScriptTarget.Latest, true);

let foundProp = false, hasWrapper = false;
function visit(node) {
    if (ts.isCallExpression(node) && node.expression.getText(sf) === 'useModalsEvents' && node.arguments.length > 0) {
        const arg = node.arguments[0];
        if (ts.isObjectLiteralExpression(arg)) {
            for (const prop of arg.properties) {
                const name = prop.name && prop.name.getText(sf);
                if (name === 'openContextModal') {
                    foundProp = true;
                    if (ts.isPropertyAssignment(prop)) hasWrapper = true;
                }
            }
        }
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (!foundProp) { console.error('openContextModal not found in useModalsEvents call'); process.exit(1); }
if (!hasWrapper) { console.error('openContextModal needs a wrapper in useModalsEvents (not direct pass-through)'); process.exit(1); }
""" % MODALS_SRC

    result = run_node(script)
    assert result.returncode == 0, (
        "Provider should convert event payload to two-arg call: " + result.stderr.strip()
    )


# =============================================================================
# PASS-TO-PASS TESTS
# =============================================================================

def test_repo_jest_modals():
    """P2P: Jest tests for @mantine/modals should pass."""
    result = subprocess.run(
        ["npx", "jest", "packages/@mantine/modals", "--no-coverage"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, (
        f"Jest tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"
    )


def test_repo_eslint_modals():
    """P2P: ESLint passes on @mantine/modals source."""
    result = subprocess.run(
        ["npx", "eslint", "packages/@mantine/modals/src", "--no-cache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, (
        f"ESLint failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"
    )


def test_repo_prettier_check():
    """P2P: Prettier formatting check passes."""
    result = subprocess.run(
        ["npx", "prettier", "--check", "packages/@mantine/modals/**/*.{ts,tsx}"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, (
        f"Prettier check failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"
    )


def test_modals_package_builds():
    """P2P: @mantine/modals package should be buildable."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--project", "tsconfig.json"],
        cwd=f"{REPO}/packages/@mantine/modals",
        capture_output=True,
        text=True,
        timeout=60
    )
    if result.returncode != 0:
        if "Cannot find module '@mantine/core'" in result.stdout or \
           "Cannot find module '@mantine/hooks'" in result.stdout:
            import pytest
            pytest.skip("Workspace dependencies not built")
        else:
            assert False, f"TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"


def test_no_close_context_modal_export():
    """P2P: closeContextModal should not be exported from index.ts."""
    index_src = open(f"{MODALS_SRC}/index.ts").read()
    lines = index_src.split("\n")
    for line in lines:
        if line.strip().startswith("//"):
            continue
        if "closeContextModal" in line and "export" in line:
            assert False, "closeContextModal should not be exported from index.ts"


def test_reducer_uses_generic_open_context_modal():
    """P2P: reducer.ts should use OpenContextModal<any> with generic parameter."""
    reducer_src = open(f"{MODALS_SRC}/reducer.ts").read()
    assert "OpenContextModal<any>" in reducer_src, (
        "reducer.ts should use OpenContextModal<any>"
    )
