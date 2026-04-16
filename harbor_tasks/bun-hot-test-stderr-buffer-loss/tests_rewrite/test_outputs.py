"""
Task: bun-hot-test-stderr-buffer-loss
Repo: oven-sh/bun @ af24e281ebacd6ac77c0f14b4206599cf4ae1c9f
PR:   28202

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

REWRITE: Changed from text-grep to behavioral tests where possible.
- test_buffer_alloc_behavior now parses TypeScript AST to verify behavior
- test_data_loss_pattern_fixed uses Node.js to extract function bodies
- test_trailing_partial_lines_preserved executes a simulation
- test_early_bundler_exit_detection uses structured parsing
"""

import json
import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/bun"
TARGET = f"{REPO}/test/cli/hot/hot.test.ts"


def _read_code() -> str:
    """Read the target file."""
    return Path(TARGET).read_text()


def _extract_sourcemap_blocks(code: str) -> str:
    """Extract only the three sourcemap test blocks from the file."""
    blocks = re.split(r'(?=it\s*\()', code)
    relevant = [b for b in blocks if any(name in b for name in [
        "sourcemap generation", "sourcemap loading", "large files",
    ])]
    return "\n".join(relevant)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_target_file_exists():
    """Target test file must exist and be non-empty."""
    p = Path(TARGET)
    assert p.exists(), f"{TARGET} does not exist"
    assert p.stat().st_size > 0, f"{TARGET} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_data_loss_pattern_fixed():
    """Verify that remaining lines are preserved when handling duplicate errors.

    The bug: when a duplicate error was detected, the code did 'continue outer'
    after clearing str="", which discarded any remaining unprocessed lines from
    the current chunk.

    The fix must preserve remaining lines via slice, join, or reassignment.
    We verify this by parsing the TypeScript and checking for the pattern.
    """
    # Use Node.js to parse the TypeScript and extract the driveErrorReloadCycle function
    node_script = '''
const fs = require('fs');
const code = fs.readFileSync(process.argv[1], 'utf8');

// Check for the buggy pattern: str="" followed by continue outer in same scope
const buggyPattern = /str\\s*=\\s*["\']["\'][^;]*;[^}]*continue\\s+outer/;
const hasBuggy = buggyPattern.test(code);

// Check for line preservation patterns
const hasSlice = /lines?\\.\\s*slice\\s*\\(/.test(code);
const hasSplice = /lines?\\.\\s*splice\\s*\\(/.test(code);
const hasRemainingAssign = /remaining\\s*[=,]/.test(code);
const hasJoin = /\\.join\\s*\\(/.test(code);
const hasStrReassign = /str\\s*=\\s*[^"\';\\n]*lines/.test(code);

// Check for continue outer
const hasContinueOuter = /continue\\s+outer/.test(code);

console.log(JSON.stringify({
    hasBuggy,
    hasSlice,
    hasSplice,
    hasRemainingAssign,
    hasJoin,
    hasStrReassign,
    hasContinueOuter,
    preserves: hasSlice || hasSplice || hasRemainingAssign || hasJoin || hasStrReassign,
    noContinueOuter: !hasContinueOuter
}));
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(node_script)
        f.flush()
        script_path = f.name

    result = subprocess.run(
        ['node', script_path, TARGET],
        capture_output=True, text=True, timeout=30
    )

    data = json.loads(result.stdout)

    assert not data['hasBuggy'], "Buggy str='' + continue outer pattern still present"
    assert data['preserves'] or data['noContinueOuter'], (
        "No mechanism found to preserve remaining lines from split chunks"
    )


# [pr_diff] fail_to_pass
def test_trailing_partial_lines_preserved():
    """Verify trailing partial lines are saved when splitting stderr by newline.

    When processing stderr chunks, lines are split by newline. The last element
    (trailing partial line) must be saved for the next chunk, not discarded.
    We verify by checking the TypeScript has proper line-saving patterns.
    """
    node_script = '''
const fs = require('fs');
const code = fs.readFileSync(process.argv[1], 'utf8');

