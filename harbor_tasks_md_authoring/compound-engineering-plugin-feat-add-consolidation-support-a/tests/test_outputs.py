"""Behavioral checks for compound-engineering-plugin-feat-add-consolidation-support-a (markdown_authoring task).

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
    text = _read('plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md')
    assert "8. **Delete when the code is gone.** If the referenced code, controller, or workflow no longer exists in the codebase and no successor can be found, delete the file — don't default to Keep just becaus" in text, "expected to find: " + "8. **Delete when the code is gone.** If the referenced code, controller, or workflow no longer exists in the codebase and no successor can be found, delete the file — don't default to Keep just becaus"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md')
    assert 'description: Refresh stale or drifting learnings and pattern docs in docs/solutions/ by reviewing, updating, consolidating, replacing, or deleting them against the current codebase. Use after refactor' in text, "expected to find: " + 'description: Refresh stale or drifting learnings and pattern docs in docs/solutions/ by reviewing, updating, consolidating, replacing, or deleting them against the current codebase. Use after refactor'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md')
    assert '9. **Evaluate document-set design, not just accuracy.** In addition to checking whether each doc is accurate, evaluate whether it is still the right unit of knowledge. If two or more docs overlap heav' in text, "expected to find: " + '9. **Evaluate document-set design, not just accuracy.** In addition to checking whether each doc is accurate, evaluate whether it is still the right unit of knowledge. If two or more docs overlap heav'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-compound/SKILL.md')
    assert 'In compact-safe mode, the overlap check is skipped (no Related Docs Finder subagent). This means compact-safe mode may create a doc that overlaps with an existing one. That is acceptable — `ce:compoun' in text, "expected to find: " + 'In compact-safe mode, the overlap check is skipped (no Related Docs Finder subagent). This means compact-safe mode may create a doc that overlaps with an existing one. That is acceptable — `ce:compoun'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-compound/SKILL.md')
    assert 'When updating an existing doc, preserve its file path and frontmatter structure. Update the solution, code examples, prevention tips, and any stale references. Add a `last_updated: YYYY-MM-DD` field t' in text, "expected to find: " + 'When updating an existing doc, preserve its file path and frontmatter structure. Update the solution, code examples, prevention tips, and any stale references. Add a `last_updated: YYYY-MM-DD` field t'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-compound/SKILL.md')
    assert '| **High** — existing doc covers the same problem, root cause, and solution | **Update the existing doc** with fresher context (new code examples, updated references, additional prevention tips) rathe' in text, "expected to find: " + '| **High** — existing doc covers the same problem, root cause, and solution | **Update the existing doc** with fresher context (new code examples, updated references, additional prevention tips) rathe'[:80]

