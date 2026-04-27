"""Behavioral checks for gemini-voyager-docs-update-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gemini-voyager")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| `src/features/backup/` | Auto-backup with File System API/JSZip fallback | Changing backup strategy, adding backup targets |' in text, "expected to find: " + '| `src/features/backup/` | Auto-backup with File System API/JSZip fallback | Changing backup strategy, adding backup targets |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| `src/features/backup/services/BackupService.ts` | Auto-backup with File System API | `backupService`, `createBackup()` |' in text, "expected to find: " + '| `src/features/backup/services/BackupService.ts` | Auto-backup with File System API | `backupService`, `createBackup()` |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| `src/features/backup/services/PromptImportExportService.ts` | Prompt backup/restore | Export/import prompt library |' in text, "expected to find: " + '| `src/features/backup/services/PromptImportExportService.ts` | Prompt backup/restore | Export/import prompt library |'[:80]

