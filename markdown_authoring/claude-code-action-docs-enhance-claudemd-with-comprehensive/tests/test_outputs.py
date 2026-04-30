"""Behavioral checks for claude-code-action-docs-enhance-claudemd-with-comprehensive (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-action")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This is a GitHub Action that enables Claude to interact with GitHub PRs and issues. The action operates in two main phases:' in text, "expected to find: " + 'This is a GitHub Action that enables Claude to interact with GitHub PRs and issues. The action operates in two main phases:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '3. **Claude Integration**: Executes via multiple providers (Anthropic API, AWS Bedrock, Google Vertex AI)' in text, "expected to find: " + '3. **Claude Integration**: Executes via multiple providers (Anthropic API, AWS Bedrock, Google Vertex AI)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The `base-action/` directory contains the core Claude Code execution logic, which serves a dual purpose:' in text, "expected to find: " + 'The `base-action/` directory contains the core Claude Code execution logic, which serves a dual purpose:'[:80]

