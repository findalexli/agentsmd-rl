"""Behavioral checks for ente-locker-add-claudemd-documentation-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ente")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('mobile/apps/locker/CLAUDE.md')
    assert "Ente Locker is a Flutter application for securely storing important documents. It's part of the Ente mobile monorepo and shares multiple packages with the Ente Photos app. The app provides encrypted f" in text, "expected to find: " + "Ente Locker is a Flutter application for securely storing important documents. It's part of the Ente mobile monorepo and shares multiple packages with the Ente Photos app. The app provides encrypted f"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('mobile/apps/locker/CLAUDE.md')
    assert "Ente is focused on privacy, transparency and trust. It's a fully open-source, end-to-end encrypted platform for storing data in the cloud. When contributing, always prioritize:" in text, "expected to find: " + "Ente is focused on privacy, transparency and trust. It's a fully open-source, end-to-end encrypted platform for storing data in the cloud. When contributing, always prioritize:"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('mobile/apps/locker/CLAUDE.md')
    assert '5. **Sync timing:** File upload operations should NOT manually call `_loadCollections()` in the callback to avoid duplicate UI refreshes (see `HomePage.onFileUploadComplete()`)' in text, "expected to find: " + '5. **Sync timing:** File upload operations should NOT manually call `_loadCollections()` in the callback to avoid duplicate UI refreshes (see `HomePage.onFileUploadComplete()`)'[:80]

