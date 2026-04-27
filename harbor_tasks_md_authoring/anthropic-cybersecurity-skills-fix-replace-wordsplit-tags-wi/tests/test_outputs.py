"""Behavioral checks for anthropic-cybersecurity-skills-fix-replace-wordsplit-tags-wi (markdown_authoring task).

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
    text = _read('skills/analyzing-azure-activity-logs-for-threats/SKILL.md')
    assert '- cloud-security' in text, "expected to find: " + '- cloud-security'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/analyzing-azure-activity-logs-for-threats/SKILL.md')
    assert '- threat-hunting' in text, "expected to find: " + '- threat-hunting'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/analyzing-azure-activity-logs-for-threats/SKILL.md')
    assert '- azure-monitor' in text, "expected to find: " + '- azure-monitor'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/analyzing-memory-forensics-with-lime-and-volatility/SKILL.md')
    assert '- incident-response' in text, "expected to find: " + '- incident-response'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/analyzing-memory-forensics-with-lime-and-volatility/SKILL.md')
    assert '- memory-forensics' in text, "expected to find: " + '- memory-forensics'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/analyzing-memory-forensics-with-lime-and-volatility/SKILL.md')
    assert '- linux-forensics' in text, "expected to find: " + '- linux-forensics'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/analyzing-powershell-script-block-logging/SKILL.md')
    assert '- obfuscation-detection' in text, "expected to find: " + '- obfuscation-detection'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/analyzing-powershell-script-block-logging/SKILL.md')
    assert '- script-block-logging' in text, "expected to find: " + '- script-block-logging'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/analyzing-powershell-script-block-logging/SKILL.md')
    assert '- windows-forensics' in text, "expected to find: " + '- windows-forensics'[:80]

