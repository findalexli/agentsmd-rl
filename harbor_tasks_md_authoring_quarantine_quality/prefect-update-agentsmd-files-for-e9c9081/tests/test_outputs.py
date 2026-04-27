"""Behavioral checks for prefect-update-agentsmd-files-for-e9c9081 (markdown_authoring task).

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
    text = _read('src/prefect/events/AGENTS.md')
    assert 'The background task is started in `__aenter__` and after each reconnect, and cancelled in `__aexit__`. If you subclass or mock `PrefectEventsClient`, ensure both checkpointing paths are exercised — th' in text, "expected to find: " + 'The background task is started in `__aenter__` and after each reconnect, and cancelled in `__aexit__`. If you subclass or mock `PrefectEventsClient`, ensure both checkpointing paths are exercised — th'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/events/AGENTS.md')
    assert '2. **Time-based** (`checkpoint_interval`, default 30s): a background `asyncio.Task` that fires periodically regardless of event count. Prevents unbounded buffer growth for low-throughput connections.' in text, "expected to find: " + '2. **Time-based** (`checkpoint_interval`, default 30s): a background `asyncio.Task` that fires periodically regardless of event count. Prevents unbounded buffer growth for low-throughput connections.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/events/AGENTS.md')
    assert '`PrefectEventsClient` uses **two independent checkpointing mechanisms** to confirm server receipt of sent events:' in text, "expected to find: " + '`PrefectEventsClient` uses **two independent checkpointing mechanisms** to confirm server receipt of sent events:'[:80]

