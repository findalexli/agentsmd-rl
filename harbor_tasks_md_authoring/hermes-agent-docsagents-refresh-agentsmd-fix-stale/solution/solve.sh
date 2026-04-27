#!/usr/bin/env bash
set -euo pipefail

cd /workspace/hermes-agent

# Idempotency guard
if grep -qF "**Agent-level tools** (todo, memory): intercepted by `run_agent.py` before `hand" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -5,78 +5,61 @@ Instructions for AI coding assistants and developers working on the hermes-agent
 ## Development Environment
 
 ```bash
-source venv/bin/activate  # ALWAYS activate before running Python
+# Prefer .venv; fall back to venv if that's what your checkout has.
+source .venv/bin/activate   # or: source venv/bin/activate
 ```
 
+`scripts/run_tests.sh` probes `.venv` first, then `venv`, then
+`$HOME/.hermes/hermes-agent/venv` (for worktrees that share a venv with the
+main checkout).
+
 ## Project Structure
 
+File counts shift constantly — don't treat the tree below as exhaustive.
+The canonical source is the filesystem. The notes call out the load-bearing
+entry points you'll actually edit.
+
 ```
 hermes-agent/
-├── run_agent.py          # AIAgent class — core conversation loop
+├── run_agent.py          # AIAgent class — core conversation loop (~12k LOC)
 ├── model_tools.py        # Tool orchestration, discover_builtin_tools(), handle_function_call()
 ├── toolsets.py           # Toolset definitions, _HERMES_CORE_TOOLS list
-├── cli.py                # HermesCLI class — interactive CLI orchestrator
+├── cli.py                # HermesCLI class — interactive CLI orchestrator (~11k LOC)
 ├── hermes_state.py       # SessionDB — SQLite session store (FTS5 search)
-├── agent/                # Agent internals
-│   ├── prompt_builder.py     # System prompt assembly
-│   ├── context_compressor.py # Auto context compression
-│   ├── prompt_caching.py     # Anthropic prompt caching
-│   ├── auxiliary_client.py   # Auxiliary LLM client (vision, summarization)
-│   ├── model_metadata.py     # Model context lengths, token estimation
-│   ├── models_dev.py         # models.dev registry integration (provider-aware context)
-│   ├── display.py            # KawaiiSpinner, tool preview formatting
-│   ├── skill_commands.py     # Skill slash commands (shared CLI/gateway)
-│   └── trajectory.py         # Trajectory saving helpers
-├── hermes_cli/           # CLI subcommands and setup
-│   ├── main.py           # Entry point — all `hermes` subcommands
-│   ├── config.py         # DEFAULT_CONFIG, OPTIONAL_ENV_VARS, migration
-│   ├── commands.py       # Slash command definitions + SlashCommandCompleter
-│   ├── callbacks.py      # Terminal callbacks (clarify, sudo, approval)
-│   ├── setup.py          # Interactive setup wizard
-│   ├── skin_engine.py    # Skin/theme engine — CLI visual customization
-│   ├── skills_config.py  # `hermes skills` — enable/disable skills per platform
-│   ├── tools_config.py   # `hermes tools` — enable/disable tools per platform
-│   ├── skills_hub.py     # `/skills` slash command (search, browse, install)
-│   ├── models.py         # Model catalog, provider model lists
-│   ├── model_switch.py   # Shared /model switch pipeline (CLI + gateway)
-│   └── auth.py           # Provider credential resolution
-├── tools/                # Tool implementations (one file per tool)
-│   ├── registry.py       # Central tool registry (schemas, handlers, dispatch)
-│   ├── approval.py       # Dangerous command detection
-│   ├── terminal_tool.py  # Terminal orchestration
-│   ├── process_registry.py # Background process management
-│   ├── file_tools.py     # File read/write/search/patch
-│   ├── web_tools.py      # Web search/extract (Parallel + Firecrawl)
-│   ├── browser_tool.py   # Browserbase browser automation
-│   ├── code_execution_tool.py # execute_code sandbox
-│   ├── delegate_tool.py  # Subagent delegation
-│   ├── mcp_tool.py       # MCP client (~1050 lines)
+├── hermes_constants.py   # get_hermes_home(), display_hermes_home() — profile-aware paths
+├── hermes_logging.py     # setup_logging() — agent.log / errors.log / gateway.log (profile-aware)
+├── batch_runner.py       # Parallel batch processing
+├── agent/                # Agent internals (provider adapters, memory, caching, compression, etc.)
+├── hermes_cli/           # CLI subcommands, setup wizard, plugins loader, skin engine
+├── tools/                # Tool implementations — auto-discovered via tools/registry.py
 │   └── environments/     # Terminal backends (local, docker, ssh, modal, daytona, singularity)
-├── gateway/              # Messaging platform gateway
-│   ├── run.py            # Main loop, slash commands, message dispatch
-│   ├── session.py        # SessionStore — conversation persistence
-│   └── platforms/        # Adapters: telegram, discord, slack, whatsapp, homeassistant, signal, qqbot
+├── gateway/              # Messaging gateway — run.py + session.py + platforms/
+│   ├── platforms/        # Adapter per platform (telegram, discord, slack, whatsapp,
+│   │                     #   homeassistant, signal, matrix, mattermost, email, sms,
+│   │                     #   dingtalk, wecom, weixin, feishu, qqbot, bluebubbles,
+│   │                     #   webhook, api_server, ...). See ADDING_A_PLATFORM.md.
+│   └── builtin_hooks/    # Always-registered gateway hooks (boot-md, ...)
+├── plugins/              # Plugin system (see "Plugins" section below)
+│   ├── memory/           # Memory-provider plugins (honcho, mem0, supermemory, ...)
+│   ├── context_engine/   # Context-engine plugins
+│   └── <others>/         # Dashboard, image-gen, disk-cleanup, examples, ...
+├── optional-skills/      # Heavier/niche skills shipped but NOT active by default
+├── skills/               # Built-in skills bundled with the repo
 ├── ui-tui/               # Ink (React) terminal UI — `hermes --tui`
-│   ├── src/entry.tsx        # TTY gate + render()
-│   ├── src/app.tsx          # Main state machine and UI
-│   ├── src/gatewayClient.ts # Child process + JSON-RPC bridge
-│   ├── src/app/             # Decomposed app logic (event handler, slash handler, stores, hooks)
-│   ├── src/components/      # Ink components (branding, markdown, prompts, pickers, etc.)
-│   ├── src/hooks/           # useCompletion, useInputHistory, useQueue, useVirtualHistory
-│   └── src/lib/             # Pure helpers (history, osc52, text, rpc, messages)
+│   └── src/              # entry.tsx, app.tsx, gatewayClient.ts + app/components/hooks/lib
 ├── tui_gateway/          # Python JSON-RPC backend for the TUI
-│   ├── entry.py             # stdio entrypoint
-│   ├── server.py            # RPC handlers and session logic
-│   ├── render.py            # Optional rich/ANSI bridge
-│   └── slash_worker.py      # Persistent HermesCLI subprocess for slash commands
 ├── acp_adapter/          # ACP server (VS Code / Zed / JetBrains integration)
-├── cron/                 # Scheduler (jobs.py, scheduler.py)
+├── cron/                 # Scheduler — jobs.py, scheduler.py
 ├── environments/         # RL training environments (Atropos)
-├── tests/                # Pytest suite (~3000 tests)
-└── batch_runner.py       # Parallel batch processing
+├── scripts/              # run_tests.sh, release.py, auxiliary scripts
+├── website/              # Docusaurus docs site
+└── tests/                # Pytest suite (~15k tests across ~700 files as of Apr 2026)
 ```
 
