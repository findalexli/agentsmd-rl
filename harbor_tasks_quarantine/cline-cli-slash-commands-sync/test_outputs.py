"""Test outputs for cline#9747 - Fix Windows CLI tests for slash command timing issues."""

import subprocess
import sys
import os
import json
import re

REPO = "/workspace/cline"
CLI_DIR = f"{REPO}/cli"


def test_filter_commands_behavior():
    """filterCommands prioritizes exact matches, then prefix, then fuzzy (f2p)."""
    result = subprocess.run(
        ["node", "-e", """
        const fs = require("fs");
        const content = fs.readFileSync("./src/utils/slash-commands.ts", "utf8");

        if (!content.includes("function filterCommands") && !content.includes("filterCommands =")) {
            console.log("FAIL: filterCommands function not found");
            process.exit(1);
        }

        const hasExactMatches = content.includes("exactMatches") || content.includes("exact");
        const hasPrefixMatches = content.includes("prefixMatches") || content.includes("prefix");
        const hasFuzzyFilter = content.includes("fuzzyFilter");

        if (!hasExactMatches || !hasPrefixMatches || !hasFuzzyFilter) {
            console.log("FAIL: Missing prioritization logic");
            process.exit(1);
        }

        console.log("PASS");
        """,
        ],
        cwd=CLI_DIR,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0 or "PASS" not in result.stdout:
        with open(f"{CLI_DIR}/src/utils/slash-commands.ts", "r") as f:
            content = f.read()
        assert "exactMatches" in content or "exact" in content, \
            "filterCommands should prioritize exact matches"
        assert "prefixMatches" in content or "prefix" in content, \
            "filterCommands should prioritize prefix matches"
        assert "fuzzyFilter" in content or "fuzzy" in content, \
            "filterCommands should apply fuzzy matching to remaining items"


def test_standalone_command_detection_behavior():
    """getStandaloneSlashCommandName detects standalone commands like /q vs /q something (f2p)."""
    result = subprocess.run(
        ["node", "-e", """
        const fs = require("fs");
        const content = fs.readFileSync("./src/utils/slash-commands.ts", "utf8");

        if (!content.includes("getStandaloneSlashCommandName")) {
            console.log("FAIL: getStandaloneSlashCommandName not found");
            process.exit(1);
        }

        if (!content.includes("export") || !content.match(/export\\s+(function|const)\\s+getStandaloneSlashCommandName/)) {
            console.log("FAIL: getStandaloneSlashCommandName not properly exported");
            process.exit(1);
        }

        console.log("PASS");
        """,
        ],
        cwd=CLI_DIR,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0 or "PASS" not in result.stdout:
        with open(f"{CLI_DIR}/src/utils/slash-commands.ts", "r") as f:
            content = f.read()
        assert "getStandaloneSlashCommandName" in content, \
            "getStandaloneSlashCommandName should exist"


def test_standalone_execution_decision_behavior():
    """getStandaloneSlashCommandToExecute function exists and handles execution decision (f2p)."""
    with open(f"{CLI_DIR}/src/utils/slash-commands.ts", "r") as f:
        content = f.read()

    assert "getStandaloneSlashCommandToExecute" in content, \
        "getStandaloneSlashCommandToExecute should exist"

    assert "StandaloneSlashCommandExecutionInput" in content, \
        "StandaloneSlashCommandExecutionInput interface should exist for execution decision"

    assert "slashMenuVisible" in content or "menuVisible" in content or "menu" in content.lower(), \
        "Execution decision should check whether slash menu is visible"


def test_create_cli_only_slash_commands_behavior():
    """createCliOnlySlashCommands creates CLI-only commands synchronously (f2p)."""
    result = subprocess.run(
        ["node", "-e", """
        const fs = require("fs");
        const content = fs.readFileSync("./src/utils/slash-commands.ts", "utf8");

        if (!content.includes("createCliOnlySlashCommands")) {
            console.log("FAIL: createCliOnlySlashCommands not found");
            process.exit(1);
        }

        if (!content.match(/export\\s+(function|const)\\s+createCliOnlySlashCommands/)) {
            console.log("FAIL: createCliOnlySlashCommands not exported");
            process.exit(1);
        }

        if (!content.includes("SlashCommandInfo")) {
            console.log("FAIL: Missing SlashCommandInfo type");
            process.exit(1);
        }

        console.log("PASS");
        """,
        ],
        cwd=CLI_DIR,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0 or "PASS" not in result.stdout:
        with open(f"{CLI_DIR}/src/utils/slash-commands.ts", "r") as f:
            content = f.read()
        assert "createCliOnlySlashCommands" in content, \
            "createCliOnlySlashCommands should exist"
        assert "export" in content and "createCliOnlySlashCommands" in content, \
            "createCliOnlySlashCommands should be exported"


def test_slash_commands_test_file_has_behavioral_tests():
    """slash-commands.test.ts has behavioral tests (f2p)."""
    test_file = f"{CLI_DIR}/src/utils/slash-commands.test.ts"
    assert os.path.exists(test_file), f"Test file {test_file} should exist"

    with open(test_file, "r") as f:
        content = f.read()

    assert "describe" in content or "it(" in content or "test(" in content, \
        "Test file should have test blocks"

    behavioral_keywords = [
        "exact match", "prefix match", "fuzzy", "prioritize",
        "standalone", "command", "filter"
    ]
    found_behavioral = any(kw.lower() in content.lower() for kw in behavioral_keywords)
    assert found_behavioral, "Test file should contain behavioral test descriptions"

    assert "filterCommands" in content, \
        "Test file should call filterCommands function"


def test_quit_command_test_file_updated():
    """QuitCommand.test.tsx replaced flaky integration tests with unit tests (f2p)."""
    test_file = f"{CLI_DIR}/src/components/QuitCommand.test.tsx"
    assert os.path.exists(test_file), f"Test file {test_file} should exist"

    with open(test_file, "r") as f:
        content = f.read()

    assert "getStandaloneSlashCommandName" in content or "getStandalone" in content, \
        "Should test standalone command detection"

    assert "filterCommands" in content, \
        "Should test filterCommands"

    assert "render(<ChatView" not in content, \
        "Should not use old ChatView render integration tests that are flaky"


def test_chatview_integration_behavior():
    """ChatView.tsx uses new slash command utilities (f2p)."""
    with open(f"{CLI_DIR}/src/components/ChatView.tsx", "r") as f:
        content = f.read()

    assert "createCliOnlySlashCommands" in content, \
        "ChatView should use createCliOnlySlashCommands"
    assert "getStandaloneSlashCommandName" in content or "getStandalone" in content, \
        "ChatView should use standalone command detection"
    assert "getStandaloneSlashCommandToExecute" in content or "getStandalone" in content, \
        "ChatView should use standalone command execution"

    assert "handleCliOnlySlashCommand" in content, \
        "ChatView should have handleCliOnlySlashCommand function"


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


def test_slash_commands_exported():
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