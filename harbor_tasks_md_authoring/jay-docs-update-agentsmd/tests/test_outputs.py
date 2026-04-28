"""Behavioral checks for jay-docs-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/jay")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('book/AGENTS.md')
    assert '| `src/control_center/cc_*.rs` | Control center panes: 11 sidebar panes + `cc_window.rs` / `cc_clients.rs` detail panes + `cc_criterion.rs` shared helper. Verify field names/ordering here |' in text, "expected to find: " + '| `src/control_center/cc_*.rs` | Control center panes: 11 sidebar panes + `cc_window.rs` / `cc_clients.rs` detail panes + `cc_criterion.rs` shared helper. Verify field names/ordering here |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('book/AGENTS.md')
    assert '| `configuration/index.md` | Config overview: replacement semantics, `jay config init`, auto-reload |' in text, "expected to find: " + '| `configuration/index.md` | Config overview: replacement semantics, `jay config init`, auto-reload |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('book/AGENTS.md')
    assert '| `configuration/startup.md` | Startup hooks (`on-graphics-initialized`, `on-idle`, `on-resume`) |' in text, "expected to find: " + '| `configuration/startup.md` | Startup hooks (`on-graphics-initialized`, `on-idle`, `on-resume`) |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('book/CLAUDE.md')
    assert 'book/CLAUDE.md' in text, "expected to find: " + 'book/CLAUDE.md'[:80]

