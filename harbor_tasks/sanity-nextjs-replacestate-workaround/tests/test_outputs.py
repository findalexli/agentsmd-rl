"""Tests for Next.js replaceState bug workaround in auth store."""

import subprocess
import re
import os

REPO = "/workspace/sanity"


def test_build_passes():
    """Repo builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-1000:]}"


def test_typescript_types():
    """TypeScript type checking passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "check:types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Type check failed:\n{r.stderr[-1000:]}"


def test_repo_oxlint():
    """Oxlint passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "check:oxlint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Oxlint failed:\n{r.stderr[-500:]}"


def test_repo_format():
    """Code format check passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "check:format"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


def test_repo_exports():
    """Export tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "test:exports"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Export tests failed:\n{r.stderr[-500:]}"


def test_repo_depcheck():
    """Dependency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "depcheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Dependency check failed:\n{r.stderr[-500:]}"


def test_clear_session_id_exported():
    """clearSessionId function is exported from sessionId.ts (fail_to_pass).

    The fix adds a new exported function clearSessionId() that calls
    consumeSessionId() to work around the Next.js replaceState bug.
    """
    session_id_path = os.path.join(
        REPO,
        "packages/sanity/src/core/store/_legacy/authStore/sessionId.ts"
    )
    with open(session_id_path, 'r') as f:
        content = f.read()

    # Check that clearSessionId is exported
    assert "export function clearSessionId()" in content, \
        "clearSessionId function should be exported from sessionId.ts"

    # Check that it calls consumeSessionId
    clear_func_pattern = r'export function clearSessionId\(\):\s*void\s*\{[^}]*consumeSessionId\(\)'
    assert re.search(clear_func_pattern, content, re.DOTALL), \
        "clearSessionId should call consumeSessionId()"

    # Check for the workaround comment
    assert "github.com/vercel/next.js/issues/91819" in content, \
        "Should include reference to the Next.js issue being worked around"


def test_clear_session_id_imported_in_auth_store():
    """clearSessionId is imported in createAuthStore.ts (fail_to_pass).

    The fix imports clearSessionId alongside getSessionId in createAuthStore.ts.
    """
    auth_store_path = os.path.join(
        REPO,
        "packages/sanity/src/core/store/_legacy/authStore/createAuthStore.ts"
    )
    with open(auth_store_path, 'r') as f:
        content = f.read()

    # Check that clearSessionId is imported from sessionId
    import_pattern = r'import\s*\{[^}]*clearSessionId[^}]*\}\s*from\s*[\'"]\.\/sessionId[\'"]'
    assert re.search(import_pattern, content), \
        "clearSessionId should be imported from './sessionId' in createAuthStore.ts"

    # Also verify getSessionId is still imported
    assert "getSessionId" in content, \
        "getSessionId should still be imported"


def test_clear_session_id_called_in_handle_callback():
    """clearSessionId is called after getSessionId in handleCallbackUrl (fail_to_pass).

    The fix calls clearSessionId() immediately after getSessionId() in the
    handleCallbackUrl function to work around the Next.js replaceState bug
    that calls replaceState twice.
    """
    auth_store_path = os.path.join(
        REPO,
        "packages/sanity/src/core/store/_legacy/authStore/createAuthStore.ts"
    )
    with open(auth_store_path, 'r') as f:
        content = f.read()

    # Find the handleCallbackUrl function
    handle_callback_pattern = r'async function handleCallbackUrl\(\)[^{]*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
    match = re.search(handle_callback_pattern, content, re.DOTALL)
    assert match, "handleCallbackUrl function should exist"

    func_body = match.group(1)

    # Check that getSessionId is called
    assert "getSessionId()" in func_body, \
        "getSessionId() should be called in handleCallbackUrl"

    # Check that clearSessionId is called after getSessionId
    # Look for the pattern where clearSessionId is called after getSessionId
    clear_after_get = r'const sessionId = getSessionId\(\)[^;]*;\s*//[^\n]*github\.com/vercel/next\.js/issues/91819[^\n]*\n\s*clearSessionId\(\)'
    assert re.search(clear_after_get, func_body, re.DOTALL) or \
           ("clearSessionId()" in func_body and func_body.find("getSessionId()") < func_body.find("clearSessionId()")), \
        "clearSessionId() should be called after getSessionId() in handleCallbackUrl with the workaround comment"


def test_session_id_function_behavior():
    """Test that clearSessionId properly calls consumeSessionId (fail_to_pass).

    This test verifies the actual behavior of the workaround function by
    examining that it properly wraps consumeSessionId().
    """
    session_id_path = os.path.join(
        REPO,
        "packages/sanity/src/core/store/_legacy/authStore/sessionId.ts"
    )
    with open(session_id_path, 'r') as f:
        content = f.read()

    # Extract the clearSessionId function
    func_match = re.search(
        r'export function clearSessionId\(\):\s*void\s*\{([^}]+)\}',
        content
    )
    assert func_match, "clearSessionId function should be defined"

    func_body = func_match.group(1).strip()

    # The function should just call consumeSessionId()
    assert "consumeSessionId()" in func_body, \
        "clearSessionId should call consumeSessionId()"

    # The function body should be simple (just the call)
    # Allow for comments but should essentially just call consumeSessionId
    lines = [l.strip() for l in func_body.split('\n') if l.strip() and not l.strip().startswith('//')]
    assert len(lines) == 1 and lines[0] == "consumeSessionId()", \
        "clearSessionId should be a simple wrapper that calls consumeSessionId()"
