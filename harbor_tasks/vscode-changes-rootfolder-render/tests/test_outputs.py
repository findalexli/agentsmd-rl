"""
Task: vscode-changes-rootfolder-render
Repo: microsoft/vscode @ 3c51a00d738294aa6e113b87e38b8ea770fbf9ee

Fix: Add root folder rendering to Changes View tree, support workspace
files without git repos, and add 'none' change type for unchanged files.

All checks must pass for reward = 1. Any failure = reward 0.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
TARGET = f"{REPO}/src/vs/sessions/contrib/changes/browser/changesView.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# --- fail_to_pass checks ---


def test_type_guards_behavior():
    """isChangesFileItem and isChangesRootItem correctly distinguish element types."""
    r = _run_node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('src/vs/sessions/contrib/changes/browser/changesView.ts', 'utf8');
const sf = ts.createSourceFile('changesView.ts', src, ts.ScriptTarget.Latest, true);

const exprs = {};
sf.forEachChild(node => {
    if (ts.isFunctionDeclaration(node) && node.name) {
        const name = node.name.text;
        if (name === 'isChangesFileItem' || name === 'isChangesRootItem') {
            const body = node.body;
            if (body && body.statements.length === 1) {
                const stmt = body.statements[0];
                if (ts.isReturnStatement(stmt) && stmt.expression) {
                    exprs[name] = stmt.expression.getText(sf);
                }
            }
        }
    }
});

if (!exprs.isChangesFileItem) throw new Error('isChangesFileItem not found');
if (!exprs.isChangesRootItem) throw new Error('isChangesRootItem not found');

const ResourceTree = { isResourceNode: (e) => e._isResourceNode === true };
const makeGuard = (exprText) => new Function('ResourceTree', 'return function(element) { return ' + exprText + '; }')(ResourceTree);

const isChangesFileItem = makeGuard(exprs.isChangesFileItem);
const isChangesRootItem = makeGuard(exprs.isChangesRootItem);

const rootItem = { type: 'root', uri: {}, name: 'test' };
const fileItem = { type: 'file', uri: {}, state: 'Accepted' };
const resourceNode = { _isResourceNode: true };

if (!isChangesFileItem(fileItem)) throw new Error('should accept file');
if (isChangesFileItem(rootItem)) throw new Error('should reject root');
if (isChangesFileItem(resourceNode)) throw new Error('should reject resource node');

if (!isChangesRootItem(rootItem)) throw new Error('should accept root');
if (isChangesRootItem(fileItem)) throw new Error('should reject file');
if (isChangesRootItem(resourceNode)) throw new Error('should reject resource node');

console.log('PASS');
""")
    assert r.returncode == 0, f"Type guard behavior test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_change_type_includes_none():
    """ChangeType union type includes 'none' for unchanged files."""
    r = _run_node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('src/vs/sessions/contrib/changes/browser/changesView.ts', 'utf8');
const sf = ts.createSourceFile('changesView.ts', src, ts.ScriptTarget.Latest, true);

