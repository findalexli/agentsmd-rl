"""Behavioral checks for horizon-docs-correct-architecture-docs-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/horizon")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Per-panel event loop thread:** alacritty_terminal `EventLoop` reads PTY output, parses VT sequences, and sends events via `mpsc::channel`' in text, "expected to find: " + '- **Per-panel event loop thread:** alacritty_terminal `EventLoop` reads PTY output, parses VT sequences, and sends events via `mpsc::channel`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Stack:** Rust (edition 2024) · eframe/egui (wgpu backend) · alacritty_terminal (VT parsing, PTY, event loop)' in text, "expected to find: " + '**Stack:** Rust (edition 2024) · eframe/egui (wgpu backend) · alacritty_terminal (VT parsing, PTY, event loop)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Shell → PTY slave → PTY master → [alacritty EventLoop thread] → Term (VT parse) → channel → main thread → egui' in text, "expected to find: " + 'Shell → PTY slave → PTY master → [alacritty EventLoop thread] → Term (VT parse) → channel → main thread → egui'[:80]

