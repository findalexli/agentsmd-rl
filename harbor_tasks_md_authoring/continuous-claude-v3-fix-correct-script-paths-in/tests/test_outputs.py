"""Behavioral checks for continuous-claude-v3-fix-correct-script-paths-in (markdown_authoring task).

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
    text = _read('.claude/skills/firecrawl-scrape/SKILL.md')
    assert 'uv run python -m runtime.harness scripts/mcp/firecrawl_scrape.py \\' in text, "expected to find: " + 'uv run python -m runtime.harness scripts/mcp/firecrawl_scrape.py \\'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/github-search/SKILL.md')
    assert 'uv run python -m runtime.harness scripts/mcp/github_search.py \\' in text, "expected to find: " + 'uv run python -m runtime.harness scripts/mcp/github_search.py \\'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/help/SKILL.md')
    assert '(cd opc && uv run python scripts/core/recall_learnings.py --query "hook patterns")' in text, "expected to find: " + '(cd opc && uv run python scripts/core/recall_learnings.py --query "hook patterns")'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/implement_task/SKILL.md')
    assert 'uv run python -m runtime.harness scripts/mcp/morph_apply.py \\' in text, "expected to find: " + 'uv run python -m runtime.harness scripts/mcp/morph_apply.py \\'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/morph-apply/SKILL.md')
    assert 'uv run python -m runtime.harness scripts/mcp/morph_apply.py \\' in text, "expected to find: " + 'uv run python -m runtime.harness scripts/mcp/morph_apply.py \\'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/morph-search/SKILL.md')
    assert 'uv run python -m runtime.harness scripts/mcp/morph_search.py \\' in text, "expected to find: " + 'uv run python -m runtime.harness scripts/mcp/morph_search.py \\'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/nia-docs/SKILL.md')
    assert 'uv run python -m runtime.harness scripts/mcp/nia_docs.py \\' in text, "expected to find: " + 'uv run python -m runtime.harness scripts/mcp/nia_docs.py \\'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/perplexity-search/SKILL.md')
    assert 'uv run python scripts/mcp/perplexity_search.py \\' in text, "expected to find: " + 'uv run python scripts/mcp/perplexity_search.py \\'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/recall-reasoning/SKILL.md')
    assert 'uv run python scripts/core/artifact_query.py "<query>" [--outcome SUCCEEDED|FAILED] [--limit N]' in text, "expected to find: " + 'uv run python scripts/core/artifact_query.py "<query>" [--outcome SUCCEEDED|FAILED] [--limit N]'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/recall-reasoning/SKILL.md')
    assert '- Run `uv run python scripts/core/artifact_index.py --all` to index existing handoffs' in text, "expected to find: " + '- Run `uv run python scripts/core/artifact_index.py --all` to index existing handoffs'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/recall-reasoning/SKILL.md')
    assert 'uv run python scripts/core/artifact_query.py "hook implementation" --outcome FAILED' in text, "expected to find: " + 'uv run python scripts/core/artifact_query.py "hook implementation" --outcome FAILED'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/recall/SKILL.md')
    assert 'cd $CLAUDE_PROJECT_DIR/opc && PYTHONPATH=. uv run python scripts/core/recall_learnings.py --query "<ARGS>" --k 5' in text, "expected to find: " + 'cd $CLAUDE_PROJECT_DIR/opc && PYTHONPATH=. uv run python scripts/core/recall_learnings.py --query "<ARGS>" --k 5'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/remember/SKILL.md')
    assert 'cd $CLAUDE_PROJECT_DIR/opc && PYTHONPATH=. uv run python scripts/core/store_learning.py \\' in text, "expected to find: " + 'cd $CLAUDE_PROJECT_DIR/opc && PYTHONPATH=. uv run python scripts/core/store_learning.py \\'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/research-agent/SKILL.md')
    assert 'uv run python -m runtime.harness scripts/mcp/perplexity_search.py \\' in text, "expected to find: " + 'uv run python -m runtime.harness scripts/mcp/perplexity_search.py \\'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/research-agent/SKILL.md')
    assert 'uv run python -m runtime.harness scripts/mcp/firecrawl_scrape.py \\' in text, "expected to find: " + 'uv run python -m runtime.harness scripts/mcp/firecrawl_scrape.py \\'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/research-agent/SKILL.md')
    assert 'uv run python -m runtime.harness scripts/mcp/nia_docs.py \\' in text, "expected to find: " + 'uv run python -m runtime.harness scripts/mcp/nia_docs.py \\'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/research-external/SKILL.md')
    assert '(cd $CLAUDE_PROJECT_DIR/opc && uv run python -m runtime.harness scripts/mcp/firecrawl_scrape.py \\' in text, "expected to find: " + '(cd $CLAUDE_PROJECT_DIR/opc && uv run python -m runtime.harness scripts/mcp/firecrawl_scrape.py \\'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/research-external/SKILL.md')
    assert '(cd $CLAUDE_PROJECT_DIR/opc && uv run python -m runtime.harness scripts/mcp/nia_docs.py \\' in text, "expected to find: " + '(cd $CLAUDE_PROJECT_DIR/opc && uv run python -m runtime.harness scripts/mcp/nia_docs.py \\'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/research-external/SKILL.md')
    assert '(cd $CLAUDE_PROJECT_DIR/opc && uv run python scripts/mcp/perplexity_search.py \\' in text, "expected to find: " + '(cd $CLAUDE_PROJECT_DIR/opc && uv run python scripts/mcp/perplexity_search.py \\'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/system_overview/SKILL.md')
    assert '| Store learning | `opc/scripts/core/store_learning.py` |' in text, "expected to find: " + '| Store learning | `opc/scripts/core/store_learning.py` |'[:80]

