"""Behavioral checks for coil-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/coil")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Multimodule Kotlin project with public modules like `coil`, `coil-core`, `coil-compose`, network adapters, and artifacts under `internal/*` and `samples/*`.' in text, "expected to find: " + '- Multimodule Kotlin project with public modules like `coil`, `coil-core`, `coil-compose`, network adapters, and artifacts under `internal/*` and `samples/*`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Source sets follow `src/commonMain`, `src/jvmMain`, `src/androidMain`, plus matching `*Test` directories (for example `coil-core/src/commonTest`).' in text, "expected to find: " + '- Source sets follow `src/commonMain`, `src/jvmMain`, `src/androidMain`, plus matching `*Test` directories (for example `coil-core/src/commonTest`).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Run `./gradlew check` for JVM/common tests and `./gradlew connectedDebugAndroidTest` for device tests (emulator required).' in text, "expected to find: " + '- Run `./gradlew check` for JVM/common tests and `./gradlew connectedDebugAndroidTest` for device tests (emulator required).'[:80]

