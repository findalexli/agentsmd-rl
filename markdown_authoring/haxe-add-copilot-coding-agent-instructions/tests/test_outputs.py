"""Behavioral checks for haxe-add-copilot-coding-agent-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/haxe")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **The Haxe compiler** - written in OCaml, targets multiple platforms (JavaScript, C++, JVM, Lua, PHP, Python, HashLink, NekoVM, Flash, and its own interpreter)' in text, "expected to find: " + '- **The Haxe compiler** - written in OCaml, targets multiple platforms (JavaScript, C++, JVM, Lua, PHP, Python, HashLink, NekoVM, Flash, and its own interpreter)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This is the Haxe compiler repository. Haxe is an open source toolkit that allows building cross-platform tools and applications. The repository contains:' in text, "expected to find: " + 'This is the Haxe compiler repository. Haxe is an open source toolkit that allows building cross-platform tools and applications. The repository contains:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Note**: Not all tests belong in the unit tests. See the Tests section above for other test directories and their purposes.' in text, "expected to find: " + '**Note**: Not all tests belong in the unit tests. See the Tests section above for other test directories and their purposes.'[:80]

