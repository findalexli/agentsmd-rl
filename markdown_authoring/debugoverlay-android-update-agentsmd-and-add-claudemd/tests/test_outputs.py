"""Behavioral checks for debugoverlay-android-update-agentsmd-and-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/debugoverlay-android")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Document all executed commands in the hand-off message. If a test is skipped, state why and note the risk. For script/config changes (Gradle `.kts`, `libs.versions.toml`, wrapper updates), run a light' in text, "expected to find: " + 'Document all executed commands in the hand-off message. If a test is skipped, state why and note the risk. For script/config changes (Gradle `.kts`, `libs.versions.toml`, wrapper updates), run a light'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Project tracks tool versions via `gradle/wrapper/gradle-wrapper.properties` (Gradle) and `gradle/libs.versions.toml` (AGP, plugins, dependencies). Keep those files as the single sources of truth; an' in text, "expected to find: " + '- Project tracks tool versions via `gradle/wrapper/gradle-wrapper.properties` (Gradle) and `gradle/libs.versions.toml` (AGP, plugins, dependencies). Keep those files as the single sources of truth; an'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- When upgrading dependencies or plugins, update the catalog (`gradle/libs.versions.toml`) and keep repository definitions centralised in `settings.gradle.kts`. Avoid reintroducing deprecated reposito' in text, "expected to find: " + '- When upgrading dependencies or plugins, update the catalog (`gradle/libs.versions.toml`) and keep repository definitions centralised in `settings.gradle.kts`. Avoid reintroducing deprecated reposito'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This repository already contains `AGENTS.md`. Claude should use that document as the canonical reference and treat this file as a Claude-specific companion that highlights preferred behaviours and com' in text, "expected to find: " + 'This repository already contains `AGENTS.md`. Claude should use that document as the canonical reference and treat this file as a Claude-specific companion that highlights preferred behaviours and com'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Keep both `AGENTS.md` and this guide open during sessions. If new conventions emerge (e.g., tool upgrades, testing matrix changes), update both documents in a coordinated PR. Happy collaborating, Clau' in text, "expected to find: " + 'Keep both `AGENTS.md` and this guide open during sessions. If new conventions emerge (e.g., tool upgrades, testing matrix changes), update both documents in a coordinated PR. Happy collaborating, Clau'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. **Pause and align** – read the full request, open tasks, and any referenced files before taking action. When requirements are ambiguous or contradictory, ask for clarification instead of guessing.' in text, "expected to find: " + '1. **Pause and align** – read the full request, open tasks, and any referenced files before taking action. When requirements are ambiguous or contradictory, ask for clarification instead of guessing.'[:80]

