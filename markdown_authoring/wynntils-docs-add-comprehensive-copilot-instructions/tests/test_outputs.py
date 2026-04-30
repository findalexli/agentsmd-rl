"""Behavioral checks for wynntils-docs-add-comprehensive-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/wynntils")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**ALWAYS run `spotlessApply` before committing code.** Spotless uses the Palantir Java format engine and enforces strict code style rules. GitHub Actions will auto-commit formatting fixes, but running' in text, "expected to find: " + '**ALWAYS run `spotlessApply` before committing code.** Spotless uses the Palantir Java format engine and enforces strict code style rules. GitHub Actions will auto-commit formatting fixes, but running'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '1. **"Plugin architectury-plugin not found"**: Usually indicates missing Maven repository or network issue. Ensure internet connection is stable. The plugin uses SNAPSHOT versions from https://maven.a' in text, "expected to find: " + '1. **"Plugin architectury-plugin not found"**: Usually indicates missing Maven repository or network issue. Ensure internet connection is stable. The plugin uses SNAPSHOT versions from https://maven.a'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Wynntils** is a Minecraft mod for the Wynncraft MMORPG server that enhances gameplay with customizable options and additions. This is a complete rewrite (originally codenamed Artemis) of the legacy ' in text, "expected to find: " + '**Wynntils** is a Minecraft mod for the Wynncraft MMORPG server that enhances gameplay with customizable options and additions. This is a complete rewrite (originally codenamed Artemis) of the legacy '[:80]

