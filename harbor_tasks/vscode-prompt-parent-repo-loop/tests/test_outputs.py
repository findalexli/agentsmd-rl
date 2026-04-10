"""
Task: vscode-prompt-parent-repo-loop
Repo: microsoft/vscode @ 68cb51843c3f0f4e551479f825d18c954e88c778

Fix: Prevent infinite loop in findParentRepoFolders when walking up
directory tree by restructuring do-while into while(true) with explicit
break on dirname fixed-point, root path, user home, and seen-set checks.

All checks must pass for reward = 1. Any failure = reward 0.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
TARGET = f"{REPO}/src/vs/workbench/contrib/chat/common/promptSyntax/utils/promptFilesLocator.ts"


def test_file_exists():
    """Target file must exist."""
    assert Path(TARGET).exists()


def test_loop_terminates_at_drive_root():
    """
    The findParentRepoFolders loop must terminate when dirname hits a
    fixed point (e.g., Windows drive root where dirname("/c:/") === "/c:/").

    Reads the actual source, verifies the while(true) + isEqual(current, parent)
    structure, then simulates the algorithm with mock URIs to confirm termination.

    Base (buggy do-while): fails — no while(true), no fixed-point check.
    Fix (while-true + break): passes — terminates at drive root.
    """
    script = Path(REPO) / "_eval_loop_test.mjs"
    script.write_text(r"""
import { readFileSync } from 'fs';

const src = readFileSync(
    'src/vs/workbench/contrib/chat/common/promptSyntax/utils/promptFilesLocator.ts',
    'utf8'
);

// Locate the findParentRepoFolders method
const idx = src.indexOf('findParentRepoFolders');
if (idx < 0) { console.error('FAIL: method not found'); process.exit(1); }
const body = src.slice(idx, idx + 3000);