-**User config:** `~/.hermes/config.yaml` (settings), `~/.hermes/.env` (API keys)
+**User config:** `~/.hermes/config.yaml` (settings), `~/.hermes/.env` (API keys only).
+**Logs:** `~/.hermes/logs/` — `agent.log` (INFO+), `errors.log` (WARNING+),
+`gateway.log` when running the gateway. Profile-aware via `get_hermes_home()`.
+Browse with `hermes logs [--follow] [--level ...] [--session ...]`.
 
 ## File Dependency Chain
 
@@ -94,20 +77,30 @@ run_agent.py, cli.py, batch_runner.py, environments/
 
 ## AIAgent Class (run_agent.py)
 
+The real `AIAgent.__init__` takes ~60 parameters (credentials, routing, callbacks,
+session context, budget, credential pool, etc.). The signature below is the
+minimum subset you'll usually touch — read `run_agent.py` for the full list.
+
 ```python
 class AIAgent:
     def __init__(self,
-        model: str = "anthropic/claude-opus-4.6",
-        max_iterations: int = 90,
+        base_url: str = None,
+        api_key: str = None,
+        provider: str = None,
+        api_mode: str = None,              # "chat_completions" | "codex_responses" | ...
+        model: str = "",                   # empty → resolved from config/provider later
+        max_iterations: int = 90,          # tool-calling iterations (shared with subagents)
         enabled_toolsets: list = None,
         disabled_toolsets: list = None,
         quiet_mode: bool = False,
         save_trajectories: bool = False,
-        platform: str = None,           # "cli", "telegram", etc.
+        platform: str = None,              # "cli", "telegram", etc.
         session_id: str = None,
         skip_context_files: bool = False,
         skip_memory: bool = False,
-        # ... plus provider, api_mode, callbacks, routing params
+        credential_pool=None,
+        # ... plus callbacks, thread/user/chat IDs, iteration_budget, fallback_model,
+        # checkpoints config, prefill_messages, service_tier, reasoning_config, etc.
     ): ...
 
     def chat(self, message: str) -> str:
@@ -120,10 +113,13 @@ class AIAgent:
 
 ### Agent Loop
 
-The core loop is inside `run_conversation()` — entirely synchronous:
+The core loop is inside `run_conversation()` — entirely synchronous, with
+interrupt checks, budget tracking, and a one-turn grace call:
 
 ```python
