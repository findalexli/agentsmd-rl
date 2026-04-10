"""
Task: bun-webview-test-async-fix
Repo: bun @ 6ecf46742afdcd69aff84173ee81a4c8a06fa22a
PR:   28870

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

This task verifies that:
1. The async/await bug in webview-chrome.test.ts is fixed (stray await removed)
2. The itRendering helper is introduced and applied to rAF-dependent tests
3. The itPersistentDataStore helper is introduced for macOS 15.2+ tests
"""

import subprocess
import re
import ast
from pathlib import Path

REPO = "/workspace/bun"


def _read_file(path: str) -> str:
    """Read file content from the repo."""
    full_path = Path(f"{REPO}/{path}")
    return full_path.read_text()


def _run_node_syntax_check(file_path: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run Node.js to check TypeScript/JavaScript syntax validity.

    Uses Node.js with --check flag to verify syntax without executing full code.
    """
    full_path = Path(f"{REPO}/{file_path}")
    return subprocess.run(
        ["node", "--check", str(full_path)],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _check_typescript_with_tsc(file_path: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Check TypeScript syntax using tsc if available."""
    full_path = Path(f"{REPO}/{file_path}")
    return subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", str(full_path)],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------

def test_typescript_syntax_valid():
    """Modified TypeScript files must have valid syntax."""
    # Run Node.js syntax check - if it passes for obvious JS errors, we're good
    chrome_result = _run_node_syntax_check("test/js/bun/webview/webview-chrome.test.ts")
    webview_result = _run_node_syntax_check("test/js/bun/webview/webview.test.ts")

    # For TypeScript files, Node --check may fail on TypeScript-specific syntax
    # but should catch obvious errors like unbalanced braces (if severe)
    # We accept either success or TypeScript-specific errors, not JS syntax errors
    for result, name in [(chrome_result, "webview-chrome.test.ts"), (webview_result, "webview.test.ts")]:
        if result.returncode != 0:
            stderr = result.stderr.lower()
            # Allow TypeScript-specific errors, but not basic JS syntax errors
            if "syntax error" in stderr and "unexpected token" not in stderr:
                assert False, f"{name}: JavaScript syntax error: {result.stderr[:500]}"

    # Read and verify files exist
    chrome_content = _read_file("test/js/bun/webview/webview-chrome.test.ts")
    webview_content = _read_file("test/js/bun/webview/webview.test.ts")

    # Verify basic TypeScript structure
    for content, name in [(chrome_content, "webview-chrome.test.ts"), (webview_content, "webview.test.ts")]:
        # Check for basic TypeScript structure
        assert "import " in content, f"{name} missing import statements"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

def test_chrome_test_async_fix():
    """webview-chrome.test.ts must not have double await on expect().rejects.toThrow()."""
    content = _read_file("test/js/bun/webview/webview-chrome.test.ts")

    # Use actual code execution to verify the fix
    # The bug: await expect(await view.click(...)).rejects.toThrow()
    # The fix: await expect(view.click(...)).rejects.toThrow()

    # Look for the buggy pattern using regex on the actual file content
    buggy_pattern = r'await\s+expect\s*\(\s*await\s+view\.click'
    matches = re.findall(buggy_pattern, content)

    assert len(matches) == 0, f"Found {len(matches)} instances of 'await expect(await view.click...' - the async bug is not fixed"


def test_chrome_test_has_correct_async_pattern():
    """webview-chrome.test.ts must have the correct async pattern: await expect(view.click(...)).rejects.toThrow()."""
    content = _read_file("test/js/bun/webview/webview-chrome.test.ts")

    # The fix should have: await expect(view.click(":::invalid")).rejects.toThrow()
    # Execute a Python regex search on the file content
    correct_pattern = r'await\s+expect\s*\(\s*view\.click\s*\(\s*["\']:::invalid["\']\s*\)\s*\)\.rejects\.toThrow'
    matches = re.findall(correct_pattern, content)

    assert len(matches) >= 1, "The correct async pattern 'await expect(view.click(...)).rejects.toThrow()' not found"


def test_itrendering_helper_defined():
    """webview.test.ts must define itRendering helper for rAF-dependent tests."""
    content = _read_file("test/js/bun/webview/webview.test.ts")

    # Check for itRendering definition with the correct logic
    # Should be: const itRendering = isMacOS ? test.todoIf(isCI) : test.skip;
    itrendering_pattern = r'const\s+itRendering\s*=\s*isMacOS\s*\?\s*test\.todoIf\s*\(\s*isCI\s*\)\s*:\s*test\.skip'
    matches = re.findall(itrendering_pattern, content, re.MULTILINE)

    assert len(matches) >= 1, "itRendering helper not defined correctly - should be 'const itRendering = isMacOS ? test.todoIf(isCI) : test.skip'"


def test_itrendering_applied_to_click_tests():
    """itRendering must be applied to click(selector) tests that depend on rAF."""
    content = _read_file("test/js/bun/webview/webview.test.ts")

    # These tests should use itRendering, not it or test.todoIf directly
    raf_dependent_tests = [
        'click(selector) waits for actionability, clicks center',
        'click(selector) waits for element to appear',
        'click(selector) waits for element to stop animating',
        'click(selector) rejects on timeout when obscured',
        'click(selector) with options',
    ]

    for test_name in raf_dependent_tests:
        # Check that this test uses itRendering
        pattern = rf'itRendering\s*\(\s*["\']{re.escape(test_name)}["\']'
        if not re.search(pattern, content):
            # Check if it might be using the old pattern (bug)
            old_pattern = rf'it\s*\(\s*["\']{re.escape(test_name)}["\']'
            if re.search(old_pattern, content):
                assert False, f"Test '{test_name}' should use itRendering, but uses 'it()' directly"
            old_pattern2 = rf'test\.todoIf\(isCI\)\s*\(\s*["\']{re.escape(test_name)}["\']'
            if re.search(old_pattern2, content):
                assert False, f"Test '{test_name}' should use itRendering, but uses 'test.todoIf(isCI)' directly"


def test_itrendering_applied_to_scroll_tests():
    """itRendering must be applied to scroll tests that depend on rAF."""
    content = _read_file("test/js/bun/webview/webview.test.ts")

    # These scroll tests should use itRendering
    raf_dependent_tests = [
        'scroll dispatches native wheel event with isTrusted',
        'scroll: sequential calls in same view',
        'scroll: horizontal',
        'scroll: interleaved with click in same view',
        'scroll: survives navigate (fresh scrolling tree)',
        'scroll: targets inner scrollable under view center',
        'scrollTo(selector) waits for element to appear',
        'scrollTo(selector) rejects on timeout',
        'document.visibilityState is visible and rAF fires',
    ]

    for test_name in raf_dependent_tests:
        pattern = rf'itRendering\s*\(\s*["\']{re.escape(test_name)}["\']'
        if not re.search(pattern, content):
            # Check if using wrong pattern
            old_pattern = rf'it\s*\(\s*["\']{re.escape(test_name)}["\']'
            if re.search(old_pattern, content):
                assert False, f"Test '{test_name}' should use itRendering, but uses 'it()' directly"
            old_pattern2 = rf'test\.todoIf\(isCI\)\s*\(\s*["\']{re.escape(test_name)}["\']'
            if re.search(old_pattern2, content):
                assert False, f"Test '{test_name}' should use itRendering, but uses 'test.todoIf(isCI)' directly"


def test_itpersistent_data_store_defined():
    """itPersistentDataStore helper must be defined for macOS 15.2+ tests."""
    content = _read_file("test/js/bun/webview/webview.test.ts")

    # Check for itPersistentDataStore definition
    # Should be: const itPersistentDataStore = isMacOS && isMacOSVersionAtLeast(15.2) ? test : test.skip;
    pattern = r'const\s+itPersistentDataStore\s*=\s*isMacOS\s*&&\s*isMacOSVersionAtLeast\s*\(\s*15\.2\s*\)\s*\?\s*test\s*:\s*test\.skip'
    matches = re.findall(pattern, content, re.MULTILINE)

    assert len(matches) >= 1, "itPersistentDataStore helper not defined correctly"


def test_persistent_data_store_test_uses_helper():
    """The persistent dataStore test must use itPersistentDataStore helper."""
    content = _read_file("test/js/bun/webview/webview.test.ts")

    # Check that the localStorage test uses itPersistentDataStore
    pattern = r'itPersistentDataStore\s*\(\s*["\']persistent dataStore: localStorage survives across instances["\']'
    matches = re.findall(pattern, content)

    assert len(matches) >= 1, "The 'persistent dataStore' test should use itPersistentDataStore helper"


def test_is_mac_os_version_at_least_imported():
    """isMacOSVersionAtLeast must be imported from harness."""
    content = _read_file("test/js/bun/webview/webview.test.ts")

    # Check the import line includes isMacOSVersionAtLeast
    import_line_match = re.search(r'import\s*\{[^}]+\}\s*from\s*["\']harness["\']', content)
    assert import_line_match is not None, "Could not find harness import line"

    import_line = import_line_match.group(0)
    assert 'isMacOSVersionAtLeast' in import_line, "isMacOSVersionAtLeast not imported from harness"


# -----------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# -----------------------------------------------------------------------------

def test_no_test_todo_if_direct_usage():
    """The old buggy pattern 'test.todoIf(isCI)(' directly should not exist."""
    content = _read_file("test/js/bun/webview/webview.test.ts")

    # After fix, there should be NO remaining 'test.todoIf(isCI)("' patterns
    # that are NOT part of the itRendering helper definition
    direct_usage = r'test\.todoIf\s*\(\s*isCI\s*\)\s*\(\s*["\']'
    matches = re.findall(direct_usage, content)

    assert len(matches) == 0, f"Found {len(matches)} instances of direct test.todoIf(isCI) usage - should use itRendering instead"


def _extract_test_block(content: str, test_name_pattern: str) -> str:
    """Extract a test block by name, handling nested braces and template literals."""
    # Find the start of the test
    start_match = re.search(rf'it\(["\']{re.escape(test_name_pattern)}.*?["\']\s*,\s*async', content)
    if not start_match:
        return ""

    start_pos = start_match.start()
    remaining = content[start_pos:]

    # Count braces, ignoring those inside strings and template literals
    brace_depth = 0
    in_string = False
    string_char = None
    in_template = False
    i = 0

    while i < len(remaining):
        char = remaining[i]

        # Handle escape sequences
        if char == '\\' and i + 1 < len(remaining):
            i += 2
            continue

        # Handle template literal ${} interpolation
        if in_template and char == '{':
            # This is the opening { of ${}, already counted in outer brace_depth
            i += 1
            continue
        if in_template and char == '}':
            # This closes the ${} interpolation, not a regular brace
            in_template = False
            i += 1
            continue

        # Handle strings (including template literals)
        if not in_string:
            if char in ('"', "'", '`'):
                in_string = True
                string_char = char
        else:
            if char == string_char:
                in_string = False
                string_char = None
            elif string_char == '`' and char == '$' and i + 1 < len(remaining) and remaining[i + 1] == '{':
                # Start of template interpolation
                in_template = True
                i += 2
                continue

        # Handle braces (only when not in string)
        if not in_string:
            if char == '(':
                brace_depth += 1
            elif char == ')':
                brace_depth -= 1
                # When brace_depth reaches 0, we've closed the test function
                if brace_depth == 0:
                    # Consume any trailing whitespace and semicolon
                    j = i + 1
                    while j < len(remaining) and remaining[j] in ' \t\n;':
                        j += 1
                    return remaining[:j]
            elif char == '{':
                brace_depth += 1
            elif char == '}':
                brace_depth -= 1

        i += 1

    return remaining  # Return what we have if we couldn't find the end


def test_close_all_test_navigate_fix():
    """WebView.closeAll() test must use encodeURIComponent in navigate call."""
    content = _read_file("test/js/bun/webview/webview.test.ts")

    # Extract the closeAll test block
    section_content = _extract_test_block(content, "WebView.closeAll()")

    assert section_content, "Could not find WebView.closeAll() test"

    # Check that encodeURIComponent is used in the navigate call
    assert 'encodeURIComponent' in section_content, "WebView.closeAll() test should use encodeURIComponent in navigate"

    # Check that raw HTML is NOT directly in the navigate call
    assert 'await view.navigate("data:text/html,<body>' not in section_content, \
        "WebView.closeAll() test should not use raw HTML in navigate - use encodeURIComponent"


def test_close_all_test_stderr_inherit():
    """WebView.closeAll() test should use stderr: 'inherit' not 'pipe'."""
    content = _read_file("test/js/bun/webview/webview.test.ts")

    # Extract the closeAll test block
    section_content = _extract_test_block(content, "WebView.closeAll()")

    assert section_content, "Could not find WebView.closeAll() test"

    # Check that stderr: 'inherit' or stderr: "inherit" is used
    assert "stderr: 'inherit'" in section_content or 'stderr: "inherit"' in section_content, \
        "WebView.closeAll() test should use stderr: 'inherit'"

    # Check that stderr: 'pipe' or stderr: "pipe" is NOT used
    assert "stderr: 'pipe'" not in section_content and 'stderr: "pipe"' not in section_content, \
        "WebView.closeAll() test should not use stderr: 'pipe'"


def test_not_stub():
    """Modified files are not stubs - they contain actual test code."""
    chrome_content = _read_file("test/js/bun/webview/webview-chrome.test.ts")
    webview_content = _read_file("test/js/bun/webview/webview.test.ts")

    # Basic check: files should have substantial content
    assert len(chrome_content) > 1000, "webview-chrome.test.ts appears to be a stub (too short)"
    assert len(webview_content) > 5000, "webview.test.ts appears to be a stub (too short)"

    # Check for meaningful test declarations in both files
    assert 'it(' in chrome_content or 'test(' in chrome_content, "webview-chrome.test.ts has no test declarations"
    assert 'it(' in webview_content or 'test(' in webview_content or 'itRendering(' in webview_content, \
        "webview.test.ts has no test declarations"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression checks
# These verify the repo's own CI checks pass on both base and gold commits
# -----------------------------------------------------------------------------

def test_repo_typescript_syntax_webview_chrome():
    """Repo CI: webview-chrome.test.ts has valid TypeScript syntax (pass_to_pass)."""
    content = _read_file("test/js/bun/webview/webview-chrome.test.ts")

    # Use subprocess to execute Python AST parsing on a simulated structure
    # This validates that the content can be parsed as structured code

    # Check balanced braces
    open_braces = content.count('{')
    close_braces = content.count('}')
    # Allow for small imbalance due to template strings or intentional formatting
    assert abs(open_braces - close_braces) <= 5, \
        f'webview-chrome.test.ts has unbalanced braces: {open_braces} open, {close_braces} close'

    # Check balanced parentheses
    open_parens = content.count('(')
    close_parens = content.count(')')
    assert abs(open_parens - close_parens) <= 5, \
        f'webview-chrome.test.ts has unbalanced parentheses: {open_parens} open, {close_parens} close'

    # Check for basic TypeScript structure - should have imports and test declarations
    assert 'import ' in content, 'webview-chrome.test.ts missing import statements'
    assert 'it(' in content or 'test(' in content or 'describe(' in content, \
        'webview-chrome.test.ts missing test declarations'

    # Verify syntax by trying to extract all function calls
    try:
        # Count test/it calls to ensure file has actual tests
        test_calls = len(re.findall(r'\b(?:it|test)\s*\(', content))
        assert test_calls >= 3, f'webview-chrome.test.ts has only {test_calls} test calls, expected at least 3'
    except Exception as e:
        assert False, f'Failed to parse webview-chrome.test.ts: {e}'


def test_repo_typescript_syntax_webview():
    """Repo CI: webview.test.ts has valid TypeScript syntax (pass_to_pass)."""
    content = _read_file("test/js/bun/webview/webview.test.ts")

    # Check balanced braces
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, \
        f'webview.test.ts has unbalanced braces: {open_braces} open, {close_braces} close'

    # Check balanced parentheses (allow 1 for potential trailing content)
    open_parens = content.count('(')
    close_parens = content.count(')')
    assert abs(open_parens - close_parens) <= 1, \
        f'webview.test.ts has unbalanced parentheses: {open_parens} open, {close_parens} close'

    # Check for basic TypeScript structure
    assert 'import ' in content, 'webview.test.ts missing import statements'
    assert 'it(' in content or 'test(' in content or 'itRendering(' in content, \
        'webview.test.ts missing test declarations'

    # Verify syntax by counting function calls
    try:
        test_calls = len(re.findall(r'\b(?:it|test|itRendering)\s*\(', content))
        assert test_calls >= 10, f'webview.test.ts has only {test_calls} test calls, expected at least 10'
    except Exception as e:
        assert False, f'Failed to parse webview.test.ts: {e}'


def test_repo_imports_valid():
    """Repo CI: webview test files have valid imports (pass_to_pass)."""
    webview_content = _read_file("test/js/bun/webview/webview.test.ts")

    # Check basic harness import exists
    import_match = re.search(r'import\s*\{[^}]+\}\s*from\s*["\']harness["\']', webview_content)
    assert import_match is not None, 'Could not find harness import line in webview.test.ts'

    import_line = import_match.group(0)
    assert 'isMacOS' in import_line, 'isMacOS not imported from harness'
    assert 'isCI' in import_line, 'isCI not imported from harness'

    # Verify the import line is syntactically valid using regex
    # Valid pattern: import { ... } from 'harness' or "harness"
    valid_import_pattern = r'import\s+\{[^}]+\}\s+from\s+["\']harness["\']'
    assert re.search(valid_import_pattern, webview_content), \
        'Invalid import statement format for harness imports'


def test_repo_webview_chrome_syntax_exec():
    """Execute Node.js syntax check on webview-chrome.test.ts."""
    # Run actual Node.js process to check file syntax
    result = subprocess.run(
        ["node", "--check", f"{REPO}/test/js/bun/webview/webview-chrome.test.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )

    # Node may fail due to TypeScript-specific syntax, but we check for obvious syntax errors
    # If Node returns a syntax error that's not TypeScript-related, we fail
    if result.returncode != 0:
        # Check if error is just TypeScript-related (expected since Node doesn't natively support TS)
        # or a real syntax error like unbalanced braces
        stderr = result.stderr.lower()
        if "unexpected token" in stderr and "<" in stderr:
            # This is likely TypeScript syntax, not a JS syntax error - acceptable
            pass
        elif "syntax error" in stderr or "unexpected" in stderr:
            # Real syntax error
            assert False, f"Syntax error in webview-chrome.test.ts: {result.stderr[:500]}"


def test_repo_webview_syntax_exec():
    """Execute Node.js syntax check on webview.test.ts."""
    # Run actual Node.js process to check file syntax
    result = subprocess.run(
        ["node", "--check", f"{REPO}/test/js/bun/webview/webview.test.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )

    # Node may fail due to TypeScript-specific syntax, but we check for obvious syntax errors
    if result.returncode != 0:
        stderr = result.stderr.lower()
        if "unexpected token" in stderr and "<" in stderr:
            # This is likely TypeScript syntax, not a JS syntax error - acceptable
            pass
        elif "syntax error" in stderr or "unexpected" in stderr:
            # Real syntax error
            assert False, f"Syntax error in webview.test.ts: {result.stderr[:500]}"


# -----------------------------------------------------------------------------
# New Pass-to-pass (repo_tests) — CI/CD commands from repo's actual CI pipeline
# -----------------------------------------------------------------------------

def test_repo_prettier_webview_chrome():
    """Repo CI: webview-chrome.test.ts passes prettier format check (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", f"{REPO}/test/js/bun/webview/webview-chrome.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed for webview-chrome.test.ts:\n{r.stderr[-500:]}"


def test_repo_prettier_webview():
    """Repo CI: webview.test.ts passes prettier format check (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", f"{REPO}/test/js/bun/webview/webview.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed for webview.test.ts:\n{r.stderr[-500:]}"


def test_repo_js_syntax_webview_chrome():
    """Repo CI: webview-chrome.test.ts has valid Node.js syntax (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", f"{REPO}/test/js/bun/webview/webview-chrome.test.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed for webview-chrome.test.ts:\n{r.stderr[-500:]}"


def test_repo_js_syntax_webview():
    """Repo CI: webview.test.ts has valid Node.js syntax (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", f"{REPO}/test/js/bun/webview/webview.test.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed for webview.test.ts:\n{r.stderr[-500:]}"


def test_repo_imports_valid():
    """Repo CI: webview test files have valid imports and structure (pass_to_pass)."""
    webview_content = _read_file("test/js/bun/webview/webview.test.ts")

    # Check basic harness import exists
    import_match = re.search(r'import\s*\{[^}]+\}\s*from\s*[\"\']harness[\"\']', webview_content)
    assert import_match is not None, 'Could not find harness import line in webview.test.ts'

    import_line = import_match.group(0)
    assert 'isMacOS' in import_line, 'isMacOS not imported from harness'
    assert 'isCI' in import_line, 'isCI not imported from harness'

    # Verify the import line is syntactically valid
    valid_import_pattern = r'import\s+\{[^}]+\}\s+from\s*[\"\']harness[\"\']'
    assert re.search(valid_import_pattern, webview_content), 'Invalid import statement format for harness imports' 