let found = false;
sf.forEachChild(node => {
    if (ts.isTypeAliasDeclaration(node) && node.name.text === 'ChangeType') {
        const typeNode = node.type;
        if (ts.isUnionTypeNode(typeNode)) {
            for (const member of typeNode.types) {
                if (ts.isLiteralTypeNode(member) && ts.isStringLiteral(member.literal) && member.literal.text === 'none') {
                    found = true;
                }
            }
        }
    }
});
if (!found) throw new Error("'none' not found in ChangeType union");
console.log('PASS');
""")
    assert r.returncode == 0, f"ChangeType test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_root_item_interfaces_defined():
    """IChangesRootItem and IChangesTreeRootInfo interfaces are defined with required members."""
    r = _run_node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('src/vs/sessions/contrib/changes/browser/changesView.ts', 'utf8');
const sf = ts.createSourceFile('changesView.ts', src, ts.ScriptTarget.Latest, true);

const interfaces = {};
sf.forEachChild(node => {
    if (ts.isInterfaceDeclaration(node)) {
        interfaces[node.name.text] = node;
    }
});

if (!interfaces['IChangesRootItem']) throw new Error('IChangesRootItem not found');
if (!interfaces['IChangesTreeRootInfo']) throw new Error('IChangesTreeRootInfo not found');

const rootItemMembers = interfaces['IChangesRootItem'].members
    .map(m => m.name ? m.name.getText(sf) : null)
    .filter(Boolean);
if (!rootItemMembers.includes('type') || !rootItemMembers.includes('uri') || !rootItemMembers.includes('name')) {
    throw new Error('IChangesRootItem missing required members (type, uri, name)');
}

const rootInfoMembers = interfaces['IChangesTreeRootInfo'].members
    .map(m => m.name ? m.name.getText(sf) : null)
    .filter(Boolean);
if (!rootInfoMembers.includes('root') || !rootInfoMembers.includes('resourceTreeRootUri')) {
    throw new Error('IChangesTreeRootInfo missing required members (root, resourceTreeRootUri)');
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Interface definition test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_build_tree_children_accepts_root_info():
    """buildTreeChildren accepts optional treeRootInfo parameter for wrapping."""
    r = _run_node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('src/vs/sessions/contrib/changes/browser/changesView.ts', 'utf8');
const sf = ts.createSourceFile('changesView.ts', src, ts.ScriptTarget.Latest, true);

let found = false;
sf.forEachChild(node => {
    if (ts.isFunctionDeclaration(node) && node.name && node.name.text === 'buildTreeChildren') {
        found = true;
        const params = node.parameters;
        let hasTreeRootInfo = false;
        for (const p of params) {
            if (p.name.getText(sf) === 'treeRootInfo') {
                hasTreeRootInfo = true;
                if (!p.questionToken) throw new Error('treeRootInfo should be optional');
            }
        }
        if (!hasTreeRootInfo) throw new Error('buildTreeChildren missing treeRootInfo parameter');
    }
});
if (!found) throw new Error('buildTreeChildren function not found');
console.log('PASS');
""")
    assert r.returncode == 0, f"buildTreeChildren test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_render_root_element_method():
    """renderRootElement method exists and uses FileKind.ROOT_FOLDER."""
    r = _run_node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('src/vs/sessions/contrib/changes/browser/changesView.ts', 'utf8');
const sf = ts.createSourceFile('changesView.ts', src, ts.ScriptTarget.Latest, true);

let found = false;
function walk(node) {
    if (ts.isClassDeclaration(node)) {
        ts.forEachChild(node, member => {
            if (ts.isMethodDeclaration(member) && member.name && member.name.getText(sf) === 'renderRootElement') {
                found = true;
                const body = member.body ? member.body.getText(sf) : '';
                if (!body.includes('ROOT_FOLDER')) {
                    throw new Error('renderRootElement should reference FileKind.ROOT_FOLDER');
                }
            }
        });
    }
    ts.forEachChild(node, walk);
}
walk(sf);
if (!found) throw new Error('renderRootElement method not found');
console.log('PASS');
""")
    assert r.returncode == 0, f"renderRootElement test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_collect_workspace_files_function():
    """collectWorkspaceFiles async function exists for non-git file enumeration."""
    r = _run_node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('src/vs/sessions/contrib/changes/browser/changesView.ts', 'utf8');
const sf = ts.createSourceFile('changesView.ts', src, ts.ScriptTarget.Latest, true);

let found = false;
sf.forEachChild(node => {
    if (ts.isFunctionDeclaration(node) && node.name && node.name.text === 'collectWorkspaceFiles') {
        found = true;
        const mods = node.modifiers || [];
        const isAsync = mods.some(m => m.kind === ts.SyntaxKind.AsyncKeyword);
        if (!isAsync) throw new Error('collectWorkspaceFiles should be async');
        if (node.parameters.length < 2) throw new Error('needs fileService and rootUri params');
    }
});
if (!found) throw new Error('collectWorkspaceFiles function not found');
console.log('PASS');
""")
    assert r.returncode == 0, f"collectWorkspaceFiles test failed: {r.stderr}"
    assert "PASS" in r.stdout


# --- pass_to_pass checks ---


def test_file_exists():
    """Target changesView.ts file must exist."""
    assert Path(TARGET).exists()
