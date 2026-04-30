"""Behavioral checks for ledger-live-chorecursor-streamline-testing-skill-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ledger-live")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/testing/SKILL.md')
    assert '7. **Use existing factories** — `genAccount()` from `@ledgerhq/coin-framework/mocks/account`, `getCryptoCurrencyById()` from `@ledgerhq/live-common/currencies`. Never recreate account/currency data fr' in text, "expected to find: " + '7. **Use existing factories** — `genAccount()` from `@ledgerhq/coin-framework/mocks/account`, `getCryptoCurrencyById()` from `@ledgerhq/live-common/currencies`. Never recreate account/currency data fr'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/testing/SKILL.md')
    assert '1. **`toBeVisible()` over `toBeInTheDocument()`** — Always. `toBeInTheDocument` only checks DOM presence; elements can be hidden. Use `toBeInTheDocument` only when testing explicitly hidden elements.' in text, "expected to find: " + '1. **`toBeVisible()` over `toBeInTheDocument()`** — Always. `toBeInTheDocument` only checks DOM presence; elements can be hidden. Use `toBeInTheDocument` only when testing explicitly hidden elements.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/testing/SKILL.md')
    assert '2. **Search before you create** — Before writing any mock, fixture, or helper, `rg` the codebase. If it exists, import it. If your new mock is reusable (2+ files), put it in a shared location.' in text, "expected to find: " + '2. **Search before you create** — Before writing any mock, fixture, or helper, `rg` the codebase. If it exists, import it. If your new mock is reusable (2+ files), put it in a shared location.'[:80]

