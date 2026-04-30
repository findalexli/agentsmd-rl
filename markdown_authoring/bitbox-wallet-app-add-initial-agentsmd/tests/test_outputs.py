"""Behavioral checks for bitbox-wallet-app-add-initial-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/bitbox-wallet-app")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '`cmd/` (e.g., `cmd/servewallet`). Frontend clients reside in `frontends/` (`web` for React, `qt` for' in text, "expected to find: " + '`cmd/` (e.g., `cmd/servewallet`). Frontend clients reside in `frontends/` (`web` for React, `qt` for'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'while automation lives in `scripts/`. Use `vendor/` for pinned Go modules and keep `config/` aligned' in text, "expected to find: " + 'while automation lives in `scripts/`. Use `vendor/` for pinned Go modules and keep `config/` aligned'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `make servewallet` starts the Go backend against the vendored modules; pair it with `make webdev`' in text, "expected to find: " + '- `make servewallet` starts the Go backend against the vendored modules; pair it with `make webdev`'[:80]

