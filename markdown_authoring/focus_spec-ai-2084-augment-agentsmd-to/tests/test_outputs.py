"""Behavioral checks for focus_spec-ai-2084-augment-agentsmd-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/focus-spec")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '* **Suggestion-first feedback:** When a concrete fix exists, post it as a GitHub `suggestion` block so the author can accept with one click. Use plain-text comments only when the feedback requires dis' in text, "expected to find: " + '* **Suggestion-first feedback:** When a concrete fix exists, post it as a GitHub `suggestion` block so the author can accept with one click. Use plain-text comments only when the feedback requires dis'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '* **Self-contained comments:** Every review comment or suggestion MUST include all context needed for the author to evaluate it independently. Do not reference other comments (e.g., "same as above" or' in text, "expected to find: " + '* **Self-contained comments:** Every review comment or suggestion MUST include all context needed for the author to evaluate it independently. Do not reference other comments (e.g., "same as above" or'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '* **Example Disclaimer:** Top-level sections with examples MUST begin with this exact note (skip all subsections): `> Note: The following examples are informative and non-normative. They do not define' in text, "expected to find: " + '* **Example Disclaimer:** Top-level sections with examples MUST begin with this exact note (skip all subsections): `> Note: The following examples are informative and non-normative. They do not define'[:80]

