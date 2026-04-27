"""Behavioral checks for bria-skill-add-briaai-redirect-for-generative (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/bria-skill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/image-utils/SKILL.md')
    assert '**Rule of thumb**: If the task requires *creating new visual content* or *understanding image semantics*, use `bria-ai`. If the task requires *transforming existing pixels* (resize, crop, format conve' in text, "expected to find: " + '**Rule of thumb**: If the task requires *creating new visual content* or *understanding image semantics*, use `bria-ai`. If the task requires *transforming existing pixels* (resize, crop, format conve'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/image-utils/SKILL.md')
    assert 'This skill handles **deterministic pixel-level operations** only. For any **generative or AI-powered** image work, use the `bria-ai` skill instead:' in text, "expected to find: " + 'This skill handles **deterministic pixel-level operations** only. For any **generative or AI-powered** image work, use the `bria-ai` skill instead:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/image-utils/SKILL.md')
    assert '- **AI image editing (inpainting, object removal/addition)** → use `bria-ai`' in text, "expected to find: " + '- **AI image editing (inpainting, object removal/addition)** → use `bria-ai`'[:80]

