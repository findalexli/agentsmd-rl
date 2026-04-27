"""Behavioral checks for sitf-skill-update-to-stick-to (markdown_authoring task).

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
    text = _read('.claude/skills/technique-proposal/SKILL.md')
    assert '**Example:** If an attacker uses CI/CD as initial access, then pivots to cloud production and uses a Kubernetes privilege escalation technique, the K8s privesc is **out of scope** for SITF. Instead:' in text, "expected to find: " + '**Example:** If an attacker uses CI/CD as initial access, then pivots to cloud production and uses a Kubernetes privilege escalation technique, the K8s privesc is **out of scope** for SITF. Instead:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/technique-proposal/SKILL.md')
    assert '**If scope check fails:** Do not generate a technique proposal. Instead, explain why the attack step is out of scope and recommend the appropriate framework (MITRE ATT&CK, etc.).' in text, "expected to find: " + '**If scope check fails:** Do not generate a technique proposal. Instead, explain why the attack step is out of scope and recommend the appropriate framework (MITRE ATT&CK, etc.).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/technique-proposal/SKILL.md')
    assert '1. For attack flows: Mark the step with `"type": "out-of-scope"` and reference the appropriate framework (e.g., "MITRE ATT&CK: Escape to Host - T1611")' in text, "expected to find: " + '1. For attack flows: Mark the step with `"type": "out-of-scope"` and reference the appropriate framework (e.g., "MITRE ATT&CK: Escape to Host - T1611")'[:80]

