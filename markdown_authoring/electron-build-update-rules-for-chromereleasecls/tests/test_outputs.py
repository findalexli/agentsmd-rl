"""Behavioral checks for electron-build-update-rules-for-chromereleasecls (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/electron")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/chrome-release-cls/SKILL.md')
    assert '- **Roll CLs — skip and find the upstream fix:** For components whose fixes land in upstream repos (PDFium, Dawn, Skia, Graphite, libaom, libvpx, ffmpeg), the chromium-review hit will be a `Roll src/t' in text, "expected to find: " + '- **Roll CLs — skip and find the upstream fix:** For components whose fixes land in upstream repos (PDFium, Dawn, Skia, Graphite, libaom, libvpx, ffmpeg), the chromium-review hit will be a `Roll src/t'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/chrome-release-cls/SKILL.md')
    assert 'Only if the upstream Gerrit instance returns no results should you fall back to reporting the roll CL — in that case, include the roll CL and note that the actual fix is upstream but the specific CL c' in text, "expected to find: " + 'Only if the upstream Gerrit instance returns no results should you fall back to reporting the roll CL — in that case, include the roll CL and note that the actual fix is upstream but the specific CL c'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/chrome-release-cls/SKILL.md')
    assert '- **`b/` bug format (Skia, Graphite, Dawn):** These repos reference bugs as `b/<id>` in commit messages rather than `Bug: <id>` footers. The Gerrit `bug:` query will return nothing. Use `message:<id>`' in text, "expected to find: " + '- **`b/` bug format (Skia, Graphite, Dawn):** These repos reference bugs as `b/<id>` in commit messages rather than `Bug: <id>` footers. The Gerrit `bug:` query will return nothing. Use `message:<id>`'[:80]

