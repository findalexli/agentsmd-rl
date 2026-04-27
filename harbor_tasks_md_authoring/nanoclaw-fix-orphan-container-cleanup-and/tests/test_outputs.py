"""Behavioral checks for nanoclaw-fix-orphan-container-cleanup-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanoclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-voice-transcription/SKILL.md')
    assert '**This step is essential.** When the NanoClaw service restarts (e.g., `launchctl kickstart -k`), the running container is detached but NOT killed. The new service instance spawns a fresh container, bu' in text, "expected to find: " + '**This step is essential.** When the NanoClaw service restarts (e.g., `launchctl kickstart -k`), the running container is detached but NOT killed. The new service instance spawns a fresh container, bu'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-voice-transcription/SKILL.md')
    assert '**Root cause:** The `ensureContainerSystemRunning()` function previously used `container ls --format {{.Names}}` which silently fails on Apple Container (only `json` and `table` formats are supported)' in text, "expected to find: " + '**Root cause:** The `ensureContainerSystemRunning()` function previously used `container ls --format {{.Names}}` which silently fails on Apple Container (only `json` and `table` formats are supported)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-voice-transcription/SKILL.md')
    assert 'The existing cleanup code in `ensureContainerSystemRunning()` in `src/index.ts` uses `container ls --format {{.Names}}` which **silently fails** on Apple Container (only `json` and `table` are valid f' in text, "expected to find: " + 'The existing cleanup code in `ensureContainerSystemRunning()` in `src/index.ts` uses `container ls --format {{.Names}}` which **silently fails** on Apple Container (only `json` and `table` are valid f'[:80]

