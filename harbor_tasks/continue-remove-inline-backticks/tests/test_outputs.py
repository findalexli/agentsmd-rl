#!/usr/bin/env python3
"""Tests for the tool instruction backtick fix.

This verifies that the system message strings for tool instructions
no longer contain raw triple-backtick sequences in the prose text,
which could cause ambiguous fence nesting in system prompts.
"""

import subprocess
import re
import os

REPO = "/workspace/continue"
TARGET_FILE = f"{REPO}/core/tools/systemMessageTools/toolCodeblocks/index.ts"


def test_typescript_compilation():
    """Verify the TypeScript file compiles without errors."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", TARGET_FILE],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    # Accept returncode 0 as success - the file has valid TypeScript syntax
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"


def test_system_message_prefix_no_inline_backticks():
    """Verify systemMessagePrefix does not contain inline triple backticks."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the systemMessagePrefix assignment - use a pattern that allows backticks inside
    match = re.search(
        r'systemMessagePrefix\s*=\s*`((?:[^`]|\\`)*?)`;',
        content,
        re.DOTALL
    )
    assert match is not None, "Could not find systemMessagePrefix definition"

    prefix_content = match.group(1)

    # The prose should NOT contain literal triple backticks (even if escaped)
    # The base commit has: "a tool code block (\`\`\`tool)"
    assert '\\`\\`\\`tool' not in prefix_content and '```tool' not in prefix_content, \
        "systemMessagePrefix contains inline triple backticks - this causes fence nesting ambiguity"

    # The corrected text should be present
    assert "the tool code block format shown below" in prefix_content, \
        "systemMessagePrefix missing expected corrected text"


def test_system_message_suffix_no_inline_backticks():
    """Verify systemMessageSuffix does not contain inline triple backticks in rules."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the systemMessageSuffix assignment
    match = re.search(
        r'systemMessageSuffix\s*=\s*`((?:[^`]|\\`)*?)`;',
        content,
        re.DOTALL
    )
    assert match is not None, "Could not find systemMessageSuffix definition"

    suffix_content = match.group(1)

    # The prose should NOT contain literal triple backticks in rule descriptions
    # Rule 1 in base: "output a \`\`\`tool code block"
    # Should be: "output a tool code block"
    assert '\\`\\`\\`tool' not in suffix_content and '```tool' not in suffix_content, \
        "Rule 1 contains inline triple backticks - should be 'tool code block' not '```tool code block'"


def test_system_message_suffix_has_expected_content():
    """Verify systemMessageSuffix contains the corrected rule text."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Match template literal
    match = re.search(
        r'systemMessageSuffix\s*=\s*`((?:[^`]|\\`)*?)`;',
        content,
        re.DOTALL
    )
    assert match is not None, "Could not find systemMessageSuffix definition"

    suffix_content = match.group(1)

    # The corrected text should be present
    assert "output a tool code block using EXACTLY" in suffix_content, \
        "Rule 1 missing expected corrected text 'output a tool code block'"

    assert "Stop immediately after the closing fence" in suffix_content, \
        "Rule 4 missing expected corrected text 'closing fence'"


def test_class_properties_are_strings():
    """Verify the class properties are defined as template literal strings."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Both should be defined with template literals (backticks)
    # Use pattern that allows escaped backticks inside
    assert re.search(r'systemMessagePrefix\s*=\s*`(?:[^`]|\\`)*`;', content, re.DOTALL), \
        "systemMessagePrefix should be a template literal"
    assert re.search(r'systemMessageSuffix\s*=\s*`(?:[^`]|\\`)*`;', content, re.DOTALL), \
        "systemMessageSuffix should be a template literal"


def test_example_fences_remain_unchanged():
    """Verify that actual code examples (in tool definitions) still use proper fences."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # The example tool definitions should still have proper triple backticks
    # Check for escaped backticks in the source
    assert "\\`\\`\\`tool_definition" in content or "```tool_definition" in content, \
        "Example tool definition fences should remain intact"
    assert "exampleDynamicToolDefinition" in content, \
        "exampleDynamicToolDefinition should be present"
    assert "exampleDynamicToolCall" in content, \
        "exampleDynamicToolCall should be present"


def test_accepted_tool_call_starts_unaffected():
    """Verify that the tool call start patterns are not affected."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # These patterns should still have the actual backticks for parsing
    assert '["```tool\\n", "```tool\\n"]' in content, \
        "acceptedToolCallStarts should still contain actual backtick patterns"


def test_repo_prettier_check():
    """Repo's Prettier formatting check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "core/tools/systemMessageTools/**/*.ts",
         "--ignore-path", ".gitignore"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


def test_repo_tsc_core():
    """Core TypeScript compilation passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/core",
    )
    # tsc returns 0 for success, 2 for errors
    assert r.returncode == 0, f"TypeScript check failed:\n{r.stdout[-500:]}"
