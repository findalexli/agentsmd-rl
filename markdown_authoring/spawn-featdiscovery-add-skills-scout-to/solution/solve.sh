#!/usr/bin/env bash
set -euo pipefail

cd /workspace/spawn

# Idempotency guard
if grep -qF "Research and maintain the `skills` section of `manifest.json`. Skills are agent-" ".claude/rules/discovery.md" && grep -qF "Research the best skills, MCP servers, and agent-specific configurations for eac" ".claude/skills/setup-agent-team/discovery-team-prompt.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/rules/discovery.md b/.claude/rules/discovery.md
@@ -73,7 +73,22 @@ Check `gh issue list --repo OpenRouterTeam/spawn --state open` for user requests
 - If something is already implemented, close the issue with a note
 - If a bug is reported, fix it
 
-## 5. Extend tests
+## 5. Curate skills catalog
+
+Research and maintain the `skills` section of `manifest.json`. Skills are agent-specific capabilities pre-installed on VMs via `--beta skills`.
+
+Three types:
+- **MCP servers** — npm packages giving agents tool access (GitHub, Playwright, databases)
+- **Agent Skills** — SKILL.md files following the Agent Skills standard (agentskills.io)
+- **Agent configs** — native config files unlocking agent features (Cursor rules, OpenClaw SOUL.md)
+
+When adding a skill:
+1. Verify the npm package exists and starts: `npm view PACKAGE version && timeout 5 npx -y PACKAGE`
+2. Document prerequisites (apt packages, Chrome, API keys)
+3. Mark OAuth-requiring skills as `"headless_compatible": false`
+4. Only add actively maintained packages (updated in last 6 months)
+
+## 6. Extend tests
 
 Tests use Bun's built-in test runner (`bun:test`). When adding a new cloud or agent:
 - Add unit tests in `packages/cli/src/__tests__/` with mocked fetch/prompts
diff --git a/.claude/skills/setup-agent-team/discovery-team-prompt.md b/.claude/skills/setup-agent-team/discovery-team-prompt.md
@@ -242,9 +242,92 @@ Every issue created by the discovery team MUST have the `discovery-team` label.
 - **LABEL**: Every issue MUST include `discovery-team` label
 - Only implement when upvote threshold (50+) is met
 
+## Phase 3: Skills Discovery
+
+### Skills Scout (spawn 1)
+
+Research the best skills, MCP servers, and agent-specific configurations for each agent in manifest.json.
+
+**What to research per agent:**
+
+For EACH agent in manifest.json (`jq -r '.agents | keys[]' manifest.json`):
+
+1. **Agent Skills standard** — search the agent's docs for SKILL.md / `.agents/skills/` support
+2. **Popular community skills** — search GitHub for `awesome-{agent}`, `{agent}-skills`, `{agent}-rules`
+3. **MCP servers** — which MCP servers are most useful for this specific agent? Check npm for:
+   - `@modelcontextprotocol/server-*` (official reference servers)
+   - `@playwright/mcp` (browser automation)
+   - `@upstash/context7-mcp` (library docs)
+   - `@brave/brave-search-mcp-server` (web search)
+   - `@sentry/mcp-server` (error tracking)
+4. **Agent-specific configs** — what native config files unlock the agent's full potential?
+   - Claude Code: skills in `~/.claude/skills/`, hooks, CLAUDE.md
+   - Cursor: `.mdc` rules in `.cursor/rules/`, `.cursor/mcp.json`
+   - OpenClaw: SOUL.md personality, skills registry, Composio integrations
+   - Codex CLI: AGENTS.md with subagent roles, `config.toml`
+   - Hermes: self-improving skills, YOLO mode config
+   - Kilo Code: custom modes (Architect/Coder/Debugger), AGENTS.md
+   - OpenCode: OmO extension, LSP configs
+   - Aider: `.aider.conf.yml`, architect mode, lint-cmd
+5. **Prerequisites** — for each skill, what needs to be pre-installed?
+   - Chrome/Chromium for Playwright (`npx playwright install chromium && npx playwright install-deps`)
+   - Docker for GitHub MCP server (official Go binary)
+   - API keys (which ones? free tier available?)
+   - System packages (apt)
+
+**Verification (MANDATORY before adding to manifest):**
+
+For MCP servers:
+```bash
+# Verify package exists on npm
+npm view PACKAGE_NAME version 2>/dev/null
+# Verify it starts (5s timeout)
+timeout 5 npx -y PACKAGE_NAME 2>&1 | head -5 || true
+```
+
+For skills (SKILL.md):
+- Verify the source repo/registry still exists
+- Check the skill content is <5000 tokens (Agent Skills spec limit)
+- Verify frontmatter has required `name` and `description` fields
+
+**Update manifest.json skills section:**
+
+Each skill entry should follow this schema:
+```json
+{
+  "name": "Human-readable name",
+  "description": "What it does — one line",
+  "type": "mcp" | "skill" | "config",
+  "package": "@scope/package-name",
+  "prerequisites": {
+    "apt": ["package1"],
+    "commands": ["npx playwright install chromium"],
+    "env_vars": ["GITHUB_TOKEN"]
+  },
+  "agents": {
+    "claude": {
+      "mcp_config": { "command": "npx", "args": ["-y", "@scope/package"] },
+      "skill_path": "~/.claude/skills/skill-name/SKILL.md",
+      "skill_content": "---\nname: ...\n---\n...",
+      "default": true
+    }
+  }
+}
+```
+
+**Rules:**
+- Only add skills that are actively maintained (updated in last 6 months)
+- Prefer official packages over community forks
+- Mark deprecated packages in the PR description
+- Test MCP server startup on this VM before adding
+- Skills requiring OAuth browser flows should be marked `"headless_compatible": false`
+- Each PR should update no more than 5 skills (small, reviewable changes)
+- **SIGN-OFF**: `-- discovery/skills-scout`
+
 Begin now. Phases:
 1. **Check thresholds** — look for proposals at 50+ upvotes → spawn implementers
 2. **Research** — spawn scouts to find new clouds/agents → create proposal issues
-3. **Issues** — respond to open issues
-4. **Monitor** — TaskList loop until ALL teammates report back
-5. **Shutdown** — Full shutdown sequence, exit
+3. **Skills** — spawn skills scout to research and update the skills catalog
+4. **Issues** — respond to open issues
+5. **Monitor** — TaskList loop until ALL teammates report back
+6. **Shutdown** — Full shutdown sequence, exit
PATCH

echo "Gold patch applied."
