"""Behavioral checks for antigravity-awesome-skills-featskills-add-minimaxaicli-as-de (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/mmx-cli/SKILL.md')
    assert 'description: "Use mmx to generate text, images, video, speech, and music via the MiniMax AI platform. Use when the user wants to create media content, chat with MiniMax models, perform web search, or ' in text, "expected to find: " + 'description: "Use mmx to generate text, images, video, speech, and music via the MiniMax AI platform. Use when the user wants to create media content, chat with MiniMax models, perform web search, or '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/mmx-cli/SKILL.md')
    assert '- Media-generation tasks can be async, quota-limited, or region-constrained; agents should handle delayed completion and provider-side failures explicitly.' in text, "expected to find: " + '- Media-generation tasks can be async, quota-limited, or region-constrained; agents should handle delayed completion and provider-side failures explicitly.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/mmx-cli/SKILL.md')
    assert '- This skill documents CLI usage only and does not replace provider policy review, content-safety checks, or downstream file validation.' in text, "expected to find: " + '- This skill documents CLI usage only and does not replace provider policy review, content-safety checks, or downstream file validation.'[:80]

