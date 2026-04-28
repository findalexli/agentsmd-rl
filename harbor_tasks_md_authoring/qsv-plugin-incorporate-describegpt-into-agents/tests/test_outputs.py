"""Behavioral checks for qsv-plugin-incorporate-describegpt-into-agents (markdown_authoring task).

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
    text = _read('.claude/skills/agents/data-analyst.md')
    assert 'See `skills/csv-wrangling/SKILL.md` for the full tool selection matrix and pipeline patterns. Key analysis tools: `qsv_stats`/`qsv_moarstats` (column statistics), `qsv_frequency` (distributions), `qsv' in text, "expected to find: " + 'See `skills/csv-wrangling/SKILL.md` for the full tool selection matrix and pipeline patterns. Key analysis tools: `qsv_stats`/`qsv_moarstats` (column statistics), `qsv_frequency` (distributions), `qsv'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/agents/data-analyst.md')
    assert '8. **Document**: Run `qsv_describegpt` with `all: true` to generate a Data Dictionary, Description, and Tags. Output defaults to `<filestem>.describegpt.md`. Uses the connected LLM automatically via M' in text, "expected to find: " + '8. **Document**: Run `qsv_describegpt` with `all: true` to generate a Data Dictionary, Description, and Tags. Output defaults to `<filestem>.describegpt.md`. Uses the connected LLM automatically via M'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/agents/data-analyst.md')
    assert '- mcp__qsv__qsv_describegpt' in text, "expected to find: " + '- mcp__qsv__qsv_describegpt'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/commands/data-describe.md')
    assert 'Generate AI-powered documentation for a tabular data file using `describegpt`. Produces a Data Dictionary (column labels, descriptions, types), a natural-language Description of the dataset, and seman' in text, "expected to find: " + 'Generate AI-powered documentation for a tabular data file using `describegpt`. Produces a Data Dictionary (column labels, descriptions, types), a natural-language Description of the dataset, and seman'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/commands/data-describe.md')
    assert '3. **Describe**: Run `qsv_describegpt` with the requested options (recommend `all: true` for comprehensive output). At least one inference option (`dictionary`, `description`, `tags`, or `all`) is req' in text, "expected to find: " + '3. **Describe**: Run `qsv_describegpt` with the requested options (recommend `all: true` for comprehensive output). At least one inference option (`dictionary`, `description`, `tags`, or `all`) is req'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/commands/data-describe.md')
    assert "If running in Claude Code or Cowork, first call `qsv_get_working_dir` to check qsv's current working directory. If it differs from your workspace root (the directory where relative paths should resolv" in text, "expected to find: " + "If running in Claude Code or Cowork, first call `qsv_get_working_dir` to check qsv's current working directory. If it differs from your workspace root (the directory where relative paths should resolv"[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/commands/data-profile.md')
    assert '10. **Document**: Run `qsv_describegpt` with `all: true` to generate a Data Dictionary, Description, and Tags. Output defaults to `<filestem>.describegpt.md`. This step leverages the stats cache creat' in text, "expected to find: " + '10. **Document**: Run `qsv_describegpt` with `all: true` to generate a Data Dictionary, Description, and Tags. Output defaults to `<filestem>.describegpt.md`. This step leverages the stats cache creat'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/commands/data-profile.md')
    assert '- **Data Dictionary, Description & Tags** (optional): AI-generated documentation from describegpt (step 10)' in text, "expected to find: " + '- **Data Dictionary, Description & Tags** (optional): AI-generated documentation from describegpt (step 10)'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/commands/data-profile.md')
    assert '- [ ] **Data Dictionary** generated with column labels, descriptions, and types (describegpt)' in text, "expected to find: " + '- [ ] **Data Dictionary** generated with column labels, descriptions, and types (describegpt)'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/skills/csv-wrangling/SKILL.md')
    assert '| Document dataset | `describegpt` | — | AI-generated Data Dictionary, Description & Tags |' in text, "expected to find: " + '| Document dataset | `describegpt` | — | AI-generated Data Dictionary, Description & Tags |'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/skills/csv-wrangling/SKILL.md')
    assert '8. **Document** - `describegpt --all` (AI-generated Data Dictionary, Description & Tags)' in text, "expected to find: " + '8. **Document** - `describegpt --all` (AI-generated Data Dictionary, Description & Tags)'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/skills/csv-wrangling/SKILL.md')
    assert 'sniff -> index -> stats --cardinality --stats-jsonl -> describegpt --all' in text, "expected to find: " + 'sniff -> index -> stats --cardinality --stats-jsonl -> describegpt --all'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/skills/data-quality/SKILL.md')
    assert '| **Documentation** | Dataset described? | `describegpt --all` | No Data Dictionary or Description |' in text, "expected to find: " + '| **Documentation** | Dataset described? | `describegpt --all` | No Data Dictionary or Description |'[:80]

