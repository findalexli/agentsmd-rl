"""Behavioral checks for bsl-language-server-add-copilot-instructions-for-repository (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/bsl-language-server")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'BSL Language Server is an implementation of the [Language Server Protocol](https://microsoft.github.io/language-server-protocol/) for 1C (BSL) - the 1C:Enterprise 8 language and [OneScript](http://osc' in text, "expected to find: " + 'BSL Language Server is an implementation of the [Language Server Protocol](https://microsoft.github.io/language-server-protocol/) for 1C (BSL) - the 1C:Enterprise 8 language and [OneScript](http://osc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This is a Java-based language server that provides code analysis, diagnostics, code actions, and other language features for 1C development.' in text, "expected to find: " + 'This is a Java-based language server that provides code analysis, diagnostics, code actions, and other language features for 1C development.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Documentation: [docs/index.md](../docs/index.md) (Russian), [docs/en/index.md](../docs/en/index.md) (English)' in text, "expected to find: " + '- Documentation: [docs/index.md](../docs/index.md) (Russian), [docs/en/index.md](../docs/en/index.md) (English)'[:80]

