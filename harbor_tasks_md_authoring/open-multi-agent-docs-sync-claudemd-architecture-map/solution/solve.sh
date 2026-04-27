#!/usr/bin/env bash
set -euo pipefail

cd /workspace/open-multi-agent

# Idempotency guard
if grep -qF "`bash`, `file_read`, `file_write`, `file_edit`, `grep`, `glob` \u2014 registered via " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -10,14 +10,16 @@ npm run dev            # Watch mode compilation
 npm run lint           # Type-check only (tsc --noEmit)
 npm test               # Run all tests (vitest run)
 npm run test:watch     # Vitest watch mode
+npm run test:coverage  # Vitest with v8 coverage
+npm run test:e2e       # E2E suite (requires RUN_E2E=1, real API keys)
 node dist/cli/oma.js help   # After build: shell/CI CLI (`oma` when installed via npm bin)
 ```
 
-Tests live in `tests/` (vitest). Examples in `examples/` are standalone scripts requiring API keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`). CLI usage and JSON schemas: `docs/cli.md`.
+Tests live in `tests/` (vitest); E2E suite under `tests/e2e/`. Examples in `examples/` are standalone scripts requiring API keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.) and are organized by intent: `basics/`, `cookbook/`, `patterns/`, `providers/`, `integrations/`, `production/`, with shared `fixtures/`. CLI usage and JSON schemas: `docs/cli.md`.
 
 ## Architecture
 
-ES module TypeScript framework for multi-agent orchestration. Three runtime dependencies: `@anthropic-ai/sdk`, `openai`, `zod`.
+ES module TypeScript framework for multi-agent orchestration. Three runtime dependencies: `@anthropic-ai/sdk`, `openai`, `zod`. Optional peer deps `@google/genai` (Gemini) and `@modelcontextprotocol/sdk` (MCP) are loaded lazily so users only install what they use; the three-dependency promise covers `dependencies` only.
 
 ### Core Execution Flow
 
@@ -42,13 +44,17 @@ This is the framework's key feature. When `runTeam()` is called:
 |-------|-------|----------------|
 | Orchestrator | `orchestrator/orchestrator.ts`, `orchestrator/scheduler.ts` | Top-level API, task decomposition, coordinator pattern |
 | Team | `team/team.ts`, `team/messaging.ts` | Agent roster, MessageBus (point-to-point + broadcast), SharedMemory binding |
-| Agent | `agent/agent.ts`, `agent/runner.ts`, `agent/pool.ts`, `agent/structured-output.ts` | Agent lifecycle (idle→running→completed/error), conversation loop, concurrency pool with Semaphore, structured output validation |
+| Agent | `agent/agent.ts`, `agent/runner.ts`, `agent/pool.ts`, `agent/structured-output.ts`, `agent/loop-detector.ts` | Agent lifecycle (idle→running→completed/error), conversation loop, concurrency pool with Semaphore, structured output validation, sliding-window loop detection |
 | Task | `task/queue.ts`, `task/task.ts` | Dependency-aware queue, auto-unblock on completion, cascade failure to dependents |
-| Tool | `tool/framework.ts`, `tool/executor.ts`, `tool/built-in/` | `defineTool()` with Zod schemas, ToolRegistry, parallel batch execution with concurrency semaphore |
-| LLM | `llm/adapter.ts`, `llm/anthropic.ts`, `llm/openai.ts` | `LLMAdapter` interface (`chat` + `stream`), factory `createAdapter()` |
+| Tool | `tool/framework.ts`, `tool/executor.ts`, `tool/mcp.ts`, `tool/text-tool-extractor.ts`, `tool/built-in/` | `defineTool()` with Zod schemas, ToolRegistry, parallel batch execution with concurrency semaphore, MCP integration, fallback text-format tool-call extraction for local models |
+| LLM | `llm/adapter.ts` + per-provider files (`anthropic`, `openai`, `azure-openai`, `gemini`, `grok`, `deepseek`, `minimax`, `qiniu`, `copilot`) + `openai-common.ts` | `LLMAdapter` interface (`chat` + `stream`); async `createAdapter()` factory imports the chosen adapter lazily so unused SDKs aren't loaded; `baseURL` parameter targets OpenAI-compatible servers (Ollama, vLLM, LM Studio) |
 | Memory | `memory/shared.ts`, `memory/store.ts` | Namespaced key-value store (`agentName/key`), markdown summary injection into prompts. Custom backends via `TeamConfig.sharedMemoryStore` (any `MemoryStore` impl); `sharedMemory: true` uses the default in-process store |
