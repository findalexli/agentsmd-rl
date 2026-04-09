"""Test outputs for appwrite session cache race condition fix.

This test validates that the fix for the race condition in email/password
login has been correctly applied. The fix reorders two operations:
1. createDocument('sessions', ...) - MUST come first
2. purgeCachedDocument('users', ...) - MUST come second

The race condition occurred because purging before creating opened a window
where concurrent requests could re-cache stale user data without the new session.
"""

import ast
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/appwrite")
TARGET_FILE = REPO / "app/controllers/api/account.php"


# ============================================================================
# Helper functions
# ============================================================================

def get_php_file_content() -> str:
    """Read the target PHP file."""
    if not TARGET_FILE.exists():
        pytest.fail(f"Target file not found: {TARGET_FILE}")
    return TARGET_FILE.read_text()


def find_email_login_section(content: str) -> str:
    """Extract the section around email/password session creation.

    The handler uses POST /v1/account/sessions/email
    We look for the code block around session creation and cache purge.
    """
    # Look for the session creation pattern in the email login handler
    # The distinctive lines we're looking for:
    # - createDocument('sessions', ...)
    # - purgeCachedDocument('users', ...)

    lines = content.split('\n')

    # Find the approximate location - look for the email login endpoint registration
    # or the session creation with permissions pattern
    for i, line in enumerate(lines):
        if "createDocument('sessions'" in line and "Permission::read" in lines[i+1] if i+1 < len(lines) else False:
            # Found the session creation, extract surrounding context (30 lines before, 10 after)
            start = max(0, i - 30)
            end = min(len(lines), i + 10)
            return '\n'.join(lines[start:end])

    # Fallback: search more broadly
    for i, line in enumerate(lines):
        if "createDocument('sessions'" in line:
            start = max(0, i - 20)
            end = min(len(lines), i + 15)
            return '\n'.join(lines[start:end])

    return ""


