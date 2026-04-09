"""Tests for user-actions popup menu display fix.

This test validates that the UserActions component displays the popup menu
regardless of authentication state, fixing a regression in OSS mode.
"""

import subprocess
import os
import re

REPO = "/workspace/OpenHands"
USER_ACTIONS_FILE = f"{REPO}/frontend/src/components/features/sidebar/user-actions.tsx"


def test_use_should_show_user_features_hook_removed():
    """Verify useShouldShowUserFeatures hook is no longer imported or used (fail-to-pass)."""
    with open(USER_ACTIONS_FILE, 'r') as f:
        content = f.read()

    # The fix removes this import
    assert "useShouldShowUserFeatures" not in content, \
        "useShouldShowUserFeatures hook should be removed from user-actions.tsx"


def test_context_menu_always_rendered():
    """Verify UserContextMenu is always rendered, not conditionally (fail-to-pass)."""
    with open(USER_ACTIONS_FILE, 'r') as f:
        content = f.read()

    # After fix, UserContextMenu should be rendered unconditionally
    # It should NOT be wrapped in {shouldShowUserActions && user && (...)}
    # We check that the component is rendered inside the wrapper div unconditionally

    # Look for the pattern where UserContextMenu is rendered
    menu_pattern = r'<UserContextMenu\s+key=\{menuResetCount\}'
    assert re.search(menu_pattern, content), \
        "UserContextMenu should be rendered with key={menuResetCount}"

    # Make sure there's no conditional wrapper around the context menu div
    # The fix removes the {shouldShowUserActions && user && (...)}
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'UserContextMenu' in line:
            # Check surrounding lines for removed conditional
            context_start = max(0, i - 10)
            context = '\n'.join(lines[context_start:i])
            assert "shouldShowUserActions" not in context, \
                f"UserContextMenu should not be conditionally rendered based on shouldShowUserActions (found near line {i+1})"


def test_context_menu_div_always_present():
    """Verify the context menu div wrapper is always in the DOM (fail-to-pass)."""
    with open(USER_ACTIONS_FILE, 'r') as f:
        content = f.read()

    # The fix ensures the div with context menu classes is always present
    # Look for the opacity classes that are part of the wrapper div
    opacity_pattern = r'"opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto"'
    assert re.search(opacity_pattern, content), \
        "Context menu wrapper div with opacity classes should always be present"

    # Verify the div is NOT inside a conditional block
    # The pattern should be: <div className={cn(...)}> followed by UserContextMenu
    div_pattern = r'<div\s+\n?\s*className=\{cn\(\s*"opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto"'
    assert re.search(div_pattern, content, re.DOTALL), \
        "Context menu wrapper div should be rendered unconditionally (not inside {condition && ...})"


def test_typescript_user_actions_no_errors():
    """Verify user-actions.tsx has no TypeScript errors related to our change (pass-to-pass).

    We only check for specific errors in the user-actions.tsx file, not the whole project.
    """
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=f"{REPO}/frontend",
        capture_output=True,
        text=True,
        timeout=120
    )
    # Filter for errors only in user-actions.tsx
    errors = result.stdout if result.stdout else ""
    user_actions_errors = [line for line in errors.split('\n') if 'user-actions.tsx' in line]
    assert len(user_actions_errors) == 0, \
        f"TypeScript errors in user-actions.tsx: {user_actions_errors}"


def test_frontend_lint_user_actions_clean():
    """Verify frontend lint passes on the modified file (pass-to-pass)."""
    result = subprocess.run(
        ["npm", "run", "lint", "--", "src/components/features/sidebar/user-actions.tsx"],
        cwd=f"{REPO}/frontend",
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Frontend lint failed for user-actions.tsx:\n{result.stderr[-500:]}"


def test_user_actions_file_exists():
    """Basic sanity check that the target file exists."""
    assert os.path.exists(USER_ACTIONS_FILE), \
        f"User actions file should exist at {USER_ACTIONS_FILE}"


def test_component_imports_clean():
    """Verify no unused imports remain after the fix."""
    with open(USER_ACTIONS_FILE, 'r') as f:
        content = f.read()

    # Check that UserContextMenu is still imported (it's used)
    assert "UserContextMenu" in content, \
        "UserContextMenu component should be imported and used"

    # Check that useMe hook is still imported (it's still used)
    assert "useMe" in content, \
        "useMe hook should still be imported"


# =============================================================================
# Pass-to-Pass Tests: Repo CI/CD Checks
# These ensure the fix doesn't break existing functionality
# =============================================================================


def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass).

    Runs react-router typegen && tsc in the frontend directory.
    """
    r = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=f"{REPO}/frontend",
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_build():
    """Repo's frontend build passes (pass_to_pass).

    Builds the frontend to ensure no compilation errors.
    """
    r = subprocess.run(
        ["npm", "run", "build"],
        cwd=f"{REPO}/frontend",
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


def test_repo_lint():
    """Repo's frontend lint passes (pass_to_pass).

    Runs npm run lint (typecheck + eslint + prettier) in the frontend directory.
    """
    r = subprocess.run(
        ["npm", "run", "lint"],
        cwd=f"{REPO}/frontend",
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"
