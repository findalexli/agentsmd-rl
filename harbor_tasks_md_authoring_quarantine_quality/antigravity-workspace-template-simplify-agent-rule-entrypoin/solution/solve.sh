#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-workspace-template

# Idempotency guard
if grep -qF "There should be one-- and preferably only one --obvious way to do it." "AGENTS.md" && grep -qF "3. Load project context from `CONTEXT.md`, `.antigravity/`, and `mission.md` onl" "CLAUDE.md" && grep -qF "There should be one-- and preferably only one --obvious way to do it." "cli/src/ag_cli/templates/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,94 +1,19 @@
-<!-- OPENSPEC:START -->
-# OpenSpec Instructions
-
-These instructions are for AI assistants working in this project.
-
-Always open `@/openspec/AGENTS.md` when the request:
-- Mentions planning or proposals (words like proposal, spec, change, plan)
-- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
-- Sounds ambiguous and you need the authoritative spec before coding
-
-Use `@/openspec/AGENTS.md` to learn:
-- How to create and apply change proposals
-- Spec format and conventions
-- Project structure and guidelines
-
-Keep this managed block so 'openspec update' can refresh the instructions.
-
-<!-- OPENSPEC:END -->
-
-# Repository Agent Guide
-
-This repo is the Antigravity Workspace Template (Python). Follow the local
-rules in `.cursorrules`, `.antigravity/rules.md`, and `CONTEXT.md`.
-
-## Must-Read Files (Before Any Work)
-- `mission.md` (required by `.antigravity/rules.md`)
-- `.antigravity/rules.md` (core agent behavior + coding standards)
-- `CONTEXT.md` (project conventions and architecture)
-- `.cursorrules` (points to the Antigravity rules engine)
-- `openspec/AGENTS.md` (when planning/spec/change work is requested)
-
-## Artifact-First Workflow
-- For non-trivial tasks, create a plan file in `artifacts/plan_[task_id].md`.
-- Store test/log output in `artifacts/logs/`.
-- If UI is modified, include a screenshot artifact.
-- Keep artifacts lightweight and deterministic.
-
-## Build / Lint / Test Commands
-### Setup
-- `python3 -m venv venv && source venv/bin/activate`
-- `pip install -e ./cli -e './engine[dev]'`
-
-### Run Knowledge Hub
-- `ag refresh --workspace .`
-- `ag ask "How does this project work?" --workspace .`
-- Engine-only entrypoints: `ag-refresh`, `ag-ask`, `ag-mcp`
-
-### Docker
-- `docker compose up --build`
-
-### Tests
-- Run all tests: `pytest engine/tests cli/tests`
-- Run engine tests: `pytest engine/tests/`
-- Run CLI tests: `pytest cli/tests/`
-- Run a single engine test file: `pytest engine/tests/test_hub_pipeline.py -v`
-- Run a single CLI test file: `pytest cli/tests/test_hub_discovery.py -v`
-- Coverage: `pytest --cov=antigravity_engine engine/tests/`
-- Sandbox tests: `pytest engine/tests/test_local_sandbox.py engine/tests/test_microsandbox_sandbox.py engine/tests/test_factory.py -v`
-
-### Lint / Format
-- No repo-level linter/formatter configs were found.
-- Follow existing style and PEP 8; avoid reformatting unrelated code.
-- Optional sanity check for tools: `python -m py_compile antigravity_engine/tools/*.py`
-
-### CI
-- GitHub Actions installs `engine/` and `cli/` separately, runs both test suites, and verifies the published CLI entrypoints (`.github/workflows/test.yml`).
-
-## Code Style (Python)
-- **Type hints are required** for all function signatures.
-- **Docstrings are required** for functions/classes; use Google-style format.
-  Include `Args:`, `Returns:`, and `Raises:` where applicable.
-- **Use Pydantic** for data models and settings (`pydantic`, `pydantic-settings`).
-- **External API calls** must be wrapped in tools under `antigravity_engine/tools/`.
-- **Use `<thought>` blocks** for non-trivial logic (see `antigravity_engine/tools/example_tool.py`).
-- **Imports**: stdlib → third-party → local (`antigravity_engine.`) with blank lines between.
-- **Formatting**: 4-space indent, one statement per line, keep lines readable.
-- **Strings**: prefer f-strings for interpolation; keep quote style consistent.
-
-## Architecture & Patterns
-- **Tool discovery**: public functions in `antigravity_engine/tools/*.py` are auto-loaded.
-  Keep tool functions small, pure when possible, and well-documented.
-- **MCP integration**: optional via `mcp_servers.json` and `.env`.
-- **Context injection**: `.context/` markdown files are auto-loaded.
-- **Memory**: JSON-based memory via `MemoryManager` (`antigravity_engine/memory.py`).
-
-## Testing & Reliability
-- Use `pytest` fixtures and `assert` statements (see `tests/`).
-- Keep tests deterministic; avoid external network calls.
-- Store test logs in `artifacts/logs/` per Antigravity rules.
-
-## Notes for Agents
-- The template expects a “Think → Act → Reflect” workflow.
-- Avoid destructive commands (`rm -rf`, etc.).
-- If a request implies a spec/proposal, follow OpenSpec flow before coding.
+Beautiful is better than ugly.
+Explicit is better than implicit.
+Simple is better than complex.
+Complex is better than complicated.
+Flat is better than nested.
+Sparse is better than dense.
+Readability counts.
+Special cases aren't special enough to break the rules.
+Although practicality beats purity.
+Errors should never pass silently.
+Unless explicitly silenced.
+In the face of ambiguity, refuse the temptation to guess.
+There should be one-- and preferably only one --obvious way to do it.
+Although that way may not be obvious at first unless you're Dutch.
+Now is better than never.
+Although never is often better than *right* now.
+If the implementation is hard to explain, it's a bad idea.
+If the implementation is easy to explain, it may be a good idea.
+Namespaces are one honking great idea -- let's do more of those!
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,6 +1,8 @@
 # CLAUDE.md
 
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+Claude Code bootstrap file.
+
+Primary behavior rules live in `AGENTS.md`.
 
 <!-- OPENSPEC:START -->
 # OpenSpec Instructions
