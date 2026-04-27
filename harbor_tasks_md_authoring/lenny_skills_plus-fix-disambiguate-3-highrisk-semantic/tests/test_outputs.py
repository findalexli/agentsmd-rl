"""Behavioral checks for lenny_skills_plus-fix-disambiguate-3-highrisk-semantic (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lenny-skills-plus")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cross-functional-collaboration/SKILL.md')
    assert 'description: "Lead ongoing cross-functional collaboration by producing a Cross-Functional Collaboration Pack (mission charter, stakeholder/incentives map, roles & expectations contract, operating cade' in text, "expected to find: " + 'description: "Lead ongoing cross-functional collaboration by producing a Cross-Functional Collaboration Pack (mission charter, stakeholder/incentives map, roles & expectations contract, operating cade'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/evaluating-trade-offs/SKILL.md')
    assert 'description: "Evaluate trade-offs and produce a Trade-off Evaluation Pack (trade-off brief, options+criteria matrix, all-in cost/opportunity cost table, impact ranges, recommendation, stop/continue tr' in text, "expected to find: " + 'description: "Evaluate trade-offs and produce a Trade-off Evaluation Pack (trade-off brief, options+criteria matrix, all-in cost/opportunity cost table, impact ranges, recommendation, stop/continue tr'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/evaluating-trade-offs/SKILL.md')
    assert '- You’re evaluating a specific technology, vendor, or build-vs-buy for a tool/platform (use `evaluating-new-technology`).' in text, "expected to find: " + '- You’re evaluating a specific technology, vendor, or build-vs-buy for a tool/platform (use `evaluating-new-technology`).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/managing-up/SKILL.md')
    assert 'description: "Manage up effectively and produce a Managing Up Operating System Pack (manager profile, comms cadence, weekly updates, escalation/ask plan, expectation & boundary script, and exec-ready ' in text, "expected to find: " + 'description: "Manage up effectively and produce a Managing Up Operating System Pack (manager profile, comms cadence, weekly updates, escalation/ask plan, expectation & boundary script, and exec-ready '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/running-decision-processes/SKILL.md')
    assert 'description: "Run a high-quality decision process and produce a Decision Process Pack (decision brief/pre-read, options + criteria matrix, RAPID/DACI roles, decision meeting plan, decision log entry, ' in text, "expected to find: " + 'description: "Run a high-quality decision process and produce a Decision Process Pack (decision brief/pre-read, options + criteria matrix, RAPID/DACI roles, decision meeting plan, decision log entry, '[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/stakeholder-alignment/SKILL.md')
    assert 'description: "Align stakeholders and secure buy-in for a specific proposal or decision by producing a Stakeholder Alignment Pack (alignment brief, stakeholder map, exec decision principles, pre-brief ' in text, "expected to find: " + 'description: "Align stakeholders and secure buy-in for a specific proposal or decision by producing a Stakeholder Alignment Pack (alignment brief, stakeholder map, exec decision principles, pre-brief '[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/systems-thinking/SKILL.md')
    assert 'description: "Apply systems thinking to leadership decisions and produce a Systems Thinking Pack (system boundary, actors & incentives map, feedback loops, second-order effects ledger, leverage points' in text, "expected to find: " + 'description: "Apply systems thinking to leadership decisions and produce a Systems Thinking Pack (system boundary, actors & incentives map, feedback loops, second-order effects ledger, leverage points'[:80]

