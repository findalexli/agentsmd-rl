"""Behavioral checks for minder-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/minder")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Minder is an open-source supply chain security platform that helps development teams build more secure software and prove their security posture. It enables proactive security policy management across' in text, "expected to find: " + 'Minder is an open-source supply chain security platform that helps development teams build more secure software and prove their security posture. It enables proactive security policy management across'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '6. **Providers** (`internal/providers/`): Integration with GitHub, GitLab, container registries' in text, "expected to find: " + '6. **Providers** (`internal/providers/`): Integration with GitHub, GitLab, container registries'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**gRPC connection refused**: Ensure server is running and config points to correct host:port' in text, "expected to find: " + '**gRPC connection refused**: Ensure server is running and config points to correct host:port'[:80]

