"""Behavioral checks for ghost-added-agentsmd-to-shade (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ghost")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/shade/AGENTS.md')
    assert '- If a component already exists in `src/components/ui`, generate the new version in a temporary workspace (scratch repo), then manually diff and port only the desired changes into the existing Shade f' in text, "expected to find: " + '- If a component already exists in `src/components/ui`, generate the new version in a temporary workspace (scratch repo), then manually diff and port only the desired changes into the existing Shade f'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/shade/AGENTS.md')
    assert '- For new UI components, prioritize comprehensive Storybook stories; add focused unit tests where they provide real value (e.g., hooks, utils, logic-heavy parts).' in text, "expected to find: " + '- For new UI components, prioritize comprehensive Storybook stories; add focused unit tests where they provide real value (e.g., hooks, utils, logic-heavy parts).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/shade/AGENTS.md')
    assert '- Storybook: add a sibling `*.stories.tsx` file with an overview (what/why) and stories showing different use cases/variants (sizes, states, important props).' in text, "expected to find: " + '- Storybook: add a sibling `*.stories.tsx` file with an overview (what/why) and stories showing different use cases/variants (sizes, states, important props).'[:80]

