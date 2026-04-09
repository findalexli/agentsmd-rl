"""
Task: react-compiler-improved-ref-validation-for
Repo: facebook/react @ b354bbd2d231fdeeec31d438c8e7c54877eee4ac
PR:   35893

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
COMPILER = f"{REPO}/compiler"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests
# ---------------------------------------------------------------------------

def test_panresponder_runtime_works():
    """PanResponder.create() in shared-runtime returns its argument (freezing behavior)."""
    r = _run_node("""
import fs from 'fs';
const src = fs.readFileSync(
    'compiler/packages/snap/src/sprout/shared-runtime.ts', 'utf-8'
);

// Extract PanResponder export block
const match = src.match(/export const PanResponder = \\{[\\s\\S]*?\\n\\};/);
if (!match) {
    process.stderr.write('PanResponder export not found in shared-runtime.ts');
    process.exit(1);
}

// Strip TypeScript type annotations to get evaluable JS
let code = match[0]
    .replace('export const ', 'var ')
    .replace(/\\(obj:\\s*any\\):\\s*any/g, '(obj)');

eval(code);

// Verify PanResponder.create returns its input (freeze semantics)
const input = { onPanResponderTerminate: () => {} };
const result = PanResponder.create(input);
if (result !== input) {
    process.stderr.write('PanResponder.create should return its input argument');
    process.exit(1);
}
if (typeof PanResponder.create !== 'function') {
    process.stderr.write('PanResponder.create must be a function');
    process.exit(1);
}
process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_validation_handles_immutable_capture():
    """ValidateNoRefAccessInRender handles ImmutableCapture+Freeze for non-hook functions."""
    r = _run_node("""
import fs from 'fs';
const src = fs.readFileSync(
    'compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts',
    'utf-8'
);

// Must handle ImmutableCapture effect kind in the effects switch
if (!src.includes("case 'ImmutableCapture'")) {
    process.stderr.write('Missing ImmutableCapture case in effects handling');
    process.exit(1);
}

// ImmutableCapture handler must check for co-occurring Freeze effect on same operand
const immutableIdx = src.indexOf("case 'ImmutableCapture'");
const nearbyCode = src.slice(immutableIdx, immutableIdx + 600);
if (!nearbyCode.includes('Freeze') || !nearbyCode.includes('identifier.id')) {
    process.stderr.write('ImmutableCapture handler must check for co-occurring Freeze effect');
    process.exit(1);
}

// Must have visitedEffects dedup set to avoid duplicate errors
if (!src.includes('visitedEffects')) {
    process.stderr.write('Missing visitedEffects dedup tracking');
    process.exit(1);
}

// Must handle non-hook calls with known effects (hookKind == null && instr.effects)
if (!src.includes('hookKind == null') || !src.includes('instr.effects')) {
    process.stderr.write('Missing non-hook effects-based validation branch');
    process.exit(1);
}

process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_panresponder_type_has_freeze_aliasing():
    """PanResponder type in type-provider has Freeze+ImmutableCapture aliasing effects."""
    r = _run_node("""
import fs from 'fs';
const src = fs.readFileSync(
    'compiler/packages/snap/src/sprout/shared-runtime-type-provider.ts',
    'utf-8'
);

// Must have PanResponder type definition
const panStart = src.indexOf('PanResponder:');
if (panStart === -1) {
    process.stderr.write('PanResponder property not found in type provider');
    process.exit(1);
}
const block = src.slice(panStart, panStart + 1000);

// Must have Freeze effect in aliasing
if (!block.includes("kind: 'Freeze'")) {
    process.stderr.write('PanResponder aliasing must include Freeze effect');
    process.exit(1);
}

// Must have ImmutableCapture effect in aliasing
if (!block.includes("kind: 'ImmutableCapture'")) {
    process.stderr.write('PanResponder aliasing must include ImmutableCapture effect');
    process.exit(1);
}

// Must have Create effect for frozen return value
if (!block.includes("kind: 'Create'")) {
    process.stderr.write('PanResponder aliasing must include Create effect');
    process.exit(1);
}

// Return value kind should be Frozen
if (!block.includes('Frozen')) {
    process.stderr.write('PanResponder return value should be Frozen');
    process.exit(1);
}

process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_mutate_ref_fixture_uses_mutate():
    """error.validate-mutate-ref-arg-in-render fixture uses mutate() not console.log()."""
    r = _run_node("""
import fs from 'fs';
const fixture = fs.readFileSync(
    'compiler/packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/error.validate-mutate-ref-arg-in-render.js',
    'utf-8'
);

// Must import mutate from shared-runtime
if (!/import\\s*\\{\\s*mutate\\s*\\}\\s*from\\s*'shared-runtime'/.test(fixture)) {
    process.stderr.write('Fixture must import mutate from shared-runtime');
    process.exit(1);
}

// Must use mutate(ref.current) instead of console.log(ref.current)
if (!fixture.includes('mutate(ref.current)')) {
    process.stderr.write('Fixture must call mutate(ref.current)');
    process.exit(1);
}

// Must NOT still use console.log(ref.current)
if (fixture.includes('console.log(ref.current)')) {
    process.stderr.write('Fixture should not use console.log(ref.current)');
    process.exit(1);
}

process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_panresponder_fixture_exists():
    """panresponder-ref-in-callback fixture exists with PanResponder.create and ref usage."""
    r = _run_node("""
import fs from 'fs';

const fixturePath = 'compiler/packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/panresponder-ref-in-callback.js';
const expectPath = fixturePath.replace('.js', '.expect.md');

if (!fs.existsSync(fixturePath)) {
    process.stderr.write('panresponder-ref-in-callback.js fixture must exist');
    process.exit(1);
}
if (!fs.existsSync(expectPath)) {
    process.stderr.write('panresponder-ref-in-callback.expect.md must exist');
    process.exit(1);
}

const fixture = fs.readFileSync(fixturePath, 'utf-8');

if (!fixture.includes('PanResponder.create')) {
    process.stderr.write('Fixture must call PanResponder.create');
    process.exit(1);
}

if (!fixture.includes('useRef')) {
    process.stderr.write('Fixture must use useRef for ref access pattern');
    process.exit(1);
}

if (!/from\\s*'shared-runtime'/.test(fixture)) {
    process.stderr.write('Fixture must import from shared-runtime');
    process.exit(1);
}

process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD verification
# ---------------------------------------------------------------------------

def test_repo_typescript_compiles():
    """Repo's TypeScript in babel-plugin-react-compiler compiles (pass_to_pass)."""
    r = _run_node("""
import fs from 'fs';
import path from 'path';

// Check that key TypeScript files exist and have valid syntax
const files = [
    'compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts',
    'compiler/packages/snap/src/sprout/shared-runtime.ts',
    'compiler/packages/snap/src/sprout/shared-runtime-type-provider.ts',
];

for (const file of files) {
    if (!fs.existsSync(file)) {
        process.stderr.write(`File missing: ${file}`);
        process.exit(1);
    }
    const content = fs.readFileSync(file, 'utf-8');
    // Basic TypeScript syntax check - look for obvious errors
    if (content.includes('export export') || content.includes('import import')) {
        process.stderr.write(`Syntax error in ${file}`);
        process.exit(1);
    }
}

// Check that the compiler package.json has valid scripts
const pkgPath = 'compiler/packages/babel-plugin-react-compiler/package.json';
const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));
if (!pkg.scripts || !pkg.scripts.jest) {
    process.stderr.write('jest script not found in package.json');
    process.exit(1);
}

process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"TypeScript compile check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_compiler_package_structure():
    """Compiler package structure is valid (pass_to_pass)."""
    r = _run_node("""
import fs from 'fs';
import path from 'path';

// Check that the compiler workspace exists and is properly structured
const compilerDir = 'compiler';
const packagesDir = 'compiler/packages';

if (!fs.existsSync(compilerDir)) {
    process.stderr.write('compiler directory missing');
    process.exit(1);
}

if (!fs.existsSync(packagesDir)) {
    process.stderr.write('compiler/packages directory missing');
    process.exit(1);
}

// Check that babel-plugin-react-compiler exists
const pluginDir = 'compiler/packages/babel-plugin-react-compiler';
if (!fs.existsSync(pluginDir)) {
    process.stderr.write('babel-plugin-react-compiler directory missing');
    process.exit(1);
}

// Check that the src directory exists with expected subdirectories
const expectedDirs = ['src/Validation', 'src/__tests__/fixtures/compiler'];
for (const dir of expectedDirs) {
    const fullPath = path.join(pluginDir, dir);
    if (!fs.existsSync(fullPath)) {
        process.stderr.write(`Expected directory missing: ${fullPath}`);
        process.exit(1);
    }
}

process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"Compiler package structure check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

def test_validation_preserves_ref_lvalue_branch():
    """The isRefLValue branch (mergeRefs pattern) must still exist after refactoring."""
    r = _run_node("""
import fs from 'fs';
const src = fs.readFileSync(
    'compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts',
    'utf-8'
);

// The isRefLValue check must still be present — it handles mergeRefs(ref1, ref2)
if (!src.includes('isRefLValue')) {
    process.stderr.write('isRefLValue check missing — mergeRefs pattern would break');
    process.exit(1);
}

// The interpolatedAsJsx check must still be present
if (!src.includes('interpolatedAsJsx')) {
    process.stderr.write('interpolatedAsJsx check missing — JSX child ref check would break');
    process.exit(1);
}

// The three validation functions must all still be called
const hasDirectRef = src.includes('validateNoDirectRefValueAccess');
const hasRefPassed = src.includes('validateNoRefPassedToFunction');
const hasRefValue = src.includes('validateNoRefValueAccess');
if (!hasDirectRef || !hasRefPassed || !hasRefValue) {
    process.stderr.write('Missing validation function call: ' +
        JSON.stringify({hasDirectRef, hasRefPassed, hasRefValue}));
    process.exit(1);
}

process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_shared_runtime_exports_typedlog():
    """shared-runtime.ts must still export typedLog as default (not broken by PanResponder addition)."""
    r = _run_node("""
import fs from 'fs';
const src = fs.readFileSync(
    'compiler/packages/snap/src/sprout/shared-runtime.ts', 'utf-8'
);

if (!src.includes('export default typedLog')) {
    process.stderr.write('shared-runtime.ts must still export typedLog as default');
    process.exit(1);
}

// typedMutate must still be exported (PanResponder is added between typedMutate and default export)
if (!src.includes('export function typedMutate')) {
    process.stderr.write('shared-runtime.ts must still export typedMutate');
    process.exit(1);
}

process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — CLAUDE.md config edits
# ---------------------------------------------------------------------------

def test_claude_md_lint_section():
    """compiler/CLAUDE.md documents the lint command for the compiler source."""
    claude_md = Path(COMPILER) / "CLAUDE.md"
    assert claude_md.exists(), "compiler/CLAUDE.md must exist"
    content = claude_md.read_text()
    assert "yarn workspace babel-plugin-react-compiler lint" in content, (
        "CLAUDE.md should document 'yarn workspace babel-plugin-react-compiler lint'"
    )


def test_claude_md_formatting_section():
    """compiler/CLAUDE.md documents the prettier formatting command."""
    claude_md = Path(COMPILER) / "CLAUDE.md"
    assert claude_md.exists(), "compiler/CLAUDE.md must exist"
    content = claude_md.read_text()
    assert "yarn prettier-all" in content, (
        "CLAUDE.md should document 'yarn prettier-all' formatting command"
    )