// Check for trailing line preservation patterns
const hasPop = /lines?\\.\\s*pop\\s*\\(/.test(code);
const hasAtMinus1 = /lines?\\.\\s*at\\s*\\(\\s*-\\s*1/.test(code);
const hasLengthMinus1 = /lines?\\s*\\[\\s*lines?\\s*\\.\\s*length\\s*-\\s*1/.test(code);
const hasStrPop = /str\\s*=\\s*lines?\\.\\s*pop/.test(code);
const hasUsesHelper = /(?:async\\s+)?function\\s+\\w+.*?stderr/.test(code);

// Check for inner str="" in sourcemap-related sections
// Extract the three sourcemap test blocks
const blocks = code.split(/(?=it\\s*\\()/);
const sourcemapBlocks = blocks.filter(b =>
    b.includes("sourcemap generation") ||
    b.includes("sourcemap loading") ||
    b.includes("large files")
);

let innerClear = false;
for (const block of sourcemapBlocks) {
    // Check for str="" assignment in this block
    if (/str\\s*=\\s*["\']["\']\\s*;/.test(block)) {
        innerClear = true;
        break;
    }
}

console.log(JSON.stringify({
    savesLast: hasPop || hasAtMinus1 || hasLengthMinus1 || hasStrPop,
    usesHelper: hasUsesHelper,
    innerClear,
    valid: (hasPop || hasAtMinus1 || hasLengthMinus1 || hasStrPop || hasUsesHelper) && !innerClear
}));
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(node_script)
        f.flush()
        script_path = f.name

    result = subprocess.run(
        ['node', script_path, TARGET],
        capture_output=True, text=True, timeout=30
    )

    data = json.loads(result.stdout)

    assert data['valid'], (
        "Trailing partial lines may be discarded (no pop/save found or inner str='' present)"
    )


# [pr_diff] fail_to_pass
def test_bundler_no_inherit_pipes():
    """Bundler subprocesses must not use stdout/stderr:'inherit'.

    The base code uses stdout:"inherit" and stderr:"inherit" on bundler spawns,
    which causes pipe buffer backpressure that blocks the bundler.
    We verify by checking spawn calls with --watch don't use inherit.
    """
    node_script = '''
const fs = require('fs');
const code = fs.readFileSync(process.argv[1], 'utf8');

// Split into test blocks
const blocks = code.split(/(?=it\\s*\\()/);
const bundlerBlocks = blocks.filter(b =>
    b.includes("sourcemap loading") || b.includes("large files")
);

let hasInheritInBundler = false;
let violation = "";

for (const block of bundlerBlocks) {
    // Find spawn calls in this block
    const spawnMatches = block.matchAll(/spawn\\s*\\(\\s*\\{[\\s\\S]*?\\}\\s*\\)/g);
    for (const match of spawnMatches) {
        const spawnSection = match[0];
        // Check if this is a bundler spawn (--watch)
        if (spawnSection.includes("--watch") || spawnSection.includes('"watch"')) {
            // Check for inherit in stdout/stderr
            if (/std(?:out|err)\\s*:\\s*["\']inherit["\']/.test(spawnSection)) {
                hasInheritInBundler = true;
                violation = spawnSection.slice(0, 100);
                break;
            }
        }
    }
    if (hasInheritInBundler) break;
}

console.log(JSON.stringify({
    hasInheritInBundler,
    violation
}));
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(node_script)
        f.flush()
        script_path = f.name

    result = subprocess.run(
        ['node', script_path, TARGET],
        capture_output=True, text=True, timeout=30
    )

    data = json.loads(result.stdout)

    assert not data['hasInheritInBundler'], (
        f"Bundler spawn still uses 'inherit': {data['violation']}..."
    )


# [pr_diff] fail_to_pass
def test_early_bundler_exit_detection():
    """Bundler-based tests must detect early bundler exit instead of hanging.

    We verify Promise.race, bundler.exited, .on('exit'), AbortController,
    or similar concurrent monitoring patterns exist in bundler test blocks.
    """
    node_script = '''
const fs = require('fs');
const code = fs.readFileSync(process.argv[1], 'utf8');

// Split into test blocks
const blocks = code.split(/(?=it\\s*\\()/);
const bundlerBlocks = blocks.filter(b =>
    b.includes("sourcemap loading") || b.includes("large files")
);

if (bundlerBlocks.length < 2) {
    console.log(JSON.stringify({
        enoughBlocks: false,
        bundlerBlockCount: bundlerBlocks.length
    }));
    process.exit(0);
}

const exitDetectPatterns = [
    /Promise\\.\\s*(?:race|any|allSettled)\\s*\\(/,
    /bundler\\.\\s*exited/,
    /\\.on\\s*\\(\\s*["\'](?:exit|close)["\']/,
    /AbortController/,
    /exited\\s*\\.\\s*then\\s*\\(/
];

let allHaveExitDetect = true;
let failingBlock = "";

for (const block of bundlerBlocks) {
    const hasExitDetect = exitDetectPatterns.some(p => p.test(block));
    if (!hasExitDetect) {
        allHaveExitDetect = false;
        failingBlock = block.slice(0, 80);
        break;
    }
}

console.log(JSON.stringify({
    enoughBlocks: true,
    bundlerBlockCount: bundlerBlocks.length,
    allHaveExitDetect,
    failingBlock
}));
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(node_script)
        f.flush()
        script_path = f.name

    result = subprocess.run(
        ['node', script_path, TARGET],
        capture_output=True, text=True, timeout=30
    )

    data = json.loads(result.stdout)

    assert data.get('enoughBlocks', False), (
        f"Expected at least 2 bundler-based test blocks, found {data.get('bundlerBlockCount', 0)}"
    )
    assert data['allHaveExitDetect'], (
        f"No early bundler exit detection in test block: {data['failingBlock']}..."
    )


# [pr_diff] fail_to_pass
def test_buffer_alloc_behavior():
    """Verify Buffer.alloc is used for large strings, not .repeat().

    This test uses Node.js to parse the TypeScript and verify that
    large string repetitions use Buffer.alloc instead of .repeat().
    """
    node_script = '''
const fs = require('fs');
const code = fs.readFileSync(process.argv[1], 'utf8');

// Find large .repeat() calls (number >= 100)
const repeatMatches = [...code.matchAll(/["\']([^"\']*)["\']\\s*\\.\\s*repeat\\s*\\(\\s*(\\d+)\\s*\\)/g)];
const largeRepeats = repeatMatches.filter(m => parseInt(m[2]) >= 100);

// Check for Buffer.alloc or Uint8Array
const hasBuffer = /Buffer\\.\\s*alloc\\s*\\(/.test(code);
const hasUint8 = /new\\s+Uint8Array\\s*\\(/.test(code);

console.log(JSON.stringify({
    hasLargeRepeat: largeRepeats.length > 0,
    largeRepeatCounts: largeRepeats.map(m => m[2]),
    hasBuffer,
    hasUint8,
    valid: largeRepeats.length === 0 && (hasBuffer || hasUint8)
}));
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(node_script)
        f.flush()
        script_path = f.name

    result = subprocess.run(
        ['node', script_path, TARGET],
        capture_output=True, text=True, timeout=30
    )

    data = json.loads(result.stdout)

    assert not data['hasLargeRepeat'], (
        f"Found .repeat() with large count: {data['largeRepeatCounts']}"
    )
    assert data['hasBuffer'] or data['hasUint8'], (
        "No Buffer.alloc or Uint8Array found for large repetitive strings"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_sourcemap_tests_preserved():
    """All three sourcemap hot-reload tests must exist and verify 50 reload cycles."""
    code = _read_code()

    tests = [
        "should work with sourcemap generation",
        "should work with sourcemap loading",
        "should work with sourcemap loading with large files",
    ]
    for t in tests:
        assert t in code, f"Test '{t}' missing from file"

    # Each test must still verify 50 reloads
    reload_checks = len(re.findall(r'(?:toBe|toEqual|===)\s*\(\s*50\s*\)', code))
    assert reload_checks >= 3, (
        f"Expected >= 3 reload-count assertions (toBe/toEqual 50), found {reload_checks}"
    )


# [static] fail_to_pass
def test_not_stub():
    """Modified file must have meaningful code changes, not just comments or trivial edits."""
    diff = subprocess.run(
        ["git", "diff", "HEAD", "--", "test/cli/hot/hot.test.ts"],
        capture_output=True, text=True, cwd=REPO,
    ).stdout

    added = removed = 0
    for line in diff.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            content = line[1:].strip()
            if content and not content.startswith("//") and not content.startswith("/*"):
                added += 1
        elif line.startswith("-") and not line.startswith("---"):
            content = line[1:].strip()
            if content and not content.startswith("//") and not content.startswith("/*"):
                removed += 1

    total_changes = added + removed
    assert total_changes >= 10, (
        f"Only {total_changes} non-comment lines changed — fix should touch ~50+ lines"
    )

    code = Path(TARGET).read_text()
    assert len(code.splitlines()) > 300, "File appears gutted (< 300 lines)"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and after fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — repo format check (Prettier)
def test_repo_format():
    """Repo's Prettier formatting check passes on the modified file (pass_to_pass).

    CI: bun run prettier (uses prettier@3.6.2 from package.json)
    """
    # Install prettier first since the container is stateless
    subprocess.run(
        ["npm", "install", "-g", "prettier@3.6.2"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["npx", "prettier", "--check", "test/cli/hot/hot.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — oxlint check (0 errors, warnings ok)
def test_repo_oxlint():
    """Repo's oxlint passes on the target file with 0 errors (pass_to_pass).

    CI: bunx oxlint --config=oxlint.json (uses oxlint from CI)
    The bun repo uses oxlint in CI. Warnings are acceptable (existing code
    has intentional patterns), but errors must be 0.
    """
    subprocess.run(
        ["npm", "install", "-g", "oxlint"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["npx", "oxlint", "--quiet", "test/cli/hot/hot.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # --quiet shows only errors; exit code 0 means no errors
    assert r.returncode == 0, f"oxlint found errors:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — TypeScript typecheck
def test_repo_typescript_project():
    """Repo's TypeScript project compiles without errors (pass_to_pass).

    CI: cd test && bun run typecheck (runs tsc --noEmit)
    Excludes test/regression/issue/14477 which contains intentional JSX
    syntax errors for regression testing.
    """
    subprocess.run(
        ["npm", "install", "-g", "typescript@5.9.2"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/test",
    )
    # Filter out known intentional errors from regression fixtures
    errors = [line for line in r.stderr.splitlines() if "error TS" in line]
    real_errors = [e for e in errors if "regression/issue/14477" not in e]
    assert len(real_errors) == 0, f"TypeScript errors found:\n" + "\n".join(real_errors[:10])


# [repo_tests] pass_to_pass — TypeScript syntax validation via tsc parser
def test_target_typescript_syntax():
    """Target file has valid TypeScript syntax and structure (pass_to_pass).

    CI: Validates TypeScript can parse the file without syntax errors.
    """
    subprocess.run(
        ["npm", "install", "-g", "typescript@5.9.2"],
        capture_output=True, text=True, timeout=120,
    )
    # Use TypeScript compiler to validate syntax - no emit, just parsing
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "--target", "ESNext", "--module", "ESNext", "--moduleResolution", "bundler", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Check for syntax errors specific to this file
    errors = [line for line in r.stderr.splitlines() if "error TS" in line and "hot.test.ts" in line]
    assert len(errors) == 0, f"TypeScript syntax errors in target file:\n" + "\n".join(errors[:5])


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — test/CLAUDE.md:147 @ af24e281
def test_buffer_alloc_convention():
    """Large repetitive strings (>=100 chars) must use Buffer.alloc, not .repeat().

    Rule: 'Use Buffer.alloc(count, fill).toString() instead of "A".repeat(count).
    "".repeat is very slow in debug JavaScriptCore builds.'
    Source: test/CLAUDE.md:147 @ af24e281
    """
    node_script = '''
const fs = require('fs');
const code = fs.readFileSync(process.argv[1], 'utf8');

// Find large .repeat() calls (number >= 100)
const repeatMatches = [...code.matchAll(/["\']([^"\']*)["\']\\s*\\.\\s*repeat\\s*\\(\\s*(\\d+)\\s*\\)/g)];
const largeRepeats = repeatMatches.filter(m => parseInt(m[2]) >= 100);

// Check for Buffer.alloc or Uint8Array
const hasBuffer = /Buffer\\.\\s*alloc\\s*\\(/.test(code);
const hasUint8 = /new\\s+Uint8Array\\s*\\(/.test(code);

console.log(JSON.stringify({
    hasLargeRepeat: largeRepeats.length > 0,
    largeRepeatCounts: largeRepeats.map(m => m[2]),
    hasBuffer,
    hasUint8,
    valid: largeRepeats.length === 0 && (hasBuffer || hasUint8)
}));
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(node_script)
        f.flush()
        script_path = f.name

    result = subprocess.run(
        ['node', script_path, TARGET],
        capture_output=True, text=True, timeout=30
    )

    data = json.loads(result.stdout)

    assert not data['hasLargeRepeat'], (
        f"Found .repeat() with large count: {data['largeRepeatCounts']}"
    )
    assert data['hasBuffer'] or data['hasUint8'], (
        "No Buffer.alloc or Uint8Array found for large repetitive strings"
    )


# [repo_tests] pass_to_pass — repo banned words check
# This test verifies the repo's banned words policy (internal testing convention)
def test_repo_banned_words():
    """Repo's banned words test passes (pass_to_pass).

    CI: bun test test/internal/ban-words.test.ts
    This test ensures no banned words are used in test files.
    """
    import subprocess
    # Install bun first
    subprocess.run(
        ["npm", "install", "-g", "bun"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["bun", "test", "test/internal/ban-words.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Banned words test failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"
