"""Behavioral checks for voicemode-docs-improve-claudemd-with-progressive (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/voicemode")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **[skills/voicemode/SKILL.md](skills/voicemode/SKILL.md)** - Voice interaction usage and MCP tools' in text, "expected to find: " + '- **[skills/voicemode/SKILL.md](skills/voicemode/SKILL.md)** - Voice interaction usage and MCP tools'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **[docs/tutorials/getting-started.md](docs/tutorials/getting-started.md)** - Installation guide' in text, "expected to find: " + '- **[docs/tutorials/getting-started.md](docs/tutorials/getting-started.md)** - Installation guide'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **[docs/guides/configuration.md](docs/guides/configuration.md)** - Configuration reference' in text, "expected to find: " + '- **[docs/guides/configuration.md](docs/guides/configuration.md)** - Configuration reference'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert 'agents.md' in text, "expected to find: " + 'agents.md'[:80]