+| Dashboard | `dashboard/render-team-run-dashboard.ts`, `dashboard/layout-tasks.ts` | Pure HTML renderer for the post-run team task DAG (no I/O) |
+| CLI | `cli/oma.ts` | Shell/CI entry; built to `dist/cli/oma.js` and exposed as the `oma` npm bin |
+| Utils | `utils/semaphore.ts`, `utils/tokens.ts`, `utils/keywords.ts`, `utils/trace.ts` | Concurrency primitive, token accounting, keyword helpers, trace plumbing |
+| Errors | `errors.ts` | Shared error types |
 | Types | `types.ts` | All interfaces in one file to avoid circular deps |
-| Exports | `index.ts` | Public API surface |
+| Exports | `index.ts` (root, `'open-multi-agent'`), `mcp.ts` (subpath, `'open-multi-agent/mcp'`) | Public API surface; MCP integration is a separate entry point so non-MCP users don't pay the import cost |
 
 ### Agent Conversation Loop (AgentRunner)
 
@@ -74,7 +80,19 @@ Optional `maxRetries`, `retryDelayMs`, `retryBackoff` on task config (used via `
 
 ### Built-in Tools
 
-`bash`, `file_read`, `file_write`, `file_edit`, `grep`, `glob` — registered via `registerBuiltInTools(registry)`. `delegate_to_agent` is opt-in (`registerBuiltInTools(registry, { includeDelegateTool: true })`) and only wired up inside pool workers by `runTeam`/`runTasks` — see "Agent Delegation" below.
+`bash`, `file_read`, `file_write`, `file_edit`, `grep`, `glob` — registered via `registerBuiltInTools(registry)`. `grep` and `glob` share a recursive directory walker in `tool/built-in/fs-walk.ts` (with a `SKIP_DIRS` set for `.git`, `node_modules`, `dist`, etc.) so their filtering rules stay consistent. `delegate_to_agent` is opt-in (`registerBuiltInTools(registry, { includeDelegateTool: true })`) and only wired up inside pool workers by `runTeam`/`runTasks` — see "Agent Delegation" below.
+
+### Local Model Support
+
+`tool/text-tool-extractor.ts` is a safety-net fallback for OpenAI-compatible local servers (Ollama thinking-model bug, vLLM, LM Studio) that emit tool calls as plain text instead of native `tool_calls` blocks. It recognises raw JSON, markdown-fenced JSON, Hermes-style `<tool_call>` tags, and JSON leaked inside unclosed `<think>` tags. Native `tool_calls` from the server always win; this only runs when none are present.
+
+### MCP Integration
+
+`connectMCPTools()` (in `tool/mcp.ts`) bridges Model Context Protocol servers into the `ToolRegistry`. Imported lazily and exposed via the dedicated `open-multi-agent/mcp` package subpath (`src/mcp.ts`) so users who don't need MCP don't load `@modelcontextprotocol/sdk`.
+
+### Loop Detection
+
+Optional `LoopDetectionConfig` on the agent runner triggers `agent/loop-detector.ts`, a sliding-window detector that hashes tool-call signatures (with sorted JSON keys) and text outputs to catch agents stuck repeating the same actions across turns.
 
 ### Agent Delegation
 
@@ -92,4 +110,4 @@ The delegated run's `AgentRunResult.tokenUsage` is surfaced via `ToolResult.meta
 
 ### Adding an LLM Adapter
 
-Implement `LLMAdapter` interface with `chat(messages, options)` and `stream(messages, options)`, then register in `createAdapter()` factory in `src/llm/adapter.ts`.
+Implement `LLMAdapter` interface with `chat(messages, options)` and `stream(messages, options)`, add the provider name to the `SupportedProvider` union, then register a new `case` in the `createAdapter()` factory in `src/llm/adapter.ts`. Use a dynamic `await import('./your-provider.js')` so the SDK only loads when that provider is requested. OpenAI-compatible providers should accept the `baseURL` parameter and reuse helpers from `openai-common.ts`.
PATCH

echo "Gold patch applied."
