"""Behavioral checks for screentimelapse-minor-adding-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/screentimelapse")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- `xcodebuild test -project TimeLapze.xcodeproj -scheme Test -destination 'platform=macOS'`: Run unit/UI tests from CLI (requires valid local signing setup)." in text, "expected to find: " + "- `xcodebuild test -project TimeLapze.xcodeproj -scheme Test -destination 'platform=macOS'`: Run unit/UI tests from CLI (requires valid local signing setup)."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Recent commits favor short, imperative summaries, sometimes with an issue/PR reference (for example, `Update timelapze.rb` or `Updating readme (#62)`).' in text, "expected to find: " + 'Recent commits favor short, imperative summaries, sometimes with an issue/PR reference (for example, `Update timelapze.rb` or `Updating readme (#62)`).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Repo-level tooling/config includes `.swift-format` (format rules), `typos.toml` (spelling checks), and `timelapze.rb` (Homebrew cask metadata).' in text, "expected to find: " + 'Repo-level tooling/config includes `.swift-format` (format rules), `typos.toml` (spelling checks), and `timelapze.rb` (Homebrew cask metadata).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

