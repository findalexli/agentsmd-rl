"""Behavioral checks for anthropic-cybersecurity-skills-add-skill-performingaidriveno (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/anthropic-cybersecurity-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/performing-ai-driven-osint-correlation/SKILL.md')
    assert '- **Threat Actor Attribution:** Correlate a suspicious username found in a phishing campaign with social media profiles, domain registrations, and breach data to build an attribution profile.' in text, "expected to find: " + '- **Threat Actor Attribution:** Correlate a suspicious username found in a phishing campaign with social media profiles, domain registrations, and breach data to build an attribution profile.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/performing-ai-driven-osint-correlation/SKILL.md')
    assert '- **Brand Impersonation Detection:** Identify accounts across platforms mimicking a target brand by correlating registration patterns, naming conventions, and temporal signals.' in text, "expected to find: " + '- **Brand Impersonation Detection:** Identify accounts across platforms mimicking a target brand by correlating registration patterns, naming conventions, and temporal signals.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/performing-ai-driven-osint-correlation/SKILL.md')
    assert '6. **Normalize all collected data into a common schema.** Create a unified JSON structure that tags each finding with its source, timestamp, and data type:' in text, "expected to find: " + '6. **Normalize all collected data into a common schema.** Create a unified JSON structure that tags each finding with its source, timestamp, and data type:'[:80]

