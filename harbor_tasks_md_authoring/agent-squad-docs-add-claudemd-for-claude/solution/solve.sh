#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-squad

# Idempotency guard
if grep -qF "3. **`Agent`** (abstract base in `agents/agent.py` / `agents/agent.ts`) \u2014 plugga" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,77 @@
+# CLAUDE.md
+
+This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+
+## Repository shape
+
+This is a **dual-language monorepo**. The framework is published as both an npm package (`agent-squad`) and a PyPI package (`agent-squad`), with **feature parity maintained between the two**. When changing framework behavior, the equivalent change is typically expected in both trees.
+
+- [python/](python/) — Python implementation, source under [python/src/agent_squad/](python/src/agent_squad/), tests under [python/src/tests/](python/src/tests/). Requires Python >= 3.11.
+- [typescript/](typescript/) — TypeScript implementation, source under [typescript/src/](typescript/src/), tests under [typescript/tests/](typescript/tests/).
+- [examples/](examples/) — Sample apps (chat demos, FastAPI streaming, Bedrock inline agents, supervisor mode, etc.). Not built/tested by the main CI; each has its own setup.
+- [docs/](docs/) — Astro-based documentation site (deployed to `2fastlabs.github.io/agent-squad`).
+- [.github/workflows/](.github/workflows/) — CI. Python and TypeScript are tested independently, gated by `paths:` filters on `python/**` and `typescript/**` respectively.
+
+The project was previously named `multi-agent-orchestrator` (you will still see `MAOTS_VERSION` and similar legacy identifiers) and was previously hosted at `awslabs/agent-squad` before moving to `2fastlabs/agent-squad`.
+
+## Common commands
+
+### Python ([python/](python/))
+
+All commands run from the `python/` directory.
+
+```bash
+pip install -r test_requirements.txt   # install test deps (incl. ruff, pytest, moto, boto3, anthropic, openai, libsql-client, strands-agents)
+make code-quality                      # ruff check src/agent_squad
+make test                              # pytest ./src/tests/
+pytest ./src/tests/test_orchestrator.py                       # single file
+pytest ./src/tests/agents/test_bedrock_llm_agent.py::TestName # single test
+```
+
+Ruff config lives in [python/ruff.toml](python/ruff.toml) (line-length 120, target py311, only `A` and `B` rules currently enabled). Package metadata and optional-extras (`aws`, `anthropic`, `openai`, `sql`, `strands-agents`, `all`) are defined in [python/setup.cfg](python/setup.cfg).
+
+### TypeScript ([typescript/](typescript/))
+
+All commands run from the `typescript/` directory.
+
+```bash
+npm install
+npm run build           # tsc — runs `generateVersionFile` prebuild hook that reads version from package.json
+npm run lint            # eslint on src/**/*.ts and tests/**/*.ts
+npm test                # jest
+npm run coverage        # jest --coverage (this is what CI runs)
+npx jest tests/Orchestrator.test.ts                           # single file
+npx jest -t "should route"                                    # by test name
+```
+
+The `prebuild` script generates [typescript/src/common/src/version.ts](typescript/src/common/src/version.ts) from `package.json`; do not edit that file by hand.
+
+## Architecture
+
+The framework orchestrates multiple AI agents behind a single entry point. The core flow is identical across both language implementations:
+
+1. **`AgentSquad` orchestrator** ([python/src/agent_squad/orchestrator.py](python/src/agent_squad/orchestrator.py), [typescript/src/orchestrator.ts](typescript/src/orchestrator.ts)) — the top-level object users interact with. Holds a registry of agents, a classifier, a chat storage, and config. Exposes `route_request` / `routeRequest`.
+2. **`Classifier`** (in `classifiers/`) — given the user input, conversation history, and the list of registered agents' names/descriptions, picks which agent should handle the request. Implementations: `BedrockClassifier`, `AnthropicClassifier`, `OpenAIClassifier`. The orchestrator defaults to `BedrockClassifier` when available, so the `aws`/boto3 extra is effectively the default runtime assumption.
+3. **`Agent`** (abstract base in `agents/agent.py` / `agents/agent.ts`) — pluggable worker. Concrete types include `BedrockLLMAgent`, `AnthropicAgent`, `OpenAIAgent`, `AmazonBedrockAgent`, `BedrockInlineAgent`, `BedrockFlowsAgent`, `BedrockTranslatorAgent`, `LambdaAgent`, `LexBotAgent`, `ComprehendFilterAgent`, `ChainAgent`, `SupervisorAgent`, and (Python only) `StrandsAgent`. Agents support both streaming and non-streaming responses; the return type branches on `response.streaming`.
+4. **`ChatStorage`** (in `storage/`) — persists per-(user, session, agent) conversation history. Implementations: `InMemoryChatStorage` (default), `DynamoDbChatStorage`, `SqlChatStorage` (libsql/Turso). The orchestrator reads history before classification and writes both sides of the exchange after the agent responds.
+5. **`Retriever`** (in `retrievers/`) — optional RAG layer; `AmazonKBRetriever` is the built-in. Agents can be configured with a retriever to augment prompts.
+
+Two composite agents are architecturally significant:
+- **`ChainAgent`** — runs a fixed pipeline of agents where each one's output feeds the next.
+- **`SupervisorAgent`** — an "agent-as-tools" pattern: a lead agent coordinates a team of sub-agents in parallel, maintaining shared context. Can be registered directly as an agent in the classifier to build hierarchical teams.
+
+Python and TypeScript keep parallel file names (e.g. `bedrock_llm_agent.py` ↔ `bedrockLLMAgent.ts`). When adding or modifying a capability in one tree, check the other for the equivalent file.
+
+## Contributing rules enforced by CI
+
+- **Issue-first policy.** Every PR **must** be linked to an issue via `Fixes #N` / `Closes #N` / `Resolves #N` in the PR body, or via GitHub's "Link an issue" UI. The [pr-issue-link-checker.yml](.github/workflows/pr-issue-link-checker.yml) workflow is a required check and will fail the PR otherwise. When opening a PR, always include an issue reference; if none exists, an issue must be opened first.
+- Follow the PR template at [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md) (Issue Link → Summary → Changes → User experience → Checklist).
+- Python CI runs on Python 3.11, 3.12, 3.13 — avoid syntax that breaks any of those.
+- TypeScript CI runs `npm run coverage` (full Jest run) and `npm run lint`; lint must pass.
+- CI also runs a Lychee link check across the repo — broken external links in markdown will fail the build.
+
+## Working across the two implementations
+
+- The Python package exports via `agent_squad.<submodule>` (snake_case) while the TypeScript package exports from a single [typescript/src/index.ts](typescript/src/index.ts) barrel with camelCase names.
+- Python uses dataclasses + `*Options` classes (e.g. `BedrockLLMAgentOptions`) as the construction pattern; TypeScript uses plain option objects. Keep option field names consistent between the two when adding new options.
+- Optional dependencies are gated at import time in Python (`try/except ImportError` guards, see orchestrator's handling of `BedrockClassifier`). When adding a new integration, follow that pattern so installing a subset of extras still works.
PATCH

echo "Gold patch applied."
