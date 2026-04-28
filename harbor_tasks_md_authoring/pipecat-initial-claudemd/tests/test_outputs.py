"""Behavioral checks for pipecat-initial-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pipecat")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Events**: Most classes in Pipecat have `BaseObject` as the very base class. `BaseObject` has support for events. Events can run in the background in an async task (default) or synchronously (`sync' in text, "expected to find: " + '- **Events**: Most classes in Pipecat have `BaseObject` as the very base class. `BaseObject` has support for events. Events can run in the background in an async task (default) or synchronously (`sync'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Interruptions**: Interruptions are usually triggered by a user turn start strategy (e.g. `VADUserTurnStartStrategy`) but they can be triggered by other processors as well, in which case the user t' in text, "expected to find: " + '- **Interruptions**: Interruptions are usually triggered by a user turn start strategy (e.g. `VADUserTurnStartStrategy`) but they can be triggered by other processors as well, in which case the user t'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Pipecat is an open-source Python framework for building real-time voice and multimodal conversational AI agents. It orchestrates audio/video, AI services, transports, and conversation pipelines using ' in text, "expected to find: " + 'Pipecat is an open-source Python framework for building real-time voice and multimodal conversational AI agents. It orchestrates audio/video, AI services, transports, and conversation pipelines using '[:80]

