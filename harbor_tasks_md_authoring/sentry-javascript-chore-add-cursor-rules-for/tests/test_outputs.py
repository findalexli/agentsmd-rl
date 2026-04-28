"""Behavioral checks for sentry-javascript-chore-add-cursor-rules-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sentry-javascript")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/adding-a-new-ai-integration.mdc')
    assert "3. **Set Sentry origin**: `SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN = 'auto.ai.openai'` (use provider name: `openai`, `anthropic`, `vercelai`, etc. - only alphanumerics, `_`, and `.` allowed)" in text, "expected to find: " + "3. **Set Sentry origin**: `SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN = 'auto.ai.openai'` (use provider name: `openai`, `anthropic`, `vercelai`, etc. - only alphanumerics, `_`, and `.` allowed)"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/adding-a-new-ai-integration.mdc')
    assert "**Streaming:** Use `startSpanManual()` and prefer event listeners/hooks when available (like Anthropic's `stream.on()`). If not available, use async generator pattern:" in text, "expected to find: " + "**Streaming:** Use `startSpanManual()` and prefer event listeners/hooks when available (like Anthropic's `stream.on()`). If not available, use async generator pattern:"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/adding-a-new-ai-integration.mdc')
    assert '- **Important:** Disable underlying AI provider wrapping (see `instrumentLangchain` in `packages/node/src/integrations/tracing/langchain/instrumentation.ts`)' in text, "expected to find: " + '- **Important:** Disable underlying AI provider wrapping (see `instrumentLangchain` in `packages/node/src/integrations/tracing/langchain/instrumentation.ts`)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sdk_development.mdc')
    assert '- `packages/core/src/tracing/{provider}/` - Core instrumentation logic (OpenAI, Anthropic, Vercel AI, LangChain, etc.)' in text, "expected to find: " + '- `packages/core/src/tracing/{provider}/` - Core instrumentation logic (OpenAI, Anthropic, Vercel AI, LangChain, etc.)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sdk_development.mdc')
    assert '- `packages/node/src/integrations/tracing/{provider}/` - Node.js-specific integration + OTel instrumentation' in text, "expected to find: " + '- `packages/node/src/integrations/tracing/{provider}/` - Node.js-specific integration + OTel instrumentation'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sdk_development.mdc')
    assert '- `packages/cloudflare/src/integrations/tracing/{provider}.ts` - Edge runtime support' in text, "expected to find: " + '- `packages/cloudflare/src/integrations/tracing/{provider}.ts` - Edge runtime support'[:80]

