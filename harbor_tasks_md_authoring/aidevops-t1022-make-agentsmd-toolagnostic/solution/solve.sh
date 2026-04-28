#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aidevops

# Idempotency guard
if grep -qF "**Session memory monitoring + respawn** (t264, t264.1): Long-running Claude Code" ".agents/AGENTS.md" && grep -qF "- Primary: `~/.config/Claude/Claude.json`, `~/.config/Claude/agent/`" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/AGENTS.md b/.agents/AGENTS.md
@@ -5,11 +5,11 @@ mode: subagent
 
 **New to aidevops?** Type `/onboarding` to get started with an interactive setup wizard.
 
-**Supported tools:** [OpenCode](https://opencode.ai/) (TUI, Desktop, and Extension for Zed/VSCode) is the only tested and supported AI coding tool for aidevops. The `opencode` CLI is used for headless worker dispatch, supervisor orchestration, and companion subagent spawning. aidevops is also available in the Claude marketplace.
+**Supported tools:** [Claude Code](https://Claude.ai/) (TUI, Desktop, and Extension for Zed/VSCode) is the only tested and supported AI coding tool for aidevops. The `Claude` CLI is used for headless worker dispatch, supervisor orchestration, and companion subagent spawning. aidevops is also available in the Claude marketplace.
 
 **Mission**: Maximise dev-ops efficiency and ROI — maximum value for the user's time and money. Self-heal, self-improve, and grow capabilities through highest-leverage tooling. See `prompts/build.txt` for the full mission statement.
 
-**Runtime identity**: You are an AI DevOps agent powered by the aidevops framework. When asked about your identity, use the app name from the version check output (e.g., "running in OpenCode") - do not guess or assume based on system prompt content. MCP tools like `claude-code-mcp` are auxiliary integrations, not your identity.
+**Runtime identity**: You are an AI DevOps agent powered by the aidevops framework. When asked about your identity, use the app name from the version check output - do not guess or assume based on system prompt content. MCP tools like `claude-code-mcp` are auxiliary integrations, not your identity.
 
 **Primary agent**: Build+ is the unified coding agent for planning and implementation. It detects intent automatically:
 - "What do you think..." / "How should we..." → Deliberation mode (research, discuss)
@@ -75,7 +75,7 @@ Never skip testing. Never declare work "done" without verification. The full-loo
 
 ## Terminal Capabilities
 
-Full PTY access: run any CLI (`vim`, `psql`, `ssh`, `htop`, dev servers, `opencode -p "subtask"`). Long-running: use `&`/`nohup`/`tmux`. Parallel AI: `tools/ai-assistants/opencode-server.md`.
+Full PTY access: run any CLI (`vim`, `psql`, `ssh`, `htop`, dev servers, `Claude -p "subtask"`). Long-running: use `&`/`nohup`/`tmux`. Parallel AI: `tools/ai-assistants/opencode-server.md`.
 
 ---
 
@@ -257,7 +257,7 @@ worktree-helper.sh add feature/x  # Fallback
 
 ## Autonomous Orchestration
 
-**CLI**: `opencode` is the ONLY supported CLI for worker dispatch. Never use `claude` CLI.
+**CLI**: `Claude` is the ONLY supported CLI for worker dispatch. Never use `claude` CLI.
 
 **Supervisor** (`supervisor-helper.sh`): Manages parallel task execution with SQLite state machine.
 
@@ -288,7 +288,7 @@ supervisor-helper.sh status <batch-id>
 
 **Cron pulse is mandatory** for autonomous operation. Without it, the supervisor is passive and requires manual `pulse` calls. The pulse cycle: check workers -> evaluate outcomes -> dispatch next -> cleanup.
 
-**Session memory monitoring + respawn** (t264, t264.1): Long-running OpenCode/Bun sessions accumulate WebKit malloc dirty pages that are never returned to the OS (25GB+ observed). Phase 11 of the pulse cycle checks the parent session's `phys_footprint` when a batch wave completes (no running/queued tasks). If memory exceeds `SUPERVISOR_SELF_MEM_LIMIT` (default: 8192MB), it saves a checkpoint, logs the respawn event to `~/.aidevops/logs/respawn-history.log`, and exits cleanly for the next cron pulse to start fresh. Use `supervisor-helper.sh mem-check` to inspect memory and `supervisor-helper.sh respawn-history` to review respawn patterns.
+**Session memory monitoring + respawn** (t264, t264.1): Long-running Claude Code/Bun sessions accumulate WebKit malloc dirty pages that are never returned to the OS (25GB+ observed). Phase 11 of the pulse cycle checks the parent session's `phys_footprint` when a batch wave completes (no running/queued tasks). If memory exceeds `SUPERVISOR_SELF_MEM_LIMIT` (default: 8192MB), it saves a checkpoint, logs the respawn event to `~/.aidevops/logs/respawn-history.log`, and exits cleanly for the next cron pulse to start fresh. Use `supervisor-helper.sh mem-check` to inspect memory and `supervisor-helper.sh respawn-history` to review respawn patterns.
 
 **Full docs**: `tools/ai-assistants/headless-dispatch.md`, `supervisor-helper.sh help`
 
@@ -404,7 +404,7 @@ Development → @code-standards → /code-simplifier → /linters-local → /pr
 
 Import community skills: `aidevops skill add <source>` (→ `*-skill.md` suffix)
 
-**Cross-tool**: Claude marketplace plugin, Agent Skills (SKILL.md), OpenCode agents, manual AGENTS.md reference.
+**Cross-tool**: Claude marketplace plugin, Agent Skills (SKILL.md), Claude Code agents, manual AGENTS.md reference.
 
 **Full docs**: `scripts/commands/add-skill.md`
 
diff --git a/AGENTS.md b/AGENTS.md
@@ -9,7 +9,7 @@
 - **Repo**: `~/Git/aidevops/`
 
 **AI Tool Config Paths**:
-- Primary: `~/.config/opencode/opencode.json`, `~/.config/opencode/agent/`
+- Primary: `~/.config/Claude/Claude.json`, `~/.config/Claude/agent/`
 - Companion CLI: `~/.claude/`, `~/.claude/settings.json`
 
 **Development Commands**:
PATCH

echo "Gold patch applied."
