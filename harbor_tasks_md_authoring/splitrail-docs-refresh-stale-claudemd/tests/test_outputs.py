"""Behavioral checks for splitrail-docs-refresh-stale-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/splitrail")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Splitrail is a high-performance, cross-platform usage tracker for AI coding assistants (Claude Code, Copilot, Cline, etc.). It analyzes local data files from these tools, aggregates usage statistics, ' in text, "expected to find: " + 'Splitrail is a high-performance, cross-platform usage tracker for AI coding assistants (Claude Code, Copilot, Cline, etc.). It analyzes local data files from these tools, aggregates usage statistics, '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '3. For JSONL files, implement `parse_single_file_incremental()` and return `supports_delta_parsing() -> true`' in text, "expected to find: " + '3. For JSONL files, implement `parse_single_file_incremental()` and return `supports_delta_parsing() -> true`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'async fn parse_conversations(&self, sources: Vec<DataSource>) -> Result<Vec<ConversationMessage>> { ... }' in text, "expected to find: " + 'async fn parse_conversations(&self, sources: Vec<DataSource>) -> Result<Vec<ConversationMessage>> { ... }'[:80]

