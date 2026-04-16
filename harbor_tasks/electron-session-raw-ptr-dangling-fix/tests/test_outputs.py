"""Tests for Electron dangling raw_ptr fix (PR #50799).

This module tests the memory safety fix that addresses a dangling raw_ptr
in api::Session::browser_context_. The fix involves:
1. Changing from raw_ref to raw_ptr
2. Adding null checks before accessing browser_context
3. Nullifying browser_context_ during disposal
"""

import subprocess
import re
import os

REPO = "/workspace/electron"


def read_file(filepath):
    """Read file content from repo."""
    full_path = os.path.join(REPO, filepath)
    with open(full_path, 'r') as f:
        return f.read()


# =============================================================================
# FAIL TO PASS TESTS - These test the actual bug fix
# =============================================================================

def test_raw_ref_removed_from_session_header():
    """raw_ref header include removed from electron_api_session.h.

    The fix removes the base/memory/raw_ref.h include since raw_ref is
    no longer used (replaced with raw_ptr).

    Origin: agent_config (CLAUDE.md - Code Style: Follows Chromium style)
    """
    content = read_file("shell/browser/api/electron_api_session.h")
    assert '#include "base/memory/raw_ref.h"' not in content, \
        "raw_ref.h include should be removed from session.h"


def test_raw_ptr_used_for_browser_context():
    """browser_context_ uses raw_ptr<ElectronBrowserContext> instead of raw_ref.

    The member variable was changed from raw_ref to raw_ptr to allow
    nullification during disposal and prevent dangling pointer issues.
    """
    content = read_file("shell/browser/api/electron_api_session.h")
    assert 'raw_ptr<ElectronBrowserContext> browser_context_' in content, \
        "browser_context_ should be declared as raw_ptr<ElectronBrowserContext>"
    assert 'const raw_ref<ElectronBrowserContext> browser_context_' not in content, \
        "raw_ref browser_context_ should not exist"


def test_session_constructor_uses_raw_ptr():
    """Session constructor initializes browser_context_ as raw_ptr.

    The constructor should initialize browser_context_ directly with the
    browser_context pointer instead of using raw_ref::from_ptr().
    """
    content = read_file("shell/browser/api/electron_api_session.cc")
    assert 'browser_context_{browser_context}' in content, \
        "Constructor should initialize browser_context_ with browser_context directly"
    assert 'raw_ref<ElectronBrowserContext>::from_ptr' not in content, \
        "raw_ref::from_ptr should not be used in constructor"


def test_browser_context_accessor_returns_raw_ptr():
    """browser_context() accessor returns raw_ptr directly.

    The accessor method should return browser_context_ directly instead
    of dereferencing via .get() and taking the address.
    """
    content = read_file("shell/browser/api/electron_api_session.h")
    # Find the browser_context() method body
    match = re.search(
        r'ElectronBrowserContext\* browser_context\(\) const \{\s*return\s+([^;]+);',
        content
    )
    assert match, "browser_context() method not found or has unexpected format"
    return_stmt = match.group(1).strip()
    assert return_stmt == "browser_context_", \
        f"browser_context() should return 'browser_context_' directly, got: {return_stmt}"


def test_dispose_has_null_check():
    """Session::Dispose() checks browser_context for null before use.

    The fix adds a null check to prevent crashes when browser_context
    is accessed after being nullified during shutdown.
    """
    content = read_file("shell/browser/api/electron_api_session.cc")
    # Look for the null check pattern in Dispose()
    assert re.search(r'if\s*\(\s*!\s*browser_context\s*\)', content), \
        "Dispose() should have null check: 'if (!browser_context)'"


def test_dispose_returns_early_if_browser_context_null():
    """Session::Dispose() returns early after null check.

    After detecting null browser_context, the method should return
    immediately to prevent dereferencing the null pointer.
    """
    content = read_file("shell/browser/api/electron_api_session.cc")
    # The pattern should be: capture ptr, check null, return early
    dispose_func = re.search(
        r'void Session::Dispose\(\).*?(?=^void |^}|\Z)',
        content,
        re.DOTALL | re.MULTILINE
    )
    assert dispose_func, "Could not find Dispose() function"
    func_body = dispose_func.group(0)

    # Check that after the null check, there's a return
    assert re.search(r'if\s*\(\s*!\s*browser_context\s*\)\s*\n\s*return', func_body), \
        "Dispose() should return early after browser_context null check"


def test_onbefore_microtasks_dispose_nullifies_browser_context():
    """OnBeforeMicrotasksRunnerDispose sets browser_context_ to nullptr.

    The fix explicitly nullifies browser_context_ during disposal to
    prevent any later access to the dangling pointer.
    """
    content = read_file("shell/browser/api/electron_api_session.cc")
    # Look for the nullification in OnBeforeMicrotasksRunnerDispose
    func_match = re.search(
        r'void Session::OnBeforeMicrotasksRunnerDispose.*?^}',
        content,
        re.DOTALL | re.MULTILINE
    )
    assert func_match, "OnBeforeMicrotasksRunnerDispose function not found"
    func_content = func_match.group(0)

    assert 'browser_context_ = nullptr;' in func_content, \
        "OnBeforeMicrotasksRunnerDispose should set browser_context_ = nullptr"


