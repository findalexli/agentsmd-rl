"""
Tests for trpc PR #7233: Fix to preserve buffered chunks on stream close.

The bug was that controller.error() was being called on both stream close and abort,
which discards buffered chunks. The fix separates:
- handleClose(): closes controllers gracefully (preserving buffered data)
- handleAbort(): errors controllers (for cancellation scenarios)
"""

import subprocess
import sys
import os

REPO = "/workspace/trpc"
STREAM_FILE = f"{REPO}/packages/server/src/unstable-core-do-not-import/stream/jsonl.ts"


def test_gold_patch_applied():
    """Verify the fix has been applied - handleClose function exists with correct logic."""
    with open(STREAM_FILE, 'r') as f:
        content = f.read()

    # Check for the key fix: handleClose function
    assert "const handleClose = () => {" in content, "handleClose function not found"

    # Check that handleClose calls closeAll (preserves buffered chunks)
    assert "streamManager.closeAll()" in content, "closeAll call not found in handleClose"

    # Check that stream closing before head rejects with proper error message
    assert "Stream closed before head was received" in content, "Error message not found"

    # Check for the closeAll function definition
    assert "function closeAll() {" in content, "closeAll function not found"
    assert "controller.close()" in content, "controller.close() call not found"


def test_closeAll_closes_controllers():
    """Test that closeAll() properly closes controllers (not errors them)."""
    with open(STREAM_FILE, 'r') as f:
        content = f.read()

    # Verify closeAll iterates over controllers and calls .close() (not .error())
    assert "for (const controller of controllerMap.values())" in content, "controller iteration not found"

    # The fix should NOT call controller.error() in closeAll
    # (error() discards buffered chunks, close() preserves them)
    lines = content.split('\n')
    in_close_all = False
    close_all_brace_count = 0
    found_controller_close = False

    for line in lines:
        if "function closeAll() {" in line:
            in_close_all = True
            close_all_brace_count = 1
            continue

        if in_close_all:
            if '{' in line:
                close_all_brace_count += line.count('{')
            if '}' in line:
                close_all_brace_count -= line.count('}')

            if "controller.close()" in line:
                found_controller_close = True

            if close_all_brace_count <= 0 and '}' in line:
                in_close_all = False

    assert found_controller_close, "controller.close() not found in closeAll function"


def test_handleClose_vs_handleAbort_separation():
    """Test that handleClose and handleAbort are separate functions with different behaviors."""
    with open(STREAM_FILE, 'r') as f:
        content = f.read()

    # Both functions should exist
    assert "const handleClose = () => {" in content, "handleClose not found"
    assert "const handleAbort = (reason?: unknown) => {" in content, "handleAbort not found"

    # handleClose should call closeAll (preserves buffered chunks)
    # Find handleClose function and check it calls closeAll
    lines = content.split('\n')
    in_handle_close = False
    handle_close_brace_count = 0
    found_close_all_in_handle_close = False
    found_reject_in_handle_close = False

    for line in lines:
        if "const handleClose = () => {" in line:
            in_handle_close = True
            handle_close_brace_count = 1
            continue

        if in_handle_close:
            if '{' in line:
                handle_close_brace_count += line.count('{')
            if '}' in line:
                handle_close_brace_count -= line.count('}')

            if "streamManager.closeAll()" in line:
                found_close_all_in_handle_close = True
            if "headDeferred.reject" in line and "Stream closed" in line:
                found_reject_in_handle_close = True

            if handle_close_brace_count <= 0 and '}' in line:
                in_handle_close = False

    assert found_close_all_in_handle_close, "closeAll not called in handleClose"
    assert found_reject_in_handle_close, "headDeferred.reject not found in handleClose"


def test_handleAbort_cancels_all():
    """Test that handleAbort properly calls cancelAll (error propagation)."""
    with open(STREAM_FILE, 'r') as f:
        content = f.read()

    # handleAbort should call cancelAll
    lines = content.split('\n')
    in_handle_abort = False
    handle_abort_brace_count = 0
    found_cancel_all = False

    for line in lines:
        if "const handleAbort = (reason?: unknown) => {" in line:
            in_handle_abort = True
            handle_abort_brace_count = 1
            continue

        if in_handle_abort:
            if '{' in line:
                handle_abort_brace_count += line.count('{')
            if '}' in line:
                handle_abort_brace_count -= line.count('}')

            if "streamManager.cancelAll(reason)" in line:
                found_cancel_all = True

            if handle_abort_brace_count <= 0 and '}' in line:
                in_handle_abort = False

    assert found_cancel_all, "cancelAll not called in handleAbort"


