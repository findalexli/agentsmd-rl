"""Behavioral checks for inspect_evals-add-skill-hygiene-section-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/inspect-evals")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- If the session surfaced a durable repo convention, reviewer expectation, or repeated failure mode, consider whether it should also be captured in REPO_CONTEXT.md or AGENTS.md, but ask the user befor' in text, "expected to find: " + '- If the session surfaced a durable repo convention, reviewer expectation, or repeated failure mode, consider whether it should also be captured in REPO_CONTEXT.md or AGENTS.md, but ask the user befor'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Also consider whether any skill used during the session is now missing steps, has outdated guidance, or could be made more robust based on what was learned.' in text, "expected to find: " + '- Also consider whether any skill used during the session is now missing steps, has outdated guidance, or could be made more robust based on what was learned.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Do not suggest a new skill for one-off work, highly personal preferences, or tasks that are too small to justify maintenance overhead.' in text, "expected to find: " + '- Do not suggest a new skill for one-off work, highly personal preferences, or tasks that are too small to justify maintenance overhead.'[:80]

