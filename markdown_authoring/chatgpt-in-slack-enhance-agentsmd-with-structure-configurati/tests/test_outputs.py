"""Behavioral checks for chatgpt-in-slack-enhance-agentsmd-with-structure-configurati (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/chatgpt-in-slack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Ask first: adding dependencies; deleting/renaming files; changing CI, `serverless.yml`, `Dockerfile`, manifests, or environment variable semantics' in text, "expected to find: " + '- Ask first: adding dependencies; deleting/renaming files; changing CI, `serverless.yml`, `Dockerfile`, manifests, or environment variable semantics'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Env/config: import from `app/env.py` and `app/openai_constants.py`; avoid re-reading `os.environ` in modules.' in text, "expected to find: " + '- Env/config: import from `app/env.py` and `app/openai_constants.py`; avoid re-reading `os.environ` in modules.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Reuse helpers in `app/` (e.g., `markdown_conversion.py`, `openai_ops.py`) instead of reimplementing.' in text, "expected to find: " + '- Reuse helpers in `app/` (e.g., `markdown_conversion.py`, `openai_ops.py`) instead of reimplementing.'[:80]

