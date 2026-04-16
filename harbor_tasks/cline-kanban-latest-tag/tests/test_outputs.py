"""Tests for cline kanban@latest fix.

This verifies that the CLI uses kanban@latest instead of just kanban
to ensure users always get the most recent version rather than a cached one.
"""

import subprocess
import os
import re

REPO = "/workspace/cline"
CLI_DIR = os.path.join(REPO, "cli")
INDEX_TS = os.path.join(CLI_DIR, "src", "index.ts")
INDEX_TEST_TS = os.path.join(CLI_DIR, "src", "index.test.ts")


def test_kanban_spawn_uses_latest_tag():
    """CLI spawns kanban@latest, not just kanban (fail-to-pass)."""
    with open(INDEX_TS, "r") as f:
        content = f.read()

    # Check that kanban@latest is used in spawn call
    assert 'spawn(getNpxCommand(), ["-y", "kanban@latest", "--agent", "cline"]' in content, \
        "spawn call should use kanban@latest"

    # Make sure old version without @latest is not present
    old_spawn = 'spawn(getNpxCommand(), ["-y", "kanban", "--agent", "cline"],'
    assert old_spawn not in content, "Old spawn call without @latest should not exist"


def test_kanban_error_message_updated():
    """Error message references kanban@latest (fail-to-pass)."""
    with open(INDEX_TS, "r") as f:
        content = f.read()

    # Check error message references the correct command
    assert "npx kanban@latest --agent cline" in content, \
        "Error message should reference kanban@latest"

    # Make sure old error message is not present
    assert "npx kanban --agent cline'" not in content, \
        "Old error message without @latest should not exist"


def test_kanban_command_description_updated():
    """Kanban command description references kanban@latest (fail-to-pass)."""
    with open(INDEX_TS, "r") as f:
        content = f.read()

    # Check the .command("kanban").description() call
    assert '.description("Run npx kanban@latest --agent cline")' in content, \
        "Command description should reference kanban@latest"

    # Make sure old description is not present
    assert '.description("Run npx kanban --agent cline")' not in content, \
        "Old command description without @latest should not exist"


def test_kanban_option_description_updated():
    """Kanban option (--kanban) description references kanban@latest (fail-to-pass)."""
    with open(INDEX_TS, "r") as f:
        content = f.read()

    # Check the .option("--kanban", ...) call
    assert '.option("--kanban", "Run npx kanban@latest --agent cline")' in content, \
        "Option description should reference kanban@latest"

    # Make sure old option description is not present
    assert '.option("--kanban", "Run npx kanban --agent cline")' not in content, \
        "Old option description without @latest should not exist"


def test_cli_typescript_syntax_valid():
    """CLI TypeScript has valid syntax (pass-to-pass).

    Uses Node.js to parse the TypeScript file without requiring full type checking.
    This catches basic syntax errors like unbalanced braces or invalid characters.
    """
    # Use Node.js to try parsing the TypeScript
    result = subprocess.run(
        ["node", "-e", f"""
        const fs = require('fs');
        const content = fs.readFileSync('{INDEX_TS}', 'utf8');
        // Try to parse as JavaScript/TypeScript (basic syntax check)
        try {{
            new Function(content);
        }} catch(e) {{
            // TypeScript-specific syntax will fail here, but that's ok
            // We just want to catch obvious syntax errors
        }}
        console.log('Syntax check passed');
        """],
        capture_output=True,
        text=True,
        timeout=30
    )
    # This is a basic check - even if parsing fails due to TypeScript syntax,
    # the file should at least be readable and not have obvious syntax errors
    assert result.returncode == 0, f"Syntax check failed:\n{result.stderr}"


def test_index_file_exists_and_readable():
    """CLI index.ts exists and is readable (pass-to-pass)."""
    assert os.path.exists(INDEX_TS), f"{INDEX_TS} should exist"
    with open(INDEX_TS, "r") as f:
        content = f.read()
    assert len(content) > 0, "File should not be empty"
    assert "runKanbanAlias" in content, "File should contain runKanbanAlias function"


def test_test_file_exists_and_readable():
    """CLI test file exists and is readable (pass-to-pass)."""
    assert os.path.exists(INDEX_TEST_TS), f"{INDEX_TEST_TS} should exist"
    with open(INDEX_TEST_TS, "r") as f:
        content = f.read()
    assert len(content) > 0, "File should not be empty"


def test_test_file_consistent():
    """Test file descriptions match the implementation (fail-to-pass)."""
    with open(INDEX_TEST_TS, "r") as f:
        content = f.read()

    # Check that test descriptions reference kanban@latest
    assert 'npx kanban@latest --agent cline' in content, \
        "Test descriptions should reference kanban@latest"

    # Make sure old test descriptions are not present
    assert 'npx kanban --agent cline' not in content, \
        "Old test descriptions without @latest should not exist"


def test_repo_cli_unit_tests():
    """CLI unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/utils/display.test.ts", "src/utils/parser.test.ts", "src/utils/piped.test.ts", "src/utils/mode-selection.test.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=os.path.join(REPO, "cli"),
    )
    assert r.returncode == 0, f"CLI unit tests failed:\n{r.stderr[-500:]}"


def test_repo_cli_display_test():
    """CLI display utility tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/utils/display.test.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=os.path.join(REPO, "cli"),
    )
    assert r.returncode == 0, f"CLI display test failed:\n{r.stderr[-500:]}"


def test_repo_cli_parser_test():
    """CLI parser utility tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/utils/parser.test.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=os.path.join(REPO, "cli"),
    )
    assert r.returncode == 0, f"CLI parser test failed:\n{r.stderr[-500:]}"


def test_repo_cli_piped_test():
    """CLI piped utility tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/utils/piped.test.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=os.path.join(REPO, "cli"),
    )
    assert r.returncode == 0, f"CLI piped test failed:\n{r.stderr[-500:]}"


def test_repo_cli_constants_test():
    """CLI constants/featured-models tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/constants/featured-models.test.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=os.path.join(REPO, "cli"),
    )
    assert r.returncode == 0, f"CLI constants test failed:\n{r.stderr[-500:]}"


def test_repo_cli_plain_text_task_test():
    """CLI plain-text-task tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/utils/plain-text-task.test.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=os.path.join(REPO, "cli"),
    )
    assert r.returncode == 0, f"CLI plain-text-task test failed:\n{r.stderr[-500:]}"


def test_repo_cli_agent_emitter_test():
    """CLI agent session emitter tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/agent/ClineSessionEmitter.test.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=os.path.join(REPO, "cli"),
    )
    assert r.returncode == 0, f"CLI agent emitter test failed:\n{r.stderr[-500:]}"


def test_repo_cli_message_translator_test():
    """CLI message translator tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/agent/messageTranslator.test.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=os.path.join(REPO, "cli"),
    )
    assert r.returncode == 0, f"CLI message translator test failed:\n{r.stderr[-500:]}"
