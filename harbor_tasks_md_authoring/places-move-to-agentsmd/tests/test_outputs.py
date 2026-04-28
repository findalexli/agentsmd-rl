"""Behavioral checks for places-move-to-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/places")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '.github/copilot-instructions.md' in text, "expected to find: " + '.github/copilot-instructions.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- One test file per integration file: every integration source file should have a single corresponding test module; add new unit tests for that integration to that existing test module. Only split int' in text, "expected to find: " + '- One test file per integration file: every integration source file should have a single corresponding test module; add new unit tests for that integration to that existing test module. Only split int'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- By default, the agent should run the full pytest suite when tests are requested (the repo is small and full pytest runs are acceptable). If the user specifically asks for a focused test run, the age' in text, "expected to find: " + '- By default, the agent should run the full pytest suite when tests are requested (the repo is small and full pytest runs are acceptable). If the user specifically asks for a focused test run, the age'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- The agent will only create branches or open PRs when the user explicitly requests it or includes the hashtag `#github-pull-request_copilot-coding-agent` to hand off to the asynchronous coding agent.' in text, "expected to find: " + '- The agent will only create branches or open PRs when the user explicitly requests it or includes the hashtag `#github-pull-request_copilot-coding-agent` to hand off to the asynchronous coding agent.'[:80]

