"""Behavioral checks for cloudbase-mcp-feat-add-call-ai-skill (markdown_authoring task).

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
    assert 'description: Complete guide for calling AI models with CloudBase - covers JS/Node SDK and WeChat Mini Program. Text generation, streaming, and image generation.' in text, "expected to find: " + 'description: Complete guide for calling AI models with CloudBase - covers JS/Node SDK and WeChat Mini Program. Text generation, streaming, and image generation.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('config/.claude/skills/ai-model-cloudbase/SKILL.md')
    assert '⚠️ **WeChat Mini Program API is DIFFERENT from JS/Node SDK.** Pay attention to the parameter structure.' in text, "expected to find: " + '⚠️ **WeChat Mini Program API is DIFFERENT from JS/Node SDK.** Pay attention to the parameter structure.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('config/.claude/skills/ai-model-cloudbase/SKILL.md')
    assert '3. **Pick the appropriate section** - **Part 1** for JS/Node SDK, **Part 3** for WeChat Mini Program' in text, "expected to find: " + '3. **Pick the appropriate section** - **Part 1** for JS/Node SDK, **Part 3** for WeChat Mini Program'[:80]

