"""Behavioral checks for nim-libp2p-chore-update-copilot-instructions-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nim-libp2p")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '| `daily_ci_report.yml` | Daily CI failure reporting: opens/updates GitHub issues for failed daily CI runs |' in text, "expected to find: " + '| `daily_ci_report.yml` | Daily CI failure reporting: opens/updates GitHub issues for failed daily CI runs |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- `service_discovery.nim` + `service_discovery/` — Service discovery (random find, routing table manager)' in text, "expected to find: " + '- `service_discovery.nim` + `service_discovery/` — Service discovery (random find, routing table manager)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **chronos** (`>= 4.2.2`) — Async I/O framework (core dependency, used everywhere)' in text, "expected to find: " + '- **chronos** (`>= 4.2.2`) — Async I/O framework (core dependency, used everywhere)'[:80]

