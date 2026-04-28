"""Behavioral checks for android-add-investigation-debugging-practices-to (markdown_authoring task).

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
    text = _read('.github/copilot-instructions.md')
    assert '- **Verify code paths with logging, not reasoning.** Add `log_warn (LOG_DEFAULT, "..."sv, ...)` in C++ or `Android.Util.Log` in C#, rebuild, re-run, and check `adb logcat -d`. If your log never fires,' in text, "expected to find: " + '- **Verify code paths with logging, not reasoning.** Add `log_warn (LOG_DEFAULT, "..."sv, ...)` in C++ or `Android.Util.Log` in C#, rebuild, re-run, and check `adb logcat -d`. If your log never fires,'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Decompile the produced `.dll` before blaming runtime.** Use `ilspycmd` or `ildasm` to inspect the actual generated IL/metadata. A missing attribute or misnamed type in generator output cascades in' in text, "expected to find: " + '- **Decompile the produced `.dll` before blaming runtime.** Use `ilspycmd` or `ildasm` to inspect the actual generated IL/metadata. A missing attribute or misnamed type in generator output cascades in'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **`am instrument` going silent means it crashed, not hung.** Check `adb logcat -d | grep -E \'FATAL|tombstone|signal\'` for a native crash dump. Do not wait for a CI timeout to "confirm" a hang that w' in text, "expected to find: " + '- **`am instrument` going silent means it crashed, not hung.** Check `adb logcat -d | grep -E \'FATAL|tombstone|signal\'` for a native crash dump. Do not wait for a CI timeout to "confirm" a hang that w'[:80]

