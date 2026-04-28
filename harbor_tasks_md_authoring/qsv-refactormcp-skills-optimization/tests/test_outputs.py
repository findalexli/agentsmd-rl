"""Behavioral checks for qsv-refactormcp-skills-optimization (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/qsv")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/skills/csv-wrangling/SKILL.md')
    assert '4. **Inspect** - `slice --len 5` (preview rows), `frequency --frequency-jsonl` (value distributions with cache for reuse)' in text, "expected to find: " + '4. **Inspect** - `slice --len 5` (preview rows), `frequency --frequency-jsonl` (value distributions with cache for reuse)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/skills/csv-wrangling/SKILL.md')
    assert '| Aggregate/GROUP BY | `sqlp` | `frequency` | `frequency` for simple counts; `--frequency-jsonl` creates cache |' in text, "expected to find: " + '| Aggregate/GROUP BY | `sqlp` | `frequency` | `frequency` for simple counts; `--frequency-jsonl` creates cache |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/skills/csv-wrangling/SKILL.md')
    assert '| Reshape wide->long | `transpose --long` | - | DuckDB UNPIVOT (external) for complex reshaping |' in text, "expected to find: " + '| Reshape wide->long | `transpose --long` | - | DuckDB UNPIVOT (external) for complex reshaping |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/skills/data-quality/SKILL.md')
    assert '| Row lengths | `fixlengths` | Pads short rows to match longest row; compare count before/after to detect ragged rows |' in text, "expected to find: " + '| Row lengths | `fixlengths` | Pads short rows to match longest row; compare count before/after to detect ragged rows |'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/skills/data-quality/SKILL.md')
    assert '7. fixlengths      -> Pad short rows to uniform length (compare count before/after to detect ragged rows)' in text, "expected to find: " + '7. fixlengths      -> Pad short rows to uniform length (compare count before/after to detect ragged rows)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/skills/data-quality/SKILL.md')
    assert '| Empty values | `apply emptyreplace col --replacement "N/A"` |' in text, "expected to find: " + '| Empty values | `apply emptyreplace col --replacement "N/A"` |'[:80]

