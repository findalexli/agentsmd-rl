"""
Tests for storybookjs/storybook PR #34274: Builder-Vite djb2 hash fix.

The bug: The naive hash function (char-code sum) produces the same hash for
anagrams, causing variable name collisions ("preview_XXXX") when pnpm's peer
dependency paths include hex suffixes.

The fix: Replace with djb2 hash that incorporates character position.
"""

import subprocess
import sys
import os
import tempfile
import json

REPO = "/workspace/storybook"
TARGET_FILE = "code/builders/builder-vite/src/codegen-project-annotations.ts"

def extract_hash_body(content):
    """
    Extract the hash function body by matching braces.
    Returns (success, body_or_error_message)
    """
    # Find the function start
    func_start = content.find('function hash(value: string)')
    if func_start == -1:
        return False, 'HASH_NOT_FOUND'

    # Find the opening brace after function signature
    brace_start = content.find('{', func_start)
    if brace_start == -1:
        return False, 'NO_BRACE'

    # Count braces to find matching closing brace
    brace_count = 1
    pos = brace_start + 1
    while pos < len(content) and brace_count > 0:
        if content[pos] == '{':
            brace_count += 1
        elif content[pos] == '}':
            brace_count -= 1
        pos += 1

    if brace_count != 0:
        return False, 'BRACE_MISMATCH'

    hash_body = content[brace_start + 1:pos - 1]
    return True, hash_body.strip()

def run_node_test(test_script):
    """Run node test script and return stdout."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(test_script)
        script_path = f.name
    try:
        r = subprocess.run(
            ["node", script_path],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30
        )
        return r.stdout.strip(), r.stderr
    finally:
        os.unlink(script_path)

def test_hash_function_exists():
    """The hash function is defined in the target file."""
    path = os.path.join(REPO, TARGET_FILE)
    with open(path) as f:
        content = f.read()
    assert "function hash" in content, f"hash function not found in {TARGET_FILE}"

def test_hash_anagrams_distinct_djb2():
    """
    djb2 hash produces different values for anagrams (fail-to-pass).
    The old naive hash (char-code sum) gives identical hashes for
    "abc" and "cba" (both = 294), but djb2 must distinguish them.
    """
    path = os.path.join(REPO, TARGET_FILE)
    with open(path) as f:
        content = f.read()

    success, result = extract_hash_body(content)
    if not success:
        assert False, f"Failed to extract hash body: {result}"

    script = """
const hashBody = %s;

// Old naive hash for comparison
function naiveHash(value) {
  return value.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
}

const abc = 'abc';
const cba = 'cba';

console.log('NAIVE_ABC:' + naiveHash(abc));
console.log('NAIVE_CBA:' + naiveHash(cba));
console.log('NAIVE_COLLISION:' + (naiveHash(abc) === naiveHash(cba)));

// Run the actual hash function
const actualHash = new Function('value', hashBody);
console.log('ACTUAL_ABC:' + actualHash(abc));
console.log('ACTUAL_CBA:' + actualHash(cba));
console.log('ACTUAL_COLLISION:' + (actualHash(abc) === actualHash(cba)));
""" % json.dumps(result)

    output, stderr = run_node_test(script)
    assert "HASH_NOT_FOUND" not in output, f"Hash function not found: {output}"

    # The old hash has collision
    assert "NAIVE_COLLISION:true" in output, f"Expected naive hash collision for anagrams, got: {output}"

    # The actual hash should NOT have collision (proving djb2 was implemented)
    assert "ACTUAL_COLLISION:false" in output, \
        f"Hash function still produces collisions for anagrams - djb2 not implemented correctly. Output: {output}"

def test_hash_string_with_position_sensitivity():
    """
    The hash function must be position-sensitive, not just character-sum.
    If the function only sums char codes, "abc", "bca", and "cab" would have the
    same hash. With djb2 they are all different.
    """
    path = os.path.join(REPO, TARGET_FILE)
    with open(path) as f:
        content = f.read()

    success, result = extract_hash_body(content)
    if not success:
        assert False, f"Failed to extract hash body: {result}"

    script = """
const hashBody = %s;

const actualHash = new Function('value', hashBody);

const s1 = 'abc';
const s2 = 'bca';
const s3 = 'cab';

const h1 = actualHash(s1);
const h2 = actualHash(s2);
const h3 = actualHash(s3);

console.log('H1:' + h1);
console.log('H2:' + h2);
console.log('H3:' + h3);

// All three must be different if position-sensitive
const allDifferent = (h1 !== h2) && (h2 !== h3) && (h1 !== h3);
console.log('ALL_DIFFERENT:' + allDifferent);
""" % json.dumps(result)

    output, stderr = run_node_test(script)
    assert "HASH_NOT_FOUND" not in output, f"Hash function not found: {output}"

    lines = {l.split(':')[0]: l.split(':')[1] for l in output.split('\n') if ':' in l}
    h1, h2, h3 = int(lines['H1']), int(lines['H2']), int(lines['H3'])

    # All three must be different (if using naive sum, they'd all be 294)
    assert h1 != h2 and h2 != h3 and h1 != h3, \
        f"Hash is not position-sensitive. All three anagrams produce same/similar hash: {h1}, {h2}, {h3}"

def test_hash_no_collisions_across_diverse_strings():
    """
    The hash must produce zero collisions across a diverse set of strings
    including: anagram clusters, single characters, short strings, long paths,
    and pnpm-style paths with hex suffixes.

    This is a behavioral test — it verifies collision-free output regardless
    of the specific algorithm used (djb2, FNV, etc.).
    """
    path = os.path.join(REPO, TARGET_FILE)
    with open(path) as f:
        content = f.read()

    success, result = extract_hash_body(content)
    if not success:
        assert False, f"Failed to extract hash body: {result}"

    script = """
