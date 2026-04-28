"""Behavioral checks for langchain-chore-update-agent-files (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/langchain")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Releases are triggered manually via `.github/workflows/_release.yml` with `working-directory` and `release-version` inputs.' in text, "expected to find: " + 'Releases are triggered manually via `.github/workflows/_release.yml` with `working-directory` and `release-version` inputs.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `.github/workflows/integration_tests.yml` – Add integration test config' in text, "expected to find: " + '- `.github/workflows/integration_tests.yml` – Add integration test config'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `.github/workflows/auto-label-by-package.yml` – Add package label' in text, "expected to find: " + '- `.github/workflows/auto-label-by-package.yml` – Add package label'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Releases are triggered manually via `.github/workflows/_release.yml` with `working-directory` and `release-version` inputs.' in text, "expected to find: " + 'Releases are triggered manually via `.github/workflows/_release.yml` with `working-directory` and `release-version` inputs.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `.github/workflows/integration_tests.yml` – Add integration test config' in text, "expected to find: " + '- `.github/workflows/integration_tests.yml` – Add integration test config'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `.github/workflows/auto-label-by-package.yml` – Add package label' in text, "expected to find: " + '- `.github/workflows/auto-label-by-package.yml` – Add package label'[:80]

