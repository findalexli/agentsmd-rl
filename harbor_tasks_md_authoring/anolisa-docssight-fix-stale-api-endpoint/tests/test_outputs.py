"""Behavioral checks for anolisa-docssight-fix-stale-api-endpoint (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/anolisa")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('src/agentsight/AGENTS.md')
    assert '| `/api/interruptions/conversation-counts` | GET | 按 conversation 分组的中断计数（`start_ns`, `end_ns`） |' in text, "expected to find: " + '| `/api/interruptions/conversation-counts` | GET | 按 conversation 分组的中断计数（`start_ns`, `end_ns`） |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/agentsight/AGENTS.md')
    assert '| `/api/token-savings` | GET | Token 节省统计（`start_ns`, `end_ns`, `agent_name`） |' in text, "expected to find: " + '| `/api/token-savings` | GET | Token 节省统计（`start_ns`, `end_ns`, `agent_name`） |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/agentsight/AGENTS.md')
    assert '| `/api/conversations/{id}/interruptions` | GET | 指定 conversation 的所有中断 |' in text, "expected to find: " + '| `/api/conversations/{id}/interruptions` | GET | 指定 conversation 的所有中断 |'[:80]

