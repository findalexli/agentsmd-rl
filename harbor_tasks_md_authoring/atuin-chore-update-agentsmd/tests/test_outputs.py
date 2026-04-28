"""Behavioral checks for atuin-chore-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/atuin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **V2**: PASETO V4 Local (XChaCha20-Poly1305 + Blake2b). Envelope encryption: each record gets a random CEK wrapped with the master key. Record metadata (id, idx, version, tag, host) is authenticated' in text, "expected to find: " + '- **V2**: PASETO V4 Local (XChaCha20-Poly1305 + Blake2b). Envelope encryption: each record gets a random CEK wrapped with the master key. Record metadata (id, idx, version, tag, host) is authenticated'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **V2 (current)**: Record store abstraction. All data types (history, KV, aliases, vars, scripts) share the same sync infrastructure using tagged records. Envelope-encrypted with PASETO V4 and per-re' in text, "expected to find: " + '- **V2 (current)**: Record store abstraction. All data types (history, KV, aliases, vars, scripts) share the same sync infrastructure using tagged records. Envelope-encrypted with PASETO V4 and per-re'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "Shell history tool. Replaces your shell's built-in history with a SQLite database, adds context (cwd, exit code, duration, hostname), and optionally syncs across machines with end-to-end encryption." in text, "expected to find: " + "Shell history tool. Replaces your shell's built-in history with a SQLite database, adds context (cwd, exit code, duration, hostname), and optionally syncs across machines with end-to-end encryption."[:80]

