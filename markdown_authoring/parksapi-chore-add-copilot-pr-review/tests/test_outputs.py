"""Behavioral checks for parksapi-chore-add-copilot-pr-review (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/parksapi")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'parksapi is a TypeScript ESM library that fetches real-time theme park data (wait times, schedules, entities) from 75+ park implementations. All park integrations live under `src/parks/<park>/`. The c' in text, "expected to find: " + 'parksapi is a TypeScript ESM library that fetches real-time theme park data (wait times, schedules, entities) from 75+ park implementations. All park integrations live under `src/parks/<park>/`. The c'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'The `HTTPObj`/`Entity`/`LiveData`/`EntitySchedule` types from `@themeparks/typelib` are intentionally strict to enforce shape at the public API boundary. Park implementations frequently use `as any as' in text, "expected to find: " + 'The `HTTPObj`/`Entity`/`LiveData`/`EntitySchedule` types from `@themeparks/typelib` are intentionally strict to enforce shape at the public API boundary. Park implementations frequently use `as any as'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '`CLAUDE.md` requires that **no URLs, keys, tokens, or credentials ever appear hardcoded in source**. Empty-string defaults force configuration via `.env` and are the documented convention. **Do not su' in text, "expected to find: " + '`CLAUDE.md` requires that **no URLs, keys, tokens, or credentials ever appear hardcoded in source**. Empty-string defaults force configuration via `.env` and are the documented convention. **Do not su'[:80]

