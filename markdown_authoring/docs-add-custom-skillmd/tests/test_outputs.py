"""Behavioral checks for docs-add-custom-skillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/docs")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('src/.mintlify/skills/deep-agents/SKILL.md')
    assert 'Deep Agents is the easiest way to start building agents powered by LLMs—with built-in capabilities for task planning, file systems for context management, subagent delegation, and long-term memory. It' in text, "expected to find: " + 'Deep Agents is the easiest way to start building agents powered by LLMs—with built-in capabilities for task planning, file systems for context management, subagent delegation, and long-term memory. It'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/.mintlify/skills/deep-agents/SKILL.md')
    assert 'description: Build batteries-included agents with planning, context management, subagent delegation, and sandboxed execution. Use for complex, multi-step tasks that need built-in capabilities.' in text, "expected to find: " + 'description: Build batteries-included agents with planning, context management, subagent delegation, and sandboxed execution. Use for complex, multi-step tasks that need built-in capabilities.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/.mintlify/skills/deep-agents/SKILL.md')
    assert '- For simple tool-calling agents without planning or subagents, use [LangChain](https://docs.langchain.com/oss/langchain/overview) agents instead—lighter weight' in text, "expected to find: " + '- For simple tool-calling agents without planning or subagents, use [LangChain](https://docs.langchain.com/oss/langchain/overview) agents instead—lighter weight'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('src/.mintlify/skills/langchain/SKILL.md')
    assert 'LangChain is an open-source framework with a prebuilt agent architecture and integrations for any model or tool. Build agents and LLM-powered applications in under 10 lines of code, with integrations ' in text, "expected to find: " + 'LangChain is an open-source framework with a prebuilt agent architecture and integrations for any model or tool. Build agents and LLM-powered applications in under 10 lines of code, with integrations '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('src/.mintlify/skills/langchain/SKILL.md')
    assert 'description: Build agents with a prebuilt architecture and integrations for any model or tool. Use when creating tool-calling agents, switching model providers, or adding structured output.' in text, "expected to find: " + 'description: Build agents with a prebuilt architecture and integrations for any model or tool. Use when creating tool-calling agents, switching model providers, or adding structured output.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('src/.mintlify/skills/langchain/SKILL.md')
    assert '- For a batteries-included agent with planning, subagents, and context management, use [Deep Agents](https://docs.langchain.com/oss/deepagents/overview) instead' in text, "expected to find: " + '- For a batteries-included agent with planning, subagents, and context management, use [Deep Agents](https://docs.langchain.com/oss/deepagents/overview) instead'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('src/.mintlify/skills/langgraph/SKILL.md')
    assert 'LangGraph is a low-level orchestration framework and runtime for building, managing, and deploying long-running, stateful agents. It provides durable execution, streaming, human-in-the-loop interactio' in text, "expected to find: " + 'LangGraph is a low-level orchestration framework and runtime for building, managing, and deploying long-running, stateful agents. It provides durable execution, streaming, human-in-the-loop interactio'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('src/.mintlify/skills/langgraph/SKILL.md')
    assert 'description: Build stateful, durable agent workflows with LangGraph. Use when you need custom graph-based control flow, human-in-the-loop, persistence, or multi-agent orchestration.' in text, "expected to find: " + 'description: Build stateful, durable agent workflows with LangGraph. Use when you need custom graph-based control flow, human-in-the-loop, persistence, or multi-agent orchestration.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('src/.mintlify/skills/langgraph/SKILL.md')
    assert '- For a simple tool-calling agent, use [LangChain](https://docs.langchain.com/oss/langchain/overview) agents instead—less boilerplate for common patterns' in text, "expected to find: " + '- For a simple tool-calling agent, use [LangChain](https://docs.langchain.com/oss/langchain/overview) agents instead—less boilerplate for common patterns'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('src/.mintlify/skills/langsmith/SKILL.md')
    assert 'LangSmith is a framework-agnostic platform for building, debugging, and deploying AI agents and LLM applications. Trace requests, evaluate outputs, test prompts, and manage deployments all in one plac' in text, "expected to find: " + 'LangSmith is a framework-agnostic platform for building, debugging, and deploying AI agents and LLM applications. Trace requests, evaluate outputs, test prompts, and manage deployments all in one plac'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('src/.mintlify/skills/langsmith/SKILL.md')
    assert '- To build agent logic or LLM pipelines, use [LangChain](https://docs.langchain.com/oss/langchain/overview), [LangGraph](https://docs.langchain.com/oss/langgraph/overview), or [Deep Agents](https://do' in text, "expected to find: " + '- To build agent logic or LLM pipelines, use [LangChain](https://docs.langchain.com/oss/langchain/overview), [LangGraph](https://docs.langchain.com/oss/langgraph/overview), or [Deep Agents](https://do'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('src/.mintlify/skills/langsmith/SKILL.md')
    assert 'description: Trace, evaluate, and deploy AI agents and LLM applications with LangSmith. Use when adding observability, running evaluations, engineering prompts, or deploying agents to production.' in text, "expected to find: " + 'description: Trace, evaluate, and deploy AI agents and LLM applications with LangSmith. Use when adding observability, running evaluations, engineering prompts, or deploying agents to production.'[:80]

