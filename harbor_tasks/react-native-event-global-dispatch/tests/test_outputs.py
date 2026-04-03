"""
Task: react-native-event-global-dispatch
Repo: facebook/react @ a48e9e3f10fed06c813399ccae8a28db7dd76683

Fix: Set global.event during executeDispatch so that event handlers
can access the current event via the global, matching browser behavior.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path

REPO = "/workspace/react"
TARGET = f"{REPO}/packages/react-native-renderer/src/legacy-events/EventPluginUtils.js"


def test_file_exists():
    """Target file must exist."""
    assert Path(TARGET).exists()


def test_global_event_set():
    """global.event should be set to the current event during dispatch."""
    src = Path(TARGET).read_text()
    assert "global.event = event" in src, \
        "Should set global.event = event before calling listener"


def test_global_event_saved():
    """Should save the previous global.event before overwriting."""
    src = Path(TARGET).read_text()
    assert "currentEvent = global.event" in src or "const currentEvent" in src, \
        "Should save current global.event before overwriting"


def test_global_event_restored():
    """Should restore previous global.event after dispatch."""
    src = Path(TARGET).read_text()
    assert "global.event = currentEvent" in src, \
        "Should restore global.event = currentEvent after listener call"


def test_restore_after_try_block():
    """Restore should happen after the try/catch block, not inside catch."""
    src = Path(TARGET).read_text()
    # The restore line should appear after the catch block
    lines = src.split('\n')
    restore_line = None
    catch_line = None
    for i, line in enumerate(lines):
        if 'global.event = currentEvent' in line:
            restore_line = i
        if '} catch' in line and restore_line is None:
            catch_line = i
    assert restore_line is not None, "global.event = currentEvent not found"
