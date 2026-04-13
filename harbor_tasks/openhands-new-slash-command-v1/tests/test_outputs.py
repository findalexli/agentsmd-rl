"""Tests for OpenHands /new slash command feature.

This test suite validates that:
1. The /new command appears in the slash command menu for V1 conversations
2. The /new command does NOT appear for V0 conversations
3. Empty items are returned while skills are loading
4. The repo's own vitest tests pass
5. TypeScript type checking passes
6. Linting passes
"""

import subprocess
import sys

REPO = "/workspace/OpenHands"
FRONTEND = f"{REPO}/frontend"


def run_npm_command(cmd: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    """Run an npm command in the frontend directory."""
    return subprocess.run(
        cmd,
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


TEST_FILE = f"{FRONTEND}/__tests__/hooks/chat/use-slash-command.test.ts"


def test_test_file_exists():
    """FAIL-TO-PASS: Test file use-slash-command.test.ts exists.

    The PR adds a test file at frontend/__tests__/hooks/chat/use-slash-command.test.ts
    """
    import os
    assert os.path.exists(TEST_FILE), f"Test file not found: {TEST_FILE}"


def test_v1_conversation_has_new_command():
    """FAIL-TO-PASS: /new command appears for V1 conversations.

    The BUILT_IN_COMMANDS should include /new and useSlashCommand should
    include it in filteredItems when conversation_version is "V1".
    """
    result = run_npm_command(
        ["npm", "run", "test", "--", "--run", "--reporter=verbose", "use-slash-command"],
        timeout=180
    )
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"
    assert "includes /new built-in command for V1" in result.stdout, "Test 'includes /new' not found in output"
    assert "PASSED" in result.stdout or "✓" in result.stdout, "Test did not pass"


def test_v0_conversation_no_new_command():
    """FAIL-TO-PASS: /new command does NOT appear for V0 conversations.

    The /new command should be gated behind the V1 conversation check.
    """
    result = run_npm_command(
        ["npm", "run", "test", "--", "--run", "--reporter=verbose", "use-slash-command"],
        timeout=180
    )
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"
    assert "does NOT include /new" in result.stdout, "Test 'does NOT include /new' not found"
    assert "PASSED" in result.stdout or "✓" in result.stdout, "Test did not pass"


def test_empty_items_while_loading():
    """FAIL-TO-PASS: Returns empty items while skills are loading.

    Prevents staggered menu bug where commands appear one by one.
    """
    result = run_npm_command(
        ["npm", "run", "test", "--", "--run", "--reporter=verbose", "use-slash-command"],
        timeout=180
    )
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"
    assert "returns empty items while skills are loading" in result.stdout, "Test 'returns empty items' not found"
    assert "PASSED" in result.stdout or "✓" in result.stdout, "Test did not pass"


def test_typecheck():
    """PASS-TO-PASS: TypeScript type checking passes.

    Ensures the code is type-safe and follows TypeScript conventions.
    """
    result = run_npm_command(
        ["npm", "run", "typecheck"],
        timeout=120
    )
    assert result.returncode == 0, f"Typecheck failed:\n{result.stdout}\n{result.stderr}"


def test_lint():
    """PASS-TO-PASS: Linting passes.

    Ensures code style and quality standards are met.
    """
    result = run_npm_command(
        ["npm", "run", "lint"],
        timeout=120
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stdout}\n{result.stderr}"


def test_build():
    """PASS-TO-PASS: Production build compiles successfully.

    Ensures the full TypeScript compilation and build pipeline works,
    including React Router typegen and Vite bundling. Mirrors the CI build step.
    """
    result = run_npm_command(
        ["npm", "run", "build"],
        timeout=180
    )
    assert result.returncode == 0, f"Build failed:\n{result.stdout}\n{result.stderr}"


def test_translation_completeness():
    """PASS-TO-PASS: All translation keys have complete language coverage.

    Ensures i18n translation files are complete and consistent across all
    supported languages. Part of the repo's lint-staged checks.
    """
    result = run_npm_command(
        ["npm", "run", "check-translation-completeness"],
        timeout=60
    )
    assert result.returncode == 0, f"Translation check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_unit_tests():
    """PASS-TO-PASS: Frontend slash-command unit tests pass (vitest run).

    Runs the repo's existing vitest test suite for slash-command functionality
    to validate the base commit has working tests. Focuses on the slash-command
    menu and related components that are relevant to the modified code.
    """
    result = run_npm_command(
        ["npm", "run", "test", "--", "--run", "--reporter=verbose", "slash-command"],
        timeout=60
    )
    assert result.returncode == 0, f"Slash-command tests failed:\n{result.stdout}\n{result.stderr}"


def test_new_conversation_command():
    """PASS-TO-PASS: useNewConversationCommand hook tests pass (vitest run).

    Tests the mutation hook that implements the /new command functionality.
    This hook is closely related to the slash command feature being modified,
    verifying that the underlying command implementation works correctly.
    """
    result = run_npm_command(
        ["npm", "run", "test", "--", "--run", "--reporter=verbose", "use-new-conversation-command"],
        timeout=60
    )
    assert result.returncode == 0, f"New conversation command tests failed:\n{result.stdout}\n{result.stderr}"


def test_hooks_mutation():
    """PASS-TO-PASS: Mutation hook tests pass (vitest run).

    Tests for TanStack Query mutation hooks including useConversationSkills
    which is used by the modified useSlashCommand hook. Validates that
    related query/mutation infrastructure works correctly.
    """
    result = run_npm_command(
        ["npm", "run", "test", "--", "--run", "hooks/mutation"],
        timeout=120
    )
    assert result.returncode == 0, f"Mutation hooks tests failed:\n{result.stdout}\n{result.stderr}"


def test_hooks_query():
    """PASS-TO-PASS: Query hook tests pass (vitest run).

    Tests for TanStack Query hooks including useActiveConversation
    which is used by the modified useSlashCommand hook. Validates that
    the data fetching infrastructure for conversations works correctly.
    """
    result = run_npm_command(
        ["npm", "run", "test", "--", "--run", "hooks/query"],
        timeout=120
    )
    assert result.returncode == 0, f"Query hooks tests failed:\n{result.stdout}\n{result.stderr}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