def test_stream_hooks_use_correct_handlers():
    """Test that stream.close uses handleClose and stream.abort uses handleAbort."""
    with open(STREAM_FILE, 'r') as f:
        content = f.read()

    # Check that the stream uses the correct handlers
    # Looking for: close: handleClose, abort: handleAbort
    assert "close: handleClose," in content, "close hook not using handleClose"
    assert "abort: handleAbort," in content, "abort hook not using handleAbort"


def test_headDeferred_null_after_reject():
    """Test that headDeferred is set to null after rejection to prevent double-rejection."""
    with open(STREAM_FILE, 'r') as f:
        content = f.read()

    # Both handlers should set headDeferred = null after rejecting
    lines = content.split('\n')

    for func_name in ["handleClose", "handleAbort"]:
        in_func = False
        brace_count = 0
        found_reject = False
        found_null_assignment = False
        null_after_reject = False

        for line in lines:
            if f"const {func_name} = " in line:
                in_func = True
                brace_count = 1
                continue

            if in_func:
                if '{' in line:
                    brace_count += line.count('{')
                if '}' in line:
                    brace_count -= line.count('}')

                if "headDeferred?.reject" in line or "headDeferred.reject" in line:
                    found_reject = True

                if found_reject and "headDeferred = null" in line:
                    found_null_assignment = True
                    null_after_reject = True

                if brace_count <= 0 and '}' in line:
                    in_func = False
                    break

        assert found_reject, f"headDeferred.reject not found in {func_name}"
        assert found_null_assignment, f"headDeferred = null not found in {func_name}"


def test_catch_block_uses_handleAbort():
    """Test that the catch block uses handleAbort (not handleClose) for errors."""
    with open(STREAM_FILE, 'r') as f:
        content = f.read()

    # Find the catch block and verify it calls handleAbort
    lines = content.split('\n')
    in_catch = False
    catch_brace_count = 0
    found_handle_abort_in_catch = False

    for line in lines:
        if ".catch((error) => {" in line or ".catch((error)" in line:
            in_catch = True
            catch_brace_count = 1
            continue

        if in_catch:
            if '{' in line:
                catch_brace_count += line.count('{')
            if '}' in line:
                catch_brace_count -= line.count('}')

            if "handleAbort(error)" in line:
                found_handle_abort_in_catch = True

            if catch_brace_count <= 0:
                in_catch = False

    assert found_handle_abort_in_catch, "handleAbort not called in catch block"


