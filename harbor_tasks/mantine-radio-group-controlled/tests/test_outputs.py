"""
Test for mantinedev/mantine#8453: Fix Radio.Group controlled/uncontrolled warning

This test verifies the fix by:
1. Compiling the Radio component TypeScript with esbuild
2. Analyzing the compiled JavaScript for the safe nullish-coalescing pattern
   (which prevents the controlled→uncontrolled transition)
3. Verifying the Radio component passes TypeScript and lint checks
"""

import subprocess
import os
import sys
import re

REPO = "/workspace/mantine"


def test_radio_compilation():
    """
    F2P: The Radio component TypeScript compiles without errors.

    This verifies the fix is syntactically valid TypeScript.
    """
    result = subprocess.run(
        ["node", "-e", """
const ts = require('typescript');
const fs = require('fs');
const path = 'packages/@mantine/core/src/components/Radio/Radio.tsx';
const content = fs.readFileSync(path, 'utf8');
const sourceFile = ts.createSourceFile(path, content, ts.ScriptTarget.Latest, true);
console.log('Parse errors:', sourceFile.parseDiagnostics.length);
if (sourceFile.parseDiagnostics.length > 0) {
    sourceFile.parseDiagnostics.forEach(d => console.error(d.messageText));
    process.exit(1);
}
console.log('TypeScript syntax is valid');
process.exit(0);
"""],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"TypeScript parsing failed:\n{result.stderr}"


def test_radio_esbuild_compile():
    """
    F2P: The Radio component compiles with esbuild and the compiled output
    uses nullish-coalescing (??) instead of || for the checked property.

    The bug: Using `||` for checked state causes controlled→uncontrolled
    transitions when ctx.value doesn't match rest.value (producing undefined).

    The fix: Using `??` (nullish coalescing) distinguishes:
    - contextChecked = false (context says not checked - use false, not undefined)
    - contextChecked = undefined (no context - fall through to local checked)
    """
    # Use npx tsx -e to run inline code that compiles Radio.tsx with esbuild
    result = subprocess.run(
        ["npx", "tsx", "-e", r"""
const esbuild = require('esbuild');
const fs = require('fs');
const path = 'packages/@mantine/core/src/components/Radio/Radio.tsx';
const content = fs.readFileSync(path, 'utf8');

async function main() {
    try {
        const result = await esbuild.transform(content, {
            loader: 'tsx',
            jsx: 'automatic',
            target: 'es2020',
            sourcemap: false,
            minify: false,
        });
        console.log('COMPILED_CODE:');
        console.log(result.code);
    } catch (err) {
        console.error('esbuild failed:', err.message);
        process.exit(1);
    }
}
main();
"""],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, f"esbuild compilation failed:\n{result.stderr}"

    compiled_code = result.stdout
    # Extract the part after "COMPILED_CODE:"
    if "COMPILED_CODE:" in compiled_code:
        compiled_code = compiled_code.split("COMPILED_CODE:")[1]

    # Check that the checked property uses ?? (nullish coalescing) specifically
    # The pattern should be: checked: <something> ?? checked
    # where <something> is derived from the context comparison
    #
    # The old buggy code had: checked: ctx?.value === rest.value || checked || undefined
    # The fix changes it to: checked: contextChecked ?? checked
    # where contextChecked = ctx ? ctx.value === rest.value : undefined

    # Look for the checked property assignment and verify it uses ??
    # Pattern: checked: <expr> ?? <expr>   (not ||)
    # We need to be careful: the line might be spread across multiple lines

    # Find all lines that have "checked:" and extract the full expression
    checked_pattern = re.compile(
        r'checked:\s*([^,\n]+)\s*\?\?\s*([^,\n]+)',
        re.MULTILINE
    )

    # Also look for the unsafe pattern that uses || undefined or || checked || undefined
    # This is the BUG - it can produce undefined which triggers React's warning
    unsafe_pattern = re.compile(
        r'checked:\s*[^,\n]*\|\|[^,\n]*\|\|\s*(?:void 0|undefined)',
        re.MULTILINE
    )

    has_unsafe = bool(unsafe_pattern.search(compiled_code))
    has_safe = bool(checked_pattern.search(compiled_code))

    assert not has_unsafe, (
        "Compiled Radio component still contains unsafe || pattern for checked property. "
        "This triggers the controlled→uncontrolled warning. "
        "The fix should use ?? (nullish coalescing) instead."
    )

    assert has_safe, (
        "Compiled Radio component does not use ?? (nullish coalescing) for checked property. "
        "The fix requires ?? to properly handle controlled/uncontrolled state."
    )


def test_radio_prettier_format():
    """
    P2P: Radio component files are formatted correctly (pass_to_pass).
    """
    result = subprocess.run(
        ["npx", "prettier", "--check", "packages/@mantine/core/src/components/Radio/*.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stderr}"


def test_radio_eslint():
    """
    P2P: Radio component files pass linting (pass_to_pass).
    """
    result = subprocess.run(
        ["npm", "run", "eslint", "--", "packages/@mantine/core/src/components/Radio"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stderr[-500:]}"


def test_radio_typescript_parse():
    """
    P2P: Radio.tsx has valid TypeScript syntax (pass_to_pass).
    """
    result = subprocess.run(
        ["node", "-e", """
const ts = require('typescript');
const fs = require('fs');
const path = 'packages/@mantine/core/src/components/Radio/Radio.tsx';
const content = fs.readFileSync(path, 'utf8');
const sourceFile = ts.createSourceFile(path, content, ts.ScriptTarget.Latest, true);
console.log('Parse errors:', sourceFile.parseDiagnostics.length);
if (sourceFile.parseDiagnostics.length > 0) {
    sourceFile.parseDiagnostics.forEach(d => console.error(d.messageText));
    process.exit(1);
}
console.log('TypeScript syntax is valid');
process.exit(0);
"""],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"TypeScript parsing failed:\n{result.stderr}"


if __name__ == "__main__":
    # Run tests
    tests = [
        ("test_radio_compilation", test_radio_compilation),
        ("test_radio_esbuild_compile", test_radio_esbuild_compile),
        ("test_radio_prettier_format", test_radio_prettier_format),
        ("test_radio_eslint", test_radio_eslint),
        ("test_radio_typescript_parse", test_radio_typescript_parse),
    ]

    failed = []
    for name, test_fn in tests:
        try:
            test_fn()
            print(f"PASS: {name}")
        except AssertionError as e:
            print(f"FAIL: {name}: {e}")
            failed.append(name)

    if failed:
        sys.exit(1)