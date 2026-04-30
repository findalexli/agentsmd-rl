"""Behavioral checks for claude-code-system-prompts-add-claudemd-for-ai-agent (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-system-prompts")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "Claude Code is Anthropic's CLI tool for agentic coding. It is distributed as a compiled npm package (`@anthropic-ai/claude-code`). Source code is not publicly available. The [anthropics/claude-code](h" in text, "expected to find: " + "Claude Code is Anthropic's CLI tool for agentic coding. It is distributed as a compiled npm package (`@anthropic-ai/claude-code`). Source code is not publicly available. The [anthropics/claude-code](h"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "System prompts extracted via script from the Claude Code npm package's compiled JavaScript source. Maintained by [Piebald AI](https://piebald.ai/), not by Anthropic." in text, "expected to find: " + "System prompts extracted via script from the Claude Code npm package's compiled JavaScript source. Maintained by [Piebald AI](https://piebald.ai/), not by Anthropic."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- **Feature requests:** For changes to Claude Code's prompts, file issues at [anthropics/claude-code/issues](https://github.com/anthropics/claude-code/issues)" in text, "expected to find: " + "- **Feature requests:** For changes to Claude Code's prompts, file issues at [anthropics/claude-code/issues](https://github.com/anthropics/claude-code/issues)"[:80]

