"""Behavioral checks for dstack-update-skillmd-to-standardize-run (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dstack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dstack/SKILL.md')
    assert '**"Connect to" or "open" a dev environment:** If a dev environment is already running, use `dstack attach <run name> --logs` (agent runs it in the background by default) to surface the IDE URL (`curso' in text, "expected to find: " + '**"Connect to" or "open" a dev environment:** If a dev environment is already running, use `dstack attach <run name> --logs` (agent runs it in the background by default) to surface the IDE URL (`curso'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dstack/SKILL.md')
    assert 'Note: `dstack attach` writes SSH alias info under `~/.dstack/ssh/config` (and may update `~/.ssh/config`) to enable `ssh <run name>`, IDE connections, port forwarding, and real-time logs (`dstack atta' in text, "expected to find: " + 'Note: `dstack attach` writes SSH alias info under `~/.dstack/ssh/config` (and may update `~/.ssh/config`) to enable `ssh <run name>`, IDE connections, port forwarding, and real-time logs (`dstack atta'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dstack/SKILL.md')
    assert '**Permissions guardrail:** If `dstack attach` fails due to sandbox permissions, request permission escalation to run it outside the sandbox. If escalation isn’t approved or attach still fails, ask the' in text, "expected to find: " + '**Permissions guardrail:** If `dstack attach` fails due to sandbox permissions, request permission escalation to run it outside the sandbox. If escalation isn’t approved or attach still fails, ask the'[:80]

