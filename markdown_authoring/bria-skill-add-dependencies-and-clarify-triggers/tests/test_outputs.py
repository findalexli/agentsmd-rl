"""Behavioral checks for bria-skill-add-dependencies-and-clarify-triggers (markdown_authoring task).

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
    text = _read('skills/bria-ai/SKILL.md')
    assert 'description: Generate, edit, and transform images with commercially-safe AI models. Create images from text, edit by natural language instruction, remove backgrounds (transparent PNG), replace backgro' in text, "expected to find: " + 'description: Generate, edit, and transform images with commercially-safe AI models. Create images from text, edit by natural language instruction, remove backgrounds (transparent PNG), replace backgro'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bria-ai/SKILL.md')
    assert 'description: "Bria AI API key (get one at https://platform.bria.ai/console/account/api-keys)"' in text, "expected to find: " + 'description: "Bria AI API key (get one at https://platform.bria.ai/console/account/api-keys)"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bria-ai/SKILL.md')
    assert 'name: BRIA_API_KEY' in text, "expected to find: " + 'name: BRIA_API_KEY'[:80]

