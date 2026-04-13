"""
Task: bun-partialdeepstrictequal-array-crash
Repo: oven-sh/bun @ e59a147d615a0b95d446c75ba836717cf0dbc513
PR:   28525

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/repo"
ASSERT_FILE = Path(REPO) / "src/js/node/assert.ts"


def _read_source():
    """Read assert.ts and return comment-stripped content."""
    src = ASSERT_FILE.read_text()
    # Strip single-line and multi-line comments to prevent comment-injection gaming
    stripped = re.sub(r"//[^\n]*", "", src)
    stripped = re.sub(r"/\*[\s\S]*?\*/", "", stripped)
    return src, stripped


def _extract_compare_branch(stripped):
    """Extract the compareBranch function body from stripped source."""
    fn_start = stripped.find("function compareBranch")
    assert fn_start != -1, "compareBranch function not found in assert.ts"
    depth = 0
    started = False
    for i in range(fn_start, len(stripped)):
        if stripped[i] == "{":
            depth += 1
            started = True
        elif stripped[i] == "}":
            depth -= 1
            if started and depth == 0:
                return stripped[fn_start : i + 1], stripped[:fn_start]
    return stripped[fn_start:], stripped[:fn_start]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """assert.ts must exist and parse without fatal syntax errors."""
    assert ASSERT_FILE.exists(), f"{ASSERT_FILE} does not exist"
    line_count = len(ASSERT_FILE.read_text().splitlines())
    assert line_count >= 400, f"assert.ts only has {line_count} lines (likely stubbed)"
    # Syntax check: strip bun $-intrinsics, then parse with Node
    r = subprocess.run(
        [
            "node",
            "-e",
            """
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const cleaned = src.replace(/\\$[a-zA-Z_][a-zA-Z0-9_]*/g, '_bun_intrinsic');
try { new Function(cleaned); } catch(e) {
    if (/Unexpected token/.test(e.message) || /Unterminated/.test(e.message)) {
        process.exit(1);
    }
}
""",
            str(ASSERT_FILE),
        ],
        capture_output=True,
        timeout=15,
    )
    assert r.returncode == 0, f"assert.ts has fatal syntax errors: {r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix verification
# AST-only because: Bun requires full C++ compilation (cmake + zig + llvm),
# cannot be built or executed in the test container.
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_direct_buggy_calls_removed():
    """Direct .$set/.$delete calls on expectedCounts must be removed from compareBranch.
    # AST-only because: Bun cannot be compiled/run in Docker — source inspection only.
    """
    _, stripped = _read_source()
    fn_body, _ = _extract_compare_branch(stripped)
    assert not re.search(
        r"expectedCounts\s*\.\s*\$set\b", fn_body
    ), "Found direct expectedCounts.$set call (the original bug)"
    assert not re.search(
        r"expectedCounts\s*\.\s*\$delete\b", fn_body
    ), "Found direct expectedCounts.$delete call (the original bug)"


# [pr_diff] fail_to_pass
def test_prototype_calls_added():
    """Prototype-based .$call invocations must replace direct map method calls.
    # AST-only because: Bun cannot be compiled/run in Docker — source inspection only.

    The fix must use X.$call(expectedCounts, ...) for set and delete operations,
    with at least 3 such calls (set+1, set init, delete, set-1).
    """
    _, stripped = _read_source()
    fn_body, _ = _extract_compare_branch(stripped)
    proto_calls = re.findall(r"\$(?:call|apply)\s*\(\s*expectedCounts\b", fn_body)
    assert len(proto_calls) >= 3, (
        f"Expected >=3 prototype .$call/$apply(expectedCounts, ...) calls, found {len(proto_calls)}"
    )


# [pr_diff] fail_to_pass
def test_prototype_extraction_available():
    """SafeMap.prototype.set and .delete must be available (extracted or inlined).
    # AST-only because: Bun cannot be compiled/run in Docker — source inspection only.

    The fix either extracts const SafeMapPrototypeSet = SafeMap.prototype.set at
    module scope, or inlines SafeMap.prototype.set.$call(...) in compareBranch.
    """
    _, stripped = _read_source()
    fn_body, before_fn = _extract_compare_branch(stripped)

    # Check for extracted variable pattern
    has_set_extraction = bool(
        re.search(
            r"(?:const|let|var)\s+\w+\s*=\s*(?:SafeMap|Map)\s*\.\s*prototype\s*\.\s*set\b",
            before_fn,
        )
    )
    has_del_extraction = bool(
        re.search(
            r"(?:const|let|var)\s+\w+\s*=\s*(?:SafeMap|Map)\s*\.\s*prototype\s*\.\s*delete\b",
            before_fn,
        )
    )
    # Check for inline pattern
    has_inline_set = bool(
        re.search(
            r"(?:SafeMap|Map)\s*\.\s*prototype\s*\.\s*set\s*\.\s*\$(?:call|apply)\s*\(\s*expectedCounts",
            fn_body,
        )
    )
    has_inline_del = bool(
        re.search(
            r"(?:SafeMap|Map)\s*\.\s*prototype\s*\.\s*delete\s*\.\s*\$(?:call|apply)\s*\(\s*expectedCounts",
            fn_body,
        )
    )
    set_ok = has_set_extraction or has_inline_set
    del_ok = has_del_extraction or has_inline_del
    assert set_ok, "No SafeMap.prototype.set extraction or inline .$call found"
    assert del_ok, "No SafeMap.prototype.delete extraction or inline .$call found"


# ---------------------------------------------------------------------------
# Behavioral simulation — tests the fix PATTERN works (not source inspection)
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_null_proto_map_set_delete():
    """Verify prototype-call pattern works on null-prototype Maps (the fix pattern).

    Creates a null-proto Map (like Bun's SafeMap after makeSafe()), confirms direct
    calls fail, and prototype-based calls succeed for set/delete with varied inputs.
    """
    r = subprocess.run(
        [
            "node",
            "-e",
            """
'use strict';
const sizeOf = Object.getOwnPropertyDescriptor(Map.prototype, 'size').get;
const map = new Map();
Object.setPrototypeOf(map, null);

// Direct calls must fail (this is why the bug exists)
let directFails = false;
try { map.set('a', 1); } catch(e) { directFails = true; }
if (!directFails) { console.error('Direct .set should fail on null-proto Map'); process.exit(1); }

// Prototype calls must work (this is the fix pattern)
// Test with strings
Map.prototype.set.call(map, 'a', 1);
Map.prototype.set.call(map, 'b', 2);
Map.prototype.set.call(map, 'c', 3);
if (sizeOf.call(map) !== 3) { console.error('Expected size 3, got ' + sizeOf.call(map)); process.exit(1); }

// Overwrite
Map.prototype.set.call(map, 'a', 10);
if (Map.prototype.get.call(map, 'a') !== 10) { console.error('Overwrite failed'); process.exit(1); }
if (sizeOf.call(map) !== 3) { console.error('Size changed after overwrite'); process.exit(1); }

// Delete
Map.prototype.delete.call(map, 'b');
if (sizeOf.call(map) !== 2) { console.error('Delete failed, size=' + sizeOf.call(map)); process.exit(1); }

// Test with numbers (like count tracking in compareBranch)
const countMap = new Map();
Object.setPrototypeOf(countMap, null);
Map.prototype.set.call(countMap, 'x', 1);
Map.prototype.set.call(countMap, 'x', Map.prototype.get.call(countMap, 'x') + 1);
if (Map.prototype.get.call(countMap, 'x') !== 2) { console.error('Count increment failed'); process.exit(1); }
Map.prototype.set.call(countMap, 'x', Map.prototype.get.call(countMap, 'x') - 1);
if (Map.prototype.get.call(countMap, 'x') !== 1) { console.error('Count decrement failed'); process.exit(1); }
Map.prototype.delete.call(countMap, 'x');
if (sizeOf.call(countMap) !== 0) { console.error('Final delete failed'); process.exit(1); }

console.log('OK');
""",
        ],
        capture_output=True,
        timeout=10,
    )
    assert r.returncode == 0, f"Null-proto Map simulation failed: {r.stderr.decode()}"


# [pr_diff] pass_to_pass
def test_null_proto_map_counting_pattern():
    """Verify the exact counting pattern used in compareBranch's array comparison.

    Simulates: for each expected item, increment count; for each actual item,
    decrement or delete — the same algorithm as compareBranch.
    """
    r = subprocess.run(
        [
            "node",
            "-e",
            """
'use strict';
const sizeOf = Object.getOwnPropertyDescriptor(Map.prototype, 'size').get;
// Simulate the compareBranch counting pattern for arrays
function testArraySubset(actual, expected) {
    const counts = new Map();
    Object.setPrototypeOf(counts, null);

    // Phase 1: count expected items (like compareBranch does)
    for (const item of expected) {
        let found = false;
        for (const { 0: key, 1: count } of Map.prototype[Symbol.iterator].call(counts)) {
            if (JSON.stringify(key) === JSON.stringify(item)) {
                Map.prototype.set.call(counts, key, count + 1);
                found = true;
                break;
            }
        }
        if (!found) {
            Map.prototype.set.call(counts, item, 1);
        }
    }

    // Phase 2: match actual items, decrement counts
    for (const item of actual) {
        for (const { 0: key, 1: count } of Map.prototype[Symbol.iterator].call(counts)) {
            if (JSON.stringify(key) === JSON.stringify(item)) {
                if (count === 1) {
                    Map.prototype.delete.call(counts, key);
                } else {
                    Map.prototype.set.call(counts, key, count - 1);
                }
                break;
            }
        }
    }
    return sizeOf.call(counts) === 0;
}

// Test cases — varied inputs
const cases = [
    { actual: ['foo'], expected: ['foo'], want: true },
    { actual: ['foo', 'bar', 'baz'], expected: ['foo', 'baz'], want: true },
    { actual: ['foo', 'foo', 'bar'], expected: ['foo', 'foo'], want: true },
    { actual: [1, 2, 3], expected: [2, 3], want: true },
    { actual: ['a'], expected: ['b'], want: false },
    { actual: ['x'], expected: ['x', 'x'], want: false },
    { actual: [1, 2], expected: [1, 2, 3], want: false },
    { actual: [], expected: [], want: true },
];

for (const { actual, expected, want } of cases) {
    const got = testArraySubset(actual, expected);
    if (got !== want) {
        console.error('FAIL: actual=' + JSON.stringify(actual) +
            ' expected=' + JSON.stringify(expected) +
            ' want=' + want + ' got=' + got);
        process.exit(1);
    }
}
console.log('OK: all ' + cases.length + ' cases passed');
""",
        ],
        capture_output=True,
        timeout=10,
    )
    assert r.returncode == 0, f"Counting pattern test failed: {r.stderr.decode()}"
    assert "OK" in r.stdout.decode()


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-deletion
# AST-only because: Bun cannot be compiled/run in Docker — source inspection only.
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_array_branch_preserved():
    """Array comparison branch must still have expectedCounts creation, iteration, and deepEqual.

    Prevents scoring by simply deleting the buggy array branch.
    """
    _, stripped = _read_source()
    fn_body, _ = _extract_compare_branch(stripped)
    assert re.search(
        r"expectedCounts\s*=\s*new\s+(?:SafeMap|Map)", fn_body
    ), "expectedCounts = new SafeMap/Map not found — array branch deleted?"
    assert re.search(
        r"for\s*\(\s*(?:const|let|var)\s+.*?\bof\s+expectedCounts\b", fn_body
    ), "for-of iteration over expectedCounts not found"
    assert "isDeepStrictEqual" in fn_body, "isDeepStrictEqual not found in compareBranch"


# [pr_diff] pass_to_pass
def test_existing_prototype_refs_intact():
    """SafeMapPrototypeHas, SafeMapPrototypeGet, and partialDeepStrictEqual must still exist."""
    _, stripped = _read_source()
    assert re.search(
        r"SafeMap(?:Prototype)?(?:Has|\.prototype\.has)", stripped
    ), "SafeMapPrototypeHas / SafeMap.prototype.has not found"
    assert re.search(
        r"SafeMap(?:Prototype)?(?:Get|\.prototype\.get)", stripped
    ), "SafeMapPrototypeGet / SafeMap.prototype.get not found"
    assert "partialDeepStrictEqual" in stripped, "partialDeepStrictEqual not found"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — src/js/CLAUDE.md:56-65 @ e59a147
def test_dollar_call_convention():
    """New prototype calls must use .$call/$apply, not plain .call/.apply.
    # AST-only because: Bun cannot be compiled/run in Docker — source inspection only.

    Rule: "CRITICAL: Use .$call and .$apply, never .call or .apply" — src/js/CLAUDE.md:56
    """
    _, stripped = _read_source()
    fn_body, _ = _extract_compare_branch(stripped)
    # Must have .$call usage
    proto_calls = re.findall(r"\$(?:call|apply)\s*\(\s*expectedCounts\b", fn_body)
    assert len(proto_calls) > 0, "No .$call/$apply(expectedCounts, ...) calls found"
    # Must NOT have plain .call on expectedCounts (without $ prefix)
    plain_calls = re.findall(r"(?<!\$)\.call\s*\(\s*expectedCounts\b", fn_body)
    assert len(plain_calls) == 0, (
        f"Found {len(plain_calls)} plain .call(expectedCounts, ...) — must use .$call per src/js/CLAUDE.md:56"
    )


# [agent_config] pass_to_pass — src/js/CLAUDE.md:103 @ e59a147
def test_require_string_literals_only():
    """require() calls in src/js/ must use string literals, not dynamic expressions.
    # AST-only because: Bun cannot be compiled/run in Docker — source inspection only.

    Rule: "String literal require() only" — src/js/CLAUDE.md:103
    """
    src, _ = _read_source()
    # Find require() calls that are NOT followed immediately by a string literal
    # Allow: require("..."), require('...'), require(`...`)
    # Disallow: require(someVar), require(getPath()), etc.
    dynamic_requires = re.findall(r'\brequire\s*\(\s*(?!["\'\`])', src)
    assert len(dynamic_requires) == 0, (
        f"Found {len(dynamic_requires)} dynamic require() call(s) — "
        "src/js/ modules must use string literal require() only (src/js/CLAUDE.md:103)"
    )


# [agent_config] pass_to_pass — src/js/CLAUDE.md:15-28 @ e59a147
def test_no_es_module_imports():
    """Modules under src/js/ are NOT ES modules — no import statements (except type imports).
    # AST-only because: Bun cannot be compiled/run in Docker — source inspection only.

    Rule: "Modules are NOT ES modules" — src/js/CLAUDE.md:15
    """
    src, _ = _read_source()
    # Find all import statements that are NOT type-only imports
    # Type imports: import type { Foo } from '...' or import { type Foo } from '...'
    non_type_imports = re.findall(
        r"^import\s+(?!type\b)(?!{[^}]*\btype\b)", src, re.MULTILINE
    )
    assert len(non_type_imports) == 0, (
        f"Found {len(non_type_imports)} non-type import statements — "
        "src/js/ modules must use require(), not import (src/js/CLAUDE.md:15)"
    )


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates — STATIC checks (file reading, not subprocess)
# These use origin: static in eval_manifest.yaml
# ---------------------------------------------------------------------------

# [static] pass_to_pass — adapted from ban-words.test.ts
def test_repo_no_strict_equality_undefined():
    """Repo JS convention: Prefer strict equality (===/!==) over loose (==/!=) for undefined.

    Adapted from ban-words.test.ts which targets Zig code. For JS/TS, we only
    check that strict equality is used, not loose equality.
    # AST-only because: Bun cannot be compiled/run in Docker.
    """
    src, _ = _read_source()
    # Only check for loose equality with undefined (bad practice in JS)
    # Allow: === undefined, !== undefined
    # Avoid: == undefined, != undefined
    loose_patterns = [
        r"(?<![=!])==\s*undefined",  # == undefined but not === undefined
        r"undefined\s*==(?!=)",        # undefined == but not undefined ===
        r"(?<![=!])!=\s*undefined",  # != undefined but not !== undefined
        r"undefined\s*!=(?!=)",        # undefined != but not undefined !==
    ]
    for pattern in loose_patterns:
        matches = re.findall(pattern, src)
        assert len(matches) == 0, (
            f"Found loose equality with undefined in assert.ts — "
            "use === or !== instead (repo JS convention)"
        )


# [static] pass_to_pass — from .github/workflows/format.yml (prettier check)
def test_repo_basic_prettier_format():
    """Repo convention: No trailing whitespace, consistent indentation.

    Basic formatting check that doesn't require prettier CLI.
    Full prettier check requires 'bun' binary which isn't in container.
    # AST-only because: Bun/prettier CLI not available in Docker.
    """
    src_lines = ASSERT_FILE.read_text().splitlines()
    for i, line in enumerate(src_lines, 1):
        # No trailing whitespace
        if line != line.rstrip():
            assert False, f"Line {i} has trailing whitespace — violates repo formatting convention"


# [static] pass_to_pass — from package.json typecheck (partial)
def test_repo_ts_no_bare_intrinsics():
    """TypeScript sanity: Bun $-intrinsics should not appear in final output.

    The fix uses .$call which is a Bun intrinsic. We verify the file
    structure is compatible with Bun's TypeScript processing.
    # AST-only because: Full tsc requires Bun build environment.
    """
    src, stripped = _read_source()
    # Check that $-prefixed identifiers follow Bun conventions
    # They should only be property accesses (.$call, .$set, etc.), not standalone vars
    bare_intrinsics = re.findall(r"\b\$[a-zA-Z_][a-zA-Z0-9_]*\b(?!\[\(\.)", stripped)
    # Filter out property access contexts we already checked
    invalid = [m for m in bare_intrinsics if not re.search(rf"\.{re.escape(m)}\b", stripped)]
    assert len(invalid) == 0, (
        f"Found {len(invalid)} bare $-intrinsics that may cause TypeScript issues"
    )


# [static] pass_to_pass — from .github/workflows/lint.yml (oxlint)
def test_repo_no_debug_log_statements():
    """Lint convention: No debug log statements left in production code.

    Checks for common debug patterns that shouldn't be in committed code.
    # AST-only because: oxlint CLI requires Bun/npm environment.
    """
    src, _ = _read_source()
    debug_patterns = [
        r"console\.log\s*\(",
        r"console\.debug\s*\(",
        r"console\.warn\s*\(",
    ]
    for pattern in debug_patterns:
        matches = re.findall(pattern, src)
        # Allow console.error (used for actual errors) but not log/debug/warn
        if "console.log" in pattern or "console.debug" in pattern or "console.warn" in pattern:
            assert len(matches) == 0, (
                f"Found {len(matches)} {pattern} statements — "
                "remove debug logging before committing (repo lint convention)"
            )


# [static] pass_to_pass — adapted from ban-words.test.ts
def test_repo_no_loose_undefined_equality():
    """Repo convention: No loose equality comparisons with undefined (pass_to_pass).

    Adapted from ban-words.test.ts: '== undefined' and '!= undefined' are banned
    as they can lead to undefined behavior in Zig and bad practice in JS.
    """
    src, _ = _read_source()
    # Check for the exact banned patterns from ban-words.test.ts
    banned_patterns = [
        (" == undefined", "'== undefined' — use '=== undefined'"),
        (" == undefined", "'== undefined' — use '=== undefined'"),
        ("undefined == ", "'undefined ==' — use 'undefined ==='"),
        ("undefined == ", "'undefined ==' — use 'undefined ==='"),
        (" != undefined", "'!= undefined' — use '!== undefined'"),
        (" != undefined", "'!= undefined' — use '!== undefined'"),
        ("undefined != ", "'undefined !=' — use 'undefined !=='"),
        ("undefined != ", "'undefined !=' — use 'undefined !=='"),
    ]
    for pattern, description in banned_patterns:
        if pattern in src:
            # Double check it's not actually === or !== (stricter check)
            stricter_pattern = pattern.replace(" == ", " === ").replace(" ==", " ===").replace("!= ", "!== ").replace("!=", "!==")
            # Search for the exact loose pattern
            idx = src.find(pattern)
            if idx != -1:
                # Get context
                context_start = max(0, idx - 30)
                context_end = min(len(src), idx + len(pattern) + 30)
                context = src[context_start:context_end].replace("\n", " ")
                assert False, (
                    f"Found banned pattern {description} at position {idx}: ...{context}... "
                    f"(from ban-words convention)"
                )


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates — ACTUAL CI COMMANDS (verified working)
# These run real commands from the repo's CI pipeline via subprocess.run()
# origin: repo_tests in eval_manifest.yaml
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — from .github/workflows/lint.yml
def test_repo_oxlint_assert():
    """Repo's oxlint passes on assert.ts (pass_to_pass).

    Runs actual oxlint CLI on src/js/node/assert.ts to verify no lint errors.
    This is the same lint check used in the repo's CI pipeline.
    """
    r = subprocess.run(
        ["npx", "oxlint", str(ASSERT_FILE)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # oxlint returns 0 on success, non-zero if errors found
    # Warnings don't cause non-zero exit by default, only errors
    if r.returncode != 0:
        err_output = r.stdout[-500:] if r.stdout else r.stderr[-500:] if r.stderr else "unknown error"
        assert False, f"oxlint found errors in assert.ts:\n{err_output}"


# [repo_tests] pass_to_pass — from .github/workflows/format.yml
def test_repo_prettier_assert():
    """Repo's prettier formatting check passes on assert.ts (pass_to_pass).

    Runs prettier --check to verify the file follows repo formatting conventions.
    This matches the format check from the repo's autofix.ci workflow.
    """
    r = subprocess.run(
        ["npx", "prettier", "--check", str(ASSERT_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    # prettier --check exits 0 if file is properly formatted
    if r.returncode != 0:
        err_output = r.stderr[-500:] if r.stderr else r.stdout[-500:] if r.stdout else "formatting error"
        assert False, (
            f"Prettier check failed for assert.ts — file does not match repo formatting conventions.\n"
            f"Error: {err_output}\n"
            f"Hint: Run 'npx prettier --write src/js/node/assert.ts' to fix."
        )



# [repo_tests] pass_to_pass — node.js structural syntax check for TypeScript
def test_repo_node_syntax_check():
    """assert.ts has balanced braces/parens - structural syntax check (pass_to_pass).

    Uses Node.js to verify basic TypeScript file structure (balanced brackets, etc).
    This is a lightweight check that doesn't require full TypeScript parsing.
    """
    r = subprocess.run(
        [
            "node",
            "-e",
            """
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
// Check for balanced braces, parens, and brackets (ignoring strings/comments)
let brace = 0, paren = 0, bracket = 0;
let inString = false, stringChar = null, escaped = false;
let inLineComment = false, inBlockComment = false;
for (let i = 0; i < src.length; i++) {
    const c = src[i], next = src[i+1] || '';
    if (!inString && !inBlockComment && c === '/' && next === '/') { inLineComment = true; i++; continue; }
    if (inLineComment && c === '\\n') { inLineComment = false; continue; }
    if (inLineComment) continue;
    if (!inString && !inLineComment && c === '/' && next === '*') { inBlockComment = true; i++; continue; }
    if (inBlockComment && c === '*' && next === '/') { inBlockComment = false; i++; continue; }
    if (inBlockComment) continue;
    if (!inString && (c === "'" || c === '"' || c === '`')) { inString = true; stringChar = c; continue; }
    if (inString) { if (escaped) { escaped = false; continue; } if (c === '\\\\') { escaped = true; continue; } if (c === stringChar) { inString = false; stringChar = null; } continue; }
    if (c === '{') brace++; else if (c === '}') brace--; else if (c === '(') paren++; else if (c === ')') paren--; else if (c === '[') bracket++; else if (c === ']') bracket--;
    if (brace < 0 || paren < 0 || bracket < 0) { console.error('Syntax error: unexpected closing at position', i); process.exit(1); }
}
if (brace !== 0 || paren !== 0 || bracket !== 0) { console.error('Syntax error: unbalanced at end'); process.exit(1); }
console.log('OK: Syntax check passed');
""",
            str(ASSERT_FILE),
        ],
        capture_output=True,
        text=True,
        timeout=15,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Node.js syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass - EditorConfig compliance check (from .editorconfig)
def test_repo_editorconfig_assert():
    """Repo's EditorConfig conventions are followed (pass_to_pass).

    Checks that assert.ts follows the repo's .editorconfig rules:
    - utf-8 encoding
    - lf line endings (no CRLF)
    - final newline at end of file
    - no trailing whitespace
    This is the same type of check used in CI to enforce formatting standards.
    """
    r = subprocess.run(
        [
            "python3",
            "-c",
            """
import sys
path = sys.argv[1]
with open(path, 'rb') as f:
    content = f.read()

# Check UTF-8 encoding (no invalid sequences)
try:
    content.decode('utf-8')
except UnicodeDecodeError:
    print('FAIL: File is not valid UTF-8')
    sys.exit(1)

# Check for CRLF line endings
if b'\\r\\n' in content:
    print('FAIL: File contains CRLF line endings, use LF only')
    sys.exit(1)

# Check for final newline
if content and not content.endswith(b'\\n'):
    print('FAIL: File must end with a newline')
    sys.exit(1)

# Check for trailing whitespace on lines
text = content.decode('utf-8')
lines = text.split('\\n')
for i, line in enumerate(lines, 1):
    # Skip the last empty line after final newline
    if i == len(lines) and not line:
        continue
    if line != line.rstrip():
        print(f'FAIL: Line {i} has trailing whitespace')
        sys.exit(1)

print('OK: EditorConfig check passed')
""",
            str(ASSERT_FILE),
        ],
        capture_output=True,
        text=True,
        timeout=15,
        cwd=REPO,
    )
    assert r.returncode == 0, f"EditorConfig check failed:\n{r.stderr or r.stdout}"
