"""Behavioral checks for invokeai-aiui-add-claudemd-to-frontend (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/invokeai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('invokeai/frontend/web/CLAUDE.md')
    assert 'Tests do not need to be written for code that is trivial or has no logic (e.g. simple type definitions, re-exports, etc.). We currently do not do UI tests.' in text, "expected to find: " + 'Tests do not need to be written for code that is trivial or has no logic (e.g. simple type definitions, re-exports, etc.). We currently do not do UI tests.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('invokeai/frontend/web/CLAUDE.md')
    assert 'Split up tasks into smaller subtasks and handle them one at a time using an agent. Ensure each subtask is completed before moving on to the next.' in text, "expected to find: " + 'Split up tasks into smaller subtasks and handle them one at a time using an agent. Ensure each subtask is completed before moving on to the next.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('invokeai/frontend/web/CLAUDE.md')
    assert '- Use @agent-javascript-pro and @agent-typescript-pro for JavaScript and TypeScript code generation and assistance.' in text, "expected to find: " + '- Use @agent-javascript-pro and @agent-typescript-pro for JavaScript and TypeScript code generation and assistance.'[:80]

