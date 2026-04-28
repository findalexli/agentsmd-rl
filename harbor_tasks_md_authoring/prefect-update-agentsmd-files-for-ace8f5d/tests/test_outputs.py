"""Behavioral checks for prefect-update-agentsmd-files-for-ace8f5d (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prefect")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/runner/AGENTS.md')
    assert '**Extending intents:** The only intent today is `"cancel"`. The byte map (`_BYTE_FOR_INTENT` in `_control_channel.py` and `_INTENT_FOR_BYTE` in `_internal/control_listener.py`) must stay in sync — add' in text, "expected to find: " + '**Extending intents:** The only intent today is `"cancel"`. The byte map (`_BYTE_FOR_INTENT` in `_control_channel.py` and `_INTENT_FOR_BYTE` in `_internal/control_listener.py`) must stay in sync — add'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/runner/AGENTS.md')
    assert '`ControlChannel` (`_control_channel.py`) is a TCP loopback socket server that delivers a single-byte *intent* to child processes before the runner sends the actual kill signal. The child-side counterp' in text, "expected to find: " + '`ControlChannel` (`_control_channel.py`) is a TCP loopback socket server that delivers a single-byte *intent* to child processes before the runner sends the actual kill signal. The child-side counterp'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/runner/AGENTS.md')
    assert '**Failure modes:** If the child never connects or never acks within 1 s, `signal()` returns `False` and the runner falls through to the normal kill path — the engine treats the termination as a crash,' in text, "expected to find: " + '**Failure modes:** If the child never connects or never acks within 1 s, `signal()` returns `False` and the runner falls through to the normal kill path — the engine treats the termination as a crash,'[:80]

