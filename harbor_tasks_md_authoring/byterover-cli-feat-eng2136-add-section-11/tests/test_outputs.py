"""Behavioral checks for byterover-cli-feat-eng2136-add-section-11 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/byterover-cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('src/server/templates/skill/SKILL.md')
    assert '**Overview:** Inspect past query and curate operations. Use `brv query-log view` to review query history, `brv curate view` to review curate history, and `brv query-log summary` to see aggregated reca' in text, "expected to find: " + '**Overview:** Inspect past query and curate operations. Use `brv query-log view` to review query history, `brv curate view` to review curate history, and `brv query-log summary` to see aggregated reca'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/server/templates/skill/SKILL.md')
    assert '- Full detail for a specific entry: all files and operations performed (logId is printed by `brv curate` on completion, e.g. `cur-1739700001000`)' in text, "expected to find: " + '- Full detail for a specific entry: all files and operations performed (logId is printed by `brv curate` on completion, e.g. `cur-1739700001000`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/server/templates/skill/SKILL.md')
    assert '- Full detail for a specific entry: matched docs and search metadata (logId is printed by `brv query` on completion, e.g. `qry-1739700001000`)' in text, "expected to find: " + '- Full detail for a specific entry: matched docs and search metadata (logId is printed by `brv query` on completion, e.g. `qry-1739700001000`)'[:80]