// Buggy version has do { ... } while(...) — misses dirname fixed-point.
// Fixed version uses while(true) { ... break when isEqual(current, parent) ... }
if (/\bdo\s*\{/.test(body) && !/while\s*\(\s*true\s*\)/.test(body)) {
    console.error('FAIL: do-while loop lacks dirname fixed-point termination');
    process.exit(1);
}
if (!/while\s*\(\s*true\s*\)/.test(body)) {
    console.error('FAIL: expected while(true) loop');
    process.exit(1);
}
if (!/isEqual\s*\(\s*current\s*,\s*parent\s*\)/.test(body)) {
    console.error('FAIL: missing isEqual(current, parent) fixed-point check');
    process.exit(1);
}

// Simulate the fixed algorithm with a Windows-style drive root
function makeUri(p) { return { path: p }; }
function dirname(uri) {
    if (/^\/[a-z]:\/$/i.test(uri.path)) return makeUri(uri.path);
    const i = uri.path.lastIndexOf('/');
    if (i <= 0) return makeUri('/');
    return makeUri(uri.path.slice(0, i));
}
function isEqual(a, b) { return a.path === b.path; }

let current = makeUri('/c:/Users/me/deep/project');
const userHome = makeUri('/unrelated/home');
const seen = new Set();
let iters = 0;

while (true) {
    if (++iters > 100) { console.error('FAIL: loop did not terminate'); process.exit(1); }
    const parent = dirname(current);
    if (isEqual(current, parent) || current.path === '/'
        || isEqual(userHome, parent) || seen.has(parent.path)) break;
    seen.add(current.path);
    current = parent;
}

console.log('PASS:terminated_after_' + iters + '_iterations');
""")
    try:
        r = subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=15, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)
    assert r.returncode == 0, f"Terminated with error: {r.stderr}"
    assert "PASS:terminated_after_" in r.stdout


def test_parent_computed_inside_loop():
    """
    dirname(current) must be computed inside the while(true) body, not
    before the loop. The buggy version pre-computes parent before the
    do-while, so the first iteration uses a stale parent value.

    Base: fails (parent = dirname(current) appears before do-while).
    Fix: passes (const parent = dirname(current) inside while-true body).
    """
    script = Path(REPO) / "_eval_parent_test.mjs"
    script.write_text(r"""
import { readFileSync } from 'fs';

const src = readFileSync(
    'src/vs/workbench/contrib/chat/common/promptSyntax/utils/promptFilesLocator.ts',
    'utf8'
);

const idx = src.indexOf('findParentRepoFolders');
if (idx < 0) { console.error('FAIL: method not found'); process.exit(1); }
const body = src.slice(idx, idx + 3000);

const loopStart = Math.max(
    body.indexOf('while (true)'),
    body.indexOf('while(true)')
);
if (loopStart < 0) {
    console.error('FAIL: no while(true) loop found');
    process.exit(1);
}

// parent = dirname(current) must appear AFTER the loop start
const afterLoop = body.slice(loopStart);
if (!/(?:const|let)\s+parent\s*=\s*dirname\(current\)/.test(afterLoop)) {
    console.error('FAIL: parent = dirname(current) not inside loop body');
    process.exit(1);
}

// Must NOT have 'let parent = dirname(current)' before the loop
const beforeLoop = body.slice(0, loopStart);
if (/let\s+parent\s*=\s*dirname\(current\)/.test(beforeLoop)) {
    console.error('FAIL: parent computed before loop (buggy pattern)');
    process.exit(1);
}

console.log('PASS');
""")
    try:
        r = subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=15, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_break_with_all_termination_conditions():
    """
    The break guard must include all four termination conditions:
    1. isEqual(current, parent) — dirname fixed-point (filesystem root)
    2. current.path === '/' — Unix root
    3. isEqual(userHome, parent) — user home boundary
    4. seen.has(parent) — already-visited folder

    Base: fails (missing isEqual(current,parent), checks current not parent
          for userHome/seen).
    Fix: passes (all four present with correct operands).
    """
    script = Path(REPO) / "_eval_break_test.mjs"
    script.write_text(r"""
import { readFileSync } from 'fs';

const src = readFileSync(
    'src/vs/workbench/contrib/chat/common/promptSyntax/utils/promptFilesLocator.ts',
    'utf8'
);

const idx = src.indexOf('findParentRepoFolders');
if (idx < 0) { console.error('FAIL: method not found'); process.exit(1); }
const body = src.slice(idx, idx + 3000);

const conditions = [
    [/isEqual\(current,\s*parent\)/, 'dirname fixed-point'],
    [/current\.path\s*===\s*'\/'/,   'root path check'],
    [/isEqual\(userHome,\s*parent\)/, 'user home boundary'],
    [/seen\.has\(parent\)/,           'seen-set dedup'],
];

const missing = conditions.filter(([re]) => !re.test(body));
if (missing.length > 0) {
    console.error('FAIL: missing: ' + missing.map(([, n]) => n).join(', '));
    process.exit(1);
}

console.log('PASS:all_conditions_present');
""")
    try:
        r = subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=15, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS:all_conditions_present" in r.stdout


def test_repo_typescript_syntax():
    """Repo's TypeScript syntax is valid (pass_to_pass).

    Uses TypeScript compiler API to parse the target file and verify
    it has no syntax errors. This validates the basic structural
    integrity of the code without requiring full type checking.
    """
    script = Path(REPO) / "_eval_ts_syntax.mjs"
    script.write_text(r"""
import { readFileSync } from 'fs';
import { createSourceFile, ScriptTarget, ScriptKind, SyntaxKind, forEachChild } from 'typescript';

const filePath = 'src/vs/workbench/contrib/chat/common/promptSyntax/utils/promptFilesLocator.ts';
const content = readFileSync(filePath, 'utf8');

// Parse the file
const sourceFile = createSourceFile(
    filePath,
    content,
    ScriptTarget.Latest,
    true,
    ScriptKind.TS
);

// Check for syntax errors by looking for Unknown nodes (typically indicates parse errors)
let hasErrors = false;
function visit(node) {
    if (node.kind === SyntaxKind.Unknown) {
        hasErrors = true;
        console.error(`Syntax error at position ${node.pos}`);
    }
    forEachChild(node, visit);
}
visit(sourceFile);

if (hasErrors) {
    console.error('FAIL: TypeScript syntax errors found');
    process.exit(1);
}

// Verify key structures exist
const src = content;

// Check for class definition
if (!/export\s+class\s+PromptFilesLocator/.test(src)) {
    console.error('FAIL: PromptFilesLocator class not found');
    process.exit(1);
}

// Check for the method
if (!/findParentRepoFolders/.test(src)) {
    console.error('FAIL: findParentRepoFolders method not found');
    process.exit(1);
}

// Verify the while(true) structure exists
if (!/while\s*\(\s*true\s*\)/.test(src)) {
    console.error('FAIL: while(true) loop not found');
    process.exit(1);
}

console.log('PASS: TypeScript syntax valid');
""")
    try:
        r = subprocess.run(
            ["node", "--experimental-strip-types", str(script)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)
    assert r.returncode == 0, f"TypeScript syntax check failed:\n{r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS in output, got:\n{r.stdout}\n{r.stderr}"


def test_repo_file_structure():
    """Repo's chat/promptSyntax module structure is intact (pass_to_pass).

    Verifies that the expected files exist in the expected locations,
    ensuring the module structure is consistent.
    """
    expected_files = [
        "src/vs/workbench/contrib/chat/common/promptSyntax/utils/promptFilesLocator.ts",
        "src/vs/workbench/contrib/chat/test/common/promptSyntax/utils/promptFilesLocator.test.ts",
        "src/vs/workbench/contrib/chat/common/promptSyntax/service/promptsService.ts",
    ]

    for rel_path in expected_files:
        full_path = Path(REPO) / rel_path
        assert full_path.exists(), f"Expected file missing: {rel_path}"

    # Verify the target file has content
    target = Path(REPO) / TARGET
    content = target.read_text()
    assert len(content) > 1000, "Target file seems too small/empty"

    # Check that basic TypeScript constructs are present
    assert "class PromptFilesLocator" in content, "PromptFilesLocator class not found"
    assert "findParentRepoFolders" in content, "findParentRepoFolders method not found"


def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass).

    Runs the mocha-based node.js unit test suite that is part of
    VS Code:'s standard CI pipeline.
    """
    r = subprocess.run(
        ["npm", "run", "test-node"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"


def test_repo_eslint():
    """Repo's ESLint checks pass (pass_to_pass).

    Runs VS Code:'s custom eslint script that checks code style
    and patterns across the codebase.
    """
    r = subprocess.run(
        ["npm", "run", "eslint"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_valid_layers():
    """Repo's layer checks pass (pass_to_pass).

    Runs VS Code:'s valid-layers-check script that validates
    architectural layering constraints in the codebase.
    """
    r = subprocess.run(
        ["npm", "run", "valid-layers-check"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Layer check failed:\n{r.stderr[-500:]}"


def test_repo_typescript_parse():
    """TypeScript files parse correctly (pass_to_pass).

    Uses the TypeScript compiler API directly to parse the target
    file and verify it has no syntax errors.
    """
    script = Path(REPO) / "_eval_ts_parse.mjs"
    script.write_text(r"""
import { readFileSync } from 'fs';
import { createSourceFile, ScriptTarget, ScriptKind, SyntaxKind, forEachChild } from 'typescript';

const filePath = 'src/vs/workbench/contrib/chat/common/promptSyntax/utils/promptFilesLocator.ts';
const content = readFileSync(filePath, 'utf8');

// Parse the file
const sourceFile = createSourceFile(
    filePath,
    content,
    ScriptTarget.Latest,
    true,
    ScriptKind.TS
);

// Check for syntax errors by looking for Unknown nodes
let hasErrors = false;
function visit(node) {
    if (node.kind === SyntaxKind.Unknown) {
        hasErrors = true;
        console.error(`Syntax error at position ${node.pos}`);
    }
    forEachChild(node, visit);
}
visit(sourceFile);

if (hasErrors) {
    console.error('FAIL: TypeScript syntax errors found');
    process.exit(1);
}

console.log('PASS: TypeScript syntax valid');
""")
    try:
        r = subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)
    assert r.returncode == 0, f"TypeScript parse failed:\n{r.stderr}"
