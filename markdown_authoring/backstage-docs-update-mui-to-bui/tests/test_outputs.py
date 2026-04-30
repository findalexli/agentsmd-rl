"""Behavioral checks for backstage-docs-update-mui-to-bui (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/backstage")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/.well-known/skills/mui-to-bui-migration/SKILL.md')
    assert '- `Button` - Action buttons (`variant="primary"`, `variant="secondary"`, `variant="tertiary"`, `isDisabled`, `destructive`, `loading`)' in text, "expected to find: " + '- `Button` - Action buttons (`variant="primary"`, `variant="secondary"`, `variant="tertiary"`, `isDisabled`, `destructive`, `loading`)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/.well-known/skills/mui-to-bui-migration/SKILL.md')
    assert '- `Accordion` - Collapsible content panels (`Accordion`, `AccordionTrigger`, `AccordionPanel`, `AccordionGroup`)' in text, "expected to find: " + '- `Accordion` - Collapsible content panels (`Accordion`, `AccordionTrigger`, `AccordionPanel`, `AccordionGroup`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/.well-known/skills/mui-to-bui-migration/SKILL.md')
    assert '- `SearchAutocomplete` - Search input with autocomplete popover (`SearchAutocomplete`, `SearchAutocompleteItem`)' in text, "expected to find: " + '- `SearchAutocomplete` - Search input with autocomplete popover (`SearchAutocomplete`, `SearchAutocompleteItem`)'[:80]

