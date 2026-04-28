"""Behavioral checks for continuous-claude-v3-fix-use-unique-output-filenames (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/continuous-claude-v3")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/aegis.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/aegis/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/aegis/output-{timestamp}.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/agentica-agent.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/agentica-agent/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/agentica-agent/output-{timestamp}.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/arbiter.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/arbiter/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/arbiter/output-{timestamp}.md'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/architect.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/architect/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/architect/output-{timestamp}.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/atlas.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/atlas/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/atlas/output-{timestamp}.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/braintrust-analyst.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/braintrust-analyst/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/braintrust-analyst/output-{timestamp}.md'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/critic.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/critic/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/critic/output-{timestamp}.md'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/debug-agent.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/debug-agent/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/debug-agent/output-{timestamp}.md'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/herald.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/herald/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/herald/output-{timestamp}.md'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/judge.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/judge/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/judge/output-{timestamp}.md'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/kraken.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/kraken/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/kraken/output-{timestamp}.md'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/liaison.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/liaison/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/liaison/output-{timestamp}.md'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/maestro.md')
    assert 'ORACLE_OUTPUT=$(ls -t .claude/cache/agents/oracle/output-*.md 2>/dev/null | head -1)' in text, "expected to find: " + 'ORACLE_OUTPUT=$(ls -t .claude/cache/agents/oracle/output-*.md 2>/dev/null | head -1)'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/maestro.md')
    assert 'SCOUT_OUTPUT=$(ls -t .claude/cache/agents/scout/output-*.md 2>/dev/null | head -1)' in text, "expected to find: " + 'SCOUT_OUTPUT=$(ls -t .claude/cache/agents/scout/output-*.md 2>/dev/null | head -1)'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/maestro.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/maestro/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/maestro/output-{timestamp}.md'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/oracle.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/oracle/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/oracle/output-{timestamp}.md'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/pathfinder.md')
    assert 'Write to `$CLAUDE_PROJECT_DIR/.claude/cache/agents/pathfinder/output-{timestamp}.md`:' in text, "expected to find: " + 'Write to `$CLAUDE_PROJECT_DIR/.claude/cache/agents/pathfinder/output-{timestamp}.md`:'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/phoenix.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/phoenix/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/phoenix/output-{timestamp}.md'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/plan-agent.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/plan-agent/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/plan-agent/output-{timestamp}.md'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/profiler.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/profiler/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/profiler/output-{timestamp}.md'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/review-agent.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/review-agent/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/review-agent/output-{timestamp}.md'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/scout.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/scout/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/scout/output-{timestamp}.md'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/session-analyst.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/session-analyst/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/session-analyst/output-{timestamp}.md'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/sleuth.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/sleuth/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/sleuth/output-{timestamp}.md'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/spark.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/spark/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/spark/output-{timestamp}.md'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/surveyor.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/surveyor/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/surveyor/output-{timestamp}.md'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/validate-agent.md')
    assert '$CLAUDE_PROJECT_DIR/.claude/cache/agents/validate-agent/output-{timestamp}.md' in text, "expected to find: " + '$CLAUDE_PROJECT_DIR/.claude/cache/agents/validate-agent/output-{timestamp}.md'[:80]

