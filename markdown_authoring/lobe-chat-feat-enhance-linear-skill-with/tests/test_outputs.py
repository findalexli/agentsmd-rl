"""Behavioral checks for lobe-chat-feat-enhance-linear-skill-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lobe-chat")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/linear/SKILL.md')
    assert '4. **Mark as In Progress**: When starting to plan or implement an issue, immediately update status to **"In Progress"** via `mcp__linear-server__update_issue`' in text, "expected to find: " + '4. **Mark as In Progress**: When starting to plan or implement an issue, immediately update status to **"In Progress"** via `mcp__linear-server__update_issue`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/linear/SKILL.md')
    assert '2. **Read images**: If the issue description contains images, MUST use `mcp__linear-server__extract_images` to read image content for full context' in text, "expected to find: " + '2. **Read images**: If the issue description contains images, MUST use `mcp__linear-server__extract_images` to read image content for full context'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/linear/SKILL.md')
    assert '3. **Check for sub-issues**: Use `mcp__linear-server__list_issues` with `parentId` filter' in text, "expected to find: " + '3. **Check for sub-issues**: Use `mcp__linear-server__list_issues` with `parentId` filter'[:80]