def test_repo_vitest_jsonl_unit_tests():
    """Repo's jsonl stream unit tests pass (pass_to_pass).

    Runs the jsonl.test.ts file which directly tests the streaming
    functionality that was modified in the PR.
    """
    result = subprocess.run(
        ["pnpm", "vitest", "run", "jsonl.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"jsonl tests failed:\n{result.stderr[-500:]}"


def test_repo_vitest_server_unit_tests():
    """Repo's @trpc/server package unit tests pass (pass_to_pass).

    Runs all unit tests for the @trpc/server package, including
    jsonl.test.ts, sse.test.ts, and other stream-related tests.
    """
    result = subprocess.run(
        ["pnpm", "vitest", "run", "--project=@trpc/server"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Server package tests failed:\n{result.stderr[-500:]}"


def test_repo_vitest_streaming_integration_tests():
    """Repo's streaming integration tests pass (pass_to_pass).

    Runs streaming.test.ts which tests httpBatchStreamLink and other
    streaming-related integration scenarios.
    """
    result = subprocess.run(
        ["pnpm", "vitest", "run", "streaming.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"Streaming tests failed:\n{result.stderr[-500:]}"


def test_repo_server_typecheck():
    """Repo's @trpc/server package typecheck passes (pass_to_pass).

    Runs TypeScript type checking on the @trpc/server package
    to ensure no type errors in the modified code.
    """
    result = subprocess.run(
        ["pnpm", "--filter=@trpc/server", "run", "typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"TypeScript typecheck failed:\n{result.stderr[-500:]}"


def test_repo_server_lint():
    """Repo's @trpc/server package lint passes (pass_to_pass).

    Runs ESLint on the @trpc/server package to ensure
    code follows the project's style guidelines.
    """
    result = subprocess.run(
        ["pnpm", "run", "lint", "--filter=@trpc/server"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stderr[-500:]}"


def test_repo_vitest_stream_unit_tests():
    """[DEPRECATED] Kept for backwards compatibility."""
    result = subprocess.run(
        ["pnpm", "vitest", "run", "jsonl.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"jsonl tests failed:\n{result.stderr[-500:]}"


def test_typescript_compiles():
    """[DEPRECATED] Use test_repo_server_typecheck instead."""
    result = subprocess.run(
        ["pnpm", "--filter=@trpc/server", "run", "typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"TypeScript typecheck failed:\n{result.stderr[-500:]}"


def test_import_type_usage():
    """Agent config: Uses import type for type-only imports (coding-guidelines.mdc)."""
    with open(STREAM_FILE, 'r') as f:
        content = f.read()

    # Check for proper import type usage
    # The file should have 'import type' for type-only imports
    assert "import type" in content, "File should use 'import type' for type imports"

    # Check that Deferred type import uses import type
    lines = content.split('\n')
    found_deferred_type_import = False
    for line in lines:
        if 'import type { Deferred }' in line or 'import type' in line and 'Deferred' in line:
            found_deferred_type_import = True
            break

    # The file imports Deferred as a type
    assert found_deferred_type_import, "Should use 'import type' for Deferred"


def test_no_function_destructuring():
    """Agent config: Avoids destructuring in function parameter declarations (coding-guidelines.mdc)."""
    with open(STREAM_FILE, 'r') as f:
        content = f.read()

    # Check for destructuring in function parameters (pattern like `function foo({a, b})`)
    import re

    # Look for function parameters with destructuring
    # Pattern: function name({ ... }) or const name = ({ ... }) =>
    func_destruct_pattern = r'(?:function\s+\w+|const\s+\w+\s*=)\s*\(\s*\{[^}]*\}'
    matches = re.findall(func_destruct_pattern, content)

    # The file should NOT have function parameter destructuring
    # We allow destructuring in body, just not in parameter declarations
    for match in matches:
        # Skip if it's in the function body (not parameter list)
        continue

    # This is a soft check - we just verify the pattern is not present in params
    # The actual destructuring check is more nuanced
    lines = content.split('\n')
    for line in lines:
        # Check function declarations with destructured params
        if re.search(r'function\s+\w+\s*\(\s*\{', line):
            raise AssertionError(f"Function parameter destructuring found: {line}")
        # Check arrow functions with destructured params
        if re.search(r'const\s+\w+\s*=\s*\(\s*\{', line):
            raise AssertionError(f"Arrow function parameter destructuring found: {line}")


def test_max_3_parameters():
    """Agent config: Functions have at most 3 parameters (coding-guidelines.mdc)."""
    with open(STREAM_FILE, 'r') as f:
        content = f.read()

    import re

    # Find all function declarations and count parameters
    # Pattern 1: function name(p1, p2, p3) or async function name(p1, p2)
    func_pattern = r'(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)'
    # Pattern 2: const name = (p1, p2) => or const name = async (p1) =>
    arrow_pattern = r'const\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>'

    for match in re.finditer(func_pattern, content):
        func_name = match.group(1)
        params_str = match.group(2).strip()

        # Skip if no params or empty
        if not params_str:
            continue

        # Count parameters (handle multiline, default values, etc.)
        # Simple count: split by comma, but be careful with object literals
        param_count = len([p for p in params_str.split(',') if p.strip()])

        if param_count > 3:
            # Allow if it has a well-defined options object pattern
            if 'opts' in params_str or 'options' in params_str:
                continue
            raise AssertionError(
                f"Function '{func_name}' has {param_count} parameters (max 3 allowed per coding guidelines)"
            )

    for match in re.finditer(arrow_pattern, content):
        func_name = match.group(1)
        params_str = match.group(2).strip()

        if not params_str:
            continue

        param_count = len([p for p in params_str.split(',') if p.strip()])

        if param_count > 3:
            if 'opts' in params_str or 'options' in params_str:
                continue
            raise AssertionError(
                f"Arrow function '{func_name}' has {param_count} parameters (max 3 allowed per coding guidelines)"
            )


def test_pnpm_used():
    """Agent config: Uses pnpm as package manager (pnpm.mdc)."""
    # Check that pnpm is available and preferred
    result = subprocess.run(
        ["which", "pnpm"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "pnpm should be installed"


def test_no_src_imports():
    """Agent config: Never import from @trpc/*/src (coding-guidelines.mdc)."""
    with open(STREAM_FILE, 'r') as f:
        content = f.read()

    # Check that there are no imports from @trpc/*/src paths
    import re
    src_import_pattern = r'from\s+[\'"]@trpc/[^\'"]+/src/[^\'"]*[\'"]'
    matches = re.findall(src_import_pattern, content)

    if matches:
        raise AssertionError(f"Found forbidden @trpc/*/src imports: {matches}")
