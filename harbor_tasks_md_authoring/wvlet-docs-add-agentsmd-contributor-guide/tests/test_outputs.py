"""Behavioral checks for wvlet-docs-add-agentsmd-contributor-guide (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/wvlet")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Commit style: conventional prefixes seen in history (e.g., `fix: ...`, `feature: ...`, `build(deps): ...`, `docs:`). Use present tense, concise scope.' in text, "expected to find: " + '- Commit style: conventional prefixes seen in history (e.g., `fix: ...`, `feature: ...`, `build(deps): ...`, `docs:`). Use present tense, concise scope.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Indentation: default Scalafmt (spaces). Use CamelCase for types/objects; lowerCamelCase for vals/defs; test classes end with `*Test` or `*Spec`.' in text, "expected to find: " + '- Indentation: default Scalafmt (spaces). Use CamelCase for types/objects; lowerCamelCase for vals/defs; test classes end with `*Test` or `*Spec`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- UI/Tools: `wvlet-ui`, `wvlet-ui-main`, `wvlet-ui-playground`, `vscode-wvlet`, `prismjs-wvlet`, `highlightjs-wvlet`, `website`.' in text, "expected to find: " + '- UI/Tools: `wvlet-ui`, `wvlet-ui-main`, `wvlet-ui-playground`, `vscode-wvlet`, `prismjs-wvlet`, `highlightjs-wvlet`, `website`.'[:80]

