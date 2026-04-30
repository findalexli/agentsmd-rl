"""Behavioral checks for claude-skills-exploringcodebases-v220-step0-setup-ref (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('exploring-codebases/SKILL.md')
    assert 'REF=main                    # branch name, tag, or SHA. For a PR: pull/N/head' in text, "expected to find: " + 'REF=main                    # branch name, tag, or SHA. For a PR: pull/N/head'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('exploring-codebases/SKILL.md')
    assert '"https://api.github.com/repos/$OWNER/$REPO/tarball/$REF" -o /tmp/$REPO.tar.gz' in text, "expected to find: " + '"https://api.github.com/repos/$OWNER/$REPO/tarball/$REF" -o /tmp/$REPO.tar.gz'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('exploring-codebases/SKILL.md')
    assert "If step 2's `--stats` later reports `Scanned 0 files ... Errors: 1`, the" in text, "expected to find: " + "If step 2's `--stats` later reports `Scanned 0 files ... Errors: 1`, the"[:80]

