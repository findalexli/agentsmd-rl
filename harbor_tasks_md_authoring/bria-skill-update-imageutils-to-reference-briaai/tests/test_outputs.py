"""Behavioral checks for bria-skill-update-imageutils-to-reference-briaai (markdown_authoring task).

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
    assert "Use alongside the **[bria-ai skill](https://clawhub.ai/galbria/bria-ai)** to post-process AI-generated images. Generate or edit images with Bria's API, then use image-utils for resizing, cropping, wat" in text, "expected to find: " + "Use alongside the **[bria-ai skill](https://clawhub.ai/galbria/bria-ai)** to post-process AI-generated images. Generate or edit images with Bria's API, then use image-utils for resizing, cropping, wat"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/image-utils/SKILL.md')
    assert 'json={"prompt": "product photo of headphones", "aspect_ratio": "1:1", "sync": True}' in text, "expected to find: " + 'json={"prompt": "product photo of headphones", "aspect_ratio": "1:1", "sync": True}'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/image-utils/SKILL.md')
    assert 'headers={"api_token": BRIA_API_KEY, "Content-Type": "application/json"},' in text, "expected to find: " + 'headers={"api_token": BRIA_API_KEY, "Content-Type": "application/json"},'[:80]

