"""Behavioral checks for cai-expansion-of-agentsmd-with-detailed (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/agents.md')
    assert 'Agents are the core of CAI. An agent uses Large Language Models (LLMs), configured with instructions and tools to perform specialized cybersecurity tasks. Each agent is defined in its own `.py` file i' in text, "expected to find: " + 'Agents are the core of CAI. An agent uses Large Language Models (LLMs), configured with instructions and tools to perform specialized cybersecurity tasks. Each agent is defined in its own `.py` file i'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/agents.md')
    assert '| **redteam_agent** | Offensive security specialist for penetration testing | Active exploitation, vulnerability discovery | nmap, metasploit, burp |' in text, "expected to find: " + '| **redteam_agent** | Offensive security specialist for penetration testing | Active exploitation, vulnerability discovery | nmap, metasploit, burp |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/agents.md')
    assert '| **blueteam_agent** | Defensive security expert for threat mitigation | Security hardening, incident response | wireshark, suricata, osquery |' in text, "expected to find: " + '| **blueteam_agent** | Defensive security expert for threat mitigation | Security hardening, incident response | wireshark, suricata, osquery |'[:80]

