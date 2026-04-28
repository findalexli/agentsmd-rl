"""Behavioral checks for gemini-skills-enhance-skillmd-with-java-sdk (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gemini-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gemini-api-dev/SKILL.md')
    assert 'description: Use this skill when building applications with Gemini models, Gemini API, working with multimodal content (text, images, audio, video), implementing function calling, using structured out' in text, "expected to find: " + 'description: Use this skill when building applications with Gemini models, Gemini API, working with multimodal content (text, images, audio, video), implementing function calling, using structured out'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gemini-api-dev/SKILL.md')
    assert "- Latest version can be found here: https://central.sonatype.com/artifact/com.google.genai/google-genai/versions (let's call it `LAST_VERSION`)" in text, "expected to find: " + "- Latest version can be found here: https://central.sonatype.com/artifact/com.google.genai/google-genai/versions (let's call it `LAST_VERSION`)"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gemini-api-dev/SKILL.md')
    assert 'implementation("com.google.genai:google-genai:${LAST_VERSION}")' in text, "expected to find: " + 'implementation("com.google.genai:google-genai:${LAST_VERSION}")'[:80]

