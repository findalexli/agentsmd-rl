#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pydantic-ai

# Idempotency guard
if grep -qF "AGENTS.md" "AGENTS.md" && grep -qF "If the user is not aware of an issue and a search doesn't turn up anything, or i" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1 +0,0 @@
-CLAUDE.md
\ No newline at end of file
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,101 @@
+Welcome to the repository for [Pydantic AI](https://ai.pydantic.dev/), an open source provider-agnostic GenAI agent framework (and LLM library) for Python, maintained by the team behind [Pydantic Validation](https://docs.pydantic.dev/) and [Pydantic Logfire](https://docs.pydantic.dev/logfire/).
+
+## Your primary responsibility is to the project and its users
+
+Being an open source library, the public API, abstractions, documentation, and the code itself _are_ the product and deserve careful consideration, as much as the functionality the library or any given change provides. This means that when implementing a feature or other change, the "how" is as important as the "what", and it's more important to ship the best solution for the project and all of its users, than to be fast.
+
+When working in this repository, you should consider yourself to primarily be working for the benefit of the project, all of its users (current and future, human and agent), and its maintainers, rather than just the specific user who happens to be driving you (or whose PR you're reviewing, whose issue you're implementing, etc).
+
+As the project has many orders of magnitude more users than maintainers, that specific user is most likely a community member who's well-intentioned and eager to contribute, but relatively unfamiliar with the code base and its patterns or standards, and they're not necessarily thinking about the bigger picture beyond the specific bug fix, feature, or other change that they're focused on.
+
+Therefore, you are the first line of defense against low-quality contributions and maintainer headaches, and you have a big role in ensuring that every contribution to this project meets or exceeds the high standards that the Pydantic brand is known and loved for:
+
+- modern, idiomatic, concise Python
+- end-to-end type-safety and test coverage
+- thoughtful, tasteful, consistent API design
+- delightful developer experience
+- comprehensive well-written documentation
+
+In other words, channel your inner Samuel Colvin. (British accent optional)
+
+## Gathering context on the task
+
+The user may not have sufficient context and understanding of the task, its solution space, and relevant tradeoffs to effectively drive a coding agent towards the version of the change that best serves the interests of the project and all of its users. (They may not even have experienced the problem or had a need for the feature themselves, only having seen an opportunity to help out.)
+
+That means that you should always start by gathering as much context as possible about the task at hand. At minimum, this means:
+
+- reading the GitHub issue/PR, using the `gh` CLI if can be (or already is) installed, or a web fetch/search tool if not
+- asking the user questions about the scope of the task, the shape they believe the solution should take, etc
+    - even if they did not specifically enable planning mode
+
+Considering that the user's input does not necessarily match what the wider user base or maintainers would prefer, you should "trust but verify" and are encouraged to do your own research to fill any gaps in your (and their) knowledge, by looking up things like:
+
+- all relevant GitHub issues and PRs
+- LLM provider API docs and SDK type definitions
+- other LLM/agent libraries' solutions to similar problems
+- Pydantic AI documentation on related features and established API patterns
+    - In particular, the docs on [agents](docs/agents.md), [dependency injection](docs/dependencies.md), [tools](docs/tools.md), [output](docs/output.md), and [message history](docs/message-history.md) are going to be relevant to many tasks.
+
+## Ensuring the task is ready for implementation
+
+If the user is not aware of an issue and a search doesn't turn up anything, or if an issue exists but the scope is insufficiently defined (e.g. there's no "obvious" solution and no maintainer input on what an acceptable solution would look like), then the task is unlikely to be ready for implementation. Any non-trivial code submitted without prior alignment with maintainers is highly unlikely to be right for the project, and more likely to be a waste of time (on all sides: user, agent, and maintainer) than to be helpful.
+
+In this case, unless the user appears to be uniquely well-suited to build a feature from scratch and submit it without (much) prior discussion (e.g. they are a maintainer or a partner submitting an integration), the most useful thing you can do to steer the user towards a good outcome for the project is to work with them on:
+
+- a clear issue description, or
+- a proposal they can submit as a comment, or
+- (only if an issue already exists) a more fleshed out plan they can submit as a PR (with just a `PLAN.md` file that can be deleted afterwards) that other users and maintainers can weigh in on ahead of implementation
+
+(Of course it's fair game for a user to generate code to gain a better understanding of the problem or experiment with different solutions, as long as the intent is not to just submit that code without first having aligned with maintainers on the approach.)
+
+(It's also worth noting that overly lengthy AI-generated issues, comments, and proposals are less likely to be helpful and more likely to be ignored than a user's attempt at explaining what they want in their own (possibly translated) words: if they are not able to, they are unlikely to be the right person to be requesting and helping implement the change.)
+
+## Philosophy
+
+Pydantic AI is meant to be a light-weight library that any Python developer who wants to work with LLMs and agents (whether simple or complex) should feel no hesitation to pull into their project. It's not meant to be everything to everyone, but it should enable people to build just about anything.
+
+As such, we prefer strong primitives, powerful abstractions, and general solutions and extension points that enable people to build things that we hadn't even thought of, over narrow solutions for specific use cases, opinionated solutions that push a particular approach to agent design that hasn't yet stood the test of time, or generally "batteries included" solutions that make the library unnecessarily bloated and less generally useful.
+
+As a specific example, any feature that could be implemented as a standalone [`AbstractToolset`](docs/toolsets.md), probably should be a separate community package rather than part of the core library.
+
+## Requirements of all contributions
+
+All changes need to:
+
+- be thoughtful and deliberate about new abstractions, public APIs, and behaviors, as every wrong-in-retrospect choice (made in a rush or with insufficient context) makes life harder for hundreds of thousands of users (and agents), and is much more difficult to change later than to do right the first time
+- be backward compatible as laid out in the [version policy](docs/version-policy.md), so that users can upgrade with confidence
+- be fully type-safe (both internally and in public API) without unnecessary `cast`s or `Any`s, so that users don't need `isinstance` checks and can trust that code that typechecks will work at runtime
+- have comprehensive tests covering 100% of code paths, favoring integration tests and real requests (using recordings and snapshots -- see below) over unit tests and mocking
+- update/add all relevant documentation, following the existing voice and patterns
+
+When you submit a PR, make sure you include the [PR template](.github/pull_request_template.md) and fill in the issue number that should be closed when the PR is merged. The "AI generated code" checkbox should always be checked manually by the user in the UI, not by the agent.
+
+## Repository structure
+
+The repo contains a `uv` workspace defining multiple Python packages:
+
+- `pydantic-ai-slim` in `pydantic_ai_slim/`: the [agent framework](docs/agents.md), including the `Agent` class and `Model` classes for each model provider/API
+    - This is a slim package with minimal dependencies and optional dependency groups for each model provider (e.g. `openai`, `anthropic`, `google`) or integration (e.g. `logfire`, `mcp`, `temporal`).
+- `pydantic-graph` in `pydantic_graph/`: the type-hint based [graph library](docs/graph.md) that powers the agent loop
+- `pydantic-evals` in `pydantic_evals/`: the [evaluation framework](docs/evals.md) for evaluating the arbitrary stochastic functions including LLMs and agents
+- `clai` in `clai/`: a [CLI](docs/cli.md) (with an optional [web UI](docs/web.md)) to chat with Pydantic AI agents
+- `pydantic-ai` defined in `pyproject.toml` at the root, bringing in the packages above as well the optional dependency groups for all model providers and select integrations.
+
+## Development workflow
+
+The project uses:
+
+- [`uv`](https://docs.astral.sh/uv/getting-started/installation/), supporting Python 3.10 through 3.13
+    - Install all dependencies with `make install`
+- `pre-commit`, can be installed with `uv tool install pre-commit`
+- `ruff` via `make lint` and `make format`
+- `pyright` via `make typecheck`
+- `pytest` in `/tests`, via `make test`, with:
+    - `inline-snapshot` for inline assertions
+    - `pytest-recording` and `vcrpy` for recording and playing back requests to model APIs
+- `mkdocs` in `/docs`, via `make docs` and `make docs-serve`, served at <https://ai.pydantic.dev>, with:
+    - `mkdocstrings-python` to generate API docs from docstrings and types
+    - `mkdocs-material` to theme the docs
+    - `tests/test_examples.py` to test all code examples in the docs (including docstrings)
+- [`logfire`](docs/logfire.md) for OTel instrumentation of Pydantic AI and `httpx`
+    - If you have access to the Logfire MCP server, you can use it to inspect agent runs, tool calls, and model requests
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,168 +0,0 @@
-# CLAUDE.md
-
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
-
-## Development Commands
-
-### Core Development Tasks
-
-- **Install dependencies**: `make install` (requires uv, pre-commit, and deno)
-- **Run all checks**: `pre-commit run --all-files`
-- **Run tests**: `make test`
-- **Build docs**: `make docs` or `make docs-serve` (local development)
-
-### Single Test Commands
-
-- **Run specific test**: `uv run pytest tests/test_agent.py::test_function_name -v`
-- **Run test file**: `uv run pytest tests/test_agent.py -v`
-- **Run with debug**: `uv run pytest tests/test_agent.py -v -s`
-
-## Project Architecture
-
-### Core Components
-
-**Agent System (`pydantic_ai_slim/pydantic_ai/agent/`)**
-- `Agent[AgentDepsT, OutputDataT]`: Main orchestrator class with generic types for dependency injection and output validation
-- Entry points: `run()`, `run_sync()`, `run_stream()` methods
-- Handles tool management, system prompts, and model interaction
-
-**Model Integration (`pydantic_ai_slim/pydantic_ai/models/`)**
-- Unified interface across providers: OpenAI, Anthropic, Google, Groq, Cohere, Mistral, Bedrock, HuggingFace
-- Model strings: `"openai:gpt-5"`, `"anthropic:claude-sonnet-4-5"`, `"google:gemini-2.5-pro"`
-- `ModelRequestParameters` for configuration, `StreamedResponse` for streaming
-
-**Graph-based Execution (`pydantic_graph/` + `_agent_graph.py`)**
-- State machine execution through: `UserPromptNode` → `ModelRequestNode` → `CallToolsNode`
-- `GraphAgentState` maintains message history and usage tracking
-- `GraphRunContext` provides execution context
-
-**Tool System (`tools.py`, `toolsets/`)**
-- `@agent.tool` decorator for function registration
-- `RunContext[AgentDepsT]` provides dependency injection in tools
-- Support for sync/async functions with automatic schema generation
-
-**Output Handling**
-- `TextOutput`: Plain text responses
-- `ToolOutput`: Structured data via tool calls
-- `NativeOutput`: Provider-specific structured output
-- `PromptedOutput`: Prompt-based structured extraction
-
-### Key Design Patterns
-
-**Dependency Injection**
-```python
-@dataclass
-class MyDeps:
-    database: DatabaseConn
-
-agent = Agent('openai:gpt-5', deps_type=MyDeps)
-
-@agent.tool
-async def get_data(ctx: RunContext[MyDeps]) -> str:
-    return await ctx.deps.database.fetch_data()
-```
-
-**Type-Safe Agents**
-```python
-class OutputModel(BaseModel):
-    result: str
-    confidence: float
-
-agent: Agent[MyDeps, OutputModel] = Agent(
-    'openai:gpt-5',
-    deps_type=MyDeps,
-    output_type=OutputModel
-)
-```
-
-## Workspace Structure
-
-This is a uv workspace with multiple packages:
-- **`pydantic_ai_slim/`**: Core framework (minimal dependencies)
-- **`pydantic_evals/`**: Evaluation system
-- **`pydantic_graph/`**: Graph execution engine
-- **`examples/`**: Example applications
-- **`clai/`**: CLI tool
-
-## Testing Strategy
-
-- **Unit tests**: `tests/` directory with comprehensive model and component coverage
-- **VCR cassettes**: `tests/cassettes/` for recorded LLM API interactions
-- **Test models**: Use `TestModel` for deterministic testing
-- **Examples testing**: `tests/test_examples.py` validates all documentation examples
-- **Multi-version testing**: Python 3.10-3.13 support
-
-## Key Configuration Files
-
-- **`pyproject.toml`**: Main workspace configuration with dependency groups
-- **`pydantic_ai_slim/pyproject.toml`**: Core package with model optional dependencies
-- **`Makefile`**: Development task automation
-- **`uv.lock`**: Locked dependencies for reproducible builds
-
-## Important Implementation Notes
-
-- **Model Provider Integration**: Each provider in `models/` directory implements the `Model` abstract base class
-- **Message System**: Vendor-agnostic message format in `messages.py` with rich content type support
-- **Streaming Architecture**: Real-time response processing with validation during streaming
-- **Error Handling**: Specific exception types with retry mechanisms at multiple levels
-- **OpenTelemetry Integration**: Built-in observability support
-
-## Documentation Development
-
-- **Local docs**: `make docs-serve` (serves at http://localhost:8000)
-- **Docs source**: `docs/` directory (MkDocs with Material theme)
-- **API reference**: Auto-generated from docstrings using mkdocstrings
-
-**macOS Note**: The docs build uses `cairosvg` for social card generation, which requires the `cairo` C library. On macOS with Homebrew, Python may fail to locate the library. Fix by setting the library path:
-```bash
-export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib"
-export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/opt/homebrew/share/pkgconfig"
-uv run mkdocs build  # or mkdocs serve
-```
-
-## Dependencies Management
-
-- **Package manager**: uv (fast Python package manager)
-- **Lock file**: `uv.lock` (commit this file)
-- **Sync command**: `make sync` to update dependencies
-- **Optional extras**: Define groups in `pyproject.toml` optional-dependencies
-
-## Best Practices
-
-This is the list of best practices for working with the codebase.
-
-### Rename a class
-
-When asked to rename a class, you need to rename the class in the code and add a deprecation warning to the old class.
-
-```python
-from typing_extensions import deprecated
-
-class NewClass: ...  # This class was renamed from OldClass.
-
-@deprecated("Use `NewClass` instead.")
-class OldClass(NewClass): ...
-```
-
-In the test suite, you MUST use the `NewClass` instead of the `OldClass`, and create a new test to verify the
-deprecation warning:
-
-```python
-def test_old_class_is_deprecated():
-    with pytest.warns(DeprecationWarning, match="Use `NewClass` instead."):
-        OldClass()
-```
-
-In the documentation, you should not have references to the old class, only the new class.
-
-### Writing documentation
-
-Always reference Python objects with the "`" (backticks) around them, and link to the API reference, for example:
-
-```markdown
-The [`Agent`][pydantic_ai.agent.Agent] class is the main entry point for creating and running agents.
-```
-
-### Coverage
-
-Every pull request MUST have 100% coverage. You can check the coverage by running `make test`.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
