"""Behavioral checks for superpowers-scale-processoriented-skills-to-task (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/superpowers")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/brainstorming/SKILL.md')
    assert 'The failure mode is not "too little ceremony." It is jumping to implementation with unchecked assumptions. Simple tasks are where this happens most — you assume you know what the user wants and start ' in text, "expected to find: " + 'The failure mode is not "too little ceremony." It is jumping to implementation with unchecked assumptions. Simple tasks are where this happens most — you assume you know what the user wants and start '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/brainstorming/SKILL.md')
    assert 'Steps 1–4 always happen. Steps 5–7 scale to the task. **GATE — when you believe a step can be safely elided, ask the user for permission.** Do not skip silently. For example: "This is straightforward ' in text, "expected to find: " + 'Steps 1–4 always happen. Steps 5–7 scale to the task. **GATE — when you believe a step can be safely elided, ask the user for permission.** Do not skip silently. For example: "This is straightforward '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/brainstorming/SKILL.md')
    assert 'Help turn ideas into fully formed designs and specs through natural collaborative dialogue. Scale your effort to the task — a link in a header needs a different process than a new subsystem — but alwa' in text, "expected to find: " + 'Help turn ideas into fully formed designs and specs through natural collaborative dialogue. Scale your effort to the task — a link in a header needs a different process than a new subsystem — but alwa'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/subagent-driven-development/SKILL.md')
    assert "Scale the review process to the task. A one-line config change doesn't need the same review rigor as a new subsystem. **GATE — when you believe review stages or the final reviewer can be safely collap" in text, "expected to find: " + "Scale the review process to the task. A one-line config change doesn't need the same review rigor as a new subsystem. **GATE — when you believe review stages or the final reviewer can be safely collap"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/subagent-driven-development/SKILL.md')
    assert '"Read plan, extract all tasks with full text, note context, create your task list" -> "Dispatch implementer subagent (./implementer-prompt.md)";' in text, "expected to find: " + '"Read plan, extract all tasks with full text, note context, create your task list" -> "Dispatch implementer subagent (./implementer-prompt.md)";'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/subagent-driven-development/SKILL.md')
    assert '"Two-stage review warranted?" -> "Ask user permission\\nto elide or collapse reviews" [label="no — may be\\noverkill"];' in text, "expected to find: " + '"Two-stage review warranted?" -> "Ask user permission\\nto elide or collapse reviews" [label="no — may be\\noverkill"];'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/writing-plans/SKILL.md')
    assert '**GATE — Do not elide without permission.** For small, single-file changes, the review loop may be unnecessary. If you believe it can be safely elided, you MUST ask the user before proceeding without ' in text, "expected to find: " + '**GATE — Do not elide without permission.** For small, single-file changes, the review loop may be unnecessary. If you believe it can be safely elided, you MUST ask the user before proceeding without '[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/writing-plans/SKILL.md')
    assert "Scale the plan to the task. A one-file change doesn't need the same plan as a new subsystem. When you believe steps can be safely elided, ask the user for permission — don't elide silently, and don't " in text, "expected to find: " + "Scale the plan to the task. A one-file change doesn't need the same plan as a new subsystem. When you believe steps can be safely elided, ask the user for permission — don't elide silently, and don't "[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/writing-plans/SKILL.md')
    assert '> "The plan is saved to `docs/superpowers/plans/<filename>.md`. Before we start implementation, I recommend compacting this session — execution works better with a fresh window."' in text, "expected to find: " + '> "The plan is saved to `docs/superpowers/plans/<filename>.md`. Before we start implementation, I recommend compacting this session — execution works better with a fresh window."'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/writing-skills/SKILL.md')
    assert '- **Behavioral gates** — decision diamonds in process flows act as enforcement mechanisms, not just documentation. Testing showed agents follow graphviz gates more reliably than prose instructions alo' in text, "expected to find: " + '- **Behavioral gates** — decision diamonds in process flows act as enforcement mechanisms, not just documentation. Testing showed agents follow graphviz gates more reliably than prose instructions alo'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/writing-skills/SKILL.md')
    assert 'Agents treat GATE-marked instructions as harder constraints than unmarked prose. Pair with a decision diamond in the process flow diagram for strongest effect.' in text, "expected to find: " + 'Agents treat GATE-marked instructions as harder constraints than unmarked prose. Pair with a decision diamond in the process flow diagram for strongest effect.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/writing-skills/SKILL.md')
    assert 'Label decision points that must not be silently bypassed with `**GATE —**` followed by the constraint:' in text, "expected to find: " + 'Label decision points that must not be silently bypassed with `**GATE —**` followed by the constraint:'[:80]

