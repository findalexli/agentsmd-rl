"""Behavioral checks for calendr-add-copilot-coding-agent-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/calendr")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Calendr is a **macOS menu bar calendar application** built in Swift targeting macOS 14+. It displays calendar events and reminders from the system calendar and supports weather integration, time zone ' in text, "expected to find: " + 'Calendr is a **macOS menu bar calendar application** built in Swift targeting macOS 14+. It displays calendar events and reminders from the system calendar and supports weather integration, time zone '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Tests use **XCTest** with **RxTest** (`HistoricalScheduler`, `TestableObserver`) for testing reactive streams. Always write tests in `CalendrTests/` using mock providers from `CalendrTests/Mocks/`.' in text, "expected to find: " + 'Tests use **XCTest** with **RxTest** (`HistoricalScheduler`, `TestableObserver`) for testing reactive streams. Always write tests in `CalendrTests/` using mock providers from `CalendrTests/Mocks/`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Localised strings are code-generated via **swiftgen** into `Calendr/Constants/Strings.generated.swift` — always reference `Strings.*` constants instead of raw string literals for UI text' in text, "expected to find: " + '- Localised strings are code-generated via **swiftgen** into `Calendr/Constants/Strings.generated.swift` — always reference `Strings.*` constants instead of raw string literals for UI text'[:80]

