"""
Tests for the UnifiedTerminal $ prefix removal fix.

This task requires removing the hardcoded "$ " Unix prompt prefix from:
1. The copy-to-clipboard content
2. The visual display in the terminal UI component

The $ prefix is a bash convention that doesn't apply to Windows users (PowerShell uses PS>, cmd uses >).
"""

import subprocess
import re
import sys

REPO = "/workspace/continue"
TERMINAL_FILE = f"{REPO}/gui/src/components/UnifiedTerminal/UnifiedTerminal.tsx"
TEST_FILE = f"{REPO}/gui/src/components/UnifiedTerminal/UnifiedTerminal.test.tsx"


def test_copy_content_no_dollar_prefix():
    """
    FAIL-TO-PASS: copyContent generation must NOT prepend '$ ' to the command.

    The copyContent variable is built in the useMemo hook and should contain
    just the command string, not '$ command'.
    """
    with open(TERMINAL_FILE, "r") as f:
        content = f.read()

    # Look for the copyContent useMemo block - should contain 'let content = command;'
    # NOT 'let content = `$ ${command}`;'
    pattern = r"const copyContent = useMemo\(\(\) => \{[^}]+let content = ([^;]+);"
    match = re.search(pattern, content, re.DOTALL)

    assert match, "Could not find copyContent useMemo block"

    content_assignment = match.group(1).strip()

    # Should be just 'command', not '`$ ${command}`' or similar
    assert content_assignment == "command", \
        f"copyContent incorrectly assigns: '{content_assignment}'. Expected just 'command' without $ prefix."


def test_display_no_dollar_prefix():
    """
    FAIL-TO-PASS: The visual display must NOT show '$ ' before the command.

    The JSX should render just {command}, not '$ {command}'.
    """
    with open(TERMINAL_FILE, "r") as f:
        content = f.read()

    # Find the command display div - should be just {command}, not '$ {command}'
    # Looking for: <div className="text-terminal pb-2">{command}</div>
    # NOT: <div className="text-terminal pb-2">$ {command}</div>

    # Check that the fix is present
    correct_pattern = '<div className="text-terminal pb-2">{command}</div>'
    incorrect_pattern = '<div className="text-terminal pb-2">$ {command}</div>'

    assert correct_pattern in content, \
        f"Command display div should contain just '{{command}}', found incorrect pattern or missing"

    assert incorrect_pattern not in content, \
        f"Command display still contains hardcoded '$ ' prefix: '{incorrect_pattern}'"


