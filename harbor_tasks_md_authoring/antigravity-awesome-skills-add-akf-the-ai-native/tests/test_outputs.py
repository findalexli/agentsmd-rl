"""Behavioral checks for antigravity-awesome-skills-add-akf-the-ai-native (markdown_authoring task).

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
    text = _read('skills/akf-trust-metadata/SKILL.md')
    assert 'description: "The AI native file format. EXIF for AI — stamps every file with trust scores, source provenance, and compliance metadata. Embeds into 20+ formats (DOCX, PDF, images, code). EU AI Act, SO' in text, "expected to find: " + 'description: "The AI native file format. EXIF for AI — stamps every file with trust scores, source provenance, and compliance metadata. Embeds into 20+ formats (DOCX, PDF, images, code). EU AI Act, SO'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/akf-trust-metadata/SKILL.md')
    assert 'Every photo has EXIF. Every song has ID3. AKF is the native metadata format for AI-generated content.' in text, "expected to find: " + 'Every photo has EXIF. Every song has ID3. AKF is the native metadata format for AI-generated content.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/akf-trust-metadata/SKILL.md')
    assert 'akf stamp <file> --agent <agent-name> --evidence "<what you did>"' in text, "expected to find: " + 'akf stamp <file> --agent <agent-name> --evidence "<what you did>"'[:80]

