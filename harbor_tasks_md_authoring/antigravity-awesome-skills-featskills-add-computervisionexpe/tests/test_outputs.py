"""Behavioral checks for antigravity-awesome-skills-featskills-add-computervisionexpe (markdown_authoring task).

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
    text = _read('skills/computer-vision-expert/SKILL.md')
    assert 'To provide expert guidance on designing, implementing, and optimizing state-of-the-art computer vision pipelines. From real-time object detection with YOLO26 to foundation model-based segmentation wit' in text, "expected to find: " + 'To provide expert guidance on designing, implementing, and optimizing state-of-the-art computer vision pipelines. From real-time object detection with YOLO26 to foundation model-based segmentation wit'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/computer-vision-expert/SKILL.md')
    assert 'description: SOTA Computer Vision Expert (2026). Specialized in YOLO26, Segment Anything 3 (SAM 3), Vision Language Models, and real-time spatial analysis.' in text, "expected to find: " + 'description: SOTA Computer Vision Expert (2026). Specialized in YOLO26, Segment Anything 3 (SAM 3), Vision Language Models, and real-time spatial analysis.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/computer-vision-expert/SKILL.md')
    assert '- **Improved Small-Object Recognition**: Expertise in using ProgLoss and STAL assignment for high precision in IoT and industrial settings.' in text, "expected to find: " + '- **Improved Small-Object Recognition**: Expertise in using ProgLoss and STAL assignment for high precision in IoT and industrial settings.'[:80]

