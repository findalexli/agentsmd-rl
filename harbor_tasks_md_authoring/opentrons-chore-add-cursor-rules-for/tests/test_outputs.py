"""Behavioral checks for opentrons-chore-add-cursor-rules-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opentrons")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/opentrons-ai-client_protocol-designer_react-component.mdc')
    assert '"Create a React component named {ComponentName} using TypeScript and CSS Modules. It should {description of functionality}. Props should include {list of props with types}. The component should {any s' in text, "expected to find: " + '"Create a React component named {ComponentName} using TypeScript and CSS Modules. It should {description of functionality}. Props should include {list of props with types}. The component should {any s'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/opentrons-ai-client_protocol-designer_react-component.mdc')
    assert '- Generally use interface to define props for a new component and interface name should be <ComponentNameProps>' in text, "expected to find: " + '- Generally use interface to define props for a new component and interface name should be <ComponentNameProps>'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/opentrons-ai-client_protocol-designer_react-component.mdc')
    assert '- CSS Modules name must be <component name>.module.css and <component name> is always lower case' in text, "expected to find: " + '- CSS Modules name must be <component name>.module.css and <component name> is always lower case'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/protocol-designer_react-component.mdc')
    assert '.cursor/rules/protocol-designer_react-component.mdc' in text, "expected to find: " + '.cursor/rules/protocol-designer_react-component.mdc'[:80]

