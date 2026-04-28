"""Behavioral checks for flightctl-noissue-internalagent-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/flightctl")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('internal/agent/AGENTS.md')
    assert 'The agent reconciles `Device.Spec` from control plane, reports resource usage, manages application lifecycles, handles OS-level configuration, and provides lifecycle hooks.' in text, "expected to find: " + 'The agent reconciles `Device.Spec` from control plane, reports resource usage, manages application lifecycles, handles OS-level configuration, and provides lifecycle hooks.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('internal/agent/AGENTS.md')
    assert '- **Managers**: `agent/device/<namespace>` mirrors spec keys (e.g., applications/, config/, os/)' in text, "expected to find: " + '- **Managers**: `agent/device/<namespace>` mirrors spec keys (e.g., applications/, config/, os/)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('internal/agent/AGENTS.md')
    assert '- **Bootstrap**: Initialization phase before reconciliation - only used in agent.go setup' in text, "expected to find: " + '- **Bootstrap**: Initialization phase before reconciliation - only used in agent.go setup'[:80]

