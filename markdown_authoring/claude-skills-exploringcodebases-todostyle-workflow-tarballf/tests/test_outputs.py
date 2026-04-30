"""Behavioral checks for claude-skills-exploringcodebases-todostyle-workflow-tarballf (markdown_authoring task).

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
    assert 'curl -sL "https://api.github.com/repos/$OWNER/$REPO/tarball/$REF" -o /tmp/$REPO.tar.gz' in text, "expected to find: " + 'curl -sL "https://api.github.com/repos/$OWNER/$REPO/tarball/$REF" -o /tmp/$REPO.tar.gz'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('exploring-codebases/SKILL.md')
    assert 'mkdir -p /tmp/$REPO && tar -xzf /tmp/$REPO.tar.gz -C /tmp/$REPO --strip-components=1' in text, "expected to find: " + 'mkdir -p /tmp/$REPO && tar -xzf /tmp/$REPO.tar.gz -C /tmp/$REPO --strip-components=1'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('exploring-codebases/SKILL.md')
    assert '- **Scale**: For large repos (>100 files), use `--skip tests,vendored,docs,...`' in text, "expected to find: " + '- **Scale**: For large repos (>100 files), use `--skip tests,vendored,docs,...`'[:80]

