"""Behavioral checks for anthropic-cybersecurity-skills-add-nist-csf-20-categories (markdown_authoring task).

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
    text = _read('skills/implementing-gdpr-data-protection-controls/SKILL.md')
    assert 'nist_csf: [GV.OC, GV.PO, GV.RR, ID.AM, PR.AA, PR.DS, RS.CO, RS.MA]' in text, "expected to find: " + 'nist_csf: [GV.OC, GV.PO, GV.RR, ID.AM, PR.AA, PR.DS, RS.CO, RS.MA]'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/implementing-iso-27001-information-security-management/SKILL.md')
    assert 'nist_csf: [GV.OC, GV.RM, GV.RR, GV.PO, GV.OV, ID.RA, PR.AA, PR.DS]' in text, "expected to find: " + 'nist_csf: [GV.OC, GV.RM, GV.RR, GV.PO, GV.OV, ID.RA, PR.AA, PR.DS]'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/implementing-pci-dss-compliance-controls/SKILL.md')
    assert 'nist_csf: [GV.PO, ID.RA, PR.AA, PR.DS, PR.PS, DE.CM, DE.AE]' in text, "expected to find: " + 'nist_csf: [GV.PO, ID.RA, PR.AA, PR.DS, PR.PS, DE.CM, DE.AE]'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/performing-nist-csf-maturity-assessment/SKILL.md')
    assert 'nist_csf: [GV.OC, GV.RM, GV.RR, GV.PO, GV.OV, GV.SC, ID.AM, ID.RA, ID.IM, PR.AA, PR.AT, PR.DS, PR.PS, PR.IR, DE.CM, DE.AE, RS.MA, RS.CO, RS.AN, RS.MI, RC.RP, RC.CO]' in text, "expected to find: " + 'nist_csf: [GV.OC, GV.RM, GV.RR, GV.PO, GV.OV, GV.SC, ID.AM, ID.RA, ID.IM, PR.AA, PR.AT, PR.DS, PR.PS, PR.IR, DE.CM, DE.AE, RS.MA, RS.CO, RS.AN, RS.MI, RC.RP, RC.CO]'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/performing-nist-csf-maturity-assessment/SKILL.md')
    assert '| **Identify** | ID | 3 | Determine current cybersecurity risk to the organization |' in text, "expected to find: " + '| **Identify** | ID | 3 | Determine current cybersecurity risk to the organization |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/performing-nist-csf-maturity-assessment/SKILL.md')
    assert '| **Recover** | RC | 2 | Restore capabilities impaired by cybersecurity incidents |' in text, "expected to find: " + '| **Recover** | RC | 2 | Restore capabilities impaired by cybersecurity incidents |'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/performing-soc2-type2-audit-preparation/SKILL.md')
    assert 'nist_csf: [GV.OC, GV.RM, GV.RR, GV.PO, GV.OV, ID.RA, PR.AA, PR.DS, DE.CM, DE.AE, RS.MA]' in text, "expected to find: " + 'nist_csf: [GV.OC, GV.RM, GV.RR, GV.PO, GV.OV, ID.RA, PR.AA, PR.DS, DE.CM, DE.AE, RS.MA]'[:80]

