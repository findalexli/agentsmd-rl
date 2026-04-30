"""
Task: bun-partialdeepstrictequal-array-crash
Repo: oven-sh/bun @ e59a147d615a0b95d446c75ba836717cf0dbc513
PR:   28525

Tests rewritten to verify BEHAVIOR, not text:
- Tests execute JavaScript that simulates the bug scenario
- Tests verify the fix pattern (prototype.$call) works on null-prototype Maps
- Tests do NOT hard-code gold-specific variable names
"""

import re
import subprocess
from pathlib import Path

REPO = "/repo"
ASSERT_FILE = Path(REPO) / "src/js/node/assert.ts"


def _read_source():
    src = ASSERT_FILE.read_text()
    stripped = re.sub(r"//[^\n]*", "", src)
    stripped = re.sub(r"/\*[\s\S]*?\*/", "", stripped)
    return src, stripped


def _extract_compare_branch(stripped):
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


# =============================================================================
# BEHAVIORAL TESTS — these actually execute code
# =============================================================================

def test_null_prototype_map_direct_set_throws():
    """
    BEHAVIORAL: Verify that calling .$set directly on a null-prototype Map throws.
    This demonstrates the BUG: SafeMap has null prototype, so .$set/.delete fail.
    """
    r = subprocess.run(
        ["node", "-e", """
'use strict';
const map = new Map();
Object.setPrototypeOf(map, null);
try {
    map.$set('key', 1);
    console.log('FAIL: Expected TypeError but call succeeded');
    process.exit(1);
} catch (e) {
    if (e instanceof TypeError && (e.message.includes('$set') || e.message.includes('set'))) {
        console.log('OK: Direct .$set on null-prototype Map throws TypeError as expected');
        process.exit(0);
    }
    throw e;
}
"""],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, f"Null-prototype .$set throw test failed: {r.stderr}"


def test_null_prototype_map_prototype_call_succeeds():
    """
    BEHAVIORAL: Verify that Map.prototype.set.call() works on a null-prototype Map.
    This demonstrates the FIX: using uncurried prototype methods to bypass null prototype.
    """
    r = subprocess.run(
        ["node", "-e", """
'use strict';
const sizeOf = Object.getOwnPropertyDescriptor(Map.prototype,'size').get;
const map = new Map();
Object.setPrototypeOf(map, null);
Map.prototype.set.call(map, 'key', 1);
const size = sizeOf.call(map);
if (size !== 1) {
    console.error('FAIL: expected size=1, got ' + size);
    process.exit(1);
}
Map.prototype.delete.call(map, 'key');
const sizeAfterDelete = sizeOf.call(map);
if (sizeAfterDelete !== 0) {
    console.error('FAIL: expected size=0 after delete, got ' + sizeAfterDelete);
    process.exit(1);
}
console.log('OK: Prototype-based set/delete works on null-prototype Map');
process.exit(0);
"""],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, f"Prototype call test failed: {r.stderr}"


def test_null_prototype_array_counting_algorithm():
    """
    BEHAVIORAL: Test the full array counting algorithm on null-prototype Map.
    This is the same algorithm compareBranch uses for arrays.
    """
    r = subprocess.run(
        ["node", "-e", """
'use strict';
const sizeOf = Object.getOwnPropertyDescriptor(Map.prototype,'size').get;

function createSafeMap() {
    const map = new Map();
    Object.setPrototypeOf(map, null);
    return map;
}

function compareArrays(actual, expected) {
    const counts = createSafeMap();
    for (const expectedItem of expected) {
        let found = false;
        for (const [key, count] of Map.prototype[Symbol.iterator].call(counts)) {
            if (JSON.stringify(key) === JSON.stringify(expectedItem)) {
                Map.prototype.set.call(counts, key, count + 1);
                found = true;
                break;
            }
        }
        if (!found) {
            Map.prototype.set.call(counts, expectedItem, 1);
        }
    }
    for (const actualItem of actual) {
        for (const [key, count] of Map.prototype[Symbol.iterator].call(counts)) {
            if (JSON.stringify(key) === JSON.stringify(actualItem)) {
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

const cases = [
    [['foo', 'bar'], ['bar', 'foo'], true],
    [['a', 'b', 'c'], ['a', 'b'], true],
    [['a', 'b'], ['a', 'b', 'c'], false],
    [[1, 1, 2], [1, 1, 2], true],
    [[], [[[]]], false],
    [[[1, 2]], [[1, 2]], true],
];

for (const [actual, expected, want] of cases) {
    const got = compareArrays(actual, expected);
    if (got !== want) {
        console.error('FAIL: compareArrays(' + JSON.stringify(actual) + ',' + JSON.stringify(expected) + ')=' + got + ', want ' + want);
        process.exit(1);
    }
}
console.log('OK: Null-prototype array counting algorithm works correctly');
"""],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Array counting algorithm test failed: {r.stderr}"


# =============================================================================
# SOURCE-STRUCTURE TESTS — verify the bug is fixed without coupling to gold names
# =============================================================================

def test_comparebranch_no_direct_instance_methods():
    """
    Verify compareBranch doesn't call .$set/.$delete directly on expectedCounts
    without handling the null-prototype issue (e.g. by restoring the prototype first).
    """
    _, stripped = _read_source()
    fn_body, _ = _extract_compare_branch(stripped)

    has_direct_set = bool(re.search(r"expectedCounts\.\$set\s*\(", fn_body))
    has_direct_delete = bool(re.search(r"expectedCounts\.\$delete\s*\(", fn_body))

    if has_direct_set or has_direct_delete:
        # If direct calls remain, the prototype must be restored first
        has_prototype_restore = bool(re.search(r"setPrototypeOf\s*\(", fn_body))
        assert has_prototype_restore, (
            "Bug not fixed: compareBranch still calls expectedCounts.$set()/$delete() directly "
            "without restoring the prototype. SafeMap has null prototype, causing TypeError."
        )


def test_comparebranch_has_valid_fix_strategy():
    """
    Verify compareBranch uses a valid strategy to handle the null-prototype SafeMap issue.
    Accepts multiple valid approaches:
    - Prototype-based calls (Map.prototype.set.$call or .call)
    - Object.setPrototypeOf to restore the prototype
    - Using a regular Map instead of SafeMap for expectedCounts
    - Using Reflect.apply
    """
    _, stripped = _read_source()
    fn_body, preamble = _extract_compare_branch(stripped)
    full_context = preamble + fn_body

    # Strategy 1: Prototype-based calls (any variable naming convention)
    uses_prototype_call = (
        bool(re.search(r"\.prototype\.(set|delete)", full_context))
        and bool(re.search(r"\.\$?call\s*\(", fn_body))
    )

    # Strategy 2: Restore prototype on the map so direct calls work
    uses_set_prototype = bool(re.search(r"setPrototypeOf\s*\(", fn_body))

    # Strategy 3: Use a regular Map instead of SafeMap for expectedCounts
    uses_regular_map = bool(re.search(r"expectedCounts\s*=\s*new\s+Map\s*\(", fn_body))

    # Strategy 4: Reflect.apply
    uses_reflect = bool(re.search(r"Reflect\s*\.\s*apply", fn_body))

    assert uses_prototype_call or uses_set_prototype or uses_regular_map or uses_reflect, (
        "compareBranch doesn't use any recognized fix for the null-prototype SafeMap issue. "
        "Expected one of: prototype-based calls (e.g. Map.prototype.set.$call), "
        "Object.setPrototypeOf, new Map(), or Reflect.apply."
    )


# =============================================================================
# PASS_TO_PASS TESTS — these verify existing functionality is preserved
# =============================================================================

def test_syntax_check():
    """assert.ts must exist, be parseable, and have sufficient lines."""
    assert ASSERT_FILE.exists(), f"{ASSERT_FILE} does not exist"
    line_count = len(ASSERT_FILE.read_text().splitlines())
    assert line_count >= 400, f"assert.ts only has {line_count} lines (likely stubbed)"
    r = subprocess.run(
        [
            "node",
            "-e",
            "const fs=require('fs');const src=fs.readFileSync(process.argv[1],'utf8');const cleaned=src.replace(/\\0[a-zA-Z0-9_]*/g,'_bun_intrinsic');try{new Function(cleaned);}catch(e){if(/Unexpected token/.test(e.message)||/Unterminated/.test(e.message)){process.exit(1);}}",
            str(ASSERT_FILE),
        ],
        capture_output=True,
        timeout=15,
    )
    assert r.returncode == 0, f"assert.ts has fatal syntax errors: {r.stderr.decode()}"


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


def test_array_branch_preserves_expected_counts_logic():
    """The array comparison branch must still use expectedCounts for counting."""
    _, stripped = _read_source()
    fn_body, _ = _extract_compare_branch(stripped)
    assert "expectedCounts" in fn_body, (
        "expectedCounts variable missing from compareBranch - array logic broken"
    )
    assert re.search(r"for\s*\(\s*const\s+\w+\s+of\s+actual", fn_body), (
        "Missing iteration over 'actual' array in compareBranch"
    )
    assert re.search(r"for\s*\(\s*const\s+\w+\s+of\s+expected", fn_body), (
        "Missing iteration over 'expected' array in compareBranch"
    )


def test_require_string_literals_only():
    """require() calls in src/js/ must use string literals, not dynamic expressions."""
    src, _ = _read_source()
    dynamic_requires = re.findall(r'\brequire\s*\(\s*(?!["\'])\w+', src)
    assert len(dynamic_requires) == 0, (
        f"Found {len(dynamic_requires)} require() calls with non-literal arguments"
    )


def test_editorconfig_compliance():
    r = subprocess.run(
        ["python3", "-c", """
import sys
path = sys.argv[1]
with open(path, 'rb') as f:
    content = f.read()
try:
    content.decode('utf-8')
except UnicodeDecodeError:
    print('FAIL: File is not valid UTF-8')
    sys.exit(1)
if b'\\r\\n' in content:
    print('FAIL: File contains CRLF line endings, use LF only')
    sys.exit(1)
if content and not content.endswith(b'\\n'):
    print('FAIL: File must end with a newline')
    sys.exit(1)
text = content.decode('utf-8')
lines = text.split('\\n')
for i, line in enumerate(lines, 1):
    if i == len(lines) and not line:
        continue
    if line != line.rstrip():
        print(f'FAIL: Line {i} has trailing whitespace')
        sys.exit(1)
print('OK: EditorConfig check passed')
""", str(ASSERT_FILE)],
        capture_output=True,
        text=True,
        timeout=15,
        cwd=REPO,
    )
    assert r.returncode == 0, f"EditorConfig check failed:\n{r.stderr or r.stdout}"


def test_node_syntax_check():
    r = subprocess.run(
        [
            "node",
            "-e",
            "const fs=require('fs');const src=fs.readFileSync(process.argv[1],'utf8').replace(/\\0[a-zA-Z0-9_]*/g,'_bun_intrinsic');let brace=0,paren=0,bracket=0,inString=false,stringChar,escaped=false;for(let i=0;i<src.length;i++){const c=src[i];if(escaped){escaped=false;continue;}if(inString){if(escaped){escaped=false;continue;}if(c==='\\\\'){escaped=true;continue;}if(c===stringChar){inString=false;stringChar=null;}continue;}if(c==='{')brace++;else if(c==='}')brace--;else if(c==='(')paren++;else if(c===')')paren--;else if(c==='[')bracket++;else if(c===']')bracket--;if(brace<0||paren<0||bracket<0){console.error('Syntax error: unexpected closing at position',i);process.exit(1);}}if(brace!==0||paren!==0||bracket!==0){console.error('Syntax error: unbalanced at end');process.exit(1);}console.log('OK: Syntax check passed');",
            str(ASSERT_FILE),
        ],
        capture_output=True,
        text=True,
        timeout=15,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Node.js syntax check failed:\n{r.stderr}"
