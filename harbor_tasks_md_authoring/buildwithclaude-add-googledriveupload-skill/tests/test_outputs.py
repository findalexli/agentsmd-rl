"""Behavioral checks for buildwithclaude-add-googledriveupload-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/buildwithclaude")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/google-drive-upload/SKILL.md')
    assert '"Uploaded successfully! Here\'s your file: https://drive.google.com/file/d/abc123/view"' in text, "expected to find: " + '"Uploaded successfully! Here\'s your file: https://drive.google.com/file/d/abc123/view"'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/google-drive-upload/SKILL.md')
    assert 'Upload files directly from Claude to Google Drive using a simple Google Apps Script.' in text, "expected to find: " + 'Upload files directly from Claude to Google Drive using a simple Google Apps Script.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/google-drive-upload/SKILL.md')
    assert '-d \'{"fileName":"name","content":"\'$B64\'","mimeType":"\'$MIME\'","apiKey":"KEY"}\' \\' in text, "expected to find: " + '-d \'{"fileName":"name","content":"\'$B64\'","mimeType":"\'$MIME\'","apiKey":"KEY"}\' \\'[:80]

