"""Behavioral checks for swift-concurrency-agent-skill-add-github-copilot-instruction (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/swift-concurrency-agent-skill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Consider cross-surface compatibility**: Skills should work across different AI coding assistants and platforms that support the Agent Skills format (for example, GitHub Copilot, Claude-based tools' in text, "expected to find: " + '- **Consider cross-surface compatibility**: Skills should work across different AI coding assistants and platforms that support the Agent Skills format (for example, GitHub Copilot, Claude-based tools'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "**Remember**: You're reviewing as an Agent Skills expert. Focus on format compliance, progressive disclosure, clear instructions, and agent usability. Help maintain the quality and interoperability of" in text, "expected to find: " + "**Remember**: You're reviewing as an Agent Skills expert. Focus on format compliance, progressive disclosure, clear instructions, and agent usability. Help maintain the quality and interoperability of"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Review code changes as an **Agent Skills expert**, focusing on the [Agent Skills open format](https://agentskills.io/home) specification and best practices.' in text, "expected to find: " + 'Review code changes as an **Agent Skills expert**, focusing on the [Agent Skills open format](https://agentskills.io/home) specification and best practices.'[:80]

