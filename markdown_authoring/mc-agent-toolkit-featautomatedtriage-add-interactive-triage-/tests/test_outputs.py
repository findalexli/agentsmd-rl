"""Behavioral checks for mc-agent-toolkit-featautomatedtriage-add-interactive-triage- (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mc-agent-toolkit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/automated-triage/SKILL.md')
    assert '**Action guard — workflow mode:** Never call write tools (`update_alert`, `set_alert_owner`, `create_or_update_alert_comment`) while building or testing a workflow, regardless of what the workflow doc' in text, "expected to find: " + '**Action guard — workflow mode:** Never call write tools (`update_alert`, `set_alert_owner`, `create_or_update_alert_comment`) while building or testing a workflow, regardless of what the workflow doc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/automated-triage/SKILL.md')
    assert '> "Are you looking to **triage some alerts right now** (I\'ll investigate them with you using the triage tools), or **set up / refine an automated triage workflow** (I\'ll help you design a process that' in text, "expected to find: " + '> "Are you looking to **triage some alerts right now** (I\'ll investigate them with you using the triage tools), or **set up / refine an automated triage workflow** (I\'ll help you design a process that'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/automated-triage/SKILL.md')
    assert '**Write tools in interactive triage:** After findings are clear, proactively offer relevant actions — updating status, declaring a severity, assigning an owner, or posting a comment. Ask before execut' in text, "expected to find: " + '**Write tools in interactive triage:** After findings are clear, proactively offer relevant actions — updating status, declaring a severity, assigning an owner, or posting a comment. Ask before execut'[:80]

