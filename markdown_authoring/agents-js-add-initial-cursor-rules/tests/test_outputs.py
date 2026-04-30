"""Behavioral checks for agents-js-add-initial-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agents-js")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/agent-core.mdc')
    assert '> Whenever you have solved a complex task, which can be a tricky debugging process or a complex code implementation, document the core process under this section to illustrates any obstables you have ' in text, "expected to find: " + '> Whenever you have solved a complex task, which can be a tricky debugging process or a complex code implementation, document the core process under this section to illustrates any obstables you have '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/agent-core.mdc')
    assert 'For plugin components such as STT, TTS, LLM. You can debug these individual components by creating a new example agent file under the `examples` directory. You do not need to have `defineAgent` functi' in text, "expected to find: " + 'For plugin components such as STT, TTS, LLM. You can debug these individual components by creating a new example agent file under the `examples` directory. You do not need to have `defineAgent` functi'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/agent-core.mdc')
    assert 'If you want to override agent hooks (sttNode, ttsNode, llmNode), you can do so by creating a class that extends the `voice.Agent` class and override the hooks. Below is an example of how to override t' in text, "expected to find: " + 'If you want to override agent hooks (sttNode, ttsNode, llmNode), you can do so by creating a class that extends the `voice.Agent` class and override the hooks. Below is an example of how to override t'[:80]

