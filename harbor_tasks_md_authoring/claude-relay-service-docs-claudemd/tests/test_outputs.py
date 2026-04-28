"""Behavioral checks for claude-relay-service-docs-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-relay-service")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Claude Relay Service 是一个多平台 AI API 中转服务，支持 **Claude (官方/Console)、Gemini、OpenAI Responses (Codex)、AWS Bedrock、Azure OpenAI、Droid (Factory.ai)、CCR** 等多种账户类型。提供完整的多账户管理、API Key 认证、代理配置、用户管理、LDAP认证、Webhoo' in text, "expected to find: " + 'Claude Relay Service 是一个多平台 AI API 中转服务，支持 **Claude (官方/Console)、Gemini、OpenAI Responses (Codex)、AWS Bedrock、Azure OpenAI、Droid (Factory.ai)、CCR** 等多种账户类型。提供完整的多账户管理、API Key 认证、代理配置、用户管理、LDAP认证、Webhoo'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **统一调度系统**: 使用 unifiedClaudeScheduler、unifiedGeminiScheduler、unifiedOpenAIScheduler、droidScheduler 实现跨账户类型的智能调度' in text, "expected to find: " + '- **统一调度系统**: 使用 unifiedClaudeScheduler、unifiedGeminiScheduler、unifiedOpenAIScheduler、droidScheduler 实现跨账户类型的智能调度'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **多账户类型支持**: 支持8种账户类型（claude-official、claude-console、bedrock、ccr、droid、gemini、openai-responses、azure-openai）' in text, "expected to find: " + '- **多账户类型支持**: 支持8种账户类型（claude-official、claude-console、bedrock、ccr、droid、gemini、openai-responses、azure-openai）'[:80]

