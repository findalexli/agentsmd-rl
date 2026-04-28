"""Behavioral checks for eas-build-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/eas-build")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'When working with this repository follow instructions from CLAUDE.md.' in text, "expected to find: " + 'When working with this repository follow instructions from CLAUDE.md.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- [./CLAUDE.md](./CLAUDE.md)' in text, "expected to find: " + '- [./CLAUDE.md](./CLAUDE.md)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'EAS Build is a cloud-based build system for Expo/React Native applications. This monorepo contains libraries used by the EAS Build service to process Android and iOS builds, supporting both traditiona' in text, "expected to find: " + 'EAS Build is a cloud-based build system for Expo/React Native applications. This monorepo contains libraries used by the EAS Build service to process Android and iOS builds, supporting both traditiona'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **CustomBuildContext** (`build-tools`): Implements `ExternalBuildContextProvider`, bridges BuildContext to steps framework, used in custom builds and generic jobs' in text, "expected to find: " + '- **CustomBuildContext** (`build-tools`): Implements `ExternalBuildContextProvider`, bridges BuildContext to steps framework, used in custom builds and generic jobs'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Android builder** (`packages/build-tools/src/builders/android.ts`): Gradle-based, handles APK/AAB generation, also see `functionGroups/build.ts`' in text, "expected to find: " + '- **Android builder** (`packages/build-tools/src/builders/android.ts`): Gradle-based, handles APK/AAB generation, also see `functionGroups/build.ts`'[:80]

