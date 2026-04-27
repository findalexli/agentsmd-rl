"""Behavioral checks for byterover-cli-projgit-semantics (markdown_authoring task).

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
    assert '**Overview:** `brv vc` provides git-based version control for your context tree. It uses standard git semantics — branching, committing, merging, history, and conflict resolution — all working locally' in text, "expected to find: " + '**Overview:** `brv vc` provides git-based version control for your context tree. It uses standard git semantics — branching, committing, merging, history, and conflict resolution — all working locally'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/server/templates/skill/SKILL.md')
    assert '**LLM usage**: `brv query` and `brv curate` send context to a configured LLM provider for processing. The LLM sees the query or curate text and any included file contents. No data is sent to ByteRover' in text, "expected to find: " + '**LLM usage**: `brv query` and `brv curate` send context to a configured LLM provider for processing. The LLM sees the query or curate text and any included file contents. No data is sent to ByteRover'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/server/templates/skill/SKILL.md')
    assert "**Cloud sync**: `brv vc push` and `brv vc pull` require authentication (`brv login`) and sync knowledge with ByteRover's cloud service via git. All other commands operate without ByteRover authenticat" in text, "expected to find: " + "**Cloud sync**: `brv vc push` and `brv vc pull` require authentication (`brv login`) and sync knowledge with ByteRover's cloud service via git. All other commands operate without ByteRover authenticat"[:80]