@@ -21,103 +23,7 @@ Keep this managed block so 'openspec update' can refresh the instructions.
 
 <!-- OPENSPEC:END -->
 
-## What This Project Is
-
-**Antigravity Workspace Template** — a production-grade starter kit for building autonomous AI agents. Core philosophy: an agent's capability ceiling equals the quality of context it can read. Everything meaningful is encoded in files (not IDE plugins), making agents portable across any AI IDE (Cursor, Claude Code, Gemini CLI, etc.).
-
-Built on Google Gemini (optimized for Gemini 2.0 Flash) but architecturally LLM-agnostic. Python 3.10+.
-
-## Common Commands
-
-### Engine Setup
-```bash
-python3 -m venv venv && source venv/bin/activate
-pip install -e ./cli -e './engine[dev]'
-```
-
-### Run Knowledge Hub
-```bash
-ag refresh --workspace .
-ag ask "How does this project work?" --workspace .
-ag-refresh --workspace .
-ag-ask "How does auth work?"
-ag-mcp --workspace .
-```
-
-### Tests
-```bash
-# All tests
-pytest engine/tests cli/tests
-
-# Engine tests only
-pytest engine/tests/
-
-# CLI tests only
-pytest cli/tests/
-```
-
-### CLI (ag init)
-```bash
-pip install git+https://github.com/study8677/antigravity-workspace-template.git#subdirectory=cli
-ag init <target_dir>
-```
-
-### Docker
-```bash
-docker-compose up --build
-docker build -t antigravity-agent:latest .
-docker build -f Dockerfile.sandbox -t antigravity-sandbox:latest .
-```
-
-CI installs `engine/` and `cli/` separately, runs both test suites, and verifies the published CLI entrypoints on Python 3.12 (`.github/workflows/test.yml`).
-
-## Architecture
-
-### Two-Package Monorepo
-
-- **`engine/`** — Core agent runtime. The main codebase.
-- **`cli/`** — Lightweight `ag init` command (Typer + Rich) that injects cognitive architecture files into target projects. Separate `pyproject.toml` with Hatchling.
-
-### Engine Internals (`engine/antigravity_engine/`)
-
-**Agent core:** `agent.py` contains `GeminiAgent` implementing the Think-Act-Reflect loop. Config in `config.py` (Pydantic Settings, workspace-aware, loads from `.env`).
-
-**Tools** (`tools/`): Public functions are **auto-discovered** at startup and exposed to the LLM. Every tool function requires type hints on all arguments/return and a Google-style docstring with `Args:`, `Returns:`, `Raises:` sections — this is how the agent discovers and understands tools.
-
-**Memory** (`memory.py`): Markdown-first storage (`memory/agent_memory.md` + `memory/agent_summary.md`). Uses recursive summarization to compress history and avoid token limits.
-
-**MCP** (`mcp_client.py`): `MCPClientManager` connects to external MCP servers defined in root `mcp_servers.json`. Supports stdio/http/sse transports. Tool names prefixed with `mcp_`. Enabled via `MCP_ENABLED=true` in `.env`.
-
-**Sandbox** (`sandbox/`): Code execution via `CodeSandbox` protocol. Factory pattern selects Local (direct Python) or Microsandbox (remote HTTP with resource limits) based on `SANDBOX_TYPE` env var.
-
-**Swarm** (`swarm.py`): Multi-agent orchestration using Router-Worker pattern. Specialist agents in `agents/` (BaseAgent → CoderAgent, ReviewerAgent, ResearcherAgent, RouterAgent). Inter-agent communication via `MessageBus`.
-
-**Skills** (`skills/`): Modular capabilities auto-loaded and registered into the agent's tool registry.
-
-### Key Directories Outside Engine
-
-- **`openspec/`** — Spec-driven development. 3-stage workflow: Create proposal → Implement → Archive. See `openspec/AGENTS.md` for details. Skip proposals for bug fixes, typos, non-breaking dep updates.
-- **`artifacts/`** — Agent output: plans (`plan_*.md`), logs, error journal (`error_journal.md`), screenshots.
-- **`.context/`** — Injected context: `coding_style.md` (Python style guide), `system_prompt.md`.
-- **`memory/`** — Persistent markdown memory files.
-- **`docs/`** — Multilingual documentation (en, zh, es).
-
-## Code Conventions
-
-- **Type hints mandatory** on all function signatures
-- **Google-style docstrings** required on all tool functions (enables agent auto-discovery)
-- **Pydantic** for data models and settings
-- **Tool isolation:** All external interactions (API calls, I/O) go in `engine/antigravity_engine/tools/`
-- **Stateless tools:** Context passed via arguments, not global state
-- **Artifact-first:** Tasks produce plans/logs in `artifacts/` before coding begins
-- **Error journal:** Mistakes logged to `artifacts/error_journal.md` with prevention rules (self-evolution pattern)
-
-## Environment Variables
-
-Configured via `.env` at project root. Key variables:
-- `GOOGLE_API_KEY` — Gemini API key
-- `GEMINI_MODEL` — Model name (default: `gemini-2.0-flash-exp`)
-- `MCP_ENABLED` — Toggle MCP integration (default: `false`)
-- `SANDBOX_TYPE` — `local` or `microsandbox`
-- `WORKSPACE_PATH` — Project root (or use `--workspace` flag)
-- `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL` — OpenAI-compatible fallback (default: local Ollama)
+Before acting:
+1. Read `AGENTS.md`.
+2. For spec or proposal work, follow `openspec/AGENTS.md`.
+3. Load project context from `CONTEXT.md`, `.antigravity/`, and `mission.md` only as needed.
diff --git a/cli/src/ag_cli/templates/AGENTS.md b/cli/src/ag_cli/templates/AGENTS.md
@@ -1,38 +1,19 @@
-# AGENTS.md
-
-This is the authoritative rulebook for AI agents in this repository.
-
-## Mission
-- Align work with `mission.md` when present.
-- Keep a clear separation between static behavior rules (this file) and dynamic project knowledge (`.antigravity/*`).
-
-## Mandatory Workflow: Plan -> Trace -> Act -> Verify
-1. Plan non-trivial work before coding.
-2. Execute in small, verifiable steps.
-3. Leave a trace for meaningful changes and decisions.
-4. Verify claims with real command output before reporting success.
-
-## Coding Constraints
-- Use type hints on function signatures.
-- Add docstrings for public functions/classes.
-- Do not silently swallow exceptions.
-- Keep changes scoped; avoid unrelated refactors.
-
-## Safety Rules
-- Never commit secrets, credentials, or keys.
-- Never force-push to `main`/`master`.
-- Never perform destructive actions without confirmation.
-
-## Context Loading Order
-1. Read this file first.
-2. Read dynamic context from `.antigravity/`:
-   - `.antigravity/conventions.md`
-   - `.antigravity/structure.md`
-   - `.antigravity/knowledge_graph.md` (if present)
-   - `.antigravity/decisions/log.md`
-   - `.antigravity/memory/`
-3. Read `CONTEXT.md` as a quick context index.
-4. Read `mission.md` for project-specific intent (if present).
-
-## Notes For IDE Bootstraps
-IDE-specific files (`CLAUDE.md`, `.cursorrules`, `.clinerules`, `.windsurfrules`, `.github/copilot-instructions.md`) are thin entrypoint shims that should defer to this file.
+Beautiful is better than ugly.
+Explicit is better than implicit.
+Simple is better than complex.
+Complex is better than complicated.
+Flat is better than nested.
+Sparse is better than dense.
+Readability counts.
+Special cases aren't special enough to break the rules.
+Although practicality beats purity.
+Errors should never pass silently.
+Unless explicitly silenced.
+In the face of ambiguity, refuse the temptation to guess.
+There should be one-- and preferably only one --obvious way to do it.
+Although that way may not be obvious at first unless you're Dutch.
+Now is better than never.
+Although never is often better than *right* now.
+If the implementation is hard to explain, it's a bad idea.
+If the implementation is easy to explain, it may be a good idea.
+Namespaces are one honking great idea -- let's do more of those!
PATCH

echo "Gold patch applied."
