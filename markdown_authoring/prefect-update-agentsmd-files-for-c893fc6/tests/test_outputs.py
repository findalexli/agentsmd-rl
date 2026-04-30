"""Behavioral checks for prefect-update-agentsmd-files-for-c893fc6 (markdown_authoring task).

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
    text = _read('ui-v2/src/api/AGENTS.md')
    assert '- Add `refetchInterval: 30_000` to list, count, and detail query factories that display live operational data (work pools, flow runs, task runs, etc.). Use `60_000` for slower-changing data (events). ' in text, "expected to find: " + '- Add `refetchInterval: 30_000` to list, count, and detail query factories that display live operational data (work pools, flow runs, task runs, etc.). Use `60_000` for slower-changing data (events). '[:80]

