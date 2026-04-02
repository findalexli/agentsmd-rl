"""
Task: vscode-terminal-markdown-escape-fix
Repo: microsoft/vscode @ 891f5f2f96fe5161122912af25d8b3af708cbd1b
PR:   306535

Fix: Remove unnecessary markdown escaping in terminal invocation messages.
escapeMarkdownSyntaxTokens() was redundantly pre-escaping displayCommand before
passing it into MarkdownString via a localize template; the backtick code spans
already handle special characters correctly.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/vscode"
TARGET = Path(
    f"{REPO}/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts"
)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file present + import structure intact
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_exists_and_has_imports():
    """Target file must exist and contain its htmlContent.js import."""
    assert TARGET.exists(), f"Target file not found: {TARGET}"
    content = TARGET.read_text()
    assert "htmlContent.js" in content, "htmlContent.js import missing from file"
    assert "MarkdownString" in content, "MarkdownString no longer present in file"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_escape_function_not_imported():
    """escapeMarkdownSyntaxTokens must not be imported from htmlContent.js.

    Base commit: import includes escapeMarkdownSyntaxTokens.
    After fix: import only contains MarkdownString and IMarkdownString.
    """
    content = TARGET.read_text()
    # Collect all import lines that pull from htmlContent.js
    htmlcontent_imports = [
        line for line in content.splitlines()
        if "htmlContent.js" in line and line.strip().startswith("import")
    ]
    assert len(htmlcontent_imports) >= 1, "htmlContent.js import line is missing"
    for line in htmlcontent_imports:
        assert "escapeMarkdownSyntaxTokens" not in line, (
            f"escapeMarkdownSyntaxTokens still imported: {line.strip()}"
        )


# [pr_diff] fail_to_pass
def test_escaped_display_command_removed():
    """The escapedDisplayCommand variable must be fully removed.

    Base commit: const escapedDisplayCommand = escapeMarkdownSyntaxTokens(displayCommand);
    After fix: no such variable exists.
    """
    content = TARGET.read_text()
    assert "const escapedDisplayCommand" not in content, (
        "escapedDisplayCommand variable declaration still present"
    )
    assert "escapedDisplayCommand" not in content, (
        "References to escapedDisplayCommand still exist in file"
    )


# [pr_diff] fail_to_pass
def test_invocation_messages_use_display_command_directly():
    """All 4 localize invocation calls must pass displayCommand (not escapedDisplayCommand).

    Base commit: all 4 calls end with `escapedDisplayCommand)`.
    After fix: all 4 calls end with `displayCommand)`.
    """
    content = TARGET.read_text()
    invocation_keys = [
        "runInTerminal.invocation.sandbox.background",
        "runInTerminal.invocation.sandbox",
        "runInTerminal.invocation.background",
        "runInTerminal.invocation",
    ]
    for key in invocation_keys:
        matching = [
            line.strip() for line in content.splitlines()
            if key in line and "localize(" in line
        ]
        assert len(matching) >= 1, f"Localize call for '{key}' not found"
        for line in matching:
            assert "escapedDisplayCommand" not in line, (
                f"Localize call for '{key}' still uses escapedDisplayCommand:\n  {line}"
            )
            # After the fix, displayCommand must appear as the argument
            assert "displayCommand" in line, (
                f"Localize call for '{key}' does not pass displayCommand:\n  {line}"
            )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression: localization structure unchanged
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_localize_keys_preserved():
    """All 4 runInTerminal invocation localize message keys must still be present.

    The fix only removes the escape step; the message structure is unchanged.
    """
    content = TARGET.read_text()
    required_keys = [
        "runInTerminal.invocation.sandbox.background",
        "runInTerminal.invocation.sandbox",
        "runInTerminal.invocation.background",
        "runInTerminal.invocation",
    ]
    for key in required_keys:
        assert key in content, f"Required localize key missing: '{key}'"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rule from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:139 @ 891f5f2f96fe5161122912af25d8b3af708cbd1b
def test_no_blank_line_left_in_import_block():
    """No blank line left behind from import removal; import block must be compact.

    Rule: "When removing an import, do not leave behind blank lines where the
    import was. Ensure the surrounding code remains compact."
    (.github/copilot-instructions.md line 139)

    Concretely: the area between the 'event.js' import and the 'lifecycle.js'
    import must contain no blank lines.
    """
    lines = TARGET.read_text().splitlines()
    # Find the import block landmarks
    event_idx = next(
        (i for i, l in enumerate(lines) if "from '../../../../../../base/common/event.js'" in l),
        None,
    )
    lifecycle_idx = next(
        (i for i, l in enumerate(lines) if "from '../../../../../../base/common/lifecycle.js'" in l),
        None,
    )
    assert event_idx is not None, "event.js import not found"
    assert lifecycle_idx is not None, "lifecycle.js import not found"
    assert lifecycle_idx > event_idx, "Unexpected file structure"

    between = lines[event_idx + 1 : lifecycle_idx]
    blank_lines = [l for l in between if l.strip() == ""]
    assert len(blank_lines) == 0, (
        f"Blank line(s) found in import block between event.js and lifecycle.js: "
        f"{len(blank_lines)} blank line(s)"
    )
