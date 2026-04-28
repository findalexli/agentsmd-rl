"""Behavioral checks for mcp-update-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Copilot submitted PRs are not trustworthy by default. Users with `write` access to the repo need to validate the contents of this PR before leaving a comment with the text `/azp run mcp - pullrequest ' in text, "expected to find: " + 'Copilot submitted PRs are not trustworthy by default. Users with `write` access to the repo need to validate the contents of this PR before leaving a comment with the text `/azp run mcp - pullrequest '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Create the auto-generated PR body as normal, but `copilot` should add an additional section after all of its regular PR body content. The contents should be:' in text, "expected to find: " + '- Create the auto-generated PR body as normal, but `copilot` should add an additional section after all of its regular PR body content. The contents should be:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '## Invoking Livetests' in text, "expected to find: " + '## Invoking Livetests'[:80]

