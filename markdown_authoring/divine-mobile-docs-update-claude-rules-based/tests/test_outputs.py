"""Behavioral checks for divine-mobile-docs-update-claude-rules-based (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/divine-mobile")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/architecture.md')
    assert "Extracting into packages improves CI speed because only the affected package's workflow runs on changes, rather than the full mobile test suite." in text, "expected to find: " + "Extracting into packages improves CI speed because only the affected package's workflow runs on changes, rather than the full mobile test suite."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/architecture.md')
    assert '- A service has grown large enough to slow down CI (each package gets its own targeted CI workflow)' in text, "expected to find: " + '- A service has grown large enough to slow down CI (each package gets its own targeted CI workflow)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/architecture.md')
    assert '- A repository or client is reused across multiple features' in text, "expected to find: " + '- A repository or client is reused across multiple features'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/code_style.md')
    assert 'Transitional or temporary code (feature flags, compatibility shims, workarounds for in-progress migrations) must include a `// TODO(#issue):` comment referencing a tracking issue for its removal. Code' in text, "expected to find: " + 'Transitional or temporary code (feature flags, compatibility shims, workarounds for in-progress migrations) must include a `// TODO(#issue):` comment referencing a tracking issue for its removal. Code'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/code_style.md')
    assert 'Pull requests should only include changes directly related to the task. Remove unrelated file modifications (stale lock files, unrelated docs, formatting changes in untouched files) before requesting ' in text, "expected to find: " + 'Pull requests should only include changes directly related to the task. Remove unrelated file modifications (stale lock files, unrelated docs, formatting changes in untouched files) before requesting '[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/code_style.md')
    assert "When adding a new dependency to `pubspec.yaml`, always use the latest stable version. Don't copy version constraints from older packages without checking for updates." in text, "expected to find: " + "When adding a new dependency to `pubspec.yaml`, always use the latest stable version. Don't copy version constraints from older packages without checking for updates."[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/state_management.md')
    assert 'Simple derivations (null checks, string formatting, boolean flags) are fine as getters. However, if the computation is expensive — sorting, filtering, or transforming a list — store the result as a fi' in text, "expected to find: " + 'Simple derivations (null checks, string formatting, boolean flags) are fine as getters. However, if the computation is expensive — sorting, filtering, or transforming a list — store the result as a fi'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/state_management.md')
    assert '// Bad — expensive list operation as a getter, recomputed on every access' in text, "expected to find: " + '// Bad — expensive list operation as a getter, recomputed on every access'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/state_management.md')
    assert 'sortedVideos: videos.toList()..sort((a, b) => b.date.compareTo(a.date)),' in text, "expected to find: " + 'sortedVideos: videos.toList()..sort((a, b) => b.date.compareTo(a.date)),'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing.md')
    assert 'When extracting code into a new package (client, repository, utility), include test coverage in the same PR. Do not defer tests to a follow-up — the extraction PR is incomplete without them.' in text, "expected to find: " + 'When extracting code into a new package (client, repository, utility), include test coverage in the same PR. Do not defer tests to a follow-up — the extraction PR is incomplete without them.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing.md')
    assert '- Model serialization if the package defines models' in text, "expected to find: " + '- Model serialization if the package defines models'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing.md')
    assert '## New and Extracted Packages Must Ship with Tests' in text, "expected to find: " + '## New and Extracted Packages Must Ship with Tests'[:80]

