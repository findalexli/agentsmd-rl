"""Behavioral checks for skills-add-generatevideo-skill-for-ai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ai-video-gen/SKILL.md')
    assert 'Generate AI videos from text prompts using the HeyGen API. Use when: (1) Generating videos from text descriptions, (2) Creating AI-generated video clips for content production, (3) Image-to-video gene' in text, "expected to find: " + 'Generate AI videos from text prompts using the HeyGen API. Use when: (1) Generating videos from text descriptions, (2) Creating AI-generated video clips for content production, (3) Image-to-video gene'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ai-video-gen/SKILL.md')
    assert 'Generate AI videos from text prompts. Supports multiple providers (VEO 3.1, Kling, Sora, Runway, Seedance), configurable aspect ratios, and optional reference images for image-to-video generation.' in text, "expected to find: " + 'Generate AI videos from text prompts. Supports multiple providers (VEO 3.1, Kling, Sora, Runway, Seedance), configurable aspect ratios, and optional reference images for image-to-video generation.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ai-video-gen/SKILL.md')
    assert '-d \'{"workflow_type": "GenerateVideoNode", "input": {"prompt": "A drone shot flying over a coastal city at sunset"}}\'' in text, "expected to find: " + '-d \'{"workflow_type": "GenerateVideoNode", "input": {"prompt": "A drone shot flying over a coastal city at sunset"}}\''[:80]

