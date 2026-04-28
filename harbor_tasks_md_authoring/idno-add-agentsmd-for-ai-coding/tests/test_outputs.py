"""Behavioral checks for idno-add-agentsmd-for-ai-coding (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/idno")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| `ActivityBuilder.php` | Builds outgoing activities (Create, Update, Delete, Accept) and objects (Note, Article, Event) |' in text, "expected to find: " + '| `ActivityBuilder.php` | Builds outgoing activities (Create, Update, Delete, Accept) and objects (Note, Article, Event) |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Plugins use braced namespace blocks: `namespace IdnoPlugins\\Foo { class Main extends \\Idno\\Common\\Plugin { } }`' in text, "expected to find: " + '- Plugins use braced namespace blocks: `namespace IdnoPlugins\\Foo { class Main extends \\Idno\\Common\\Plugin { } }`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| **Webmention** | `Idno\\Core\\Webmention` — sends and receives webmentions; endpoint at `/webmention/endpoint` |' in text, "expected to find: " + '| **Webmention** | `Idno\\Core\\Webmention` — sends and receives webmentions; endpoint at `/webmention/endpoint` |'[:80]

