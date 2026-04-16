"""Tests for excalidraw clipboard fix."""

import subprocess
import re

REPO = "/workspace/excalidraw"
CLIPBOARD_TS = f"{REPO}/packages/excalidraw/clipboard.ts"


def test_const_plainTextEntry_not_let():
    """Fail-to-pass: plainTextEntry should be const, not let."""
    with open(CLIPBOARD_TS, "r") as f:
        content = f.read()

    # Should have 'const plainTextEntry' (the fix)
    assert "const plainTextEntry = entries.find" in content, \
        "plainTextEntry should be declared as const, not let"

    # Should NOT have 'let plainTextEntry'
    assert "let plainTextEntry" not in content, \
        "Found 'let plainTextEntry' - should be changed to const"


def test_return_inside_clipboardEvent_block():
    """Fail-to-pass: First return should be inside if (clipboardEvent) block."""
    with open(CLIPBOARD_TS, "r") as f:
        content = f.read()

    # Find the copyTextToSystemClipboard function body
    func_match = re.search(
        r'export const copyTextToSystemClipboard = async.*?\(.*?\) => \{',
        content,
        re.DOTALL
    )
    assert func_match, "Could not find copyTextToSystemClipboard function"

    # Extract function body (find from function start to next export const or EOF)
    func_start = func_match.end() - 1  # Start at the opening brace
    func_end = content.find("\nexport const copyTextViaExecCommand", func_start)
    if func_end == -1:
        func_end = len(content)
    func_body = content[func_start:func_end]

    # Find the try block containing the if (clipboardEvent)
    # Check that there's a return INSIDE the if block (after the for loop)
    # The bug: return was outside the if block, causing early exit
    # The fix: return is inside the if block, after the for loop

    # Look for the pattern where 'return;' appears between 'if (clipboardEvent) {'
    # and its closing '}', but after the for loop

    # Find the if (clipboardEvent) block
    if_start = func_body.find("if (clipboardEvent)")
    assert if_start != -1, "Could not find 'if (clipboardEvent)' in function"

    # Find the opening brace of the if block
    brace_start = func_body.find("{", if_start)
    assert brace_start != -1, "Could not find opening brace of if block"

    # Find the matching closing brace by counting braces
    brace_count = 1
    pos = brace_start + 1
    while brace_count > 0 and pos < len(func_body):
        if func_body[pos] == '{':
            brace_count += 1
        elif func_body[pos] == '}':
            brace_count -= 1
        pos += 1

    if_block = func_body[brace_start:pos]

    # Check that there's a 'return;' inside the if block (after the for loop)
    assert "return;" in if_block, \
        "The 'return' statement should be inside the 'if (clipboardEvent)' block, not outside it"


def test_return_after_navigator_clipboard_writeText():
    """Fail-to-pass: Should return after navigator.clipboard.writeText succeeds."""
    with open(CLIPBOARD_TS, "r") as f:
        content = f.read()

    # Find the section after navigator.clipboard.writeText
    # The fix removes "plainTextEntry = undefined;" and adds "return;" instead

    # Should NOT have the old pattern of setting to undefined
    old_pattern = r'plainTextEntry = undefined;'
    assert not re.search(old_pattern, content), \
        "Found 'plainTextEntry = undefined' - should be removed and replaced with 'return;'"

    # Should have return; after navigator.clipboard.writeText
    pattern = r'await navigator\.clipboard\.writeText\(plainTextEntry\[1\]\);\s*return;'
    assert re.search(pattern, content, re.DOTALL), \
        "Should have 'return;' after 'await navigator.clipboard.writeText(plainTextEntry[1]);'"


def test_no_plainTextEntry_reassignment():
    """Fail-to-pass: plainTextEntry should not be reassigned."""
    with open(CLIPBOARD_TS, "r") as f:
        content = f.read()

    # Should not have any assignment to plainTextEntry after its declaration
    # (the old code had "plainTextEntry = undefined")
    assignments = re.findall(r'plainTextEntry\s*=', content)

    # Should only have ONE assignment (the declaration)
    assert len(assignments) == 1, \
        f"plainTextEntry should only be assigned once (at declaration), found {len(assignments)} assignments"


def test_typecheck_passes():
    """Pass-to-pass: TypeScript type checking should pass."""
    r = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"TypeScript type check failed:\n{r.stdout}\n{r.stderr}"


def test_clipboard_ts_no_syntax_errors():
    """Pass-to-pass: clipboard.ts should have no syntax errors."""
    # Check that the file can be parsed by attempting to build with esbuild
    # which is what the project uses for building
    r = subprocess.run(
        ["npx", "esbuild", "packages/excalidraw/clipboard.ts", "--platform=neutral", "--outfile=/tmp/clipboard.js"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    # esbuild will fail on syntax errors but may pass with type errors
    assert "error" not in r.stderr.lower() or "syntax" not in r.stderr.lower(), \
        f"Syntax error detected in clipboard.ts: {r.stderr}"


def test_repo_lint_passes():
    """Pass-to-pass: Repo ESLint checks pass (yarn test:code)."""
    r = subprocess.run(
        ["yarn", "test:code"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_prettier_passes():
    """Pass-to-pass: Repo Prettier checks pass (yarn test:other)."""
    r = subprocess.run(
        ["yarn", "test:other"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


def test_clipboard_unit_tests():
    """Pass-to-pass: Clipboard unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "vitest", "run", "packages/excalidraw/clipboard.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"Clipboard unit tests failed:\n{r.stderr[-500:]}"


def test_clipboard_integration_tests():
    """Pass-to-pass: Clipboard integration tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "vitest", "run", "packages/excalidraw/tests/clipboard.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"Clipboard integration tests failed:\n{r.stderr[-500:]}"
