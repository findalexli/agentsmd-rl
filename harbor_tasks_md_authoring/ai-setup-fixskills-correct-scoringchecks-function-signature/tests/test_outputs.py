"""Behavioral checks for ai-setup-fixskills-correct-scoringchecks-function-signature (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai-setup")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/scoring-checks/SKILL.md')
    assert '1. **Choose or create a check file** in `src/scoring/checks/` matching the category (`existence.ts`, `quality.ts`, `grounding.ts`, `accuracy.ts`, `freshness.ts`, `bonus.ts`, `sources.ts`).' in text, "expected to find: " + '1. **Choose or create a check file** in `src/scoring/checks/` matching the category (`existence.ts`, `quality.ts`, `grounding.ts`, `accuracy.ts`, `freshness.ts`, `bonus.ts`, `sources.ts`).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/scoring-checks/SKILL.md')
    assert '1. **Check must return `Check[]`** — Never return a single check or a Promise. Return an empty array `[]` only if there are genuinely zero checks; always push at least one check object.' in text, "expected to find: " + '1. **Check must return `Check[]`** — Never return a single check or a Promise. Return an empty array `[]` only if there are genuinely zero checks; always push at least one check object.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/scoring-checks/SKILL.md')
    assert '4. **File structure**: Add checks to existing category files in `src/scoring/checks/`. Export a **named function** with signature `check{Category}(dir: string): Check[]`.' in text, "expected to find: " + '4. **File structure**: Add checks to existing category files in `src/scoring/checks/`. Export a **named function** with signature `check{Category}(dir: string): Check[]`.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/scoring-checks/SKILL.md')
    assert "Choose the right file in `src/scoring/checks/` based on category (`existence.ts`, `quality.ts`, `grounding.ts`, `accuracy.ts`, `freshness.ts`, `bonus.ts`, `sources.ts`). Add your logic to that file's " in text, "expected to find: " + "Choose the right file in `src/scoring/checks/` based on category (`existence.ts`, `quality.ts`, `grounding.ts`, `accuracy.ts`, `freshness.ts`, `bonus.ts`, `sources.ts`). Add your logic to that file's "[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/scoring-checks/SKILL.md')
    assert '- Use `mkdtempSync` to create a temp dir; write files with `writeFileSync`; clean up with `rmSync(dir, { recursive: true })` in a `finally` block.' in text, "expected to find: " + '- Use `mkdtempSync` to create a temp dir; write files with `writeFileSync`; clean up with `rmSync(dir, { recursive: true })` in a `finally` block.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/scoring-checks/SKILL.md')
    assert '- **Function signature**: `export function check{Category}(dir: string): Check[]` — takes a directory path, not a fingerprint or config object.' in text, "expected to find: " + '- **Function signature**: `export function check{Category}(dir: string): Check[]` — takes a directory path, not a fingerprint or config object.'[:80]

