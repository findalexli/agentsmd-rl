"""Behavioral checks for hermes-agent-docsagents-refresh-agentsmd-fix-stale (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hermes-agent")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Agent-level tools** (todo, memory): intercepted by `run_agent.py` before `handle_function_call()`. See `tools/todo_tool.py` for the pattern.' in text, "expected to find: " + '**Agent-level tools** (todo, memory): intercepted by `run_agent.py` before `handle_function_call()`. See `tools/todo_tool.py` for the pattern.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| `load_config()` | `hermes tools`, `hermes setup`, most CLI subcommands | `hermes_cli/config.py` — merges `DEFAULT_CONFIG` + user YAML |' in text, "expected to find: " + '| `load_config()` | `hermes tools`, `hermes setup`, most CLI subcommands | `hermes_cli/config.py` — merges `DEFAULT_CONFIG` + user YAML |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| Direct YAML load | Gateway runtime | `gateway/run.py` + `gateway/config.py` — reads user YAML raw |' in text, "expected to find: " + '| Direct YAML load | Gateway runtime | `gateway/run.py` + `gateway/config.py` — reads user YAML raw |'[:80]

