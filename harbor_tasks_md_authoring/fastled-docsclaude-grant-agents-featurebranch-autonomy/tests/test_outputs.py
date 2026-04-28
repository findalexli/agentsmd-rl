"""Behavioral checks for fastled-docsclaude-grant-agents-featurebranch-autonomy (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fastled")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Default mindset: finish the job.** Agents should not leave uncommitted changes dangling on `master`/`main`. If you made edits on `master`, the correct end-state is a feature branch + pushed PR — n' in text, "expected to find: " + '- **Default mindset: finish the job.** Agents should not leave uncommitted changes dangling on `master`/`main`. If you made edits on `master`, the correct end-state is a feature branch + pushed PR — n'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Feature branches — full autonomy, no user consent required.** Agents may freely create branches, commit, push, and open PRs against any branch that is NOT `master`/`main`. Do this proactively when' in text, "expected to find: " + '- **Feature branches — full autonomy, no user consent required.** Agents may freely create branches, commit, push, and open PRs against any branch that is NOT `master`/`main`. Do this proactively when'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- If changes exist on `master`, move them: `git checkout -b feat/<topic>` carries the working-tree changes to a feature branch, then commit + push + open a PR there.' in text, "expected to find: " + '- If changes exist on `master`, move them: `git checkout -b feat/<topic>` carries the working-tree changes to a feature branch, then commit + push + open a PR there.'[:80]