def test_vitest_unified_terminal_tests_pass():
    """
    POINT-TO-POINT: Run the UnifiedTerminal vitest tests.

    The test file was updated to expect commands WITHOUT the $ prefix.
    All tests should pass on the fixed version.
    """
    result = subprocess.run(
        ["npx", "vitest", "run", "UnifiedTerminal", "--reporter=verbose"],
        cwd=f"{REPO}/gui",
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Vitest tests failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"

    # Verify all expected tests passed
    assert "UnifiedTerminalCommand" in result.stdout or "Test Files" in result.stdout, \
        "Test output doesn't indicate UnifiedTerminal tests ran"


def test_copy_content_with_output():
    """
    FAIL-TO-PASS: When there is output, copyContent should be 'command\n\noutput'.

    NOT '$ command\n\noutput' as it was before the fix.
    """
    with open(TERMINAL_FILE, "r") as f:
        content = f.read()

    # Find the useMemo block for copyContent
    pattern = r"const copyContent = useMemo\(\(\) => \{([^}]+)\}, \[command, (?:output, )?hasOutput\]\)"
    match = re.search(pattern, content, re.DOTALL)

    assert match, "Could not find copyContent useMemo block with correct dependencies"

    memo_body = match.group(1)

    # Verify the logic:
    # 1. Starts with just command (not $ command)
    # 2. Appends output when hasOutput is true

    assert "let content = command;" in memo_body, \
        "copyContent should initialize with just 'command', not '$ command'"

    assert 'content += `\\n\\n${output}`' in memo_body or 'content += "\\n\\n" + output' in memo_body, \
        "copyContent should append output with newlines when hasOutput is true"


def test_three_test_files_updated():
    """
    POINT-TO-POINT: The test file should have 3 updated assertions removing $ prefix.

    All three test assertions should check for just MOCK_COMMAND, not `$ ${MOCK_COMMAND}`.
    """
    with open(TEST_FILE, "r") as f:
        content = f.read()

    # Count occurrences of the correct pattern (without $)
    correct_count = content.count("screen.getByText(MOCK_COMMAND)")

    # Count occurrences of the old pattern (with $)
    incorrect_count = content.count("screen.getByText(`$ ${MOCK_COMMAND}`)")

    assert incorrect_count == 0, \
        f"Test file still contains {incorrect_count} assertions with '$ ' prefix"

    assert correct_count >= 3, \
        f"Expected at least 3 assertions checking for MOCK_COMMAND without $, found {correct_count}"


def test_no_regression_dollar_in_comments():
    """
    Verify that the word 'command' appears without $ prefix in the right contexts.

    This is a sanity check that the fix was applied correctly.
    """
    with open(TERMINAL_FILE, "r") as f:
        content = f.read()

    # The line '{command}' should appear exactly once in the div
    display_occurrences = content.count('>{command}<')
    assert display_occurrences == 1, \
        f"Expected exactly 1 occurrence of '>{{command}}<', found {display_occurrences}"


# ============================================================================
# PASS-TO-PASS TESTS - Repo CI/CD checks that must pass on base and fixed code
# ============================================================================

REPO_GUI = f"{REPO}/gui"


def setup_repo_deps():
    """Helper to install all necessary dependencies for repo commands."""
    # This is a setup helper - run once before repo tests
    # Install root dependencies
    subprocess.run(
        ["npm", "install"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    # Build packages
    subprocess.run(
        ["node", "./scripts/build-packages.js"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    # Install core dependencies
    subprocess.run(
        ["npm", "install"],
        cwd=f"{REPO}/core",
        capture_output=True,
        timeout=300,
    )


def test_repo_typecheck():
    """
    PASS-TO-PASS: Repo GUI package TypeScript typecheck passes.

    Runs `npx tsc --noEmit` in the GUI package to verify type correctness.
    This is part of the repo's CI/CD pipeline (gui-checks job).
    """
    setup_repo_deps()
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_GUI,
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stderr[-500:]}"


def test_repo_lint():
    """
    PASS-TO-PASS: Repo GUI package ESLint passes.

    Runs `npm run lint` in the GUI package to verify code style.
    This is part of the repo's CI/CD pipeline (gui-checks job).
    """
    setup_repo_deps()
    r = subprocess.run(
        ["npm", "run", "lint"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_GUI,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_unified_terminal_tests():
    """
    PASS-TO-PASS: Repo UnifiedTerminal vitest tests pass.

    Runs `npx vitest run UnifiedTerminal` in the GUI package.
    This is the same test suite used for the p2p check but run as a repo CI test.
    """
    setup_repo_deps()
    r = subprocess.run(
        ["npx", "vitest", "run", "UnifiedTerminal", "--reporter=verbose"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_GUI,
    )
    assert r.returncode == 0, f"UnifiedTerminal tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


if __name__ == "__main__":
    # Run all tests
    test_functions = [
        test_copy_content_no_dollar_prefix,
        test_display_no_dollar_prefix,
        test_copy_content_with_output,
        test_three_test_files_updated,
        test_no_regression_dollar_in_comments,
        test_vitest_unified_terminal_tests_pass,
        test_repo_typecheck,
        test_repo_lint,
        test_repo_unified_terminal_tests,
    ]

    passed = 0
    failed = 0

    for test in test_functions:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: ERROR: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
