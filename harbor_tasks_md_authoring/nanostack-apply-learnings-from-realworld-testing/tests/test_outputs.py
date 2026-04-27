"""Behavioral checks for nanostack-apply-learnings-from-realworld-testing (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanostack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert '- **Not reading CONTRIBUTING.md.** Every project has different rules. Some require video evidence, some require specific naming conventions, some have line limits. Read the rules before writing the PR' in text, "expected to find: " + '- **Not reading CONTRIBUTING.md.** Every project has different rules. Some require video evidence, some require specific naming conventions, some have line limits. Read the rules before writing the PR'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert '- **Creating PRs without checking existing work.** Submitted a PR to FastAPI without realizing 8 other PRs existed for the same issue, including one the maintainer preferred. Always search first.' in text, "expected to find: " + '- **Creating PRs without checking existing work.** Submitted a PR to FastAPI without realizing 8 other PRs existed for the same issue, including one the maintainer preferred. Always search first.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert "- **CI checks that only maintainers resolve.** Label checks, CLA checks, approval gates. These will fail on your PR and there's nothing you can do. Know which checks you own and which you don't." in text, "expected to find: " + "- **CI checks that only maintainers resolve.** Label checks, CLA checks, approval gates. These will fail on your PR and there's nothing you can do. Know which checks you own and which you don't."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('think/SKILL.md')
    assert '- **Same intensity for everyone.** The first version challenged a user\'s personal pain point ("are your bookmarks even worth saving?"). Calibrate by mode. Founder mode pushes hard. Startup/Builder mod' in text, "expected to find: " + '- **Same intensity for everyone.** The first version challenged a user\'s personal pain point ("are your bookmarks even worth saving?"). Calibrate by mode. Founder mode pushes hard. Startup/Builder mod'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('think/SKILL.md')
    assert '- **Running the diagnostic on a problem that doesn\'t need a diagnostic.** "Fix this bug" doesn\'t need six forcing questions. Detect when the user already knows what they want and skip to the brief.' in text, "expected to find: " + '- **Running the diagnostic on a problem that doesn\'t need a diagnostic.** "Fix this bug" doesn\'t need six forcing questions. Detect when the user already knows what they want and skip to the brief.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('think/SKILL.md')
    assert '- **Skipping Search Before Building.** A user wanted to build a feature that 3 other people had already submitted PRs for in the target repo. 30 seconds of search would have saved hours.' in text, "expected to find: " + '- **Skipping Search Before Building.** A user wanted to build a feature that 3 other people had already submitted PRs for in the target repo. 30 seconds of search would have saved hours.'[:80]

