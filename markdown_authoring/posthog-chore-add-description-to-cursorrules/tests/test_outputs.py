"""Behavioral checks for posthog-chore-add-description-to-cursorrules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/posthog")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/django-python.mdc')
    assert 'description: Rules for writing Python services at PostHog (Python servers powered by the Django framework)' in text, "expected to find: " + 'description: Rules for writing Python services at PostHog (Python servers powered by the Django framework)'[:80]

