"""Behavioral checks for open-multi-agent-docs-sync-claudemd-architecture-map (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/open-multi-agent")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '`bash`, `file_read`, `file_write`, `file_edit`, `grep`, `glob` — registered via `registerBuiltInTools(registry)`. `grep` and `glob` share a recursive directory walker in `tool/built-in/fs-walk.ts` (wi' in text, "expected to find: " + '`bash`, `file_read`, `file_write`, `file_edit`, `grep`, `glob` — registered via `registerBuiltInTools(registry)`. `grep` and `glob` share a recursive directory walker in `tool/built-in/fs-walk.ts` (wi'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Implement `LLMAdapter` interface with `chat(messages, options)` and `stream(messages, options)`, add the provider name to the `SupportedProvider` union, then register a new `case` in the `createAdapte' in text, "expected to find: " + 'Implement `LLMAdapter` interface with `chat(messages, options)` and `stream(messages, options)`, add the provider name to the `SupportedProvider` union, then register a new `case` in the `createAdapte'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '`tool/text-tool-extractor.ts` is a safety-net fallback for OpenAI-compatible local servers (Ollama thinking-model bug, vLLM, LM Studio) that emit tool calls as plain text instead of native `tool_calls' in text, "expected to find: " + '`tool/text-tool-extractor.ts` is a safety-net fallback for OpenAI-compatible local servers (Ollama thinking-model bug, vLLM, LM Studio) that emit tool calls as plain text instead of native `tool_calls'[:80]

