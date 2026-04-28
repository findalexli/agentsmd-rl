#!/usr/bin/env bash
set -euo pipefail

cd /workspace/docs

# Idempotency guard
if grep -qF "Deep Agents is the easiest way to start building agents powered by LLMs\u2014with bui" "src/.mintlify/skills/deep-agents/SKILL.md" && grep -qF "LangChain is an open-source framework with a prebuilt agent architecture and int" "src/.mintlify/skills/langchain/SKILL.md" && grep -qF "LangGraph is a low-level orchestration framework and runtime for building, manag" "src/.mintlify/skills/langgraph/SKILL.md" && grep -qF "LangSmith is a framework-agnostic platform for building, debugging, and deployin" "src/.mintlify/skills/langsmith/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/.mintlify/skills/deep-agents/SKILL.md b/src/.mintlify/skills/deep-agents/SKILL.md
@@ -0,0 +1,105 @@
+---
+name: deep-agents
+description: Build batteries-included agents with planning, context management, subagent delegation, and sandboxed execution. Use for complex, multi-step tasks that need built-in capabilities.
+license: MIT
+compatibility: Python 3.10+, Node.js 20+. Requires a model that supports tool calling.
+metadata:
+  author: langchain-ai
+  version: "1.0"
+---
+
+# Deep Agents
+
+Deep Agents is the easiest way to start building agents powered by LLMs—with built-in capabilities for task planning, file systems for context management, subagent delegation, and long-term memory. It is an "agent harness" built on [LangChain](https://docs.langchain.com/oss/langchain/overview) core building blocks and the [LangGraph](https://docs.langchain.com/oss/langgraph/overview) runtime.
+
+## When to use
+
+Use Deep Agents when you need to:
+- **Build agents fast** with sensible defaults and minimal configuration
+- **Handle complex, multi-step tasks** that benefit from automatic planning
+- **Manage context** with a built-in virtual filesystem for large inputs
+- **Delegate subtasks** to specialized subagents
+- **Run code safely** in sandboxed execution environments
+- **Use a terminal agent** via the Deep Agents CLI
+
+## When NOT to use
+
+- For simple tool-calling agents without planning or subagents, use [LangChain](https://docs.langchain.com/oss/langchain/overview) agents instead—lighter weight
+- For custom graph-based orchestration with explicit control flow, use [LangGraph](https://docs.langchain.com/oss/langgraph/overview) directly
+- Deep Agents is the **highest-level abstraction**—it trades flexibility for convenience
+
+## Install
+
+```bash
+# Python
+pip install deepagents
+
+# JavaScript/TypeScript
+npm install deepagents langchain @langchain/core
+```
+
+## Quick reference
+
+### Create a deep agent
+
+```python
+# pip install deepagents langchain-anthropic
+from deepagents import create_deep_agent
+
+def get_weather(city: str) -> str:
+    """Get weather for a given city."""
+    return f"It's always sunny in {city}!"
+
+agent = create_deep_agent(
+    model="anthropic:claude-sonnet-4-6",
+    tools=[get_weather],
+    system_prompt="You are a helpful assistant",
+)
+
+result = agent.invoke(
+    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]}
+)
+```
+
+### Use the CLI
+
+```bash
+# Install the CLI
+pip install deepagents-cli
+
+# Run an interactive terminal agent
+deepagents
+```
+
+### Built-in capabilities
+
+| Capability | Description |
+|-----------|-------------|
+| Planning | Automatic task decomposition for complex requests |
+| File system | Virtual filesystem for reading, writing, and managing context |
+| Subagents | Spawn child agents for parallel subtask execution |
+| Context management | Automatic context compression for long conversations |
+| Sandboxed execution | Run code in isolated environments (Modal, Runloop, Daytona) |
+| Protocols | ACP, MCP, and A2A support for interoperability |
+
+## Key documentation
+
+- [Overview](https://docs.langchain.com/oss/deepagents/overview)—What Deep Agents is and how it compares to LangChain and LangGraph
+- [Quickstart](https://docs.langchain.com/oss/deepagents/quickstart)—Build your first deep agent
+- [Customization](https://docs.langchain.com/oss/deepagents/customization)—Configure models, tools, and behavior
+- [Context engineering](https://docs.langchain.com/oss/deepagents/context-engineering)—Manage context for complex tasks
+- [Subagents](https://docs.langchain.com/oss/deepagents/subagents)—Delegate work to child agents
+- [Sandboxes](https://docs.langchain.com/oss/deepagents/sandboxes)—Run code in isolated environments
+- [CLI](https://docs.langchain.com/oss/deepagents/cli/overview)—Terminal agent interface
+- [Deploy](https://docs.langchain.com/oss/deepagents/deploy)—Deploy to production
+
+## API reference
+
+For SDK class and method details, use the [LangChain API Reference](https://reference.langchain.com) site:
+- MCP server: `https://reference.langchain.com/mcp`
+
+## Related skills
+
+- **langchain**—Core building blocks that Deep Agents is built on
+- **langgraph**—Runtime that powers Deep Agents' durable execution
+- **langsmith**—Trace, evaluate, and deploy your deep agents
diff --git a/src/.mintlify/skills/langchain/SKILL.md b/src/.mintlify/skills/langchain/SKILL.md
@@ -0,0 +1,121 @@
+---
+name: langchain
+description: Build agents with a prebuilt architecture and integrations for any model or tool. Use when creating tool-calling agents, switching model providers, or adding structured output.
+license: MIT
+compatibility: Python 3.10+, Node.js 20+
+metadata:
+  author: langchain-ai
+  version: "1.0"
+---
+
+# LangChain
+
+LangChain is an open-source framework with a prebuilt agent architecture and integrations for any model or tool. Build agents and LLM-powered applications in under 10 lines of code, with integrations for OpenAI, Anthropic, Google, and hundreds more.
+
+## When to use
+
+Use LangChain when you need to:
+- **Build tool-calling agents** with `create_agent()` and a prebuilt agent loop
+- **Switch model providers** without changing application code via `init_chat_model()`
+- **Add structured output** to parse LLM responses into typed objects
+- **Integrate with any model or tool** using LangChain's provider packages
+- **Use middleware** for cross-cutting concerns like rate limiting and caching
+
+## When NOT to use
+
+- For complex multi-step workflows with custom control flow, use [LangGraph](https://docs.langchain.com/oss/langgraph/overview) instead
+- For a batteries-included agent with planning, subagents, and context management, use [Deep Agents](https://docs.langchain.com/oss/deepagents/overview) instead
+- LangChain provides the **core building blocks**; LangGraph adds orchestration; Deep Agents adds high-level capabilities on top
+
+## Install
+
+```bash
+# Python
+pip install -U langchain
+
+# JavaScript/TypeScript
+npm install langchain @langchain/core
+```
+
+Install a provider integration:
+
+```bash
+# Python
+pip install -U langchain-openai       # or langchain-anthropic, langchain-google-genai
+
+# JavaScript/TypeScript
+npm install @langchain/openai         # or @langchain/anthropic, @langchain/google-genai
+```
+
+## Quick reference
+
+### Create an agent
+
+```python
+from langchain.agents import create_agent
+
+def get_weather(city: str) -> str:
+    """Get weather for a given city."""
+    return f"It's always sunny in {city}!"
+
+agent = create_agent(
+    model="openai:gpt-5.4",
+    tools=[get_weather],
+    system_prompt="You are a helpful assistant",
+)
+
+result = agent.invoke(
+    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]}
+)
+```
+
+### Initialize a chat model
+
+```python
+from langchain.chat_models import init_chat_model
+
+# Switch providers by changing the string
+model = init_chat_model("openai:gpt-5.4")
+model = init_chat_model("anthropic:claude-opus-4-6")
+model = init_chat_model("google_genai:gemini-2.5-flash-lite")
+```
+
+### Define a tool
+
+```python
+from langchain.tools import tool
+
+@tool
+def search(query: str) -> str:
+    """Search the web for information."""
+    return "search results"
+```
+
+## Gotchas
+
+1. **Snake_case tool names**—Tool function names must be valid Python identifiers. Use `get_weather`, not `get-weather`.
+2. **Reserved parameters**—Do not name tool parameters `type`, `name`, or `description` as these conflict with the tool schema.
+3. **Provider packages**—Models live in separate packages (e.g., `langchain-openai`). The base `langchain` package does not include providers.
+4. **Model string format**—Use `"provider:model-name"` format with `init_chat_model()` (e.g., `"openai:gpt-5.4"`).
+
+## Key documentation
+
+- [Overview](https://docs.langchain.com/oss/langchain/overview)—What LangChain is and how to get started
+- [Quickstart](https://docs.langchain.com/oss/langchain/quickstart)—Build your first agent
+- [Agents](https://docs.langchain.com/oss/langchain/agents)—Prebuilt agent architecture
+- [Models](https://docs.langchain.com/oss/langchain/models)—Chat models and provider integrations
+- [Tools](https://docs.langchain.com/oss/langchain/tools)—Define and use tools
+- [Structured output](https://docs.langchain.com/oss/langchain/structured-output)—Parse LLM responses into typed objects
+- [MCP integration](https://docs.langchain.com/oss/langchain/mcp)—Use Model Context Protocol servers as tools
+
+## API reference
+
+For SDK class and method details, use the [LangChain API Reference](https://reference.langchain.com) site:
+- Browse: `https://reference.langchain.com/python/langchain-core`
+- MCP server: `https://reference.langchain.com/mcp`
+
+## Related skills
+
+- **langgraph**—Low-level orchestration for stateful, durable agent workflows
+- **deep-agents**—Batteries-included agent harness built on LangChain
+- **langsmith**—Trace, evaluate, and deploy your LangChain agents
diff --git a/src/.mintlify/skills/langgraph/SKILL.md b/src/.mintlify/skills/langgraph/SKILL.md
@@ -0,0 +1,117 @@
+---
+name: langgraph
+description: Build stateful, durable agent workflows with LangGraph. Use when you need custom graph-based control flow, human-in-the-loop, persistence, or multi-agent orchestration.
+license: MIT
+compatibility: Python 3.10+, Node.js 20+
+metadata:
+  author: langchain-ai
+  version: "1.0"
+---
+
+# LangGraph
+
+LangGraph is a low-level orchestration framework and runtime for building, managing, and deploying long-running, stateful agents. It provides durable execution, streaming, human-in-the-loop interactions, and time-travel debugging.
+
+## When to use
+
+Use LangGraph when you need to:
+- **Design custom agent workflows** with explicit graph-based control flow
+- **Add durable execution** so agents survive failures and restarts
+- **Implement human-in-the-loop** with interrupts and approval steps
+- **Build multi-agent systems** with state shared across agents
+- **Stream intermediate results** from long-running agent tasks
+- **Time-travel debug** by replaying agent execution from any checkpoint
+
+## When NOT to use
+
+- For a simple tool-calling agent, use [LangChain](https://docs.langchain.com/oss/langchain/overview) agents instead—less boilerplate for common patterns
+- For a batteries-included agent with planning and subagents, use [Deep Agents](https://docs.langchain.com/oss/deepagents/overview) instead
+- LangGraph is the **orchestration layer**—use it when you need fine-grained control over agent behavior
+
+## Install
+
+```bash
+# Python
+pip install -U langgraph
+
+# JavaScript/TypeScript
+npm install @langchain/langgraph @langchain/core
+```
+
+## Quick reference
+
+### Graph API (recommended for most use cases)
+
+```python
+from langgraph.graph import StateGraph, MessagesState, START, END
+
+def my_node(state: MessagesState):
+    return {"messages": [{"role": "ai", "content": "hello world"}]}
+
+graph = StateGraph(MessagesState)
+graph.add_node(my_node)
+graph.add_edge(START, "my_node")
+graph.add_edge("my_node", END)
+graph = graph.compile()
+
+result = graph.invoke(
+    {"messages": [{"role": "user", "content": "Hello!"}]}
+)
+```
+
+### Functional API (for simple pipelines)
+
+```python
+from langgraph.func import entrypoint, task
+
+@task
+def step_one(input: str) -> str:
+    return f"processed: {input}"
+
+@entrypoint()
+def pipeline(input: str) -> str:
+    return step_one(input).result()
+```
+
+### Add human-in-the-loop
+
+```python
+from langgraph.types import interrupt
+
+def human_approval(state: MessagesState):
+    answer = interrupt({"question": "Approve this action?"})
+    return {"messages": [{"role": "user", "content": answer}]}
+```
+
+## Key concepts
+
+| Concept | Description |
+|---------|-------------|
+| `StateGraph` | Define nodes and edges that form your agent's control flow |
+| `MessagesState` | Built-in state schema for chat-based agents |
+| `compile()` | Compile a graph builder into an executable graph |
+| `interrupt()` | Pause execution and wait for human input |
+| Checkpointer | Persist state for durable execution and time-travel |
+| Graph API vs Functional API | Graph API for complex workflows; Functional API for linear pipelines |
+
+## Key documentation
+
+- [Overview](https://docs.langchain.com/oss/langgraph/overview)—What LangGraph is and when to use it
+- [Quickstart](https://docs.langchain.com/oss/langgraph/quickstart)—Build your first graph
+- [Persistence](https://docs.langchain.com/oss/langgraph/persistence)—Add memory and durable execution
+- [Interrupts](https://docs.langchain.com/oss/langgraph/interrupts)—Human-in-the-loop patterns
+- [Streaming](https://docs.langchain.com/oss/langgraph/streaming)—Stream intermediate results
+- [Graph API](https://docs.langchain.com/oss/langgraph/graph-api)—Define nodes, edges, and state
+- [Deploy](https://docs.langchain.com/oss/langgraph/deploy)—Deploy to production with LangSmith
+
+## API reference
+
+For SDK class and method details, use the [LangChain API Reference](https://reference.langchain.com) site:
+- Browse: `https://reference.langchain.com/python/langgraph`
+- MCP server: `https://reference.langchain.com/mcp`
+
+## Related skills
+
+- **langchain**—Core building blocks for models, tools, and simple agents
+- **deep-agents**—High-level agent harness built on LangGraph
+- **langsmith**—Trace, evaluate, and deploy your LangGraph agents
diff --git a/src/.mintlify/skills/langsmith/SKILL.md b/src/.mintlify/skills/langsmith/SKILL.md
@@ -0,0 +1,89 @@
+---
+name: langsmith
+description: Trace, evaluate, and deploy AI agents and LLM applications with LangSmith. Use when adding observability, running evaluations, engineering prompts, or deploying agents to production.
+license: MIT
+compatibility: Framework-agnostic. Works with LangChain, LangGraph, Deep Agents, OpenAI Agents SDK, CrewAI, Pydantic AI, and more.
+metadata:
+  author: langchain-ai
+  version: "1.0"
+---
+
+# LangSmith
+
+LangSmith is a framework-agnostic platform for building, debugging, and deploying AI agents and LLM applications. Trace requests, evaluate outputs, test prompts, and manage deployments all in one place at [smith.langchain.com](https://smith.langchain.com).
+
+## When to use
+
+Use LangSmith when you need to:
+- **Trace and debug** LLM calls, agent steps, retrieval, and tool use
+- **Evaluate** LLM outputs with automated or human-in-the-loop scoring
+- **Engineer prompts** with a visual playground and version control
+- **Deploy agents** to production with the LangGraph-based agent server
+- **Monitor** production systems with dashboards, alerts, and cost tracking
+
+## When NOT to use
+
+- To build agent logic or LLM pipelines, use [LangChain](https://docs.langchain.com/oss/langchain/overview), [LangGraph](https://docs.langchain.com/oss/langgraph/overview), or [Deep Agents](https://docs.langchain.com/oss/deepagents/overview) instead
+- LangSmith is the **platform layer** that complements these frameworks
+
+## Quick setup
+
+Set two environment variables to enable tracing from any supported framework:
+
+```bash
+export LANGSMITH_TRACING=true
+export LANGSMITH_API_KEY="your-api-key"  # from smith.langchain.com/settings
+```
+
+### Install the SDK
+
+```bash
+# Python
+pip install langsmith
+
+# JavaScript/TypeScript
+npm install langsmith
+```
+
+### Verify tracing
+
+```python
+from langsmith import traceable
+
+@traceable
+def my_function(query: str) -> str:
+    # Your LLM logic here—all calls inside are traced automatically
+    return "result"
+```
+
+## Core capabilities
+
+| Capability | Description |
+|-----------|-------------|
+| Observability | Trace every step of your LLM app with automatic or manual instrumentation |
+| Evaluation | Run evaluations with code, LLM-as-judge, or composite evaluators |
+| Prompt engineering | Create, version, and test prompts in a visual playground |
+| Agent deployment | Deploy LangGraph agents with streaming, human-in-the-loop, and durable execution |
+| Monitoring | Dashboards, alerts, and cost tracking for production workloads |
+
+## Key documentation
+
+- [Overview](https://docs.langchain.com/langsmith/home)—Get started with LangSmith
+- [Observability quickstart](https://docs.langchain.com/langsmith/observability-quickstart)—Add tracing in minutes
+- [Evaluation quickstart](https://docs.langchain.com/langsmith/evaluation-quickstart)—Run your first evaluation
+- [Prompt engineering quickstart](https://docs.langchain.com/langsmith/prompt-engineering-quickstart)—Iterate on prompts
+- [Deployment quickstart](https://docs.langchain.com/langsmith/deployment-quickstart)—Deploy an agent
+- [Integrations](https://docs.langchain.com/langsmith/integrations)—Connect your framework or provider
+- [Create account & API key](https://docs.langchain.com/langsmith/create-account-api-key)—Account setup
+
+## API reference
+
+For SDK class and method details, use the [LangChain API Reference](https://reference.langchain.com) site:
+- Browse: `https://reference.langchain.com/python/langsmith`
+- MCP server: `https://reference.langchain.com/mcp`
+
+## Related skills
+
+- **langchain**—Build agents with prebuilt architecture and model integrations
+- **langgraph**—Orchestrate stateful, durable agent workflows
+- **deep-agents**—Batteries-included agent harness with planning and subagents
PATCH

echo "Gold patch applied."
