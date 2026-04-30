"""Behavioral checks for gastown-docsconvoy-add-stagelaunch-workflow-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gastown")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/skills/convoy/SKILL.md')
    assert "description: The definitive guide for working with gastown's convoy system -- batch work tracking, event-driven feeding, stage-launch workflow, and dispatch safety guards. Use when writing convoy code" in text, "expected to find: " + "description: The definitive guide for working with gastown's convoy system -- batch work tracking, event-driven feeding, stage-launch workflow, and dispatch safety guards. Use when writing convoy code"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/skills/convoy/SKILL.md')
    assert '> Implemented in [PR #1820](https://github.com/steveyegge/gastown/pull/1820). Depends on the feeder safety guards from [PR #1759](https://github.com/steveyegge/gastown/pull/1759). Design docs: `docs/d' in text, "expected to find: " + '> Implemented in [PR #1820](https://github.com/steveyegge/gastown/pull/1820). Depends on the feeder safety guards from [PR #1759](https://github.com/steveyegge/gastown/pull/1759). Design docs: `docs/d'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/skills/convoy/SKILL.md')
    assert '- **Stranded scan** (`convoy_manager.go`): Runs every 30s. `feedFirstReady` iterates all ready issues. The ready list is pre-filtered by `IsSlingableType` in `findStrandedConvoys` (cmd/convoy.go). **O' in text, "expected to find: " + '- **Stranded scan** (`convoy_manager.go`): Runs every 30s. `feedFirstReady` iterates all ready issues. The ready list is pre-filtered by `IsSlingableType` in `findStrandedConvoys` (cmd/convoy.go). **O'[:80]

