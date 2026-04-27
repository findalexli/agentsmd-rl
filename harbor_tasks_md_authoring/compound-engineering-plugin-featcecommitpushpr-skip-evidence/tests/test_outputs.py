"""Behavioral checks for compound-engineering-plugin-featcecommitpushpr-skip-evidence (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-commit-push-pr/SKILL.md')
    assert 'Otherwise, run the full decision: if the branch diff changes observable behavior (UI, CLI output, API behavior with runnable code, generated artifacts, workflow output) and evidence is not otherwise b' in text, "expected to find: " + 'Otherwise, run the full decision: if the branch diff changes observable behavior (UI, CLI output, API behavior with runnable code, generated artifacts, workflow output) and evidence is not otherwise b'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-commit-push-pr/SKILL.md')
    assert '1. **User explicitly asked for evidence.** If the user\'s invocation requested it ("ship with a demo", "include a screenshot"), proceed directly to capture. If capture turns out to be not possible (no ' in text, "expected to find: " + '1. **User explicitly asked for evidence.** If the user\'s invocation requested it ("ship with a demo", "include a screenshot"), proceed directly to capture. If capture turns out to be not possible (no '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-commit-push-pr/SKILL.md')
    assert '2. **Agent judgment on authored changes.** If you authored the commits in this session and know the change is clearly non-observable (internal plumbing, backend refactor without user-facing effect, ty' in text, "expected to find: " + '2. **Agent judgment on authored changes.** If you authored the commits in this session and know the change is clearly non-observable (internal plumbing, backend refactor without user-facing effect, ty'[:80]

