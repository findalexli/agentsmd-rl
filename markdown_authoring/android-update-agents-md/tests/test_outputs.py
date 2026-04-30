"""Behavioral checks for android-update-agents-md (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/android")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The `com.nextcloud.utils.extensions` package contains helper extensions organized by type (e.g., `FileExtensions.kt`, `StringExtensions.kt`, `ViewExtensions.kt`). Create focused extension files rather' in text, "expected to find: " + 'The `com.nextcloud.utils.extensions` package contains helper extensions organized by type (e.g., `FileExtensions.kt`, `StringExtensions.kt`, `ViewExtensions.kt`). Create focused extension files rather'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `./app/src/main/res/values/` Translations. Only update `./app/src/main/res/values/strings.xml`. Do not modify any other translation files or folders. Ignore all `values-*` directories (e.g., `values' in text, "expected to find: " + '- `./app/src/main/res/values/` Translations. Only update `./app/src/main/res/values/strings.xml`. Do not modify any other translation files or folders. Ignore all `values-*` directories (e.g., `values'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Pull Request**: When the agent creates a PR, it should include a description summarizing the changes and why they were made. If a GitHub issue exists, reference it (e.g., “Closes #123”).' in text, "expected to find: " + '- **Pull Request**: When the agent creates a PR, it should include a description summarizing the changes and why they were made. If a GitHub issue exists, reference it (e.g., “Closes #123”).'[:80]

