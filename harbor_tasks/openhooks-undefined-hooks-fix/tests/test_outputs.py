"""Tests for the OpenHands undefined hooks fix."""

import subprocess
import sys
import os

REPO = "/workspace/openhands"
FRONTEND = f"{REPO}/frontend"


def test_type_definition_updated():
    """Verify HookMatcher interface marks hooks as optional."""
    type_file = f"{FRONTEND}/src/api/conversation-service/v1-conversation-service.types.ts"
    with open(type_file) as f:
        content = f.read()

    # Check that hooks is now optional (hooks?:)
    assert "hooks?: HookDefinition[]" in content, \
        "HookMatcher.hooks should be marked as optional with ?:"

    # Check for comment explaining why it can be undefined
    assert "undefined" in content.lower() or "executing" in content.lower() or "server" in content.lower(), \
        "Should have a comment explaining why hooks can be undefined"


def test_hook_event_item_handles_undefined():
    """Verify hook-event-item.tsx uses nullish coalescing for matcher.hooks."""
    file_path = f"{FRONTEND}/src/components/features/conversation-panel/hook-event-item.tsx"
    with open(file_path) as f:
        content = f.read()

    # Check for nullish coalescing operator
    assert "matcher.hooks ?? []" in content, \
        "hook-event-item.tsx should use matcher.hooks ?? [] to handle undefined"

    # Make sure the reduce function uses the nullish coalescing
    assert "(matcher.hooks ?? []).length" in content, \
        "Should access length on coalesced array"


def test_hook_matcher_content_handles_undefined():
    """Verify hook-matcher-content.tsx uses nullish coalescing for matcher.hooks."""
    file_path = f"{FRONTEND}/src/components/features/conversation-panel/hook-matcher-content.tsx"
    with open(file_path) as f:
        content = f.read()

    # Check for nullish coalescing operator
    assert "matcher.hooks ?? []" in content, \
        "hook-matcher-content.tsx should use matcher.hooks ?? [] to handle undefined"

    # Make sure map is called on coalesced array
    assert "(matcher.hooks ?? []).map" in content, \
        "Should call map on coalesced array"


def test_typescript_compiles():
    """Verify TypeScript compiles without NEW errors in modified files."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Filter for errors only in the files we care about
    # Pre-existing errors in other files (like settings.tsx) should not fail this test
    modified_files = [
        "hook-event-item.tsx",
        "hook-matcher-content.tsx",
        "v1-conversation-service.types.ts"
    ]

    if result.returncode != 0:
        errors = result.stdout + result.stderr
        relevant_errors = [line for line in errors.split('\n')
                         if any(f in line for f in modified_files) and 'error TS' in line]

        if relevant_errors:
            assert False, f"TypeScript errors in modified files:\n" + "\n".join(relevant_errors)
        # If only pre-existing errors in other files, test passes


def test_unit_tests_pass():
    """Run the specific unit tests for the hooks modal."""
    result = subprocess.run(
        ["npm", "run", "test", "--", "-t", "should not crash when a matcher has undefined hooks"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Test passes if either it runs successfully or the test pattern matches
    # The test might not exist on base commit, but should pass after fix
    if result.returncode != 0:
        # Check if it's because tests don't exist yet (base commit)
        if "No tests found" in result.stdout or "No tests found" in result.stderr:
            return

    assert result.returncode == 0, \
        f"Unit tests failed:\n{result.stdout}\n{result.stderr}"


def test_mixed_matchers_test():
    """Verify tests handle mixed matchers (with and without hooks)."""
    result = subprocess.run(
        ["npm", "run", "test", "--", "-t", "should handle a mix of matchers"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        if "No tests found" in result.stdout or "No tests found" in result.stderr:
            return

    assert result.returncode == 0, \
        f"Mixed matchers test failed:\n{result.stdout}\n{result.stderr}"


def test_lint_passes():
    """Verify frontend linting passes."""
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Linting failed:\n{result.stdout}\n{result.stderr}"


def test_eslint_passes():
    """Repo's ESLint check passes (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "eslint", "src", "--ext", ".ts,.tsx,.js"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"ESLint failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_prettier_passes():
    """Repo's Prettier formatting check passes (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "prettier", "--check", "src/**/*.{ts,tsx}"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Prettier check failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_repo_builds():
    """Repo's frontend build passes (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Build failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_translation_completeness():
    """Repo's translation completeness check passes (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "check-translation-completeness"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"Translation check failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_conversation_panel_tests():
    """Repo's conversation-panel tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "test", "--", "__tests__/components/features/conversation-panel/"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Conversation panel tests failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"
