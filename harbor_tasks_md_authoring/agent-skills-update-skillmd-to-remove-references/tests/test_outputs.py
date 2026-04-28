"""Behavioral checks for agent-skills-update-skillmd-to-remove-references (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firebase-ai-logic-basics/SKILL.md')
    assert 'Consider that you do not need to hardcode model names (e.g., `gemini-flash-lite-latest`). Use Firebase Remote Config to update model versions dynamically without deploying new client code.  See [Chang' in text, "expected to find: " + 'Consider that you do not need to hardcode model names (e.g., `gemini-flash-lite-latest`). Use Firebase Remote Config to update model versions dynamically without deploying new client code.  See [Chang'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firebase-ai-logic-basics/SKILL.md')
    assert '- Start with Gemini for most use cases, and choose Imagen for specialized tasks where image quality and specific styles are critical. (Example: gemini-2.5-flash-image)' in text, "expected to find: " + '- Start with Gemini for most use cases, and choose Imagen for specialized tasks where image quality and specific styles are critical. (Example: gemini-2.5-flash-image)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firebase-ai-logic-basics/SKILL.md')
    assert '**Always use the most recent version of Gemini (gemini-flash-latest) unless another model is requested by the docs or the user. DO NOT USE gemini-1.5-flash**' in text, "expected to find: " + '**Always use the most recent version of Gemini (gemini-flash-latest) unless another model is requested by the docs or the user. DO NOT USE gemini-1.5-flash**'[:80]

