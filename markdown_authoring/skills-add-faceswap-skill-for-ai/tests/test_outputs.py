"""Behavioral checks for skills-add-faceswap-skill-for-ai (markdown_authoring task).

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
    text = _read('skills/faceswap/SKILL.md')
    assert 'Swap faces in a video using AI via the HeyGen API. Use when: (1) Replacing a face in a video with another face, (2) Face swapping from a source image onto a target video, (3) Creating personalized vid' in text, "expected to find: " + 'Swap faces in a video using AI via the HeyGen API. Use when: (1) Replacing a face in a video with another face, (2) Face swapping from a source image onto a target video, (3) Creating personalized vid'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/faceswap/SKILL.md')
    assert 'Swap a face from a source image into a target video using GPU-accelerated AI processing. The source image provides the face to swap in, and the target video receives the new face.' in text, "expected to find: " + 'Swap a face from a source image into a target video using GPU-accelerated AI processing. The source image provides the face to swap in, and the target video receives the new face.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/faceswap/SKILL.md')
    assert '-d \'{"workflow_type": "FaceswapNode", "input": {"source_image_url": "https://example.com/face.jpg", "target_video_url": "https://example.com/video.mp4"}}\'' in text, "expected to find: " + '-d \'{"workflow_type": "FaceswapNode", "input": {"source_image_url": "https://example.com/face.jpg", "target_video_url": "https://example.com/video.mp4"}}\''[:80]

