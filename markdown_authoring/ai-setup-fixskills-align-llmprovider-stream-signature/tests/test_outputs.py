"""Behavioral checks for ai-setup-fixskills-align-llmprovider-stream-signature (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai-setup")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/llm-provider/SKILL.md')
    assert '- **Interface contract**: Provider MUST implement `LLMProvider` from `src/llm/types.ts` — both `call(options: LLMCallOptions): Promise<string>` and `stream(options: LLMStreamOptions, callbacks: LLMStr' in text, "expected to find: " + '- **Interface contract**: Provider MUST implement `LLMProvider` from `src/llm/types.ts` — both `call(options: LLMCallOptions): Promise<string>` and `stream(options: LLMStreamOptions, callbacks: LLMStr'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/llm-provider/SKILL.md')
    assert '- `call(options: LLMCallOptions)` returns `Promise<string>`; `stream(options: LLMStreamOptions, callbacks: LLMStreamCallbacks)` returns `Promise<void>`' in text, "expected to find: " + '- `call(options: LLMCallOptions)` returns `Promise<string>`; `stream(options: LLMStreamOptions, callbacks: LLMStreamCallbacks)` returns `Promise<void>`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/llm-provider/SKILL.md')
    assert '- Verify `stream()` calls `callbacks.onText()` for each chunk and `callbacks.onEnd()` when done' in text, "expected to find: " + '- Verify `stream()` calls `callbacks.onText()` for each chunk and `callbacks.onEnd()` when done'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/llm-provider/SKILL.md')
    assert '- **Streaming via callbacks**: `stream()` invokes `callbacks.onText(text)` for each chunk, `callbacks.onEnd(meta?)` when complete, and `callbacks.onError(error)` on failure — it does NOT return an asy' in text, "expected to find: " + '- **Streaming via callbacks**: `stream()` invokes `callbacks.onText(text)` for each chunk, `callbacks.onEnd(meta?)` when complete, and `callbacks.onError(error)` on failure — it does NOT return an asy'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/llm-provider/SKILL.md')
    assert '- **All providers must implement `LLMProvider` interface** from `src/llm/types.ts`: `call(options: LLMCallOptions): Promise<string>` and `stream(options: LLMStreamOptions, callbacks: LLMStreamCallback' in text, "expected to find: " + '- **All providers must implement `LLMProvider` interface** from `src/llm/types.ts`: `call(options: LLMCallOptions): Promise<string>` and `stream(options: LLMStreamOptions, callbacks: LLMStreamCallback'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/llm-provider/SKILL.md')
    assert '- **"Stream callbacks never fire; onEnd not called"**: `stream()` must be `async` (not a generator). Ensure `callbacks.onEnd()` is called after the loop completes, not inside it.' in text, "expected to find: " + '- **"Stream callbacks never fire; onEnd not called"**: `stream()` must be `async` (not a generator). Ensure `callbacks.onEnd()` is called after the loop completes, not inside it.'[:80]

