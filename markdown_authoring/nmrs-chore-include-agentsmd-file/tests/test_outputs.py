"""Behavioral checks for nmrs-chore-include-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nmrs")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Tests**: unit tests live in `#[cfg(test)] mod tests` within the module or in `api/models/tests.rs`. Integration tests in `nmrs/tests/`. Assert behavior, not implementation.' in text, "expected to find: " + '- **Tests**: unit tests live in `#[cfg(test)] mod tests` within the module or in `api/models/tests.rs`. Integration tests in `nmrs/tests/`. Assert behavior, not implementation.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Error handling**: all public fallible operations return `nmrs::Result<T>` (alias for `Result<T, ConnectionError>`). Use `ConnectionError` variants, not raw strings.' in text, "expected to find: " + '- **Error handling**: all public fallible operations return `nmrs::Result<T>` (alias for `Result<T, ConnectionError>`). Use `ConnectionError` variants, not raw strings.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Builder pattern**: config structs use `with_*` builder methods returning `Self` with `#[must_use]`. See `WireGuardConfig`, `OpenVpnConfig`, `EapOptions`.' in text, "expected to find: " + '- **Builder pattern**: config structs use `with_*` builder methods returning `Self` with `#[must_use]`. See `WireGuardConfig`, `OpenVpnConfig`, `EapOptions`.'[:80]

