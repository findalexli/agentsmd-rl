"""Behavioral checks for ace-add-cursor-rules-for-pr (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ace")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/ace-context.mdc')
    assert 'To use the PR review rules, configure the GitHub MCP server in Cursor\'s "Tools & MCP" settings. You will need a read-only personal access token with the following permissions: Pull requests, Issues, C' in text, "expected to find: " + 'To use the PR review rules, configure the GitHub MCP server in Cursor\'s "Tools & MCP" settings. You will need a read-only personal access token with the following permissions: Pull requests, Issues, C'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/ace-context.mdc')
    assert 'This is a Python machine learning project for atmospheric modeling (ACE - AI2 Climate Emulator).' in text, "expected to find: " + 'This is a Python machine learning project for atmospheric modeling (ACE - AI2 Climate Emulator).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/ace-context.mdc')
    assert '- Code is in the `fme/` directory (ace, core, coupled, diffusion, downscaling modules)' in text, "expected to find: " + '- Code is in the `fme/` directory (ace, core, coupled, diffusion, downscaling modules)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pr-rereview.mdc')
    assert '1. **Previous Review Context Available**: If the current conversation contains a previous PR review or re-review from the Assistant, note those findings to compare against new changes. Ignore any revi' in text, "expected to find: " + '1. **Previous Review Context Available**: If the current conversation contains a previous PR review or re-review from the Assistant, note those findings to compare against new changes. Ignore any revi'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pr-rereview.mdc')
    assert '- **If no commit SHA is provided**: Ask the user for the commit SHA where the previous review ended, OR offer to review all changes since the last review comment timestamp.' in text, "expected to find: " + '- **If no commit SHA is provided**: Ask the user for the commit SHA where the previous review ended, OR offer to review all changes since the last review comment timestamp.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pr-rereview.mdc')
    assert '> **Note**: The following issues from the previous Assistant review were not addressed in the PR review comments. Would you like me to include these in the summary?' in text, "expected to find: " + '> **Note**: The following issues from the previous Assistant review were not addressed in the PR review comments. Would you like me to include these in the summary?'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pr-review.mdc')
    assert 'When asked to review a pull request (e.g., "Review PR #N in the ace repo"):' in text, "expected to find: " + 'When asked to review a pull request (e.g., "Review PR #N in the ace repo"):'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pr-review.mdc')
    assert '2. **Analyze and Output** a structured review with these sections:' in text, "expected to find: " + '2. **Analyze and Output** a structured review with these sections:'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pr-review.mdc')
    assert '- Reference specific files and line numbers when applicable' in text, "expected to find: " + '- Reference specific files and line numbers when applicable'[:80]

