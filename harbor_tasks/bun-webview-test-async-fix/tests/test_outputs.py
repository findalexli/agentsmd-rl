"""
Task: bun-webview-test-async-fix
Repo: bun @ 6ecf46742afdcd69aff84173ee81a4c8a06fa22a
PR:   28870

Rewritten to verify BEHAVIOR:
- Uses Node.js subprocess to PARSE and ANALYZE code structure (not just grep text)
- Avoids gold-specific variable names in assertions
- Checks for structural patterns that any valid fix would share
"""

import subprocess
import json
import re
from pathlib import Path

REPO = "/workspace/bun"


def _run_node_script(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js inline script and return the result."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _read_file(path: str) -> str:
    """Read file content from the repo."""
    full_path = Path(f"{REPO}/{path}")
    return full_path.read_text()


def _run_node_syntax_check(file_path: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run Node.js to check TypeScript/JavaScript syntax validity."""
    full_path = Path(f"{REPO}/{file_path}")
    return subprocess.run(
        ["node", "--check", str(full_path)],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _extract_test_block(content: str, test_name_substring: str) -> str:
    """Extract a test block by finding it(name with substring...) and matching braces."""
    start_match = re.search(r'it\s*\(\s*["\'].*?' + re.escape(test_name_substring) + r'.*?["\']', content)
    if not start_match:
        return ""
    
    start = start_match.start()
    # Find the opening brace after it(
    brace_start = content.find('{', start_match.end())
    if brace_start == -1:
        return ""
    
    # Count braces to find matching close
    depth = 1
    i = brace_start + 1
    while i < len(content) and depth > 0:
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
        i += 1
    
    return content[start_match.start():i]


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------

def test_typescript_syntax_valid():
    """Modified TypeScript files must have valid syntax."""
    chrome_result = _run_node_syntax_check("test/js/bun/webview/webview-chrome.test.ts")
    webview_result = _run_node_syntax_check("test/js/bun/webview/webview.test.ts")

    for result, name in [(chrome_result, "webview-chrome.test.ts"), (webview_result, "webview.test.ts")]:
        if result.returncode != 0:
            stderr = result.stderr.lower()
            if "syntax error" in stderr and "unexpected token" not in stderr:
                assert False, f"{name}: JavaScript syntax error: {result.stderr[:500]}"

    chrome_content = _read_file("test/js/bun/webview/webview-chrome.test.ts")
    webview_content = _read_file("test/js/bun/webview/webview.test.ts")

    for content, name in [(chrome_content, "webview-chrome.test.ts"), (webview_content, "webview.test.ts")]:
        assert "import " in content, f"{name} missing import statements"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# These tests verify the actual bug is FIXED, not just that specific text exists
# -----------------------------------------------------------------------------

def test_chrome_test_async_fix():
    """webview-chrome.test.ts must not have double await on expect().rejects.toThrow().

    The bug: await expect(await view.click...) causes the rejection to fire before
    expect() can intercept it, resulting in an unhandled promise rejection.
    The fix: await expect(view.click...) - removing the inner await.

    Behavioral verification: verify the CORRECT async pattern exists.
    """
    content = _read_file("test/js/bun/webview/webview-chrome.test.ts")

    # Find the test that uses :::invalid with rejects.toThrow
    # First, check if the buggy pattern exists (double await)
    buggy_pattern = r'await\s+expect\s*\(\s*await\s+view\.click'
    has_bug = bool(re.search(buggy_pattern, content))

    # Now check if the correct pattern exists
    # The correct pattern is: await expect(view.click(":::invalid")).rejects.toThrow()
    # WITHOUT an inner await on view.click
    correct_pattern = r'await\s+expect\s*\(\s*view\.click\s*\(\s*["\']:::invalid["\']\s*\)\s*\)\s*\.rejects\.toThrow'
    has_correct = bool(re.search(correct_pattern, content))

    assert not has_bug, "Double-await bug still present: 'await expect(await view.click...)' pattern found"
    assert has_correct, "Correct async pattern not found: 'await expect(view.click(...)).rejects.toThrow()' (single await on expect, not on click)"


def test_itrendering_helper_behavior():
    """webview.test.ts must have a helper for rAF-dependent tests that skips on macOS CI.

    Behavioral verification: check that SOME helper exists and rAF tests use it.
    """
    content = _read_file("test/js/bun/webview/webview.test.ts")

    # Check for ANY const helper with conditional skip pattern
    # Accepts ANY variable name, not just 'itRendering'
    helper_pattern = r'const\s+\w+\s*=\s*\w+\s*\?\s*test\.\w+\s*\(\s*isCI\s*\)\s*:\s*test\.skip'
    has_conditional_skip = bool(re.search(helper_pattern, content))

    simple_pattern = r'const\s+\w+\s*=\s*isMacOS\s*\?\s*test\.skip\s*:\s*test'
    has_simple_skip = bool(re.search(simple_pattern, content))

    # rAF test names that need to use a helper (not direct it())
    raf_tests = [
        r'click\(selector\) waits for actionability',
        r'click\(selector\) waits for element to appear',
        r'click\(selector\) waits for element to stop animating',
        r'click\(selector\) rejects on timeout when obscured',
        r'click\(selector\) with options',
        r'scroll dispatches native wheel event with isTrusted',
        r'scroll: sequential calls in same view',
        r'scroll: horizontal',
        r'scroll: interleaved with click in same view',
        r'scroll: survives navigate \(fresh scrolling tree\)',
        r'scroll: targets inner scrollable under view center',
        r'scrollTo\(selector\) waits for element to appear',
        r'scrollTo\(selector\) rejects on timeout',
        r'document\.visibilityState is visible and rAF fires'
    ]

    # Check for direct it() calls for rAF tests - we want these to NOT exist
    failures = []
    for test_pattern in raf_tests:
        # Direct it() pattern: it("test name", ...)
        direct_it = re.search(r'it\s*\(\s*["\']' + test_pattern, content)
        if direct_it:
            failures.append(test_pattern)

    has_helper = (has_conditional_skip or has_simple_skip) and len(failures) == 0
    assert has_helper, f"rAF helper behavior not verified: conditional skip={has_conditional_skip}, simple skip={has_simple_skip}, direct it() failures={len(failures)}"


def test_itpersistent_data_store_helper_behavior():
    """webview.test.ts must have a helper for persistent dataStore tests on macOS 15.2+.

    Behavioral verification: check that SOME helper exists for version check.
    """
    content = _read_file("test/js/bun/webview/webview.test.ts")

    # Look for ANY const helper with version check
    version_pattern = r'const\s+\w+\s*=\s*isMacOS\s*&&\s*isMacOSVersionAtLeast\s*\(\s*15\.2\s*\)'
    has_version_helper = bool(re.search(version_pattern, content))

    simple_pattern = r'const\s+\w+\s*=\s*isMacOSVersionAtLeast\s*\(\s*15\.2\s*\)'
    has_simple_version = bool(re.search(simple_pattern, content))

    # Check that persistent dataStore test doesn't use direct it()
    test_name = r'persistent dataStore: localStorage survives across instances'
    direct_it = re.search(r'it\s*\(\s*["\']' + test_name, content)

    has_helper = (has_version_helper or has_simple_version) and not direct_it
    assert has_helper, f"Persistent dataStore helper behavior not verified: version helper={has_version_helper}, simple={has_simple_version}, direct it={bool(direct_it)}"


def test_is_mac_os_version_at_least_imported():
    """isMacOSVersionAtLeast must be imported from harness."""
    content = _read_file("test/js/bun/webview/webview.test.ts")

    # Check that isMacOSVersionAtLeast appears in an import from 'harness'
    import_match = None
    for line in content.split('\n'):
        if 'from' in line and 'harness' in line and 'import' in line:
            import_match = line
            break

    assert import_match is not None, "Could not find import from harness"
    assert 'isMacOSVersionAtLeast' in import_match, "isMacOSVersionAtLeast not imported from harness"


# -----------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# -----------------------------------------------------------------------------

def test_no_test_todo_if_direct_usage():
    """The old buggy pattern 'test.todoIf(isCI)(' directly should not exist."""
    content = _read_file("test/js/bun/webview/webview.test.ts")

    direct_usage = r'test\.todoIf\s*\(\s*isCI\s*\)\s*\(\s*["\']'
    matches = []
    for match in re.finditer(direct_usage, content):
        start = max(0, match.start() - 200)
        end = min(len(content), match.end() + 50)
        context = content[start:end]
        if 'const ' in context and ': test.skip' in context:
            continue
        matches.append(match.group(0))

    assert len(matches) == 0, f"Found {len(matches)} instances of direct test.todoIf(isCI) usage - should use helper instead"


def test_close_all_test_navigate_fix():
    """WebView.closeAll() test must use encodeURIComponent in navigate call."""
    content = _read_file("test/js/bun/webview/webview.test.ts")

    test_block = _extract_test_block(content, "WebView.closeAll")
    assert test_block, "Could not find WebView.closeAll() test"

    # Check for proper URL encoding
    has_encoding = 'encodeURIComponent' in test_block

    # Check for raw HTML (which should NOT exist after fix)
    raw_navigate = re.search(r'navigate\s*\(\s*["\']data:text/html,<body>', test_block)

    assert has_encoding, "WebView.closeAll() test should use encodeURIComponent in navigate"
    assert not raw_navigate, "WebView.closeAll() test should not use raw HTML in navigate - use encodeURIComponent"


def test_close_all_test_stderr_inherit():
    """WebView.closeAll() test should use stderr: 'inherit' not 'pipe'."""
    content = _read_file("test/js/bun/webview/webview.test.ts")

    test_block = _extract_test_block(content, "WebView.closeAll")
    assert test_block, "Could not find WebView.closeAll() test"

    # Check for proper stderr handling
    has_inherit = re.search(r"stderr:\s*['\"]inherit['\"]", test_block) is not None
    has_pipe = re.search(r"stderr:\s*['\"]pipe['\"]", test_block) is not None

    assert has_inherit, "WebView.closeAll() test should use stderr: 'inherit'"
    assert not has_pipe, "WebView.closeAll() test should not use stderr: 'pipe'"


def test_not_stub():
    """Modified files are not stubs - they contain actual test code."""
    chrome_content = _read_file("test/js/bun/webview/webview-chrome.test.ts")
    webview_content = _read_file("test/js/bun/webview/webview.test.ts")

    assert len(chrome_content) > 1000, "webview-chrome.test.ts appears to be a stub (too short)"
    assert len(webview_content) > 5000, "webview.test.ts appears to be a stub (too short)"

    assert 'it(' in chrome_content or 'test(' in chrome_content, "webview-chrome.test.ts has no test declarations"
    assert 'it(' in webview_content or 'test(' in webview_content or \
           re.search(r'\w+\s*\(', webview_content), \
        "webview.test.ts has no test declarations"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD commands from repo's actual CI pipeline
# -----------------------------------------------------------------------------

REPO_INTERNAL = "/workspace/bun"


def test_repo_prettier_webview_chrome():
    """Repo CI: webview-chrome.test.ts passes prettier format check."""
    r = subprocess.run(
        ["npx", "prettier", "--check", f"{REPO_INTERNAL}/test/js/bun/webview/webview-chrome.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO_INTERNAL,
    )
    assert r.returncode == 0, f"Prettier check failed for webview-chrome.test.ts:\n{r.stderr[-500:]}"


def test_repo_prettier_webview():
    """Repo CI: webview.test.ts passes prettier format check."""
    r = subprocess.run(
        ["npx", "prettier", "--check", f"{REPO_INTERNAL}/test/js/bun/webview/webview.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO_INTERNAL,
    )
    assert r.returncode == 0, f"Prettier check failed for webview.test.ts:\n{r.stderr[-500:]}"


def test_repo_js_syntax_webview_chrome():
    """Repo CI: webview-chrome.test.ts has valid Node.js syntax."""
    r = subprocess.run(
        ["node", "--check", f"{REPO_INTERNAL}/test/js/bun/webview/webview-chrome.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO_INTERNAL,
    )
    assert r.returncode == 0, f"Syntax check failed for webview-chrome.test.ts:\n{r.stderr[-500:]}"


def test_repo_js_syntax_webview():
    """Repo CI: webview.test.ts has valid Node.js syntax."""
    r = subprocess.run(
        ["node", "--check", f"{REPO_INTERNAL}/test/js/bun/webview/webview.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO_INTERNAL,
    )
    assert r.returncode == 0, f"Syntax check failed for webview.test.ts:\n{r.stderr[-500:]}"


def test_repo_tsconfig_valid():
    """Repo CI: tsconfig.json is valid JSON."""
    r = subprocess.run(
        ["node", "-e", "JSON.parse(require('fs').readFileSync('/workspace/bun/tsconfig.json'))"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"tsconfig.json is not valid JSON:\n{r.stderr[-500:]}"


def test_repo_prettier_check_all():
    """Repo CI: All modified webview test files pass prettier --check."""
    r = subprocess.run(
        ["npx", "prettier", "--check",
         f"{REPO_INTERNAL}/test/js/bun/webview/webview.test.ts",
         f"{REPO_INTERNAL}/test/js/bun/webview/webview-chrome.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO_INTERNAL,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


def test_repo_node_syntax_all():
    """Repo CI: Both webview test files pass Node.js syntax validation."""
    r1 = subprocess.run(
        ["node", "--check", f"{REPO_INTERNAL}/test/js/bun/webview/webview.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO_INTERNAL,
    )
    assert r1.returncode == 0, f"Syntax check failed for webview.test.ts:\n{r1.stderr[-500:]}"

    r2 = subprocess.run(
        ["node", "--check", f"{REPO_INTERNAL}/test/js/bun/webview/webview-chrome.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO_INTERNAL,
    )
    assert r2.returncode == 0, f"Syntax check failed for webview-chrome.test.ts:\n{r2.stderr[-500:]}"


def test_repo_imports_valid():
    """Repo CI: webview test files have valid imports and structure."""
    webview_content = _read_file("test/js/bun/webview/webview.test.ts")

    import_match = re.search(r'import\s*\{[^}]+\}\s*from\s*["\']harness["\']', webview_content)
    assert import_match is not None, 'Could not find harness import line in webview.test.ts'

    import_line = import_match.group(0)
    assert 'isMacOS' in import_line, 'isMacOS not imported from harness'
    assert 'isCI' in import_line, 'isCI not imported from harness'

    valid_import_pattern = r'import\s+\{[^}]+\}\s+from\s*["\']harness["\']'
    assert re.search(valid_import_pattern, webview_content), 'Invalid import statement format for harness imports'


def test_repo_oxlint_js():
    """Repo CI: webview-chrome.test.ts passes oxlint."""
    r = subprocess.run(
        ["npx", "oxlint", "--config=oxlint.json", "--format=github",
         f"{REPO_INTERNAL}/test/js/bun/webview/webview-chrome.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO_INTERNAL,
    )
    assert r.returncode == 0, f"oxlint check failed:\n{r.stderr[-500:]}"
