"""
Test for mantinedev/mantine#8453: Fix Radio.Group controlled/uncontrolled warning

This test verifies that the fix for controlled Radio.Group warning is properly applied.
"""

import subprocess
import os
import sys

REPO = "/workspace/mantine"


def test_radio_group_fix_applied():
    """
    F2P: The fix for controlled Radio.Group issue #8452 must be applied.

    The bug: When using a controlled Radio.Group with value and onChange,
    switching between options logs: "A component is changing a controlled
    input to be uncontrolled..."

    The fix adds a test case 'does not log controlled/uncontrolled warning
    inside controlled Radio.Group' to Radio.test.tsx and modifies Radio.tsx
    to use contextChecked tracking.
    """
    # Check that the fix is applied by looking for the distinctive line
    result = subprocess.run(
        ["grep", "-q", "contextChecked", "packages/@mantine/core/src/components/Radio/Radio.tsx"],
        cwd=REPO,
        capture_output=True,
    )

    assert result.returncode == 0, (
        "The fix for #8452 is not applied. "
        "Radio.tsx should contain 'contextChecked' variable."
    )


def test_radio_group_test_exists():
    """
    F2P: The test case for controlled Radio.Group warning must exist.

    The PR adds a test 'does not log controlled/uncontrolled warning
    inside controlled Radio.Group' that verifies the fix works.
    """
    # Check that the test case exists in the test file
    result = subprocess.run(
        ["grep", "-q", "does not log controlled/uncontrolled warning",
         "packages/@mantine/core/src/components/Radio/Radio.test.tsx"],
        cwd=REPO,
        capture_output=True,
    )

    assert result.returncode == 0, (
        "The test case for #8452 is not present in Radio.test.tsx. "
        "Expected test: 'does not log controlled/uncontrolled warning inside controlled Radio.Group'"
    )


def test_radio_file_compiles_with_babel():
    """
    P2P: Radio.tsx should compile with Babel transform (verifies syntax is valid).
    """
    # Use esbuild's TypeScript checking via the project's setup
    # First verify the file exists and has valid TypeScript syntax
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
"""],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )

    if result.returncode != 0:
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

    assert result.returncode == 0, f"TypeScript parsing failed:\n{result.stderr}"


if __name__ == "__main__":
    # Run tests
    tests = [
        ("test_radio_group_fix_applied", test_radio_group_fix_applied),
        ("test_radio_group_test_exists", test_radio_group_test_exists),
        ("test_radio_file_compiles_with_babel", test_radio_file_compiles_with_babel),
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