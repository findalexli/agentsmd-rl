"""Behavioral checks for gemini-cli-desktop-add-agentsmd-for-codex-cli (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gemini-cli-desktop")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Rust: stable toolchain, `cargo fmt` and `cargo clippy` (pedantic/nursery enabled in `tauri-app`). 4‑space indent, snake_case for modules/functions, PascalCase for types.' in text, "expected to find: " + '- Rust: stable toolchain, `cargo fmt` and `cargo clippy` (pedantic/nursery enabled in `tauri-app`). 4‑space indent, snake_case for modules/functions, PascalCase for types.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Commit style: Conventional Commits with scopes (e.g., `feat(ui): ...`, `fix(backend): ...`, `refactor(...)`). Version bumps use `vX.Y.Z`.' in text, "expected to find: " + '- Commit style: Conventional Commits with scopes (e.g., `feat(ui): ...`, `fix(backend): ...`, `refactor(...)`). Version bumps use `vX.Y.Z`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Frameworks: Rust unit/integration tests (tokio, mockall, serial_test). Frontend currently relies on type/lint checks.' in text, "expected to find: " + '- Frameworks: Rust unit/integration tests (tokio, mockall, serial_test). Frontend currently relies on type/lint checks.'[:80]