const hashBody = %s;
const actualHash = new Function('value', hashBody);

// Diverse set of strings: anagrams, single chars, short/long, pnpm paths, hex suffixes
const testStrings = [
  // Anagram cluster: 3-char
  'abc', 'bca', 'cab', 'cba', 'bac', 'acb',
  // Anagram cluster: 4-char
  'abcd', 'bcda', 'cdab', 'dabc',
  // Single chars
  'a', 'b', 'c', 'x', 'z',
  // Empty string
  '',
  // Short strings
  'hi', 'ih', 'ab', 'ba',
  // pnpm-style paths
  '/node_modules/.pnpm/react@21.0.0+abc/node_modules/react',
  '/node_modules/.pnpm/react@21.0.0+cba/node_modules/react',
  '/node_modules/.pnpm/react@21.0.0+123/node_modules/react',
  '/node_modules/.pnpm/react@21.0.0+321/node_modules/react',
  // More hex-suffix variants
  'pkg@1.0.0+aaa/node_modules/pkg',
  'pkg@1.0.0+bbb/node_modules/pkg',
  'pkg@1.0.0+abc/node_modules/pkg',
  'pkg@1.0.0+def/node_modules/pkg',
  // Long path segments
  'long-package-name-with-many-chars-and-subdirs',
  'LongPackageNameWithManyCharsAndSubdirs',
  'LONG_PACKAGE_NAME_WITH_UNDERSCORES',
  // Numeric-ish strings
  '123', '321', '132', '231', '312', '213'
];

const hashes = testStrings.map(s => ({ s, h: actualHash(s) }));

// Check for duplicates
const seen = new Map();
for (const { s, h } of hashes) {
  if (seen.has(h)) {
    console.log('COLLISION:' + JSON.stringify({ s1: seen.get(h), s2: s, hash: h }));
  }
  seen.set(h, s);
}

const uniqueCount = new Set(hashes.map(x => x.h)).size;
console.log('TOTAL:' + testStrings.length);
console.log('UNIQUE:' + uniqueCount);
console.log('ALL_UNIQUE:' + (uniqueCount === testStrings.length));
""" % json.dumps(result)

    output, stderr = run_node_test(script)
    assert "HASH_NOT_FOUND" not in output

    lines = {l.split(':')[0]: l.split(':')[1] for l in output.split('\n') if ':' in l}

    total = int(lines['TOTAL'])
    unique = int(lines['UNIQUE'])
    all_unique = lines['ALL_UNIQUE'] == 'true'

    collision_line = [l for l in output.split('\n') if l.startswith('COLLISION:')]
    assert all_unique, \
        f"Hash produced collisions across diverse strings (expected {total} unique, got {unique}). " + \
        (f"First collision: {collision_line[0]}" if collision_line else "")

def test_hash_no_collision_with_pnpm_paths():
    """
    Simulate pnpm-style paths with hex suffixes that caused collisions.
    Example: two different packages might have paths like:
    - /node_modules/.pnpm/react@21.0.0+abc/node_modules/react
    - /node_modules/.pnpm/react@21.0.0+cba/node_modules/react

    The old hash would give same result for the react parts, causing
    duplicate preview_XXXX variable names.
    """
    path = os.path.join(REPO, TARGET_FILE)
    with open(path) as f:
        content = f.read()

    success, result = extract_hash_body(content)
    if not success:
        assert False, f"Failed to extract hash body: {result}"

    script = """
const hashBody = %s;

const actualHash = new Function('value', hashBody);

// pnpm-style paths with different hex suffixes
const path1 = '/node_modules/.pnpm/react@21.0.0+abc/node_modules/react';
const path2 = '/node_modules/.pnpm/react@21.0.0+cba/node_modules/react';

const h1 = actualHash(path1);
const h2 = actualHash(path2);

console.log('H1:' + h1);
console.log('H2:' + h2);
console.log('COLLISION:' + (h1 === h2));
""" % json.dumps(result)

    output, stderr = run_node_test(script)
    assert "HASH_NOT_FOUND" not in output

    lines = {l.split(':')[0]: l.split(':')[1] for l in output.split('\n') if ':' in l}

    h1, h2 = int(lines['H1']), int(lines['H2'])
    collision = lines['COLLISION'] == 'true'

    assert not collision, \
        f"Hash still produces collisions for pnpm-style paths: {h1} vs {h2}"

def test_typescript_compiles():
    """The modified TypeScript file compiles without errors."""
    r = subprocess.run(
        ["yarn", "nx", "compile", "builder-vite"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stderr}"

def test_vitest_builder_vite():
    """Repo's vitest tests for builder-vite pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "vitest", "run", "code/builders/builder-vite/src",
         "--config", "code/builders/builder-vite/vitest.config.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert r.returncode == 0, f"Vitest tests failed:\n{r.stderr[-1000:]}"

def test_nx_check_builder_vite():
    """Repo's typecheck for builder-vite passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "nx", "check", "builder-vite"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"Nx check failed:\n{r.stderr[-1000:]}"