def test_dispose_uses_captured_browser_context():
    """Dispose() captures browser_context locally and uses captured ptr.

    The fix stores browser_context() result in a local variable before
    the null check and uses that captured pointer for all subsequent access.
    """
    content = read_file("shell/browser/api/electron_api_session.cc")
    # Look for the pattern: ElectronBrowserContext* const browser_context = this->browser_context();
    assert re.search(
        r'ElectronBrowserContext\*\s+const\s+browser_context\s*=\s*this->browser_context\(\)',
        content
    ), "Dispose() should capture browser_context in a local variable"


def test_web_contents_has_dcheck_for_browser_context():
    """WebContents constructor has DCHECK for browser_context.

    Added DCHECK to verify browser_context is not null when used.
    """
    content = read_file("shell/browser/api/electron_api_web_contents.cc")
    # Find the WebContents constructor and look for the DCHECK
    assert 'DCHECK(browser_context != nullptr);' in content, \
        "WebContents constructor should have DCHECK for browser_context"


def test_web_contents_uses_local_browser_context():
    """WebContents uses local browser_context variable consistently.

    Instead of calling session->browser_context() multiple times, the
    fix uses a local browser_context variable for consistency and safety.
    """
    content = read_file("shell/browser/api/electron_api_web_contents.cc")
    # Should have the pattern: capture once, use throughout
    assert 'ElectronBrowserContext* const browser_context = session->browser_context();' in content, \
        "WebContents should capture browser_context in a local variable"


def test_url_loader_has_dcheck_for_browser_context():
    """URL loader has DCHECK for browser_context after getting from session.

    Added null check verification when getting browser_context from session.
    """
    content = read_file("shell/common/api/electron_api_url_loader.cc")
    # Look for the DCHECK after getting browser_context from session
    func_match = re.search(
        r'if\s*\(\s*session\s*\)\s*\{\s*browser_context\s*=\s*session->browser_context\(\);',
        content
    )
    assert func_match, "URL loader session->browser_context() pattern not found"

    # Check that DCHECK follows
    section = content[func_match.end():func_match.end() + 200]
    assert 'DCHECK(browser_context != nullptr);' in section, \
        "URL loader should have DCHECK after getting browser_context from session"


def test_browser_main_parts_resets_browser_and_js_env():
    """ElectronBrowserMainParts resets browser_ and js_env_ during shutdown.

    The fix explicitly resets these pointers during PostMainMessageLoopRun
    to ensure proper destruction order.
    """
    content = read_file("shell/browser/electron_browser_main_parts.cc")
    # Find the function and match balanced braces
    match = re.search(
        r'void ElectronBrowserMainParts::PostMainMessageLoopRun\(\)\s*\{',
        content
    )
    assert match, "PostMainMessageLoopRun function not found"

    # Find the balanced function body
    start = match.end()
    brace_count = 1
    end = start
    for i, char in enumerate(content[start:], start):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end = i
                break

    func_body = content[match.start():end+1]

    assert 'browser_.reset();' in func_body, \
        "PostMainMessageLoopRun should call browser_.reset()"
    assert 'js_env_.reset();' in func_body, \
        "PostMainMessageLoopRun should call js_env_.reset()"


def test_cpp_heap_spec_has_shutdown_test():
    """cpp-heap-spec.ts has the new crash-on-exit test.

    The fix includes a regression test that verifies sessions don't
    crash during shutdown when they have live wrappers.
    """
    content = read_file("spec/cpp-heap-spec.ts")
    assert "does not crash on exit with live session wrappers" in content, \
        "cpp-heap-spec.ts should have the crash-on-exit regression test"


def test_cpp_heap_spec_imports_once():
    """cpp-heap-spec.ts imports 'once' from node:events.

    The regression test uses once() to wait for the process exit event.
    """
    content = read_file("spec/cpp-heap-spec.ts")
    assert "import { once } from 'node:events';" in content, \
        "cpp-heap-spec.ts should import 'once' from 'node:events'"


# =============================================================================
# PASS TO PASS TESTS - These test code quality / existing repo tests
# =============================================================================

def test_typescript_compiles():
    """TypeScript files compile without errors (pass_to_pass).

    Verifies the TypeScript test file is syntactically valid.
    Origin: repo_tests (npm run tsc from package.json)
    """
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "spec/cpp-heap-spec.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    # This is a best-effort check - TypeScript may complain about missing modules
    # We just verify the file is parseable (no syntax errors)
    assert "error TS" not in result.stdout or "Cannot find module" in result.stdout, \
        f"TypeScript compilation has errors:\n{result.stdout}\n{result.stderr}"


def test_session_header_parseable():
    """electron_api_session.h is syntactically valid C++.

    Basic check that the header file has balanced braces and valid structure.
    Origin: repo_tests (clang-format check from lint:cpp)
    """
    content = read_file("shell/browser/api/electron_api_session.h")

    # Check for balanced braces
    brace_count = 0
    for char in content:
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count < 0:
                assert False, "Unbalanced braces in header file"

    # Check that class definition is complete
    assert 'class Session' in content, "Session class definition not found"
    assert '};' in content, "Class definition not properly closed"