-while api_call_count < self.max_iterations and self.iteration_budget.remaining > 0:
+while (api_call_count < self.max_iterations and self.iteration_budget.remaining > 0) \
+        or self._budget_grace_call:
+    if self._interrupt_requested: break
     response = client.chat.completions.create(model=model, messages=messages, tools=tool_schemas)
     if response.tool_calls:
         for tool_call in response.tool_calls:
@@ -134,7 +130,8 @@ while api_call_count < self.max_iterations and self.iteration_budget.remaining >
         return response.content
 ```
 
-Messages follow OpenAI format: `{"role": "system/user/assistant/tool", ...}`. Reasoning content is stored in `assistant_msg["reasoning"]`.
+Messages follow OpenAI format: `{"role": "system/user/assistant/tool", ...}`.
+Reasoning content is stored in `assistant_msg["reasoning"]`.
 
 ---
 
@@ -280,17 +277,21 @@ The registry handles schema collection, dispatch, availability checking, and err
 
 **State files**: If a tool stores persistent state (caches, logs, checkpoints), use `get_hermes_home()` for the base directory — never `Path.home() / ".hermes"`. This ensures each profile gets its own state.
 
-**Agent-level tools** (todo, memory): intercepted by `run_agent.py` before `handle_function_call()`. See `todo_tool.py` for the pattern.
+**Agent-level tools** (todo, memory): intercepted by `run_agent.py` before `handle_function_call()`. See `tools/todo_tool.py` for the pattern.
 
 ---
 
 ## Adding Configuration
 
 ### config.yaml options:
 1. Add to `DEFAULT_CONFIG` in `hermes_cli/config.py`
-2. Bump `_config_version` (currently 5) to trigger migration for existing users
+2. Bump `_config_version` (check the current value at the top of `DEFAULT_CONFIG`)
+   ONLY if you need to actively migrate/transform existing user config
+   (renaming keys, changing structure). Adding a new key to an existing
+   section is handled automatically by the deep-merge and does NOT require
+   a version bump.
 
-### .env variables:
+### .env variables (SECRETS ONLY — API keys, tokens, passwords):
 1. Add to `OPTIONAL_ENV_VARS` in `hermes_cli/config.py` with metadata:
 ```python
 "NEW_API_KEY": {
@@ -302,13 +303,29 @@ The registry handles schema collection, dispatch, availability checking, and err
 },
 ```
 
-### Config loaders (two separate systems):
+Non-secret settings (timeouts, thresholds, feature flags, paths, display
+preferences) belong in `config.yaml`, not `.env`. If internal code needs an
+env var mirror for backward compatibility, bridge it from `config.yaml` to
+the env var in code (see `gateway_timeout`, `terminal.cwd` → `TERMINAL_CWD`).
+
+### Config loaders (three paths — know which one you're in):
 
 | Loader | Used by | Location |
 |--------|---------|----------|
-| `load_cli_config()` | CLI mode | `cli.py` |
-| `load_config()` | `hermes tools`, `hermes setup` | `hermes_cli/config.py` |
-| Direct YAML load | Gateway | `gateway/run.py` |
+| `load_cli_config()` | CLI mode | `cli.py` — merges CLI-specific defaults + user YAML |
+| `load_config()` | `hermes tools`, `hermes setup`, most CLI subcommands | `hermes_cli/config.py` — merges `DEFAULT_CONFIG` + user YAML |
+| Direct YAML load | Gateway runtime | `gateway/run.py` + `gateway/config.py` — reads user YAML raw |
+
+If you add a new key and the CLI sees it but the gateway doesn't (or vice
+versa), you're on the wrong loader. Check `DEFAULT_CONFIG` coverage.
+
+### Working directory:
+- **CLI** — uses the process's current directory (`os.getcwd()`).
+- **Messaging** — uses `terminal.cwd` from `config.yaml`. The gateway bridges this
+  to the `TERMINAL_CWD` env var for child tools. **`MESSAGING_CWD` has been
+  removed** — the config loader prints a deprecation warning if it's set in
+  `.env`. Same for `TERMINAL_CWD` in `.env`; the canonical setting is
+  `terminal.cwd` in `config.yaml`.
 
 ---
 
@@ -401,7 +418,95 @@ Activate with `/skin cyberpunk` or `display.skin: cyberpunk` in config.yaml.
 
 ---
 
+## Plugins
+
+Hermes has two plugin surfaces. Both live under `plugins/` in the repo so
+repo-shipped plugins can be discovered alongside user-installed ones in
+`~/.hermes/plugins/` and pip-installed entry points.
+
+### General plugins (`hermes_cli/plugins.py` + `plugins/<name>/`)
+
+`PluginManager` discovers plugins from `~/.hermes/plugins/`, `./.hermes/plugins/`,
+and pip entry points. Each plugin exposes a `register(ctx)` function that
+can:
+
+- Register Python-callback lifecycle hooks:
+  `pre_tool_call`, `post_tool_call`, `pre_llm_call`, `post_llm_call`,
+  `on_session_start`, `on_session_end`
+- Register new tools via `ctx.register_tool(...)`
+- Register CLI subcommands via `ctx.register_cli_command(...)` — the
+  plugin's argparse tree is wired into `hermes` at startup so
+  `hermes <pluginname> <subcmd>` works with no change to `main.py`
+
+Hooks are invoked from `model_tools.py` (pre/post tool) and `run_agent.py`
+(lifecycle). **Discovery timing pitfall:** `discover_plugins()` only runs
+as a side effect of importing `model_tools.py`. Code paths that read plugin
+state without importing `model_tools.py` first must call `discover_plugins()`
+explicitly (it's idempotent).
+
+### Memory-provider plugins (`plugins/memory/<name>/`)
+
+Separate discovery system for pluggable memory backends. Current built-in
+providers include **honcho, mem0, supermemory, byterover, hindsight,
+holographic, openviking, retaindb**.
+
+Each provider implements the `MemoryProvider` ABC (see `agent/memory_provider.py`)
+and is orchestrated by `agent/memory_manager.py`. Lifecycle hooks include
+`sync_turn(turn_messages)`, `prefetch(query)`, `shutdown()`, and optional
+`post_setup(hermes_home, config)` for setup-wizard integration.
+
+**CLI commands via `plugins/memory/<name>/cli.py`:** if a memory plugin
+defines `register_cli(subparser)`, `discover_plugin_cli_commands()` finds
+it at argparse setup time and wires it into `hermes <plugin>`. The
+framework only exposes CLI commands for the **currently active** memory
+provider (read from `memory.provider` in config.yaml), so disabled
+providers don't clutter `hermes --help`.
+
+**Rule (Teknium, May 2026):** plugins MUST NOT modify core files
+(`run_agent.py`, `cli.py`, `gateway/run.py`, `hermes_cli/main.py`, etc.).
+If a plugin needs a capability the framework doesn't expose, expand the
+generic plugin surface (new hook, new ctx method) — never hardcode
+plugin-specific logic into core. PR #5295 removed 95 lines of hardcoded
+honcho argparse from `main.py` for exactly this reason.
+
+### Dashboard / context-engine / image-gen plugin directories
+
+`plugins/context_engine/`, `plugins/image_gen/`, `plugins/example-dashboard/`,
+etc. follow the same pattern (ABC + orchestrator + per-plugin directory).
+Context engines plug into `agent/context_engine.py`; image-gen providers
+into `agent/image_gen_provider.py`.
+
+---
+
+## Skills
+
+Two parallel surfaces:
+
+- **`skills/`** — built-in skills shipped and loadable by default.
+  Organized by category directories (e.g. `skills/github/`, `skills/mlops/`).
+- **`optional-skills/`** — heavier or niche skills shipped with the repo but
+  NOT active by default. Installed explicitly via
+  `hermes skills install official/<category>/<skill>`. Adapter lives in
+  `tools/skills_hub.py` (`OptionalSkillSource`). Categories include
+  `autonomous-ai-agents`, `blockchain`, `communication`, `creative`,
+  `devops`, `email`, `health`, `mcp`, `migration`, `mlops`, `productivity`,
+  `research`, `security`, `web-development`.
+
+When reviewing skill PRs, check which directory they target — heavy-dep or
+niche skills belong in `optional-skills/`.
+
+### SKILL.md frontmatter
+
+Standard fields: `name`, `description`, `version`, `platforms`
+(OS-gating list: `[macos]`, `[linux, macos]`, ...),
+`metadata.hermes.tags`, `metadata.hermes.category`,
+`metadata.hermes.config` (config.yaml settings the skill needs — stored
+under `skills.config.<key>`, prompted during setup, injected at load time).
+
+---
+
 ## Important Policies
+
 ### Prompt Caching Must Not Break
 
 Hermes-Agent ensures caching remains valid throughout a conversation. **Do NOT implement changes that would:**
@@ -411,9 +516,10 @@ Hermes-Agent ensures caching remains valid throughout a conversation. **Do NOT i
 
 Cache-breaking forces dramatically higher costs. The ONLY time we alter context is during context compression.
 
-### Working Directory Behavior
-- **CLI**: Uses current directory (`.` → `os.getcwd()`)
-- **Messaging**: Uses `MESSAGING_CWD` env var (default: home directory)
+Slash commands that mutate system-prompt state (skills, tools, memory, etc.)
+must be **cache-aware**: default to deferred invalidation (change takes
+effect next session), with an opt-in `--now` flag for immediate
+invalidation. See `/skills install --now` for the canonical pattern.
 
 ### Background Process Notifications (Gateway)
 
@@ -435,7 +541,7 @@ Hermes supports **profiles** — multiple fully isolated instances, each with it
 `HERMES_HOME` directory (config, API keys, memory, sessions, skills, gateway, etc.).
 
 The core mechanism: `_apply_profile_override()` in `hermes_cli/main.py` sets
-`HERMES_HOME` before any module imports. All 119+ references to `get_hermes_home()`
+`HERMES_HOME` before any module imports. All `get_hermes_home()` references
 automatically scope to the active profile.
 
 ### Rules for profile-safe code
@@ -492,8 +598,12 @@ Use `get_hermes_home()` from `hermes_constants` for code paths. Use `display_her
 for user-facing print/log messages. Hardcoding `~/.hermes` breaks profiles — each profile
 has its own `HERMES_HOME` directory. This was the source of 5 bugs fixed in PR #3575.
 
