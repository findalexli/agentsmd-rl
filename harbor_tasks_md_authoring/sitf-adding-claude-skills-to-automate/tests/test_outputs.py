"""Behavioral checks for sitf-adding-claude-skills-to-automate (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sitf")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/attack-flow/SKILL.md')
    assert 'description: Generate SITF-compliant attack flow JSON files from attack descriptions or incident reports. Use when analyzing supply chain attacks, breaches, or security incidents.' in text, "expected to find: " + 'description: Generate SITF-compliant attack flow JSON files from attack descriptions or incident reports. Use when analyzing supply chain attacks, breaches, or security incidents.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/attack-flow/SKILL.md')
    assert '- Example: Uploading stolen data to repos → T-V003 (Secret Exfiltration), NOT T-V008 (Malicious Hosting)' in text, "expected to find: " + '- Example: Uploading stolen data to repos → T-V003 (Secret Exfiltration), NOT T-V008 (Malicious Hosting)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/attack-flow/SKILL.md')
    assert '- **Secondary**: Within same attack step, order by stage (Initial Access → Discovery → Post-Compromise)' in text, "expected to find: " + '- **Secondary**: Within same attack step, order by stage (Initial Access → Discovery → Post-Compromise)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/technique-proposal/SKILL.md')
    assert "description: Generate a PR-ready technique proposal when an attack step doesn't map to existing SITF techniques. Use after /attack-flow identifies technique gaps." in text, "expected to find: " + "description: Generate a PR-ready technique proposal when an attack step doesn't map to existing SITF techniques. Use after /attack-flow identifies technique gaps."[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/technique-proposal/SKILL.md')
    assert '"description": "Attacker invokes AI CLI tools with permission-bypass flags to scan filesystem and catalog sensitive files for exfiltration",' in text, "expected to find: " + '"description": "Attacker invokes AI CLI tools with permission-bypass flags to scan filesystem and catalog sensitive files for exfiltration",'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/technique-proposal/SKILL.md')
    assert '- https://www.stepsecurity.io/blog/supply-chain-security-alert-popular-nx-build-system-package-compromised-with-data-stealing-malware' in text, "expected to find: " + '- https://www.stepsecurity.io/blog/supply-chain-security-alert-popular-nx-build-system-package-compromised-with-data-stealing-malware'[:80]

