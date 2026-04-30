"""Behavioral checks for litestream-docsagents-add-ipc-leasing-library (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/litestream")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **`$PID` config expansion**: Config files support `$PID` to expand to the current process ID, plus standard `$ENV_VAR` expansion. See `cmd/litestream/main.go`' in text, "expected to find: " + '- **`$PID` config expansion**: Config files support `$PID` to expand to the current process ID, plus standard `$ENV_VAR` expansion. See `cmd/litestream/main.go`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Retention enabled by default**: `Store.RetentionEnabled` is `true` by default. Disable only when cloud lifecycle policies handle cleanup. See `store.go`' in text, "expected to find: " + '- **Retention enabled by default**: `Store.RetentionEnabled` is `true` by default. Disable only when cloud lifecycle policies handle cleanup. See `store.go`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **IPC socket disabled by default**: Control socket is off by default. Enable with `socket.enabled: true` in config. See `server.go`' in text, "expected to find: " + '- **IPC socket disabled by default**: Control socket is off by default. Enable with `socket.enabled: true` in config. See `server.go`'[:80]

