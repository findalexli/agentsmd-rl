"""Behavioral checks for compound-engineering-plugin-fixceworkceworkbeta-add-safety-c (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work-beta/SKILL.md')
    assert '2. Cross-check for discovered file collisions: compare the actual files modified by all subagents in the batch (not just their declared `Files:` lists). Subagents may create or modify files not antici' in text, "expected to find: " + '2. Cross-check for discovered file collisions: compare the actual files modified by all subagents in the batch (not just their declared `Files:` lists). Subagents may create or modify files not antici'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work-beta/SKILL.md')
    assert '**Parallel subagent mode:** When units run as parallel subagents, the subagents do not commit — the orchestrator handles staging and committing after the entire parallel batch completes (see Parallel ' in text, "expected to find: " + '**Parallel subagent mode:** When units run as parallel subagents, the subagents do not commit — the orchestrator handles staging and committing after the entire parallel batch completes (see Parallel '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work-beta/SKILL.md')
    assert 'Even with no file overlap, parallel subagents sharing a working directory face git index contention (concurrent staging/committing corrupts the index) and test interference (concurrent test runs pick ' in text, "expected to find: " + 'Even with no file overlap, parallel subagents sharing a working directory face git index contention (concurrent staging/committing corrupts the index) and test interference (concurrent test runs pick '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert '2. Cross-check for discovered file collisions: compare the actual files modified by all subagents in the batch (not just their declared `Files:` lists). Subagents may create or modify files not antici' in text, "expected to find: " + '2. Cross-check for discovered file collisions: compare the actual files modified by all subagents in the batch (not just their declared `Files:` lists). Subagents may create or modify files not antici'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert '**Parallel subagent mode:** When units run as parallel subagents, the subagents do not commit — the orchestrator handles staging and committing after the entire parallel batch completes (see Parallel ' in text, "expected to find: " + '**Parallel subagent mode:** When units run as parallel subagents, the subagents do not commit — the orchestrator handles staging and committing after the entire parallel batch completes (see Parallel '[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert 'Even with no file overlap, parallel subagents sharing a working directory face git index contention (concurrent staging/committing corrupts the index) and test interference (concurrent test runs pick ' in text, "expected to find: " + 'Even with no file overlap, parallel subagents sharing a working directory face git index contention (concurrent staging/committing corrupts the index) and test interference (concurrent test runs pick '[:80]

