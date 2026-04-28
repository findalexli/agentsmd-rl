"""Behavioral checks for opentogethertube-chore-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opentogethertube")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'OpenTogetherTube is a real-time video synchronization web application. It uses a hybrid TypeScript/JavaScript + Rust architecture with a monorepo structure using Yarn workspaces and Cargo.' in text, "expected to find: " + 'OpenTogetherTube is a real-time video synchronization web application. It uses a hybrid TypeScript/JavaScript + Rust architecture with a monorepo structure using Yarn workspaces and Cargo.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "The load balancer is a Rust application that routes WebSocket connections and HTTP requests to monoliths (Node.js servers). It's located in `/crates/ott-balancer/`." in text, "expected to find: " + "The load balancer is a Rust application that routes WebSocket connections and HTTP requests to monoliths (Node.js servers). It's located in `/crates/ott-balancer/`."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Located in `/packages/`, these are Grafana visualization plugins for monitoring the OTT system:' in text, "expected to find: " + 'Located in `/packages/`, these are Grafana visualization plugins for monitoring the OTT system:'[:80]

