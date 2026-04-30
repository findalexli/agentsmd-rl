"""Behavioral checks for neo-featagents-codify-peerescalation-discipline-as (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/neo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '7. **Peer Escalation Protocol (Swarm Strength Primitive):** *"Stuck is data, not failure. Asking is discipline."* When you encounter friction that resists multiple debugging hypotheses (substrate-edge' in text, "expected to find: " + '7. **Peer Escalation Protocol (Swarm Strength Primitive):** *"Stuck is data, not failure. Asking is discipline."* When you encounter friction that resists multiple debugging hypotheses (substrate-edge'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '5. **Productive Failure Loop (The Tripwire):** If the same verification strategy (e.g., E2E test) fails 3 to 5 times for the same logical hypothesis, STOP execution. Do not panic. Instead, step back a' in text, "expected to find: " + '5. **Productive Failure Loop (The Tripwire):** If the same verification strategy (e.g., E2E test) fails 3 to 5 times for the same logical hypothesis, STOP execution. Do not panic. Instead, step back a'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '6. **Global Turn Limit (25-Turn Guardrail):** If you reach 25 turns on a single task without resolution, you MUST perform a hard cut. Stop coding, invoke `add_memory`, and provide a comprehensive stat' in text, "expected to find: " + '6. **Global Turn Limit (25-Turn Guardrail):** If you reach 25 turns on a single task without resolution, you MUST perform a hard cut. Stop coding, invoke `add_memory`, and provide a comprehensive stat'[:80]