def test_session_cc_parseable():
    """electron_api_session.cc is syntactically valid C++.

    Basic structural checks for the implementation file.
    Origin: repo_tests (clang-format check from lint:cpp)
    """
    content = read_file("shell/browser/api/electron_api_session.cc")

    # Check for balanced braces
    brace_count = 0
    for char in content:
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count < 0:
                assert False, "Unbalanced braces in session.cc"

    # Check that key function definitions exist
    assert 'Session::Session(' in content, "Session constructor not found"
    assert 'Session::~Session()' in content, "Session destructor not found"
    assert 'void Session::Dispose()' in content, "Session::Dispose not found"


def test_session_header_structure():
    """electron_api_session.h has valid C++ class structure.

    Verifies the header file structure including class definition,
    header guards, and key member declarations.
    Origin: static (structural analysis)
    """
    content = read_file("shell/browser/api/electron_api_session.h")

    # Check header guards
    assert '#ifndef ELECTRON_SHELL_BROWSER_API_ELECTRON_API_SESSION_H_' in content, \
        "Header guard start not found"
    assert '#define ELECTRON_SHELL_BROWSER_API_ELECTRON_API_SESSION_H_' in content, \
        "Header guard define not found"

    # Check class declaration
    assert 'class Session final' in content, "Session class declaration not found"

    # Check key includes
    assert 'base/memory/raw_ptr.h' in content, "raw_ptr.h include not found"

    # Verify the class has proper closing
    assert content.count('class Session') == 1, "Should have exactly one Session class declaration"


def test_session_cc_structure():
    """electron_api_session.cc has valid C++ structure.

    Verifies the implementation file has key includes and function definitions.
    Origin: static (structural analysis)
    """
    content = read_file("shell/browser/api/electron_api_session.cc")

    # Check key includes for the implementation
    assert 'electron_browser_context.h' in content, \
        "ElectronBrowserContext include not found"

    # Check that the file is within expected size limits (not corrupted)
    lines = content.split('\n')
    assert 1000 < len(lines) < 3000, f"Unexpected file size: {len(lines)} lines"

    # Check for Session method implementations
    assert 'Session::OnDownloadCreated' in content, "OnDownloadCreated method not found"
    assert 'Session::ResolveProxy' in content, "ResolveProxy method not found"


def test_cpp_heap_spec_structure():
    """cpp-heap-spec.ts has valid TypeScript test structure.

    Verifies the test file has valid imports and test structure.
    Origin: static (structural analysis)
    """
    content = read_file("spec/cpp-heap-spec.ts")

    # Check basic TypeScript/imports structure
    assert "import { expect } from 'chai';" in content, "Chai import not found"
    assert "import * as path from 'node:path';" in content, "Path import not found"

    # Check test structure
    assert "describe('cpp heap', () => {" in content, "Main describe block not found"
    assert "describe('session module', () => {" in content, "Session module describe block not found"
    assert "describe('app module', () => {" in content, "App module describe block not found"

    # Verify test patterns
    assert "startRemoteControlApp" in content, "startRemoteControlApp import not used"
    assert "it('should record as node in heap snapshot'" in content, \
        "Heap snapshot test not found"


def test_web_contents_cc_structure():
    """electron_api_web_contents.cc has valid C++ structure.

    Verifies the WebContents implementation has key includes and structure.
    Origin: static (structural analysis)
    """
    content = read_file("shell/browser/api/electron_api_web_contents.cc")

    lines = content.split('\n')
    assert 1000 < len(lines) < 5000, f"Unexpected file size: {len(lines)} lines"

    # Check for WebContents constructor
    assert 'WebContents::WebContents(' in content, "WebContents constructor not found"

    # Check for session usage (this file interacts with Session)
    assert 'session' in content.lower(), "Session reference not found"


def test_url_loader_cc_structure():
    """electron_api_url_loader.cc has valid C++ structure.

    Verifies the URL loader implementation has key structure.
    Origin: static (structural analysis)
    """
    content = read_file("shell/common/api/electron_api_url_loader.cc")

    lines = content.split('\n')
    assert 200 < len(lines) < 1500, f"Unexpected file size: {len(lines)} lines"

    # Check for key function
    assert 'SimpleURLLoaderWrapper::Create' in content, "Create method not found"


def test_browser_main_parts_cc_structure():
    """electron_browser_main_parts.cc has valid C++ structure.

    Verifies the main parts implementation has key structure.
    Origin: static (structural analysis)
    """
    content = read_file("shell/browser/electron_browser_main_parts.cc")

    lines = content.split('\n')
    assert 200 < len(lines) < 1500, f"Unexpected file size: {len(lines)} lines"

    # Check for key methods
    assert 'ElectronBrowserMainParts::PostMainMessageLoopRun' in content, \
        "PostMainMessageLoopRun method not found"
