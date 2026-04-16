"""
Test suite for the /new slash command menu feature.

This validates that:
1. The /new built-in command is included for V1 conversations
2. The /new command is NOT included for V0 conversations
3. The menu returns empty items while skills are loading (prevents staggered menu bug)
4. The existing repo tests pass (pass-to-pass)
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/OpenHands/frontend")


def test_v1_conversation_includes_new_command():
    """
    Fail-to-pass: /new command must appear in slash menu for V1 conversations.

    The hook should include BUILT_IN_COMMANDS (which contains /new) when
    the conversation version is "V1".
    """
    # First check: the test file must exist (it's created by the gold patch)
    test_file = REPO / "__tests__" / "hooks" / "chat" / "use-slash-command.test.ts"
    assert test_file.exists(), f"Test file not found - feature not implemented: {test_file}"

    # Run the repo's own test suite
    result = subprocess.run(
        ["npm", "run", "test", "--", "-t", "includes /new built-in command for V1 conversations"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Test failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"


def test_v0_conversation_excludes_new_command():
    """
    Fail-to-pass: /new command must NOT appear for V0 conversations.

    The hook should only show BUILT_IN_COMMANDS for V1 conversations,
    not for V0.
    """
    # First check: the test file must exist (it's created by the gold patch)
    test_file = REPO / "__tests__" / "hooks" / "chat" / "use-slash-command.test.ts"
    assert test_file.exists(), f"Test file not found - feature not implemented: {test_file}"

    result = subprocess.run(
        ["npm", "run", "test", "--", "-t", "does NOT include /new built-in command for V0 conversations"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Test failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"


def test_returns_empty_while_loading():
    """
    Fail-to-pass: While skills are loading, filteredItems should be empty.

    This prevents the "staggered menu" bug where commands appear one by one.
    """
    # First check: the test file must exist (it's created by the gold patch)
    test_file = REPO / "__tests__" / "hooks" / "chat" / "use-slash-command.test.ts"
    assert test_file.exists(), f"Test file not found - feature not implemented: {test_file}"

    result = subprocess.run(
        ["npm", "run", "test", "--", "-t", "returns empty items while skills are loading"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Test failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"


def test_use_slash_command_hook_exists():
    """
    Pass-to-pass: The use-slash-command hook file must exist and exports must be valid.
    """
    hook_file = REPO / "src" / "hooks" / "chat" / "use-slash-command.ts"
    assert hook_file.exists(), f"Hook file not found: {hook_file}"

    content = hook_file.read_text()
    # Check hook exports useSlashCommand
    assert "export const useSlashCommand" in content, "useSlashCommand not exported"


def test_constants_file_updated():
    """
    Fail-to-pass: constants.ts must include BUILT_IN_COMMANDS with /new.
    """
    constants_file = REPO / "src" / "utils" / "constants.ts"
    assert constants_file.exists(), f"Constants file not found: {constants_file}"

    content = constants_file.read_text()

    # Check for BUILT_IN_COMMANDS export
    assert "BUILT_IN_COMMANDS" in content, "BUILT_IN_COMMANDS not found in constants.ts"

    # Check it includes the /new command
    assert '/new' in content, "/new command not found in BUILT_IN_COMMANDS"

    # Check it imports SlashCommandItem type
    assert "SlashCommandItem" in content, "SlashCommandItem import not found"


def test_active_conversation_hook_imported():
    """
    Fail-to-pass: use-slash-command.ts must import useActiveConversation.
    """
    hook_file = REPO / "src" / "hooks" / "chat" / "use-slash-command.ts"
    content = hook_file.read_text()

    assert "useActiveConversation" in content, "useActiveConversation hook not imported"


def test_v1_conversation_check_implemented():
    """
    Fail-to-pass: Hook must check conversation_version === "V1".
    """
    hook_file = REPO / "src" / "hooks" / "chat" / "use-slash-command.ts"
    content = hook_file.read_text()

    # Check for V1 conversation version check
    assert 'conversation_version === "V1"' in content or "conversation_version === 'V1'" in content, \
        "V1 conversation version check not found"


def test_skills_loading_check():
    """
    Fail-to-pass: Hook must check isSkillsLoading to prevent staggered menu.
    """
    hook_file = REPO / "src" / "hooks" / "chat" / "use-slash-command.ts"
    content = hook_file.read_text()

    assert "isSkillsLoading" in content, "isSkillsLoading check not found"


def test_typecheck_passes():
    """
    Pass-to-pass: TypeScript type checking must pass.
    """
    result = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Typecheck failed:\n{result.stderr[-1000:]}"


def test_lint_passes():
    """
    Pass-to-pass: Linting must pass (as per AGENTS.md requirements).
    """
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stderr[-1000:]}"


def test_new_conversation_command():
    """
    Pass-to-pass: useNewConversationCommand hook tests pass (repo CI).

    Tests the hook that implements the /new command functionality,
    which is closely related to the slash command menu feature.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "--run", "__tests__/hooks/mutation/use-new-conversation-command.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"useNewConversationCommand tests failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"


def test_skill_modal():
    """
    Pass-to-pass: SkillsModal component tests pass (repo CI).

    Tests the skills modal which exercises useConversationSkills hook,
    the same hook used by use-slash-command.ts.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "--run", "__tests__/components/modals/skills/skill-modal.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"SkillsModal tests failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"
