"""Behavioral checks for agents-skill-airflow-hitl (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agents")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/airflow-hitl/SKILL.md')
    assert 'description: Use when the user needs human-in-the-loop workflows in Airflow (approval/reject, form input, or human-driven branching). Covers ApprovalOperator, HITLOperator, HITLBranchOperator, HITLEnt' in text, "expected to find: " + 'description: Use when the user needs human-in-the-loop workflows in Airflow (approval/reject, form input, or human-driven branching). Covers ApprovalOperator, HITLOperator, HITLBranchOperator, HITLEnt'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/airflow-hitl/SKILL.md')
    assert 'Implement human approval gates, form inputs, and human-driven branching in Airflow DAGs using the HITL operators. These deferrable operators pause workflow execution until a human responds via the Air' in text, "expected to find: " + 'Implement human approval gates, form inputs, and human-driven branching in Airflow DAGs using the HITL operators. These deferrable operators pause workflow execution until a human responds via the Air'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/airflow-hitl/SKILL.md')
    assert "> **UI Location**: View pending actions at **Browse → Required Actions** in Airflow UI. Respond via the **task instance page's Required Actions tab** or the REST API." in text, "expected to find: " + "> **UI Location**: View pending actions at **Browse → Required Actions** in Airflow UI. Respond via the **task instance page's Required Actions tab** or the REST API."[:80]

