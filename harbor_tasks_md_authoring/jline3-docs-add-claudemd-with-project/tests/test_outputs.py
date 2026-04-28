"""Behavioral checks for jline3-docs-add-claudemd-with-project (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/jline3")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'JLine is a Java library for building interactive command-line applications. It provides terminal handling, line editing with history and completion, configurable key bindings, Unicode and mouse suppor' in text, "expected to find: " + 'JLine is a Java library for building interactive command-line applications. It provides terminal handling, line editing with history and completion, configurable key bindings, Unicode and mouse suppor'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Do NOT add `Co-Authored-By: Claude ...` lines to commits. Do NOT add "Generated with Claude Code" or similar attribution to PR descriptions. Commits and PRs should look like normal human contributions' in text, "expected to find: " + 'Do NOT add `Co-Authored-By: Claude ...` lines to commits. Do NOT add "Generated with Claude Code" or similar attribution to PR descriptions. Commits and PRs should look like normal human contributions'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Key modules: `terminal`, `reader`, `native`, `style`, `builtins`, `console`, `console-ui`, `prompt`, `curses`, `remote-ssh`, `remote-telnet`, `groovy`, `demo`.' in text, "expected to find: " + 'Key modules: `terminal`, `reader`, `native`, `style`, `builtins`, `console`, `console-ui`, `prompt`, `curses`, `remote-ssh`, `remote-telnet`, `groovy`, `demo`.'[:80]

