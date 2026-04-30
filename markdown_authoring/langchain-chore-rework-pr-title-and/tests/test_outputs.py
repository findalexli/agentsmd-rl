"""Behavioral checks for langchain-chore-rework-pr-title-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/langchain")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Start the text after `type(scope):` with a lowercase letter, unless the first word is a proper noun (e.g. `Azure`, `GitHub`, `OpenAI`) or a named entity (class, function, method, parameter, or varia' in text, "expected to find: " + '- Start the text after `type(scope):` with a lowercase letter, unless the first word is a proper noun (e.g. `Azure`, `GitHub`, `OpenAI`) or a named entity (class, function, method, parameter, or varia'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Follow Conventional Commits. See `.github/workflows/pr_lint.yml` for allowed types and scopes. All titles must include a scope with no exceptions — even for the main `langchain` package.' in text, "expected to find: " + 'Follow Conventional Commits. See `.github/workflows/pr_lint.yml` for allowed types and scopes. All titles must include a scope with no exceptions — even for the main `langchain` package.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Write for readers who may be unfamiliar with this area of the codebase. Avoid insider shorthand and prefer language that is friendly to public viewers — this aids interpretability.' in text, "expected to find: " + '- Write for readers who may be unfamiliar with this area of the codebase. Avoid insider shorthand and prefer language that is friendly to public viewers — this aids interpretability.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Start the text after `type(scope):` with a lowercase letter, unless the first word is a proper noun (e.g. `Azure`, `GitHub`, `OpenAI`) or a named entity (class, function, method, parameter, or varia' in text, "expected to find: " + '- Start the text after `type(scope):` with a lowercase letter, unless the first word is a proper noun (e.g. `Azure`, `GitHub`, `OpenAI`) or a named entity (class, function, method, parameter, or varia'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Follow Conventional Commits. See `.github/workflows/pr_lint.yml` for allowed types and scopes. All titles must include a scope with no exceptions — even for the main `langchain` package.' in text, "expected to find: " + 'Follow Conventional Commits. See `.github/workflows/pr_lint.yml` for allowed types and scopes. All titles must include a scope with no exceptions — even for the main `langchain` package.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Write for readers who may be unfamiliar with this area of the codebase. Avoid insider shorthand and prefer language that is friendly to public viewers — this aids interpretability.' in text, "expected to find: " + '- Write for readers who may be unfamiliar with this area of the codebase. Avoid insider shorthand and prefer language that is friendly to public viewers — this aids interpretability.'[:80]

