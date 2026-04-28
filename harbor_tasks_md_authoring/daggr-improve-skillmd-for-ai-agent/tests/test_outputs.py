"""Behavioral checks for daggr-improve-skillmd-for-ai-agent (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/daggr")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/daggr/SKILL.md')
    assert 'Find Spaces with semantic queries (describe what you need): `https://huggingface.co/api/spaces/semantic-search?q=generate+music+for+a+video&sdk=gradio&includeNonRunning=false`' in text, "expected to find: " + 'Find Spaces with semantic queries (describe what you need): `https://huggingface.co/api/spaces/semantic-search?q=generate+music+for+a+video&sdk=gradio&includeNonRunning=false`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/daggr/SKILL.md')
    assert 'Or by category: `https://huggingface.co/api/spaces/semantic-search?category=image-generation&sdk=gradio&includeNonRunning=false`' in text, "expected to find: " + 'Or by category: `https://huggingface.co/api/spaces/semantic-search?category=image-generation&sdk=gradio&includeNonRunning=false`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/daggr/SKILL.md')
    assert "Replace `<space-subdomain>` with the Space's subdomain (e.g., `Tongyi-MAI/Z-Image-Turbo` → `tongyi-mai-z-image-turbo`)." in text, "expected to find: " + "Replace `<space-subdomain>` with the Space's subdomain (e.g., `Tongyi-MAI/Z-Image-Turbo` → `tongyi-mai-z-image-turbo`)."[:80]

