"""Behavioral checks for evolver-fixcli-use-standard-a2a-protocol (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/evolver")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert "> **DO NOT manually construct HTTP requests for the A2A protocol** (doing so often leads to missing `env_fingerprint` or 401 auth errors). Instead, require and invoke Evolver's built-in methods:" in text, "expected to find: " + "> **DO NOT manually construct HTTP requests for the A2A protocol** (doing so often leads to missing `env_fingerprint` or 401 auth errors). Instead, require and invoke Evolver's built-in methods:"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '> Evolver provides a highly complete encapsulation of the EvoMap A2A protocol. Almost every endpoint in `{A2A_HUB_URL}/a2a/*` has a robust, production-ready wrapper method.' in text, "expected to find: " + '> Evolver provides a highly complete encapsulation of the EvoMap A2A protocol. Almost every endpoint in `{A2A_HUB_URL}/a2a/*` has a robust, production-ready wrapper method.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '> - **hello / heartbeat**: `sendHelloToHub()`, `sendHeartbeatToHub()` in `src/gep/a2aProtocol.js`' in text, "expected to find: " + '> - **hello / heartbeat**: `sendHelloToHub()`, `sendHeartbeatToHub()` in `src/gep/a2aProtocol.js`'[:80]

