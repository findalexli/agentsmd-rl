"""Behavioral checks for terraforming-mars-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/terraforming-mars")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The `Behavior` type (`src/server/behavior/Behavior.ts`) is a declarative DSL for card effects: production changes, resource gains, tile placement, TR changes, etc. Cards set `behavior` (on play) and/o' in text, "expected to find: " + 'The `Behavior` type (`src/server/behavior/Behavior.ts`) is a declarative DSL for card effects: production changes, resource gains, tile placement, TR changes, etc. Cards set `behavior` (on play) and/o'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Each expansion has its own directory under `src/server/cards/` and a manifest. Modules: `base`, `corpera` (Corporate Era), `promo`, `venus`, `colonies`, `prelude`, `prelude2`, `turmoil`, `community`, ' in text, "expected to find: " + 'Each expansion has its own directory under `src/server/cards/` and a manifest. Modules: `base`, `corpera` (Corporate Era), `promo`, `venus`, `colonies`, `prelude`, `prelude2`, `turmoil`, `community`, '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. **Card class** (`src/server/cards/<module>/CardName.ts`) - Extends `Card`, defines cost, tags, requirements, behavior, and metadata. Simple cards are purely declarative via the `behavior` property.' in text, "expected to find: " + '1. **Card class** (`src/server/cards/<module>/CardName.ts`) - Extends `Card`, defines cost, tags, requirements, behavior, and metadata. Simple cards are purely declarative via the `behavior` property.'[:80]

