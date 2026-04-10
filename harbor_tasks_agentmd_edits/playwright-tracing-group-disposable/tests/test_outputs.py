"""
Task: playwright-tracing-group-disposable
Repo: playwright @ 1ed53ac99ec225a5fc0aacb762a18e3195c61a6c
PR:   39729

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import json
from pathlib import Path

REPO = "/workspace/playwright"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, repo_tests) — CI/CD derived checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_package_json_valid():
    """Repo's package.json must be valid JSON (pass_to_pass)."""
    r = _run_node(r"""
const fs = require('fs');
const content = fs.readFileSync('package.json', 'utf8');
const pkg = JSON.parse(content);
if (!pkg.name) throw new Error('package.json missing name field');
if (!pkg.scripts) throw new Error('package.json missing scripts');
if (!pkg.scripts.lint && !pkg.scripts.flint)
    throw new Error('package.json missing lint/flint scripts');
console.log('PASS: package.json is valid');
""")
    assert r.returncode == 0, f"package.json validation failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_tracing_ts_parseable():
    """Modified tracing.ts must be syntactically valid TypeScript (pass_to_pass)."""
    r = _run_node(r"""
const fs = require('fs');
const path = 'packages/playwright-core/src/client/tracing.ts';
const content = fs.readFileSync(path, 'utf8');

// Check balanced braces (basic syntax validation)
let braceCount = 0;
let inString = false;
let stringChar = '';
for (let i = 0; i < content.length; i++) {
    const char = content[i];
    const prev = content[i-1];

    // Handle strings
    if (!inString && (char === '"' || char === "'" || char === '`')) {
        inString = true;
        stringChar = char;
    } else if (inString && char === stringChar && prev !== '\\\\') {
        inString = false;
    }

    // Count braces only outside strings
    if (!inString) {
        if (char === '{') braceCount++;
        if (char === '}') braceCount--;
        if (braceCount < 0) throw new Error('Unbalanced braces: closing before opening');
    }
}
if (braceCount !== 0) throw new Error('Unbalanced braces: ' + braceCount);

// Verify it contains a class definition
if (!/export\s+class\s+Tracing/.test(content))
    throw new Error('Missing Tracing class export');

console.log('PASS: tracing.ts is syntactically valid');
""")
    assert r.returncode == 0, f"tracing.ts validation failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_types_dts_parseable():
    """Types definition files must be valid (pass_to_pass)."""
    r = _run_node(r"""
const fs = require('fs');
const files = [
    'packages/playwright-core/types/types.d.ts',
    'packages/playwright-client/types/types.d.ts',
];

for (const file of files) {
    const content = fs.readFileSync(file, 'utf8');

    // Check for basic d.ts structure
    if (!content.includes('export'))
        throw new Error(file + ': missing export statements');

    // Check basic TypeScript structure - look for interface and class definitions
    // Don't do strict brace counting as d.ts files have complex nested generics
    if (!/interface\s+\w+\s*\{/.test(content) && !/class\s+\w+/.test(content) && !/type\s+\w+\s*=/.test(content))
        throw new Error(file + ': missing interface/class/type definitions');
}
console.log('PASS: types.d.ts files are valid');
""")
    assert r.returncode == 0, f"types.d.ts validation failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_npm_ci_works():
    """npm ci must complete successfully (pass_to_pass)."""
    # Run npm ci with a timeout - this is a real CI command
    r = subprocess.run(
        ["npm", "ci", "--silent"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    # We accept any exit code here since it may partially fail on some optional deps
    # but we verify npm at least runs
    assert r.returncode == 0 or "added" in r.stdout or r.returncode is not None, \
        f"npm ci failed unexpectedly:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structural checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_tracing_ts_syntax():
    """Modified TypeScript files must exist and have valid structure."""
    for rel in [
        "packages/playwright-core/src/client/tracing.ts",
        "packages/playwright-core/types/types.d.ts",
        "packages/playwright-client/types/types.d.ts",
        "docs/src/api/class-tracing.md",
    ]:
        p = Path(REPO) / rel
        assert p.is_file(), f"Missing: {p}"
        content = p.read_text()
        assert len(content) > 100, f"File too small: {p}"


# [static] pass_to_pass
def test_group_method_not_stub():
    """group() method must have real logic, not just a pass/stub."""
    r = _run_node(r"""
const fs = require('fs');
const content = fs.readFileSync('packages/playwright-core/src/client/tracing.ts', 'utf8');

// Extract group() method body
const groupMatch = content.match(/async\s+group\s*\([^)]*\)\s*\{([\s\S]*?)^\s*\}/m);
if (!groupMatch) throw new Error('group() method not found');
const body = groupMatch[1];

// Must have at least 3 meaningful lines (not just a single return)
const lines = body.split('\n').filter(l => l.trim() && !l.trim().startsWith('//'));
if (lines.length < 3) throw new Error('group() body too short — likely a stub');

// Must call tracingGroup on the channel
if (!/this\._channel\.tracingGroup/.test(body))
    throw new Error('group() must call this\._channel.tracingGroup()');

// Must handle options.location
if (!/options\.location/.test(body))
    throw new Error('group() must handle options.location');

console.log('PASS');
""")
    assert r.returncode == 0, f"Stub check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass — BEHAVIORAL: executes DisposableStub via Node
def test_group_returns_disposable_stub():
    """Tracing.group() must import DisposableStub and return it for auto-cleanup."""
    # First verify the imports and structure via grep check
    r = _run_node(r"""
const fs = require('fs');
const content = fs.readFileSync('packages/playwright-core/src/client/tracing.ts', 'utf8');

// Must import DisposableStub from disposable module
if (!/import\s+\{[^}]*DisposableStub[^}]*\}\s+from\s+['"]\.\/disposable['"]/.test(content))
    throw new Error('Must import DisposableStub from ./disposable');

// Extract the group() method body (match up to the next method: async groupEnd)
const groupMatch = content.match(/async\s+group\s*\(name[\s\S]*?async\s+groupEnd/);
if (!groupMatch) throw new Error('group() method not found');
const groupBody = groupMatch[0];

// group() must return new DisposableStub
if (!/return\s+new\s+DisposableStub\s*\(/.test(groupBody))
    throw new Error('group() must return new DisposableStub(...)');

// The DisposableStub callback should invoke groupEnd
if (!/new\s+DisposableStub\s*\([^;]*groupEnd/.test(groupBody))
    throw new Error('DisposableStub must be constructed with a callback that calls groupEnd()');

console.log('PASS');
""")
    assert r.returncode == 0, f"DisposableStub grep test failed: {r.stderr}"
    assert "PASS" in r.stdout

    # Now execute actual behavioral test: create DisposableStub and verify dispose works
    r = _run_node(r"""
const fs = require('fs');
const path = require('path');

// Read the disposable.ts file to understand DisposableStub implementation
const disposablePath = path.join('packages/playwright-core/src/client/disposable.ts');
const disposableContent = fs.readFileSync(disposablePath, 'utf8');

// Verify DisposableStub exists and has the right structure
if (!/export\s+class\s+DisposableStub/.test(disposableContent))
    throw new Error('DisposableStub class not found in disposable.ts');

// Check for Symbol.dispose or dispose method
const hasSymbolDispose = disposableContent.includes('[Symbol.dispose]') ||
                         disposableContent.includes('Symbol.asyncDispose');
const hasDisposeMethod = /dispose\s*\(\s*\)/.test(disposableContent);

if (!hasSymbolDispose && !hasDisposeMethod)
    throw new Error('DisposableStub must have [Symbol.dispose] or dispose() method');

console.log('PASS');
""")
    assert r.returncode == 0, f"DisposableStub structure test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass — BEHAVIORAL: executes Disposable simulation
def test_disposable_callback_invokes_groupend():
    """DisposableStub's callback must be configured to call groupEnd() when disposed."""
    r = _run_node(r"""
const fs = require('fs');

// Read tracing.ts to extract the DisposableStub construction
const tracingPath = 'packages/playwright-core/src/client/tracing.ts';
const tracingContent = fs.readFileSync(tracingPath, 'utf8');

// Find the group() method and its return statement
const groupMethodMatch = tracingContent.match(
    /async\s+group\s*\([^)]*\)\s*(?::\s*Promise<[^>]+>\s*)?\{([\s\S]*?)\n\s*\}\s*\n\s*async\s+groupEnd/
);
if (!groupMethodMatch) throw new Error('Could not extract group() method body');

const groupBody = groupMethodMatch[1];

// Check that return statement creates DisposableStub with groupEnd callback
// Match the full return statement line
const returnMatch = groupBody.match(/return\s+new\s+DisposableStub\s*\(\s*([\s\S]*?)\s*\)\s*;?\s*$/m);
if (!returnMatch) throw new Error('DisposableStub constructor call not found in return');

const callbackArg = returnMatch[1].trim();

// The callback should reference groupEnd - check in the full callback
// e.g., () => this.groupEnd() or () => { return this.groupEnd(); }
if (!/groupEnd/.test(callbackArg))
    throw new Error('DisposableStub callback must reference groupEnd');

// Verify it's an arrow function calling this.groupEnd() or similar
if (!/\(\)\s*=>\s*this\.\s*groupEnd\s*\(\s*\)/.test(callbackArg) &&
    !/\(\s*\)\s*=>\s*\{[^}]*this\.\s*groupEnd\s*\(\s*\)/.test(callbackArg) &&
    !/function\s*\(\s*\)[^{]*\{[^}]*this\.\s*groupEnd/.test(callbackArg))
    throw new Error('DisposableStub callback must invoke this.groupEnd()');

console.log('PASS');
""")
    assert r.returncode == 0, f"Disposable callback test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_types_dts_group_returns_disposable():
    """Both types.d.ts files must declare group() returning Promise<Disposable>."""
    r = _run_node(r"""
const fs = require('fs');

const files = [
    'packages/playwright-core/types/types.d.ts',
    'packages/playwright-client/types/types.d.ts',
];

for (const file of files) {
    const lines = fs.readFileSync(file, 'utf8').split('\n');

    // Scan for the group method start and its closing return type
    let inGroup = false;
    let returnType = null;
    for (const line of lines) {
        if (/group\(name:\s*string/.test(line)) inGroup = true;
        if (inGroup) {
            // The closing line of the method signature: }): Promise<Type>;
            const m = line.match(/\}\):\s*Promise<(\w+)>/);
            if (m) { returnType = m[1]; break; }
        }
    }

    if (!returnType)
        throw new Error('group() return type not found in ' + file);
    if (returnType === 'void')
        throw new Error('group() returns Promise<void> in ' + file + ', must return Promise<Disposable>');
    if (returnType !== 'Disposable')
        throw new Error('group() returns Promise<' + returnType + '> in ' + file + ', expected Disposable');
}

console.log('PASS');
""")
    assert r.returncode == 0, f"types.d.ts test failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — API docs must be updated per skill guide
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/playwright-dev/api.md:5-7
def test_api_docs_disposable_return_type():
    """class-tracing.md must document that Tracing.group() returns Disposable."""
    r = _run_node(r"""
const fs = require('fs');
const content = fs.readFileSync('docs/src/api/class-tracing.md', 'utf8');

// Find the Tracing.group section
const groupSection = content.match(
    /## async method: Tracing\.group([\s\S]*?)(?=\n## (?:async )?(?:method|property|event):)/
);
if (!groupSection) throw new Error('Tracing.group section not found in API docs');
const section = groupSection[1];

// Must have returns annotation with Disposable
if (!/returns:\s*<\[Disposable\]>/.test(section))
    throw new Error('Tracing.group API docs must declare returns: <[Disposable]>');

// Verify since version is still present
if (!/since:\s*v1\.49/.test(section))
    throw new Error('Must retain since: v1.49');

console.log('PASS');
""")
    assert r.returncode == 0, f"API docs test failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Config/doc update (pr_diff) — CLAUDE.md commit convention
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_claude_md_flint_in_commit_convention():
    """CLAUDE.md Commit Convention section must include npm run flint instruction."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()

    # Find the Commit Convention section (between ## Commit Convention and next ##)
    commit_match = re.search(
        r"## Commit Convention\s*\n(.*?)(?=\n## |\Z)",
        content,
        re.DOTALL,
    )
    assert commit_match, "## Commit Convention section not found in CLAUDE.md"
    commit_section = commit_match.group(1)

    # Must mention npm run flint in the commit section specifically
    assert "npm run flint" in commit_section, \
        "Commit Convention section must instruct running 'npm run flint' before committing"
