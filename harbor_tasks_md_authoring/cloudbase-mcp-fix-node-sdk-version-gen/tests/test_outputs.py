"""Behavioral checks for cloudbase-mcp-fix-node-sdk-version-gen (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cloudbase-mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('config/.claude/skills/ai-model-cloudbase/SKILL.md')
    assert '⚠️ **Node SDK AI feature requires version 3.16.0 or above.** Check your version with `npm list @cloudbase/node-sdk`.' in text, "expected to find: " + '⚠️ **Node SDK AI feature requires version 3.16.0 or above.** Check your version with `npm list @cloudbase/node-sdk`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('config/.claude/skills/ai-model-cloudbase/SKILL.md')
    assert '⚠️ **Image generation is currently only available in Node SDK**, not in JS SDK (Web) or WeChat Mini Program.' in text, "expected to find: " + '⚠️ **Image generation is currently only available in Node SDK**, not in JS SDK (Web) or WeChat Mini Program.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('config/.claude/skills/ai-model-cloudbase/SKILL.md')
    assert '| Node.js (Server/Cloud Functions) | `@cloudbase/node-sdk` ≥3.16.0 | Part 1 (same API, different init) |' in text, "expected to find: " + '| Node.js (Server/Cloud Functions) | `@cloudbase/node-sdk` ≥3.16.0 | Part 1 (same API, different init) |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('config/.cursor/rules/cloudbase-rules.mdc')
    assert '- **AI Model Calling**: `rules/ai-model-cloudbase/rule.md` - Call AI models (Hunyuan, DeepSeek) via CloudBase JS/Node SDK, HTTP API, and WeChat Mini Program. Supports text generation, streaming, and i' in text, "expected to find: " + '- **AI Model Calling**: `rules/ai-model-cloudbase/rule.md` - Call AI models (Hunyuan, DeepSeek) via CloudBase JS/Node SDK, HTTP API, and WeChat Mini Program. Supports text generation, streaming, and i'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('config/.cursor/rules/cloudbase-rules.mdc')
    assert '- `rules/ai-model-cloudbase/rule.md` - AI model calling (text generation, streaming, image generation via Node SDK ≥3.16.0)' in text, "expected to find: " + '- `rules/ai-model-cloudbase/rule.md` - AI model calling (text generation, streaming, image generation via Node SDK ≥3.16.0)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('config/.cursor/rules/cloudbase-rules.mdc')
    assert '- **AI Model Integration**: Projects requiring AI capabilities (text generation, streaming responses, image generation)' in text, "expected to find: " + '- **AI Model Integration**: Projects requiring AI capabilities (text generation, streaming responses, image generation)'[:80]

