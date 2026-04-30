"""Behavioral checks for compound-engineering-plugin-fixgitcommitpushpr-rewrite-descr (markdown_authoring task).

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
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert '- **Describe the net result, not the journey**: The description covers the end state, not how you got there. No iteration history, debugging steps, intermediate failures, or bugs found and fixed durin' in text, "expected to find: " + '- **Describe the net result, not the journey**: The description covers the end state, not how you got there. No iteration history, debugging steps, intermediate failures, or bugs found and fixed durin'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert '- **Lead with value**: Open with what\'s now possible or fixed, not what was moved around. The subtler failure is leading with the mechanism ("Replace the hardcoded capture block with a tiered skill") ' in text, "expected to find: " + '- **Lead with value**: Open with what\'s now possible or fixed, not what was moved around. The subtler failure is leading with the mechanism ("Replace the hardcoded capture block with a tiered skill") '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert '1. **Capture now** -- load the `ce-demo-reel` skill with a target description inferred from the branch diff. ce-demo-reel returns `Tier`, `Description`, and `URL`. Build a `## Demo` or `## Screenshots' in text, "expected to find: " + '1. **Capture now** -- load the `ce-demo-reel` skill with a target description inferred from the branch diff. ce-demo-reel returns `Tier`, `Description`, and `URL`. Build a `## Demo` or `## Screenshots'[:80]