-### DO NOT use `simple_term_menu` for interactive menus
-Rendering bugs in tmux/iTerm2 — ghosting on scroll. Use `curses` (stdlib) instead. See `hermes_cli/tools_config.py` for the pattern.
+### DO NOT introduce new `simple_term_menu` usage
+Existing call sites in `hermes_cli/main.py` remain for legacy fallback only;
+the preferred UI is curses (stdlib) because `simple_term_menu` has
+ghost-duplication rendering bugs in tmux/iTerm2 with arrow keys. New
+interactive menus must use `hermes_cli/curses_ui.py` — see
+`hermes_cli/tools_config.py` for the canonical pattern.
 
 ### DO NOT use `\033[K` (ANSI erase-to-EOL) in spinner/display code
 Leaks as literal `?[K` text under `prompt_toolkit`'s `patch_stdout`. Use space-padding: `f"\r{line}{' ' * pad}"`.
@@ -504,6 +614,30 @@ Leaks as literal `?[K` text under `prompt_toolkit`'s `patch_stdout`. Use space-p
 ### DO NOT hardcode cross-tool references in schema descriptions
 Tool schema descriptions must not mention tools from other toolsets by name (e.g., `browser_navigate` saying "prefer web_search"). Those tools may be unavailable (missing API keys, disabled toolset), causing the model to hallucinate calls to non-existent tools. If a cross-reference is needed, add it dynamically in `get_tool_definitions()` in `model_tools.py` — see the `browser_navigate` / `execute_code` post-processing blocks for the pattern.
 
