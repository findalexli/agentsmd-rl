"""Behavioral checks for rdc-cli-docsskill-add-remote-split-android (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rdc-cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('src/rdc/_skills/SKILL.md')
    assert 'Always run `rdc doctor` first. It reports status for renderdoc module, renderdoccmd, adb, Android APK, and platform-specific toolchains. Only the missing-renderdoc-module case emits a dedicated build-' in text, "expected to find: " + 'Always run `rdc doctor` first. It reports status for renderdoc module, renderdoccmd, adb, Android APK, and platform-specific toolchains. Only the missing-renderdoc-module case emits a dedicated build-'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/rdc/_skills/SKILL.md')
    assert '- `rdc remote capture <app> -o frame.rdc [--args ...] [--frame N] [--keep-remote]` — inject, capture, and transfer back. `--keep-remote` skips the transfer and prints the remote path; replay it with `' in text, "expected to find: " + '- `rdc remote capture <app> -o frame.rdc [--args ...] [--frame N] [--keep-remote]` — inject, capture, and transfer back. `--keep-remote` skips the transfer and prints the remote path; replay it with `'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/rdc/_skills/SKILL.md')
    assert '- For remote replay: `rdc open frame.rdc --android [--serial SERIAL]` — this is the only form that rewrites the saved `adb://SERIAL` to the forwarded `localhost:PORT`. Passing `--proxy adb://SERIAL` d' in text, "expected to find: " + '- For remote replay: `rdc open frame.rdc --android [--serial SERIAL]` — this is the only form that rewrites the saved `adb://SERIAL` to the forwarded `localhost:PORT`. Passing `--proxy adb://SERIAL` d'[:80]

