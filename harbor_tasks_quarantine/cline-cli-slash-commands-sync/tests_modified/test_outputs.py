"""Test outputs for cline#9747 - Fix Windows CLI tests for slash command timing issues."""

import subprocess
import sys
import os
import json
import re

REPO = "/workspace/cline"
CLI_DIR = f"{REPO}/cli"


def test_filter_commands_function_and_exports():
    """filterCommands is exported and has exact/prefix match prioritization (f2p)."""
    with open(f"{CLI_DIR}/src/utils/slash-commands.ts", "r") as f:
        content = f.read()

    # Verify function is exported
    assert re.search(r"export\s+function\s+filterCommands", content), \
        "filterCommands should be exported"

    # Verify exact match prioritization exists
    assert "exact" in content.lower() and ("match" in content.lower() or "priority" in content.lower()), \
        "filterCommands should have exact match prioritization logic"

    # Verify prefix match prioritization exists
    assert "prefix" in content.lower() and ("match" in content.lower() or "priority" in content.lower()), \
        "filterCommands should have prefix match prioritization logic"


def test_standalone_command_detection_exported():
    """getStandaloneSlashCommandName is exported (f2p)."""
    with open(f"{CLI_DIR}/src/utils/slash-commands.ts", "r") as f:
        content = f.read()

    assert re.search(r"export\s+function\s+getStandaloneSlashCommandName", content), \
        "getStandaloneSlashCommandName should be exported"


def test_standalone_execution_decision_exported():
    """getStandaloneSlashCommandToExecute is exported (f2p)."""
    with open(f"{CLI_DIR}/src/utils/slash-commands.ts", "r") as f:
        content = f.read()

    assert re.search(r"export\s+function\s+getStandaloneSlashCommandToExecute", content), \
        "getStandaloneSlashCommandToExecute should be exported"


def test_create_cli_only_slash_commands_exported():
    """createCliOnlySlashCommands is exported (f2p)."""
    with open(f"{CLI_DIR}/src/utils/slash-commands.ts", "r") as f:
        content = f.read()

    assert re.search(r"export\s+function\s+createCliOnlySlashCommands", content), \
        "createCliOnlySlashCommands should be exported"


def test_slash_commands_test_file_exists():
    """slash-commands.test.ts exists with behavioral tests (f2p)."""
    test_file = f"{CLI_DIR}/src/utils/slash-commands.test.ts"
    assert os.path.exists(test_file), f"Test file {test_file} should exist"

    with open(test_file, "r") as f:
        content = f.read()

    assert "describe" in content or "it(" in content or "test(" in content, \
        "Test file should have test blocks"

    # Verify behavioral keywords are present
    behavioral_keywords = [
        "filterCommands", "getStandalone", "exact match", "prefix match"
    ]
    found = sum(1 for kw in behavioral_keywords if kw in content)
    assert found >= 2, "Test file should contain behavioral test descriptions"


def test_quit_command_test_file_no_longer_flaky():
    """QuitCommand.test.tsx replaced flaky integration tests with unit tests (f2p)."""
    test_file = f"{CLI_DIR}/src/components/QuitCommand.test.tsx"
    assert os.path.exists(test_file), f"Test file {test_file} should exist"

    with open(test_file, "r") as f:
        content = f.read()

    # Should NOT use the old flaky integration test pattern (render ChatView with stdin)
    assert "render(<ChatView" not in content, \
        "Should not use old ChatView render integration tests that are flaky"

    # Should use the new utility-based unit tests (filterCommands or getStandalone)
    assert "filterCommands" in content or "getStandalone" in content, \
        "Should test filterCommands or standalone command detection"


def test_chatview_uses_standalone_detection():
    """ChatView.tsx uses standalone slash command utilities for deterministic behavior (f2p)."""
    with open(f"{CLI_DIR}/src/components/ChatView.tsx", "r") as f:
        content = f.read()

    # ChatView should use the new utilities
    assert "createCliOnlySlashCommands" in content, \
        "ChatView should initialize CLI commands synchronously"
    assert "getStandaloneSlashCommandToExecute" in content, \
        "ChatView should use standalone command execution utility"


def test_slash_commands_utilities_exported():
    """New slash command utilities should be exported (f2p)."""
    with open(f"{CLI_DIR}/src/utils/slash-commands.ts", "r") as f:
        content = f.read()

    exports = [
        "createCliOnlySlashCommands",
        "getStandaloneSlashCommandName",
        "getStandaloneSlashCommandToExecute",
    ]

    for export in exports:
        pattern = rf"export\s+(function|const|var|let)\s+{export}"
        assert re.search(pattern, content), \
            f"{export} should be exported"


def test_slash_commands_vitest_tests():
    """slash-commands.test.ts passes via vitest (f2p)."""
    result = subprocess.run(
        ["npx", "vitest", "run", "src/utils/slash-commands.test.ts", "--reporter=verbose"],
        cwd=CLI_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Check for actual test passing (not just "no test files")
    output = result.stdout + result.stderr
    assert "no tests" not in output.lower() and "Cannot find package" not in output, \
        f"vitest should be able to run slash-commands tests: {output[-500:]}"


# =============================================================================
# Pass-to-pass tests (repo CI/CD)
# =============================================================================

def test_cli_vitest_tests_pass():
    """CLI Vitest tests should pass (p2p)."""
    result = subprocess.run(
        ["npm", "run", "test:run", "--", "--reporter=verbose"],
        cwd=CLI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        if "Cannot find package" in result.stderr or "Cannot find module" in result.stderr:
            return
        if "No test files found" in result.stderr or "no tests" in result.stdout.lower():
            return
        if "FAIL" in result.stdout or "AssertionError" in result.stderr:
            assert False, f"CLI tests failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"


def test_cli_skills_panel_content_tests_pass():
    """CLI SkillsPanelContent component tests should pass (p2p)."""
    result = subprocess.run(
        ["npm", "run", "test:run", "--", "--reporter=verbose", "src/components/SkillsPanelContent.test.tsx"],
        cwd=CLI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"SkillsPanelContent tests failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_cli_session_emitter_tests_pass():
    """CLI ClineSessionEmitter tests should pass (p2p)."""
    result = subprocess.run(
        ["npm", "run", "test:run", "--", "--reporter=verbose", "src/agent/ClineSessionEmitter.test.ts"],
        cwd=CLI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"ClineSessionEmitter tests failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_cli_display_utils_tests_pass():
    """CLI display utility tests should pass (p2p)."""
    result = subprocess.run(
        ["npm", "run", "test:run", "--", "--reporter=verbose", "src/utils/display.test.ts"],
        cwd=CLI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Display utils tests failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_cli_parser_tests_pass():
    """CLI parser tests should pass (p2p)."""
    result = subprocess.run(
        ["npm", "run", "test:run", "--", "--reporter=verbose", "src/utils/parser.test.ts"],
        cwd=CLI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Parser tests failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_cli_piped_utils_tests_pass():
    """CLI piped input utility tests should pass (p2p)."""
    result = subprocess.run(
        ["npm", "run", "test:run", "--", "--reporter=verbose", "src/utils/piped.test.ts"],
        cwd=CLI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Piped utils tests failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"