def check_php_syntax(file_path: Path) -> tuple[bool, str]:
    """Check if PHP file has valid syntax using php -l."""
    try:
        result = subprocess.run(
            ["php", "-l", str(file_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stderr
    except FileNotFoundError:
        # PHP not installed, try alternative approach with basic parsing
        content = file_path.read_text()
        # Basic PHP syntax checks
        open_tags = content.count("<?php") + content.count("<?")
        close_tags = content.count("?>")
        # Check brace balance
        open_braces = content.count("{")
        close_braces = content.count("}")

        if open_braces != close_braces:
            return False, f"Brace mismatch: {open_braces} open, {close_braces} close"

        return True, "Basic syntax check passed (PHP not available for full check)"
    except subprocess.TimeoutExpired:
        return False, "PHP syntax check timed out"


# ============================================================================
# Fail-to-pass tests (must fail on base commit, pass on fixed commit)
# ============================================================================

def test_session_created_before_cache_purge():
    """F2P: Session must be created BEFORE user cache is purged.

    This is the core fix for the race condition. The old code had:
        purgeCachedDocument('users', ...);  // Line N
        createDocument('sessions', ...);     // Line N+2

    The fix swaps them so session creation happens first.
    """
    content = get_php_file_content()

    # Find both operations in the email login section
    email_section = find_email_login_section(content)
    assert email_section, "Could not find email login section with session creation"

    lines = email_section.split('\n')

    # Find line numbers for both operations (relative to section)
    purge_line = None
    create_line = None

    for i, line in enumerate(lines):
        if "purgeCachedDocument('users'" in line:
            purge_line = i
        if "createDocument('sessions'" in line and "Permission::read" in lines[i+1] if i+1 < len(lines) else False:
            create_line = i

    assert create_line is not None, "Could not find createDocument('sessions') call"
    assert purge_line is not None, "Could not find purgeCachedDocument('users') call"

    # CRITICAL CHECK: create must come BEFORE purge
    assert create_line < purge_line, (
        f"Race condition not fixed: purgeCachedDocument (line {purge_line}) "
        f"comes before createDocument (line {create_line}). "
        f"The session must be created BEFORE purging the cache to prevent "
        f"concurrent requests from caching stale user data."
    )


def test_operations_are_adjacent_with_no_other_cache_ops():
    """F2P: The two operations should be adjacent with only the session creation between them.

    This ensures we haven't introduced other cache operations in between that could
    reintroduce the race condition.
    """
    content = get_php_file_content()
    email_section = find_email_login_section(content)
    assert email_section, "Could not find email login section"

    lines = email_section.split('\n')

    # Find positions
    purge_idx = None
    create_idx = None

    for i, line in enumerate(lines):
        if "purgeCachedDocument('users'" in line:
            purge_idx = i
        if "createDocument('sessions'" in line and "Permission::read" in lines[i+1] if i+1 < len(lines) else False:
            create_idx = i

    assert create_idx is not None and purge_idx is not None, "Missing required operations"

    # Check that no other cache operations happen between create and purge
    for i in range(create_idx + 1, purge_idx):
        line = lines[i].strip()
        # Skip empty lines and comments
        if not line or line.startswith('//') or line.startswith('*') or line.startswith('/*'):
            continue
        # Check for cache-related operations
        assert 'purgeCachedDocument' not in line, (
            f"Unexpected cache purge at line {i}: {line}. "
            f"Only one purge should exist after session creation."
        )


# ============================================================================
# Pass-to-pass tests (should pass on both base and fixed commits)
# ============================================================================

def test_php_syntax_is_valid():
    """P2P: Modified file must have valid PHP syntax."""
    valid, message = check_php_syntax(TARGET_FILE)
    assert valid, f"PHP syntax error: {message}"


def test_composer_validate():
    """P2P: Repo composer.json must be valid (CI check)."""
    r = subprocess.run(
        ["composer", "validate", "--no-check-publish"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"composer validate failed:\n{r.stdout}{r.stderr}"


def test_session_permissions_are_correct():
    """P2P: Session must have correct read/update/delete permissions for the user.

    This verifies the fix preserves the permission structure.
    """
    content = get_php_file_content()
    email_section = find_email_login_section(content)
    assert email_section, "Could not find email login section"

    # Check that the session has the correct permission pattern
    assert "Permission::read(Role::user($user->getId()))" in email_section, (
        "Session missing read permission for user"
    )
    assert "Permission::update(Role::user($user->getId()))" in email_section, (
        "Session missing update permission for user"
    )
    assert "Permission::delete(Role::user($user->getId()))" in email_section, (
        "Session missing delete permission for user"
    )


def test_pattern_matches_other_auth_flows():
    """P2P: The fix should match the pattern used in other authentication flows.

    Check that other flows (anonymous, OAuth, token-based) use the correct
    pattern: create session first, then purge cache.
    """
    content = get_php_file_content()

    # Look for anonymous session creation pattern (around line 1269 per PR description)
    # The PR says anonymous, OAuth, and token-based flows already have the correct order

    # Find all occurrences of createDocument('sessions') followed by purgeCachedDocument('users')
    lines = content.split('\n')

    # Count instances where create comes before purge (correct pattern)
    correct_patterns = 0
    incorrect_patterns = 0

    session_create_indices = []
    purge_indices = []

    for i, line in enumerate(lines):
        if "createDocument('sessions'" in line:
            # Check if it's the session with permissions (not some other createDocument)
            if i + 3 < len(lines) and "Permission::read" in lines[i + 1]:
                session_create_indices.append(i)
        if "purgeCachedDocument('users'" in line:
            purge_indices.append(i)

    # For each purge, check if there's a session create before it in close proximity
    for purge_idx in purge_indices:
        # Find the nearest session create before this purge
        nearest_create = None
        for create_idx in session_create_indices:
            if create_idx < purge_idx and (nearest_create is None or create_idx > nearest_create):
                nearest_create = create_idx

        if nearest_create is not None:
            # Check if they're in the same function context (within ~20 lines)
            if purge_idx - nearest_create < 20:
                correct_patterns += 1

    # The PR mentions that anonymous, OAuth, and token-based flows already have correct order
    # So we should see at least some correct patterns
    assert correct_patterns >= 1, (
        "No correct patterns found (session create before cache purge). "
        "The fix should align with patterns in other auth flows."
    )


def test_file_structure_preserved():
    """P2P: No unintended structural changes to the file.

    Check that we haven't accidentally deleted or added large sections.
    """
    content = get_php_file_content()

    # Basic structural checks
    # File should start with <?php
    assert content.strip().startswith('<?php'), "File should start with PHP opening tag"

    # Should contain required imports
    required_imports = [
        'use Utopia\\Database\\Database;',
        'use Utopia\\Database\\Helpers\\Permission;',
        'use Utopia\\Database\\Helpers\\Role;',
    ]
    for imp in required_imports:
        assert imp in content, f"Missing required import: {imp}"


# ============================================================================
# Self-audit helpers
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