+### The gateway has TWO message guards — both must bypass approval/control commands
+When an agent is running, messages pass through two sequential guards:
+(1) **base adapter** (`gateway/platforms/base.py`) queues messages in
+`_pending_messages` when `session_key in self._active_sessions`, and
+(2) **gateway runner** (`gateway/run.py`) intercepts `/stop`, `/new`,
+`/queue`, `/status`, `/approve`, `/deny` before they reach
+`running_agent.interrupt()`. Any new command that must reach the runner
+while the agent is blocked (e.g. approval prompts) MUST bypass BOTH
+guards and be dispatched inline, not via `_process_message_background()`
+(which races session lifecycle).
+
+### Squash merges from stale branches silently revert recent fixes
+Before squash-merging a PR, ensure the branch is up to date with `main`
+(`git fetch origin main && git reset --hard origin/main` in the worktree,
+then re-apply the PR's commits). A stale branch's version of an unrelated
+file will silently overwrite recent fixes on main when squashed. Verify
+with `git diff HEAD~1..HEAD` after merging — unexpected deletions are a
+red flag.
+
+### Don't wire in dead code without E2E validation
+Unused code that was never shipped was dead for a reason. Before wiring an
+unused module into a live code path, E2E test the real resolution chain
+with actual imports (not mocks) against a temp `HERMES_HOME`.
+
 ### Tests must not write to `~/.hermes/`
 The `_isolate_hermes_home` autouse fixture in `tests/conftest.py` redirects `HERMES_HOME` to a temp dir. Never hardcode `~/.hermes/` paths in tests.
 
@@ -559,7 +693,7 @@ If you can't use the wrapper (e.g. on Windows or inside an IDE that shells
 pytest directly), at minimum activate the venv and pass `-n 4`:
 
 ```bash
-source venv/bin/activate
+source .venv/bin/activate   # or: source venv/bin/activate
 python -m pytest tests/ -q -n 4
 ```
 
PATCH

echo "Gold patch applied."
