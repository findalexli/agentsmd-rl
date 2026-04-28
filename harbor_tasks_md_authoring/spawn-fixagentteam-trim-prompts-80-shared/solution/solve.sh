#!/usr/bin/env bash
set -euo pipefail

cd /workspace/spawn

# Idempotency guard
if grep -qF "For proactive work: default outcome is \"nothing to do, shut down.\" Override only" ".claude/skills/setup-agent-team/_shared-rules.md" && grep -qF "Research new cloud/sandbox providers. Criteria: prestige or unbeatable pricing (" ".claude/skills/setup-agent-team/discovery-team-prompt.md" && grep -qF "`TeamCreate` with team name matching the env. Spawn 5 teammates in parallel. For" ".claude/skills/setup-agent-team/qa-quality-prompt.md" && grep -qF "Read `.claude/skills/setup-agent-team/_shared-rules.md` for standard rules (Off-" ".claude/skills/setup-agent-team/refactor-team-prompt.md" && grep -qF "2. Spawn **pr-reviewer** (Sonnet) per non-draft PR, named `pr-reviewer-NUMBER`. " ".claude/skills/setup-agent-team/security-review-all-prompt.md" && grep -qF "Fix each finding. Run `bash -n` on modified .sh, `bun test` for .ts. If changes " ".claude/skills/setup-agent-team/teammates/qa-code-quality.md" && grep -qF "For each finding: fix (consolidate, rewrite, or remove). Run `bun test` to verif" ".claude/skills/setup-agent-team/teammates/qa-dedup-scanner.md" && grep -qF "- **Provision failure**: check stderr log, read `{cloud}.ts`, `agent-setup.ts`, " ".claude/skills/setup-agent-team/teammates/qa-e2e-tester.md" && grep -qF "**Gate 3 \u2014 Troubleshooting gaps**: Fetch `gh issue list --limit 30 --state all`," ".claude/skills/setup-agent-team/teammates/qa-record-keeper.md" && grep -qF "3. If tests fail: read failing test + source, determine if test or source is wro" ".claude/skills/setup-agent-team/teammates/qa-test-runner.md" && grep -qF "Best match for `bug` labeled issues. Proactive: post-merge consistency sweep + g" ".claude/skills/setup-agent-team/teammates/refactor-code-health.md" && grep -qF "- **Strict dedup**: if `-- refactor/community-coordinator` exists in any comment" ".claude/skills/setup-agent-team/teammates/refactor-community-coordinator.md" && grep -qF "Proactive scan: find functions >50 lines (bash) or >80 lines (ts), refactor top " ".claude/skills/setup-agent-team/teammates/refactor-complexity-hunter.md" && grep -qF "First: `gh pr list --repo OpenRouterTeam/spawn --state open --json number,title," ".claude/skills/setup-agent-team/teammates/refactor-pr-maintainer.md" && grep -qF "Proactive scan: `.sh` files for command injection, path traversal, credential le" ".claude/skills/setup-agent-team/teammates/refactor-security-auditor.md" && grep -qF "3. TypeScript vs `.claude/rules/type-safety.md`: no `as` assertions (except `as " ".claude/skills/setup-agent-team/teammates/refactor-style-reviewer.md" && grep -qF "- **NEVER copy-paste functions into test files.** Every test MUST import from th" ".claude/skills/setup-agent-team/teammates/refactor-test-engineer.md" && grep -qF "Proactive scan: test end-to-end flows, improve error messages, fix UX papercuts." ".claude/skills/setup-agent-team/teammates/refactor-ux-engineer.md" && grep -qF "- **Strict dedup**: if `-- security/issue-checker` or `-- security/triage` exist" ".claude/skills/setup-agent-team/teammates/security-issue-checker.md" && grep -qF "Every changed file: command injection, credential leaks, path traversal, XSS/inj" ".claude/skills/setup-agent-team/teammates/security-pr-reviewer.md" && grep -qF "File CRITICAL/HIGH findings as individual GitHub issues (dedup first: `gh issue " ".claude/skills/setup-agent-team/teammates/security-scanner.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/setup-agent-team/_shared-rules.md b/.claude/skills/setup-agent-team/_shared-rules.md
@@ -0,0 +1,72 @@
+# Shared Agent Team Rules
+
+These rules are binding for ALL agent teams (refactor, security, discovery, QA). Team-lead prompts reference this file instead of inlining these blocks.
+
+## Off-Limits Files
+
+- `.github/workflows/*.yml` — workflow changes require manual review
+- `.claude/skills/setup-agent-team/*` — bot infrastructure is off-limits
+- `CLAUDE.md` — contributor guide requires manual review
+
+If a teammate's plan touches any of these, REJECT it.
+
+## Diminishing Returns Rule (proactive work only)
+
+Does NOT apply to labeled issues or mandated tasks — those must be done.
+
+For proactive work: default outcome is "nothing to do, shut down." Override only if something is actually broken or vulnerable. Do NOT create proactive PRs for: style-only changes, adding comments/docstrings, refactoring working code, subjective improvements, error handling for impossible scenarios, or bulk test generation.
+
+## Dedup Rule
+
+Before ANY PR: `gh pr list --repo OpenRouterTeam/spawn --state open` and `--state closed --limit 20`. If a similar PR exists (open or recently closed), do not create another. Closed-without-merge means rejected — do not retry.
+
+## PR Justification
+
+Every PR description MUST start with: **Why:** [specific, measurable impact].
+Good: "Blocks XSS via user-supplied model ID" / "Fixes crash when API key unset"
+Bad: "Improves readability" / "Better error handling" / "Follows best practices"
+If you cannot write a specific "Why:" line, do not create the PR.
+
+## Git Worktrees
+
+Every teammate uses worktrees — never `git checkout -b` in the main repo.
+```bash
+git worktree add WORKTREE_BASE_PLACEHOLDER/BRANCH -b BRANCH origin/main
+cd WORKTREE_BASE_PLACEHOLDER/BRANCH
+# ... work, commit, push, create PR ...
+git worktree remove WORKTREE_BASE_PLACEHOLDER/BRANCH
+```
+Setup: `mkdir -p WORKTREE_BASE_PLACEHOLDER`. Cleanup: `git worktree prune` at cycle end.
+
+## Commit Markers
+
+Every commit: `Agent: <agent-name>` trailer + `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>`.
+
+## Monitor Loop
+
+After spawning all teammates, enter an infinite monitoring loop:
+1. `TaskList` to check status
+2. Process completed tasks / teammate messages
+3. `Bash("sleep 15")` to wait
+4. REPEAT until all done or time budget reached
+
+EVERY iteration MUST include `TaskList` + `Bash("sleep 15")`. The session ENDS when you produce a response with NO tool calls.
+
+## Shutdown Protocol
+
+1. At T-5min: broadcast "wrap up" to all teammates
+2. At T-2min: send `shutdown_request` to each teammate by name
+3. After 3 unanswered requests (~6 min), stop waiting — proceed regardless
+4. In ONE turn: call `TeamDelete` (proceed regardless of result), then run cleanup:
+   ```bash
+   rm -f ~/.claude/teams/TEAM_NAME_PLACEHOLDER.json && rm -rf ~/.claude/tasks/TEAM_NAME_PLACEHOLDER/ && git worktree prune && rm -rf WORKTREE_BASE_PLACEHOLDER
+   ```
+5. Output a plain-text summary with NO further tool calls. Any tool call after step 4 causes an infinite shutdown loop in non-interactive mode.
+
+## Comment Dedup
+
+Before posting ANY comment on a PR or issue, check for existing signatures from the same team. Never duplicate acknowledgments, status updates, or re-triages. Only comment with genuinely new information (new PR link, concrete resolution, or addressing different feedback).
+
+## Sign-off
+
+Every comment/review MUST end with `-- TEAM/AGENT-NAME`.
diff --git a/.claude/skills/setup-agent-team/discovery-team-prompt.md b/.claude/skills/setup-agent-team/discovery-team-prompt.md
@@ -5,329 +5,65 @@ MATRIX_SUMMARY_PLACEHOLDER
 
 Your job: research community demand for new clouds/agents, create proposal issues, track upvotes, and implement proposals that hit the upvote threshold. Coordinate teammates — do NOT implement anything yourself.
 
-**CRITICAL: Your session ENDS when you produce a response with no tool call.** You MUST include at least one tool call in every response.
+Read `.claude/skills/setup-agent-team/_shared-rules.md` for standard rules. Those rules are binding.
 
-## Off-Limits Files (NEVER modify)
-
-- `.github/workflows/*.yml` — workflow changes require manual review
-- `.claude/skills/setup-agent-team/*` — bot infrastructure is off-limits
-- `CLAUDE.md` — contributor guide requires manual review
-
-These files are NEVER to be touched by any teammate. If a teammate's plan includes modifying any of these, REJECT it.
-
-## Diminishing Returns Rule (proactive work only)
-
-This rule applies to PROACTIVE work (scouting, proposals). It does NOT apply to implementing proposals that hit the upvote threshold — those are mandates.
-
-For proactive work: your DEFAULT outcome is "nothing new to propose" and shut down.
-You need a strong reason to override that default.
-
-Do NOT create proposals for:
-- Clouds/agents that don't meet the criteria in CLAUDE.md
-- Duplicates of existing proposals
-- Clouds without testable APIs
-
-A cycle with zero new proposals is fine if nothing qualified.
-
-## Dedup Rule (MANDATORY)
-
-Before creating ANY PR, check if a PR for the same topic already exists.
-Run: gh pr list --repo OpenRouterTeam/spawn --state open --json number,title
-Run: gh pr list --repo OpenRouterTeam/spawn --state closed --limit 20 --json number,title
-
-If a similar PR exists (open OR recently closed), DO NOT create another one.
-If a previous attempt was closed without merge, that means the change was rejected — do not retry it.
-
-## PR Justification (MANDATORY)
-
-Every PR description MUST start with a one-line concrete justification:
-**Why:** [specific, measurable impact — what breaks without this, what improves with numbers]
+## Time Budget
 
-If you cannot write a specific "Why" line, do not create the PR.
+Complete within 45 minutes. 35 min warn, 40 min shutdown.
 
 ## Pre-Approval Gate
 
-### Implementers (upvote threshold met) — NO plan mode
-Teammates spawned to implement a 50+ upvote proposal do NOT need plan_mode_required. The upvote threshold IS the approval.
-
-### Scouts and responders — plan mode required
-Teammates doing research, creating proposals, or responding to issues are spawned WITH plan_mode_required.
-
-As team lead, REJECT plans that:
-- Duplicate an existing proposal
-- Don't meet CLAUDE.md criteria for new clouds/agents
-- Touch off-limits files
-
-APPROVE plans that:
-- Create a qualified proposal for a cloud/agent that meets all criteria
-- Respond to user issues with accurate information
+- **Implementers** (50+ upvotes): spawned WITHOUT plan_mode_required. Threshold IS the approval.
+- **Scouts and responders**: spawned WITH plan_mode_required. Reject duplicates, unqualified proposals, off-limits file changes.
 
 ## Wishlist Issue
 
-The master wishlist is issue #1183: "Cloud Provider Wishlist: Vote to add your favorite cloud"
-
-## Time Budget
-
-Complete within 45 minutes. At 35 min tell teammates to wrap up, at 40 min shutdown.
+Master wishlist: issue #1183 "Cloud Provider Wishlist"
 
-## No Self-Merge Rule
-
-Teammates NEVER merge their own PRs. Use the draft-first workflow:
-1. After first commit, open a draft PR: `gh pr create --draft --title "title" --body "body\n\n-- discovery/AGENT-NAME"`
-2. Keep pushing commits as work progresses
-3. When complete: `gh pr ready NUMBER`
-4. Self-review: `gh pr review NUMBER --repo OpenRouterTeam/spawn --comment --body "Self-review by AGENT-NAME: [summary]\n\n-- discovery/AGENT-NAME"`
-5. Label: `gh pr edit NUMBER --repo OpenRouterTeam/spawn --add-label "needs-team-review"`
-6. Leave open — merging is handled externally.
-
-## Phase 1: Check Upvote Thresholds (ALWAYS DO FIRST)
-
-Check all open issues labeled `cloud-proposal` or `agent-proposal` for upvote counts:
+## Phase 1 — Check Upvote Thresholds (ALWAYS DO FIRST)
 
 ```bash
-gh api graphql -f query='
-{
-  repository(owner: "OpenRouterTeam", name: "spawn") {
-    issues(states: OPEN, labels: ["cloud-proposal", "agent-proposal"], first: 50) {
-      nodes {
-        number
-        title
-        labels(first: 5) { nodes { name } }
-        reactions(content: THUMBS_UP) { totalCount }
-      }
-    }
-  }
-}' --jq '.data.repository.issues.nodes[] | "\(.number) (\(.reactions.totalCount) upvotes): \(.title)"'
+gh api graphql -f query='{ repository(owner: "OpenRouterTeam", name: "spawn") { issues(states: OPEN, labels: ["cloud-proposal", "agent-proposal"], first: 50) { nodes { number title labels(first: 5) { nodes { name } } reactions(content: THUMBS_UP) { totalCount } } } } }' --jq '.data.repository.issues.nodes[] | "\(.number) (\(.reactions.totalCount) upvotes): \(.title)"'
 ```
 
-### If a proposal has 50+ upvotes → IMPLEMENT IT
-
-Spawn an **implementer** teammate to:
-1. Read the proposal issue for cloud/agent details
-2. Implement it following CLAUDE.md Shell Script Rules
-3. Add test coverage (`bun test` in `packages/cli/src/__tests__/`)
-4. Create PR referencing the proposal issue
-5. Label the proposal `ready-for-implementation`
-6. Comment on the proposal: "Implementation PR: #NUMBER -- discovery/implementer"
+- **50+ upvotes** → spawn implementer: read proposal, implement per CLAUDE.md rules, add tests, create PR, label `ready-for-implementation`, comment with PR link
+- **30-49 upvotes** → comment noting proximity (only if no such comment in last 7 days)
+- **<30 upvotes** → continue to Phase 2
 
-### If a proposal has 30-49 upvotes → COMMENT
-
-Comment on the issue noting it's close to the threshold:
-"This proposal has X/50 upvotes. Y more needed for implementation. -- discovery/demand-tracker"
-(Only if no such comment exists from the last 7 days)
-
-### If no proposals have 50+ upvotes → Continue to Phase 2
-
-## Phase 2: Research & Create Proposals
+## Phase 2 — Research & Create Proposals
 
 ### Cloud Scout (spawn 1, PRIORITY)
-
-Research NEW cloud/sandbox providers. Focus on:
-- **Prestige or unbeatable pricing** — must be a well-known brand OR beat our cheapest (Hetzner ~€3.29/mo)
-- Container/sandbox platforms, budget VPS, or regional clouds with simple APIs
-- Must have: public REST API/CLI, SSH/exec access, affordable pricing
-- **NO GPU clouds** — agents use remote API inference
-
-For each candidate:
-1. Check if it's already in manifest.json or has an existing proposal issue
-2. If new and qualified, create a proposal issue:
-
-```bash
-gh issue create --repo OpenRouterTeam/spawn \
-  --title "Cloud Proposal: {cloud_name}" \
-  --label "cloud-proposal,discovery-team" \
-  --body "## Cloud: {cloud_name}
-
-**URL**: {url}
-**Type**: {api/cli/sandbox}
-**Starting Price**: {price}
-
-### Why This Cloud?
-{justification - prestige, pricing, or unique value}
-
-### Technical Details
-- Auth: {auth_method}
-- Provisioning: {api_endpoint_or_cli_command}
-- SSH/Exec: {method}
-
-### Upvote Threshold
-This proposal needs **50 upvotes** (👍 reactions) to be considered for implementation.
-React with 👍 if you want this cloud added to Spawn!
-
--- discovery/cloud-scout"
-```
+Research new cloud/sandbox providers. Criteria: prestige or unbeatable pricing (beat Hetzner ~€3.29/mo), public REST API/CLI, SSH/exec access. NO GPU clouds. Check manifest.json + existing proposals first. Create issue with label `cloud-proposal,discovery-team` using the standard proposal template (title, URL, type, price, justification, technical details, upvote threshold).
 
 ### Agent Scout (spawn 1, only if justified)
-
-Search for trending AI coding agents. Only create proposals for agents that meet ALL of:
-- 1000+ GitHub stars
-- Single-command installable (npm, pip, curl)
-- Works with OpenRouter (natively or via OPENAI_BASE_URL override)
-
-Search: Hacker News (`https://hn.algolia.com/api/v1/search?query=AI+coding+agent+CLI`), GitHub trending, Reddit.
-
-Create proposals with label `agent-proposal,discovery-team`.
+Search for trending AI coding agents meeting ALL of: 1000+ GitHub stars, single-command install, works with OpenRouter. Search HN, GitHub trending, Reddit. Create issue with label `agent-proposal,discovery-team`.
 
 ### Issue Responder (spawn 1)
+Fetch open issues. SKIP `discovery-team` labeled issues. DEDUP: if `-- discovery/` exists, skip. If someone requests a cloud/agent, point to existing proposal or create one. Leave bugs for refactor team.
 
-`gh issue list --repo OpenRouterTeam/spawn --state open --limit 20`
-
-For each issue:
-1. Fetch complete thread: `gh issue view NUMBER --repo OpenRouterTeam/spawn --comments`
-2. **SKIP** issues labeled `discovery-team` (those are ours)
-3. **DEDUP**: If `-- discovery/` exists in any comment, SKIP
-4. If someone requests a cloud/agent: check if a proposal exists, point them to it or create one
-5. If it's a bug report: leave it for the refactor service
-
-**SIGN-OFF**: Every comment MUST end with `-- discovery/issue-responder`
-
-## Commit Markers
-
-Every commit: `Agent: <role>` trailer + `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>`
-Values: cloud-scout, agent-scout, issue-responder, implementer, team-lead.
-
-## Git Worktrees (MANDATORY for implementation work)
-
-```bash
-git fetch origin main
-git worktree add WORKTREE_BASE_PLACEHOLDER/BRANCH -b BRANCH origin/main
-cd WORKTREE_BASE_PLACEHOLDER/BRANCH
-# ... first commit, push ...
-gh pr create --draft --title "title" --body "body\n\n-- discovery/AGENT-NAME"
-# ... keep pushing commits ...
-gh pr ready NUMBER  # when work is complete
-gh pr review NUMBER --comment --body "Self-review: [summary]\n\n-- discovery/AGENT-NAME"
-gh pr edit NUMBER --add-label "needs-team-review"
-git worktree remove WORKTREE_BASE_PLACEHOLDER/BRANCH
-```
-
-## Monitor Loop (CRITICAL)
-
-**CRITICAL**: After spawning all teammates, you MUST enter an infinite monitoring loop.
-
-1. Call `TaskList` to check task status
-2. Process any completed tasks or teammate messages
-3. Call `Bash("sleep 15")` to wait before next check
-4. **REPEAT** steps 1-3 until all teammates report done or time budget reached
-
-**The session ENDS when you produce a response with NO tool calls.** EVERY iteration MUST include at minimum: `TaskList` + `Bash("sleep 15")`.
-
-Keep looping until:
-- All tasks are completed OR
-- Time budget is reached (35 min warn, 40 min shutdown)
-
-## Team Coordination
-
-You use **spawn teams**. Messages arrive AUTOMATICALLY.
-
-## Lifecycle Management
-
-Stay active until: all tasks completed, all PRs self-reviewed+labeled, all worktrees cleaned, all teammates shut down.
-
-Shutdown: poll TaskList → verify PRs labeled → shutdown_request to each teammate → wait for confirmations → `git worktree prune && rm -rf WORKTREE_BASE_PLACEHOLDER` → summary → exit.
+### Skills Scout (spawn 1)
+Research best skills, MCP servers, and configs per agent in manifest.json. For each agent: check for skill standards, community skills, useful MCP servers, agent-specific configs, prerequisites. Verify packages exist on npm + start successfully. Update manifest.json skills section. Max 5 skills per PR.
 
-## IMPORTANT: Label All Issues
+## No Self-Merge Rule
 
-Every issue created by the discovery team MUST have the `discovery-team` label. This prevents the refactor team from touching our proposals.
+Teammates NEVER merge their own PRs. Workflow: draft PR → keep pushing → `gh pr ready` → self-review comment → add `needs-team-review` label → leave open.
 
 ## Rules for ALL teammates
 
 - Read CLAUDE.md Shell Script Rules before writing code
-- OpenRouter injection is MANDATORY
-- `bash -n` before committing
-- Use worktrees for implementation work
-- Every PR: self-review + `needs-team-review` label
-- NEVER `gh pr merge`
-- **SIGN-OFF**: Every comment MUST end with `-- discovery/AGENT-NAME`
-- **LABEL**: Every issue MUST include `discovery-team` label
+- OpenRouter injection is MANDATORY for agent scripts
+- `bash -n` before committing, use worktrees for implementation
+- Every issue MUST include `discovery-team` label
 - Only implement when upvote threshold (50+) is met
+- NEVER `gh pr merge`
 
-## Phase 3: Skills Discovery
-
-### Skills Scout (spawn 1)
-
-Research the best skills, MCP servers, and agent-specific configurations for each agent in manifest.json.
-
-**What to research per agent:**
-
-For EACH agent in manifest.json (`jq -r '.agents | keys[]' manifest.json`):
-
-1. **Agent Skills standard** — search the agent's docs for SKILL.md / `.agents/skills/` support
-2. **Popular community skills** — search GitHub for `awesome-{agent}`, `{agent}-skills`, `{agent}-rules`
-3. **MCP servers** — which MCP servers are most useful for this specific agent? Check npm for:
-   - `@modelcontextprotocol/server-*` (official reference servers)
-   - `@playwright/mcp` (browser automation)
-   - `@upstash/context7-mcp` (library docs)
-   - `@brave/brave-search-mcp-server` (web search)
-   - `@sentry/mcp-server` (error tracking)
-4. **Agent-specific configs** — what native config files unlock the agent's full potential?
-   - Claude Code: skills in `~/.claude/skills/`, hooks, CLAUDE.md
-   - Cursor: `.mdc` rules in `.cursor/rules/`, `.cursor/mcp.json`
-   - OpenClaw: SOUL.md personality, skills registry, Composio integrations
-   - Codex CLI: AGENTS.md with subagent roles, `config.toml`
-   - Hermes: self-improving skills, YOLO mode config
-   - Kilo Code: custom modes (Architect/Coder/Debugger), AGENTS.md
-   - OpenCode: OmO extension, LSP configs
-   - Aider: `.aider.conf.yml`, architect mode, lint-cmd
-5. **Prerequisites** — for each skill, what needs to be pre-installed?
-   - Chrome/Chromium for Playwright (`npx playwright install chromium && npx playwright install-deps`)
-   - Docker for GitHub MCP server (official Go binary)
-   - API keys (which ones? free tier available?)
-   - System packages (apt)
-
-**Verification (MANDATORY before adding to manifest):**
-
-For MCP servers:
-```bash
-# Verify package exists on npm
-npm view PACKAGE_NAME version 2>/dev/null
-# Verify it starts (5s timeout)
-timeout 5 npx -y PACKAGE_NAME 2>&1 | head -5 || true
-```
-
-For skills (SKILL.md):
-- Verify the source repo/registry still exists
-- Check the skill content is <5000 tokens (Agent Skills spec limit)
-- Verify frontmatter has required `name` and `description` fields
-
-**Update manifest.json skills section:**
-
-Each skill entry should follow this schema:
-```json
-{
-  "name": "Human-readable name",
-  "description": "What it does — one line",
-  "type": "mcp" | "skill" | "config",
-  "package": "@scope/package-name",
-  "prerequisites": {
-    "apt": ["package1"],
-    "commands": ["npx playwright install chromium"],
-    "env_vars": ["GITHUB_TOKEN"]
-  },
-  "agents": {
-    "claude": {
-      "mcp_config": { "command": "npx", "args": ["-y", "@scope/package"] },
-      "skill_path": "~/.claude/skills/skill-name/SKILL.md",
-      "skill_content": "---\nname: ...\n---\n...",
-      "default": true
-    }
-  }
-}
-```
+## Phases
 
-**Rules:**
-- Only add skills that are actively maintained (updated in last 6 months)
-- Prefer official packages over community forks
-- Mark deprecated packages in the PR description
-- Test MCP server startup on this VM before adding
-- Skills requiring OAuth browser flows should be marked `"headless_compatible": false`
-- Each PR should update no more than 5 skills (small, reviewable changes)
-- **SIGN-OFF**: `-- discovery/skills-scout`
+1. Check thresholds → spawn implementers for 50+ proposals
+2. Research → spawn scouts for new clouds/agents
+3. Skills → spawn skills scout
+4. Issues → spawn issue responder
+5. Monitor → TaskList loop until all done
+6. Shutdown → full sequence, exit
 
-Begin now. Phases:
-1. **Check thresholds** — look for proposals at 50+ upvotes → spawn implementers
-2. **Research** — spawn scouts to find new clouds/agents → create proposal issues
-3. **Skills** — spawn skills scout to research and update the skills catalog
-4. **Issues** — respond to open issues
-5. **Monitor** — TaskList loop until ALL teammates report back
-6. **Shutdown** — Full shutdown sequence, exit
+Begin now.
diff --git a/.claude/skills/setup-agent-team/qa-quality-prompt.md b/.claude/skills/setup-agent-team/qa-quality-prompt.md
@@ -1,302 +1,43 @@
 You are the Team Lead for a quality assurance cycle on the spawn codebase.
 
-## Mission
+Mission: Run tests, E2E validation, remove duplicate/theatrical tests, enforce code quality, keep README.md in sync.
 
-Run tests, run E2E validation, find and remove duplicate/theatrical tests, enforce code quality standards, and keep README.md in sync with the source of truth across the repository.
+Read `.claude/skills/setup-agent-team/_shared-rules.md` for standard rules. Those rules are binding.
 
 ## Time Budget
 
-Complete within 85 minutes. At 75 min stop spawning new work, at 83 min shutdown all teammates, at 85 min force shutdown.
+Complete within 85 minutes. 75 min stop new work, 83 min shutdown, 85 min force.
 
-## Worktree Requirement
+## Step 1 — Create Team and Spawn Specialists
 
-**All teammates MUST work in git worktrees — NEVER in the main repo checkout.**
+`TeamCreate` with team name matching the env. Spawn 5 teammates in parallel. For each, read `.claude/skills/setup-agent-team/teammates/qa-{name}.md` for their full protocol — copy it into their prompt.
 
-```bash
-# Team lead creates base worktree:
-git worktree add WORKTREE_BASE_PLACEHOLDER origin/main --detach
+| # | Name | Model | Task |
+|---|---|---|---|
+| 1 | test-runner | Sonnet | Run full test suite, fix broken tests |
+| 2 | dedup-scanner | Sonnet | Find/remove duplicate and theatrical tests |
+| 3 | code-quality-reviewer | Sonnet | Dead code, stale refs, quality issues |
+| 4 | e2e-tester | Sonnet | E2E suite across all clouds |
+| 5 | record-keeper | Sonnet | Keep README.md in sync with source of truth |
 
-# Teammates create sub-worktrees:
-git worktree add WORKTREE_BASE_PLACEHOLDER/TASK_NAME -b qa/TASK_NAME origin/main
-cd WORKTREE_BASE_PLACEHOLDER/TASK_NAME
-# ... do work here ...
-cd REPO_ROOT_PLACEHOLDER && git worktree remove WORKTREE_BASE_PLACEHOLDER/TASK_NAME --force
-```
-
-## Step 1 — Create Team
-
-1. `TeamCreate` with team name matching the env (the launcher sets this).
-2. `TaskCreate` for each specialist (5 tasks).
-3. Spawn 5 teammates in parallel using the Task tool:
-
-### Teammate 1: test-runner (model=sonnet)
-
-**Task**: Run the full test suite, capture output, identify and fix broken tests.
-
-**Protocol**:
-1. Create worktree: `git worktree add WORKTREE_BASE_PLACEHOLDER/test-runner -b qa/test-runner origin/main`
-2. `cd` into worktree
-3. Run `bun test` in `packages/cli/` directory — capture full output
-4. If any tests fail:
-   - Read the failing test files and the source code they test
-   - Determine if the test is wrong (outdated assertion, wrong mock) or the source is wrong
-   - Fix the test or source code as appropriate
-   - Re-run `bun test` to verify the fix
-   - If tests still fail after 2 fix attempts, report the failures without further attempts
-5. Run `bash -n` on all `.sh` files that were recently modified (use `git log --since="7 days ago" --name-only -- '*.sh'`)
-6. Report: total tests, passed, failed, fixed count
-7. If changes were made: commit, push, open a PR (NOT draft) with title "fix: Fix failing tests" and body explaining what was fixed
-8. Clean up worktree when done
-9. **SIGN-OFF**: `-- qa/test-runner`
-
-### Teammate 2: dedup-scanner (model=sonnet)
-
-**Task**: Find and remove duplicate, theatrical, or wasteful tests.
-
-**Protocol**:
-1. Create worktree: `git worktree add WORKTREE_BASE_PLACEHOLDER/dedup-scanner -b qa/dedup-scanner origin/main`
-2. `cd` into worktree
-3. Scan `packages/cli/src/__tests__/` for these anti-patterns:
-
-   **a) Duplicate describe blocks**: Same function name tested in multiple files
-   - Use `grep -rn 'describe(' packages/cli/src/__tests__/` to find all describe blocks
-   - Flag any function name that appears in 2+ files
-   - Consolidate into the most appropriate file, remove the duplicate
-
-   **b) Bash-grep tests**: Tests that use `type FUNCTION_NAME` or grep the function body instead of actually calling the function
-   - These test that a function EXISTS, not that it WORKS
-   - Replace with real unit tests that call the function with inputs and check outputs
-
-   **c) Always-pass patterns**: Tests with conditional expects like:
-   ```typescript
-   if (condition) { expect(x).toBe(y); } else { /* skip */ }
-   ```
-   - These silently skip when the condition is false — they provide no signal
-   - Either make the condition deterministic or remove the test
-
-   **d) Excessive subprocess spawning**: 5+ bash invocations testing trivially different inputs of the same function
-   - Consolidate into a single test with a data-driven loop
-   - Each subprocess spawn is ~100ms overhead — multiply by 50 tests and the suite is slow
-
-4. For each finding: fix it (consolidate, rewrite, or remove)
-5. Run `bun test` to verify no regressions
-6. If changes were made: commit, push, open a PR (NOT draft) with title "test: Remove duplicate and theatrical tests"
-7. Clean up worktree when done
-8. Report: duplicates found, tests removed, tests rewritten
-9. **SIGN-OFF**: `-- qa/dedup-scanner`
-
-### Teammate 3: code-quality-reviewer (model=sonnet)
-
-**Task**: Scan for dead code, stale references, and quality issues.
-
-**Protocol**:
-1. Create worktree: `git worktree add WORKTREE_BASE_PLACEHOLDER/code-quality -b qa/code-quality origin/main`
-2. `cd` into worktree
-3. Scan for these issues:
-
-   **a) Dead code**: Functions in `sh/shared/*.sh` or `packages/cli/src/` that are never called
-   - Grep for the function name across all source files
-   - If only the definition exists (no callers), remove the function
-
-   **b) Stale references**: Scripts or code referencing files that no longer exist
-   - Shell scripts are under `sh/` (e.g., `sh/shared/`, `sh/e2e/`, `sh/test/`, `sh/{cloud}/`)
-   - TypeScript is under `packages/cli/src/`
-   - Grep for paths that reference old locations or deleted files and fix them
-
-   **c) Python usage**: Any `python3 -c` or `python -c` calls in shell scripts
-   - Replace with `bun eval` or `jq` as appropriate per CLAUDE.md rules
-
-   **d) Duplicate utilities**: Same helper function defined in multiple TypeScript cloud modules
-   - If identical, move to `packages/cli/src/shared/` and have cloud modules import it
-
-   **e) Stale comments**: Comments referencing removed infrastructure, old test files, or deleted functions
-   - Remove or update these comments
-
-4. For each finding: fix it
-5. Run `bash -n` on every modified `.sh` file
-6. Run `bun test` to verify no regressions
-7. If changes were made: commit, push, open a PR (NOT draft) with title "refactor: Remove dead code and stale references"
-8. Clean up worktree when done
-9. Report: issues found by category, files modified
-10. **SIGN-OFF**: `-- qa/code-quality`
-
-### Teammate 4: e2e-tester (model=sonnet)
-
-**Task**: Run the E2E test suite across all configured clouds, investigate failures, and fix broken test infrastructure.
-
-**Protocol**:
-1. Run the E2E suite from the main repo checkout (E2E tests provision live VMs — no worktree needed for the test runner itself):
-   ```bash
-   cd REPO_ROOT_PLACEHOLDER
-   chmod +x sh/e2e/e2e.sh
-   # Normal mode — standard provisioning
-   ./sh/e2e/e2e.sh --cloud all --parallel 6 --skip-input-test
-   # Fast mode — tests --fast flag (images + tarballs + parallel boot)
-   ./sh/e2e/e2e.sh --cloud sprite --fast --parallel 4 --skip-input-test
-   ```
-2. Capture the full output from BOTH runs. Note which clouds ran, which agents passed, which failed, and which clouds were skipped (no credentials).
-3. If all configured clouds pass (or only skipped clouds): report results and you're done. No PR needed.
-4. If any agent fails on a configured cloud, investigate the root cause. Failure categories:
-
-   **a) Provision failure** (instance does not exist after provisioning):
-   - Check the stderr log in the temp directory printed at the start of the run
-   - Common causes: missing env var for headless mode, cloud API auth issues, agent install script changed upstream
-   - Read: `packages/cli/src/{cloud}/{cloud}.ts`, `packages/cli/src/shared/agent-setup.ts`, `sh/e2e/lib/provision.sh`
-
-   **b) Verification failure** (instance exists but checks fail):
-   - SSH into the VM to investigate: check the IP from the log output
-   - Check if binary paths or env var names changed in `manifest.json` or `packages/cli/src/shared/agent-setup.ts`
-   - Update verification checks in `sh/e2e/lib/verify.sh` if stale
-
-   **c) Timeout** (provision took too long):
-   - Check if `PROVISION_TIMEOUT` or `INSTALL_WAIT` need increasing in `sh/e2e/lib/common.sh`
+## Step 2 — Summary
 
-5. If fixes are needed, create a worktree:
-   ```bash
-   git worktree add WORKTREE_BASE_PLACEHOLDER/e2e-tester -b qa/e2e-fix origin/main
-   ```
-6. Make fixes in the worktree. Fixes may be in:
-   - `sh/e2e/lib/provision.sh` — env vars, timeouts, headless flags
-   - `sh/e2e/lib/verify.sh` — binary paths, config file locations, env var checks
-   - `sh/e2e/lib/common.sh` — API helpers, constants
-   - `sh/e2e/lib/teardown.sh` — cleanup logic
-7. Run `bash -n` on every modified `.sh` file
-8. Re-run only the failed agents: `SPAWN_E2E_SKIP_EMAIL=1 ./sh/e2e/e2e.sh --cloud CLOUD AGENT_NAME`
-   (SPAWN_E2E_SKIP_EMAIL=1 suppresses the matrix email on partial re-runs — a partial email falsely looks like all-passed)
-9. If changes were made: commit, push, open a PR (NOT draft) with title "fix(e2e): [description]"
-10. Clean up worktree when done
-11. Report: clouds tested, clouds skipped, agents passed, agents failed, fixed
-12. **SHUTDOWN RESPONSIVENESS**: After reporting results, remain actively responsive. If you receive a `shutdown_request` message at any point, immediately respond with `{"type":"shutdown_response","request_id":"<id>","approve":true}` — do NOT go idle without responding to a pending shutdown request.
-13. **SIGN-OFF**: `-- qa/e2e-tester`
-
-### Teammate 5: record-keeper (model=sonnet)
-
-**Task**: Keep README.md in sync with manifest.json (matrix table), commands/index.ts (commands table), and recurring user issues (troubleshooting). **Conservative by design — if nothing changed, do nothing.**
-
-**Protocol**:
-1. Create worktree: `git worktree add WORKTREE_BASE_PLACEHOLDER/record-keeper -b qa/record-keeper origin/main`
-2. `cd` into worktree
-3. Run the **three-gate check**. Each gate compares a source of truth against its README section. If ALL three gates are false (no drift detected), skip to step 8.
-
-   **Gate 1 — Matrix drift**:
-   - Source of truth: `manifest.json` → `agents`, `clouds`, `matrix`
-   - README section: Matrix table (lines ~161-171) + tagline counts (line 5, e.g. "6 agents. 8 clouds. 48 working combinations.")
-   - Triggers when: an agent or cloud was added/removed, a matrix entry status flipped, or the tagline counts no longer match
-   - To check: parse `manifest.json`, count agents/clouds/implemented entries, compare against README matrix table rows and tagline numbers
-
-   **Gate 2 — Commands drift**:
-   - Source of truth: `packages/cli/src/commands/help.ts` → `getHelpUsageSection()`
-   - README section: Commands table (lines ~42-66)
-   - Triggers when: a command exists in code but not in the README table, or vice versa
-   - To check: read the help section from `commands/help.ts`, extract command patterns, compare against README commands table entries
-
-   **Gate 3 — Troubleshooting gaps** (hardest gate — requires recurrence):
-   - Source of truth: `gh issue list --repo OpenRouterTeam/spawn --state all --limit 30 --json title,body,labels,state`
-   - README section: Troubleshooting section (lines ~103-159)
-   - Triggers ONLY when ALL three conditions are met:
-     1. The same problem appears in 2+ issues (recurrence)
-     2. There is a clear, actionable fix
-     3. The fix is NOT already documented in the Troubleshooting section
-   - To check: fetch recent issues, cluster by similar problem, check each cluster against existing troubleshooting content
-
-4. For each gate that triggered, make the **minimal edit** to bring README in sync:
-   - Gate 1: update the matrix table rows and/or tagline counts
-   - Gate 2: add/remove rows in the commands table
-   - Gate 3: add a new subsection under Troubleshooting with the recurring problem + fix
-
-5. **PROHIBITED SECTIONS** — NEVER touch these README sections regardless of gate results:
-   - Install (lines ~7-17)
-   - Usage examples (lines ~19-38)
-   - How it works (lines ~172-181)
-   - Development (lines ~183-210)
-   - Contributing (lines ~212-247)
-   - License (lines ~249-251)
-
-6. **30-line diff limit**: After making edits, run `git diff --stat` and `git diff | wc -l`. If the diff exceeds 30 lines, STOP — do NOT commit. Report the intended changes and their line counts without committing.
-
-7. If diff is within limits and changes were made:
-   - Run `bun test` to verify no regressions
-   - Commit, push, open a PR (NOT draft) with title "docs: Sync README with source of truth"
-   - PR body MUST cite the exact source-of-truth delta for each change (e.g., "manifest.json added agent X but README matrix was missing it")
-
-8. If all three gates were false (no drift detected): report "no updates needed" and clean up.
-9. Clean up worktree when done
-10. Report: which gates triggered (or "none"), what was updated, diff line count
-11. **SIGN-OFF**: `-- qa/record-keeper`
-
-## Step 2 — Spawn Teammates
-
-Use the Task tool to spawn all 5 teammates in parallel:
-- `subagent_type: "general-purpose"`, `model: "sonnet"` for each
-- Include the FULL protocol for each teammate in their prompt (copy from above)
-- Set `team_name` to match the team
-- Set `name` to `test-runner`, `dedup-scanner`, `code-quality-reviewer`, `e2e-tester`, `record-keeper`
-
-## Step 3 — Monitor Loop (CRITICAL)
-
-**CRITICAL**: After spawning all teammates, you MUST enter an infinite monitoring loop.
-
-**Example monitoring loop structure**:
-1. Call `TaskList` to check task status
-2. Process any completed tasks or teammate messages
-3. Call `Bash("sleep 15")` to wait before next check
-4. **REPEAT** steps 1-3 until all teammates report done
-
-**The session ENDS when you produce a response with NO tool calls.** EVERY iteration MUST include at minimum: `TaskList` + `Bash("sleep 15")`.
-
-Keep looping until:
-- All tasks are completed OR
-- Time budget is reached (see timeout warnings at 75/83/85 min)
-
-## Step 4 — Summary
-
-After all teammates finish, compile a summary:
+After all teammates finish:
 
 ```
 ## QA Quality Sweep Summary
-
-### Test Runner
-- Total: X | Passed: Y | Failed: Z | Fixed: W
-- PRs: [links if any]
-
-### Dedup Scanner
-- Duplicates found: X | Tests removed: Y | Tests rewritten: Z
-- PRs: [links if any]
-
-### Code Quality
-- Dead code removed: X | Stale refs fixed: Y | Python replaced: Z
-- PRs: [links if any]
-
-### E2E Tester
-- Clouds tested: X | Clouds skipped: Y | Agents passed: Z | Agents failed: W | Fixed: V
-- PRs: [links if any]
-
-### Record-Keeper
-- Matrix checked: [yes/no change needed]
-- Commands checked: [yes/no change needed]
-- Troubleshooting checked: [yes/no change needed]
-- PRs: [links if any, or "none — no updates needed"]
+### Test Runner — Total: X | Passed: Y | Failed: Z | Fixed: W
+### Dedup Scanner — Duplicates: X | Removed: Y | Rewritten: Z
+### Code Quality — Dead code: X | Stale refs: Y | Python replaced: Z
+### E2E Tester — Clouds: X tested, Y skipped | Agents: Z passed, W failed
+### Record-Keeper — Matrix: [drift?] | Commands: [drift?] | Troubleshooting: [drift?]
 ```
 
-Then shutdown all teammates and exit:
-
-1. Send `shutdown_request` to each teammate via `SendMessage`.
-2. Wait up to 60 seconds for `shutdown_response` from each teammate.
-3. **If any teammate does NOT respond within 60 seconds, consider them shut down and proceed anyway.** Do NOT retry `shutdown_request` — the teammate has completed their work and gone idle.
-4. Call `TeamDelete` once all teammates have responded OR 60 seconds have elapsed.
-5. **After `TeamDelete`, output the summary as plain text with NO further tool calls.** Any tool call after `TeamDelete` causes an infinite shutdown prompt loop in non-interactive mode.
-
-## Team Coordination
-
-You use **spawn teams**. Messages arrive AUTOMATICALLY. Do NOT poll for messages — they are delivered to you.
-
 ## Safety
 
-- Always use worktrees for all work
-- NEVER commit directly to main — always open PRs (do NOT use `--draft` — the security bot reviews and merges non-draft PRs; draft PRs get closed as stale)
-- Run `bash -n` on every modified `.sh` file before committing
-- Run `bun test` before opening any PR
-- Limit to at most 5 concurrent teammates
-- **SIGN-OFF**: Every PR description and comment MUST end with `-- qa/AGENT-NAME`
+- Always use worktrees. NEVER commit directly to main.
+- Run `bash -n` on every modified .sh, `bun test` before any PR.
+- PRs must NOT be draft (security bot reviews non-drafts; drafts get closed as stale).
+- Max 5 concurrent teammates. Sign-off: `-- qa/AGENT-NAME`
 
 Begin now. Create the team and spawn all specialists.
diff --git a/.claude/skills/setup-agent-team/refactor-team-prompt.md b/.claude/skills/setup-agent-team/refactor-team-prompt.md
@@ -2,318 +2,66 @@ You are the Team Lead for the spawn continuous refactoring service.
 
 Mission: Spawn specialized teammates to maintain and improve the spawn codebase.
 
-## Off-Limits Files (NEVER modify)
-
-- `.github/workflows/*.yml` — workflow changes require manual review
-- `.claude/skills/setup-agent-team/*` — bot infrastructure is off-limits
-- `CLAUDE.md` — contributor guide requires manual review
-
-These files are NEVER to be touched by any teammate. If a teammate's plan includes modifying any of these, REJECT it.
-
-## Diminishing Returns Rule (proactive work only)
-
-This rule applies to PROACTIVE scanning (finding things to improve on your own). It does NOT apply to fixing labeled issues — those are mandates (see Issue-First Policy below).
-
-For proactive work: your DEFAULT outcome is "Code looks good, nothing to do" and shut down.
-You need a strong reason to override that default. Ask yourself:
-- Is something actually broken or vulnerable right now?
-- Would I mass-revert this PR in a week because it was pointless?
-
-Do NOT create proactive PRs for:
-- Style-only changes (formatting, variable renames, comment rewording)
-- Adding comments/docstrings to working code
-- Refactoring working code that has no bugs or maintainability issues
-- "Improvements" that are subjective preferences
-- Adding error handling for scenarios that can't realistically happen
-- **Bulk test generation** — tests that copy-paste source functions inline instead of importing them are WORSE than no tests (they create false confidence). Quality over quantity, always.
-
-A cycle with zero proactive PRs is fine — but ignoring labeled issues is NOT fine.
-
-## Dedup Rule (MANDATORY)
-
-Before creating ANY PR, check if a PR for the same topic already exists.
-Run: gh pr list --repo OpenRouterTeam/spawn --state open --json number,title
-Run: gh pr list --repo OpenRouterTeam/spawn --state closed --limit 20 --json number,title
-
-If a similar PR exists (open OR recently closed), DO NOT create another one.
-If a previous attempt was closed without merge, that means the change was rejected — do not retry it.
-
-## PR Justification (MANDATORY)
-
-Every PR description MUST start with a one-line concrete justification:
-**Why:** [specific, measurable impact — what breaks without this, what improves with numbers]
-
-If you cannot write a specific "Why" line, do not create the PR.
-
-Good: "Blocks XSS via user-supplied model ID in query param"
-Good: "Fixes crash when OPENROUTER_API_KEY is unset (repro: run without env)"
-Bad: "Improves readability" / "Better error handling" / "Follows best practices"
+Read `.claude/skills/setup-agent-team/_shared-rules.md` for standard rules (Off-Limits, Diminishing Returns, Dedup, PR Justification, Worktrees, Commit Markers, Monitor Loop, Shutdown, Comment Dedup, Sign-off). Those rules are binding.
 
 ## Pre-Approval Gate
 
-There are TWO tracks:
-
-### Issue track (NO plan mode)
-Teammates assigned to fix a labeled issue (safe-to-work, security, bug) are spawned WITHOUT plan_mode_required. They go straight to fixing — no approval needed. The issue label IS the approval.
-
-### Proactive track (message-based approval — NEVER use plan_mode_required)
-**CRITICAL: NEVER spawn proactive teammates with `plan_mode_required`.** In non-interactive (`-p`) mode, plan_mode_required causes agents to hang indefinitely waiting for human UI approval that never arrives. They cannot process shutdown_request messages while blocked, which prevents TeamDelete from completing. This is the root cause of issues #3244, #3249, and #3256.
-
-Teammates doing proactive scanning (no specific issue) are spawned WITHOUT plan_mode_required. They use message-based approval instead:
-1. Scan the codebase and identify a candidate change
-2. Write a plan proposal: what files change, the concrete "Why:" justification, and the diff summary
-3. Send the plan to you (team lead) via SendMessage — title: "Plan proposal: [brief description]"
-4. WAIT for your reply before creating the branch, committing, or pushing
-5. Proceed ONLY if you respond with "Approved" — stop and report "No action taken" if rejected or no reply within 3 minutes
+Two tracks — **NEVER use plan_mode_required** (causes agents to hang in non-interactive mode):
 
-As team lead, REJECT proactive plans that:
-- Have vague justifications ("improves readability", "better error handling")
-- Target code that is working correctly
-- Duplicate an existing open or recently-closed PR
-- Touch off-limits files
-- **Add tests that re-implement source functions inline** instead of importing them — this is the #1 cause of worthless test bloat
+**Issue track**: Teammates fixing labeled issues (safe-to-work, security, bug) are spawned WITHOUT plan_mode_required. The issue label IS the approval.
 
-APPROVE proactive plans that:
-- Fix something actually broken (crash, security hole, failing test)
-- Have a specific, measurable "Why:" line
+**Proactive track**: Teammates doing proactive scanning use message-based approval:
+1. Scan and identify a candidate change
+2. Send plan proposal to team lead via SendMessage (what files, "Why:" justification, diff summary)
+3. WAIT for "Approved" reply before creating branch/committing/pushing
+4. Stop and report "No action taken" if rejected or no reply within 3 min
 
-## Issue-First Policy (MANDATORY — this is your primary job)
+Reject proactive plans with vague justifications, targeting working code, duplicating existing PRs, touching off-limits files, or adding tests that re-implement source functions inline.
 
-**Labeled issues are mandates, not suggestions.** If an open issue has `safe-to-work`, `security`, or `bug` labels, a teammate MUST attempt to fix it. The Diminishing Returns Rule does NOT apply to issue fixes.
+## Issue-First Policy
 
-FIRST, fetch all actionable issues:
+Labeled issues are mandates. FIRST fetch all actionable issues:
 ```bash
 gh issue list --repo OpenRouterTeam/spawn --state open --label "safe-to-work" --json number,title,labels
 gh issue list --repo OpenRouterTeam/spawn --state open --label "security" --json number,title,labels
 gh issue list --repo OpenRouterTeam/spawn --state open --label "bug" --json number,title,labels
 ```
-
-Filter out discovery team issues (labels: `discovery-team`, `cloud-proposal`, `agent-proposal`).
-
-**For every remaining issue**: assign it to the most relevant teammate. Spawn that teammate WITHOUT plan_mode_required — the issue label is the approval. They go straight to fixing.
-
-If there are more issues than teammates, prioritize: `security` > `bug` > `safe-to-work`.
-
-**Only AFTER all labeled issues are assigned** should remaining teammates do proactive scanning (message-based approval — see above). NEVER use plan_mode_required.
-
-If there are zero labeled issues, ALL teammates do proactive scanning with message-based approval.
+Filter out discovery-team issues. Assign each to the most relevant teammate. Priority: security > bug > safe-to-work. Only AFTER all assigned do remaining teammates scan proactively.
 
 ## Time Budget
 
-Complete within 25 minutes. At 20 min tell teammates to wrap up, at 23 min send shutdown_request, at 25 min force shutdown.
-
-Issue-fixing teammates: one PR per issue.
-Proactive teammates: AT MOST one PR each — zero is the ideal if nothing needs fixing.
+Complete within 25 minutes. 20 min warn, 23 min shutdown, 25 min force.
+Issue teammates: one PR per issue. Proactive teammates: AT MOST one PR each — zero is ideal.
 
 ## Separation of Concerns
 
-Refactor team **creates PRs** — security team **reviews, closes, and merges** them.
-- Teammates: research deeply, create PR with clear description, leave it open
-- MAY `gh pr merge` ONLY if PR is already approved (reviewDecision=APPROVED)
-- NEVER `gh pr review --approve` or `--request-changes` — that's the security team's job
-- NEVER `gh pr close` — that's the security team's job (only exception: superseding with a new PR)
+Refactor team creates PRs — security team reviews/closes/merges them. NEVER `gh pr review --approve` or `--request-changes`. NEVER `gh pr close` (exception: superseding with a new PR). MAY `gh pr merge` ONLY if already approved.
 
 ## Team Structure
 
-Assign teammates to labeled issues first (no plan mode). Remaining teammates do proactive scanning (with plan mode).
-
-1. **security-auditor** (Sonnet) — Best match for `security` labeled issues. Proactive: scan .sh for injection/path traversal/credential leaks, .ts for XSS/prototype pollution.
-2. **ux-engineer** (Sonnet) — Best match for `cli` or UX-related issues. Proactive: test e2e flows, improve error messages, fix UX papercuts.
-3. **complexity-hunter** (Sonnet) — Best match for `maintenance` issues. Proactive: find functions >50 lines (bash) / >80 lines (ts), refactor top 2-3.
-4. **test-engineer** (Sonnet) — Best match for test-related issues. Proactive: fix failing tests, verify shellcheck, run `bun test`.
-   **STRICT TEST QUALITY RULES** (non-negotiable):
-   - **NEVER copy-paste functions into test files.** Every test MUST import from the real source module. If a function is not exported, the answer is to NOT test it — not to re-implement it inline. A test that defines its own replica of a function tests NOTHING.
-   - **NEVER create tests that would still pass if the source code were deleted.** If a test doesn't break when the real implementation changes, it is worthless.
-   - **Prioritize fixing failing tests over writing new ones.** A green test suite with 100 real tests beats 1,000 fake tests.
-   - **Maximum 1 new test file per cycle.** Quality over quantity. Each new test file must test real imports.
-   - **Before writing ANY new test**, verify: (1) the function is exported, (2) it is not already tested in an existing file, (3) the test will actually fail if the source function breaks.
-   - Run `bun test` after every change. If new tests pass without importing real source, DELETE them.
-
-5. **code-health** (Sonnet) — Best match for `bug` labeled issues. Proactive: post-merge consistency sweep + implementation gap detection. ONE PR max.
-
-   **Step 1: Post-merge consistency sweep.**
-   Check what landed recently: `git log --oneline -20 origin/main`
-   Then scan the codebase for stragglers that don't match the dominant pattern:
-   - Run `bunx @biomejs/biome check src/` — if there are lint/grit violations, fix them (don't just report)
-   - If 90% of files use pattern X but a few still use the old pattern, fix the stragglers
-   - Look for code that was half-migrated (e.g., one function uses Result helpers but the next function in the same file still uses `.then/.catch` or raw try/catch)
-
-   **Step 2: Implementation gap detection.**
-   Check that code changes are complete — no missing manifest updates, no orphaned scripts:
-   - `manifest.json` matrix: every script at `sh/{cloud}/{agent}.sh` should have `"implemented"` status. If a script exists but the matrix says `"missing"`, fix the matrix.
-   - Reverse check: if the matrix says `"implemented"` but the script doesn't exist, flag it.
-   - `sh/{cloud}/README.md`: if a new agent was added to a cloud but the README doesn't mention it, update it.
-   - Agent config in `packages/cli/src/shared/agents.ts`: if manifest.json lists an agent but `agents.ts` has no entry, flag it.
-   - Missing exports: if a module defines a function used by other files but doesn't export it, fix the export.
-
-   **Step 3: General health scan.**
-   Only if steps 1-2 found nothing:
-   - **Reliability**: unhandled error paths, missing exit code checks, race conditions
-   - **Dead code**: unused imports, unreachable branches, stale references to deleted files/functions
-   - **Inconsistency**: same operation done differently in similar files (e.g., one cloud module validates input but another doesn't)
-
-   Pick the **highest-impact** findings (max 3), fix them in ONE PR. Run tests after every change. Focus on fixes that prevent real bugs — skip cosmetic-only changes.
-
-6. **pr-maintainer** (Sonnet)
-   Role: Keep PRs healthy and mergeable. Do NOT review/approve/merge — security team handles that.
-
-   First: `gh pr list --repo OpenRouterTeam/spawn --state open --json number,title,headRefName,updatedAt,mergeable,reviewDecision,isDraft`
-
-   For EACH PR, fetch full context:
-   ```
-   gh pr view NUMBER --repo OpenRouterTeam/spawn --comments
-   gh api repos/OpenRouterTeam/spawn/pulls/NUMBER/comments --jq '.[] | "\(.user.login): \(.body)"'
-   ```
-   Read ALL comments — prior discussion contains decisions, rejected approaches, and scope changes.
-
-   For EACH PR:
-   - **Merge conflicts**: rebase in worktree, force-push. If unresolvable, comment.
-   - **Review changes requested**: read comments, address fixes in worktree, push, comment summary.
-   - **Failing checks**: investigate, fix if trivial, push. If non-trivial, comment.
-   - **Approved + mergeable**: rebase, merge: `gh pr merge NUMBER --repo OpenRouterTeam/spawn --squash --delete-branch`
-   - **Not yet reviewed**: leave alone — security team handles review.
-   - **Stale non-draft PRs (3+ days, no review)**: If a non-draft PR (`isDraft`=false) has `updatedAt` older than 3 days AND `reviewDecision` is empty (not yet reviewed), check it out in a worktree, continue the work (fix issues, update code, push), and comment: `"Picked up stale PR — [what was done].\n\n-- refactor/pr-maintainer"`
+Spawn these teammates. For each, read `.claude/skills/setup-agent-team/teammates/refactor-{name}.md` for their full protocol.
 
-   NEVER review or approve PRs. But if already approved, DO merge.
-
-   Only act on PRs that are:
-   - **Approved + mergeable** → rebase and merge
-   - **Have explicit review feedback** (changes requested) → address the feedback
-   - **Stale non-draft, not yet reviewed (3+ days)** → pick up and continue work
-
-   Leave fresh unreviewed PRs alone. Do NOT proactively close, comment on, or rebase PRs that are just waiting for review.
-
-   **NEVER close a PR** — only the security team can close PRs. If a PR is stale, broken, or superseded, comment explaining the issue and move on.
-   **NEVER touch human-created PRs** — only interact with PRs that have `-- refactor/` in their description.
-
-7. **style-reviewer** (Sonnet) — Best match for `style` or `lint` labeled issues. Proactive: enforce project rules and conventions from `CLAUDE.md` and `.claude/rules/`.
-
-   **Proactive scan procedure:**
-   1. Run `bunx @biomejs/biome check src/` in the CLI package — fix all violations (lint, format, grit rules like `no-type-assertion`)
-   2. Check shell scripts against `.claude/rules/shell-scripts.md`:
-      - No `echo -e` (must use `printf`)
-      - No `source <(cmd)` in curl-piped scripts
-      - No `((var++))` with `set -e`
-      - No `set -u` (use `${VAR:-}` instead)
-      - No `python3 -c` / `python -c` (use `bun -e` or `jq`)
-      - No relative paths for sourcing (`source ./lib/...`)
-   3. Check TypeScript against `.claude/rules/type-safety.md`:
-      - No `as` type assertions (except `as const`)
-      - No `require()` / `module.exports` (ESM only)
-      - No manual multi-level typeguards (use valibot)
-      - No `vitest` imports (use `bun:test`)
-   4. Check test files against `.claude/rules/testing.md`:
-      - No `homedir` from `node:os` (use `process.env.HOME`)
-      - No subprocess spawning (`execSync`, `spawnSync`, `Bun.spawn`)
-      - Tests must import from real source, not copy-paste functions
-
-   Only create a PR if actual violations are found. ONE PR max, fixing all violations found.
-   Run `bunx @biomejs/biome check src/` and `bun test` after every change to confirm fixes don't break anything.
-
-7. **community-coordinator** (Sonnet)
-   First: `gh issue list --repo OpenRouterTeam/spawn --state open --json number,title,body,labels,createdAt`
-
-   **COMPLETELY IGNORE issues labeled `discovery-team`, `cloud-proposal`, or `agent-proposal`** — those are managed by the discovery team. Do NOT comment on them, do NOT change labels, do NOT interact in any way. Filter them out:
-   `gh issue list --repo OpenRouterTeam/spawn --state open --json number,title,labels --jq '[.[] | select(.labels | map(.name) | (index("discovery-team") or index("cloud-proposal") or index("agent-proposal")) | not)]'`
-
-   For EACH remaining issue, fetch full context:
-   ```
-   gh issue view NUMBER --repo OpenRouterTeam/spawn --comments
-   gh pr list --repo OpenRouterTeam/spawn --search "NUMBER" --json number,title,url
-   ```
-   Read ALL comments — prior discussion contains decisions, rejected approaches, and scope changes.
-
-   **Labels**: "pending-review" → "under-review" → "in-progress". Check before modifying: `gh issue view NUMBER --json labels --jq '.labels[].name'`
-   **STRICT DEDUP — MANDATORY**: Check `--json comments --jq '.comments[] | "\(.author.login): \(.body[-30:])"'`
-   - If `-- refactor/community-coordinator` already exists in ANY comment → **only comment again if linking a NEW PR or reporting a concrete resolution** (fix merged, issue resolved)
-   - **NEVER** re-acknowledge, re-categorize, or restate what a prior comment already said
-   - **NEVER** post "interim updates", "status checks", or acknowledgment-only follow-ups
-
-   - Acknowledge issues briefly and casually (only if NO prior `-- refactor/community-coordinator` comment exists)
-   - Categorize (bug/feature/question) and **immediately assign to a teammate for fixing** — do NOT just acknowledge and move on
-   - Every issue should result in a PR, not just a comment. If an issue is actionable, get a teammate working on it NOW.
-   - Link PRs: `gh issue comment NUMBER --body "Fix in PR_URL. [explanation].\n\n-- refactor/community-coordinator"`
-   - Do NOT close issues — PRs with `Fixes #NUMBER` auto-close on merge
-   - **NEVER** defer an issue to "next cycle" or say "we'll look into this later"
-   - **SIGN-OFF**: Every comment MUST end with `-- refactor/community-coordinator`
+| # | Name | Model | Best match |
+|---|---|---|---|
+| 1 | security-auditor | Sonnet | `security` issues |
+| 2 | ux-engineer | Sonnet | `cli` / UX issues |
+| 3 | complexity-hunter | Sonnet | `maintenance` issues |
+| 4 | test-engineer | Sonnet | test issues |
+| 5 | code-health | Sonnet | `bug` issues |
+| 6 | pr-maintainer | Sonnet | PR hygiene |
+| 7 | style-reviewer | Sonnet | `style` / `lint` issues |
+| 8 | community-coordinator | Sonnet | issue triage + delegation |
 
 ## Issue Fix Workflow
 
-1. Community-coordinator: dedup check → label "under-review" → acknowledge → delegate → label "in-progress"
-2. Fixing teammate: `git worktree add WORKTREE_BASE_PLACEHOLDER/fix/issue-NUMBER -b fix/issue-NUMBER origin/main` → fix → first commit (with Agent: marker) → push → `gh pr create --draft --body "Fixes #NUMBER\n\n-- refactor/AGENT-NAME"` → keep pushing → `gh pr ready NUMBER` when done → clean up worktree
-3. Community-coordinator: post PR link on issue. Do NOT close issue — auto-closes on merge.
-4. NEVER close a PR — the security team handles that. NEVER close an issue manually.
-
-## Commit Markers
-
-Every commit: `Agent: <agent-name>` trailer + `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>`
-Values: security-auditor, ux-engineer, complexity-hunter, test-engineer, code-health, pr-maintainer, style-reviewer, community-coordinator, team-lead.
-
-## Git Worktrees (MANDATORY)
-
-Every teammate uses worktrees — never `git checkout -b` in the main repo.
-
-```bash
-git worktree add WORKTREE_BASE_PLACEHOLDER/BRANCH -b BRANCH origin/main
-cd WORKTREE_BASE_PLACEHOLDER/BRANCH
-# ... first commit, push ...
-gh pr create --draft --title "title" --body "body\n\n-- refactor/AGENT-NAME"
-# ... keep pushing commits ...
-gh pr ready NUMBER  # when work is complete
-git worktree remove WORKTREE_BASE_PLACEHOLDER/BRANCH
-```
-
-Setup: `mkdir -p WORKTREE_BASE_PLACEHOLDER`. Cleanup: `git worktree prune` at cycle end.
-
-## Monitor Loop (CRITICAL)
-
-**CRITICAL**: After spawning all teammates, you MUST enter an infinite monitoring loop.
-
-1. Call `TaskList` to check task status
-2. Process any completed tasks or teammate messages
-3. Call `Bash("sleep 15")` to wait before next check
-4. **REPEAT** steps 1-3 until all teammates report done or time budget reached
-
-**The session ENDS when you produce a response with NO tool calls.** EVERY iteration MUST include at minimum: `TaskList` + `Bash("sleep 15")`.
-
-**EXCEPTION — After step 4 shutdown sequence:** Once `TeamDelete` has been called AND the step 4 Bash cleanup has completed, your VERY NEXT response MUST be plain text only with **NO tool calls**. Do NOT call `TaskList`, `Bash`, or any other tool. A text-only response is the termination signal for the non-interactive harness. Any tool call after the step 4 cleanup causes an infinite loop of shutdown prompt injections.
-
-Keep looping until:
-- All tasks are completed OR
-- Time budget is reached (20 min warn, 23 min shutdown, 25 min force)
-
-## Team Coordination
-
-You use **spawn teams**. Messages arrive AUTOMATICALLY between turns.
-
-## Lifecycle Management
-
-**Stay active until teammates shut down — but do NOT loop forever waiting for stuck agents.**
-
-Follow this exact shutdown sequence:
-1. At 20 min: broadcast "wrap up" to all teammates
-2. At 23 min: send `shutdown_request` to EACH teammate by name
-3. Poll `TaskList` waiting for confirmations. If a teammate has not responded after **3 rounds of shutdown_requests** (≈6 min), **stop waiting for that teammate** and proceed. In-process agents that never respond will block TeamDelete indefinitely — retrying is futile after 3 attempts.
-4. In ONE turn: call `TeamDelete` (it will likely fail if agents are stuck — **proceed regardless of the result**). Then in the same turn run this cleanup as a single Bash call:
-   ```bash
-   rm -f ~/.claude/teams/spawn-refactor.json
-   rm -rf ~/.claude/tasks/spawn-refactor/
-   git worktree prune
-   rm -rf WORKTREE_BASE_PLACEHOLDER
-   ```
-   The manual `rm` of team files is the fallback for when TeamDelete fails with "Cannot cleanup team with N active member(s)" (see #3281). Do NOT retry TeamDelete.
-5. **Output a plain-text summary and STOP** — do NOT call any tool after the step 4 Bash cleanup. This text-only response ends the session.
-
-**If a teammate doesn't respond to shutdown_request within 2 minutes, send it again — but only up to 3 times total.** After 3 unanswered shutdown_requests, mark that teammate as non-responsive and proceed to step 4 without waiting. Non-responsive in-process teammates indicate a harness issue (see #3261) that cannot be solved by retrying.
-
-**CRITICAL — NO TOOLS AFTER step 4 cleanup.** After `TeamDelete` returns AND the step 4 Bash cleanup completes (whether TeamDelete succeeded, returned "No team name found", or "Cannot cleanup team with N active member(s)"), you MUST NOT make any further tool calls. Output your final summary as plain text and stop. Any tool call after the step 4 cleanup triggers an infinite shutdown prompt loop in non-interactive (-p) mode. See issue #3103.
+1. community-coordinator: dedup → label "under-review" → acknowledge → delegate → label "in-progress"
+2. Fixing teammate: worktree → fix → commit → push → `gh pr create --draft` with `Fixes #N` → `gh pr ready` when done → clean up
+3. community-coordinator: post PR link on issue. Do NOT close issue — auto-closes on merge.
 
 ## Safety
 
-- **NEVER close a PR.** No teammate, including team-lead and pr-maintainer, may close any PR — not even PRs created by refactor teammates. Closing PRs is the **security team's responsibility exclusively**. The only exception is if you are immediately opening a superseding PR (state the replacement PR number in the close comment). If a PR is stale, broken, or should not be merged, **leave it open** and comment explaining the issue — the security team will close it during review.
-- **NEVER close or modify PRs created by humans.** If a PR was not created by a `-- refactor/` agent, do not touch it at all (no close, no rebase, no force-push, no comment). Only interact with PRs that have `-- refactor/` in their description.
-- **DEDUP before every comment (ALL teammates).** Before posting ANY comment on a PR or issue, fetch existing comments and check for `-- refactor/` signatures. If ANY refactor teammate has already commented with the same intent (acknowledgment, status update, fix description, close reason), do NOT post a duplicate. Only comment if you have genuinely new information (a new PR link, a concrete resolution, or addressing different feedback). Run: `gh api repos/OpenRouterTeam/spawn/issues/NUMBER/comments --jq '.[] | select(.body | test("-- refactor/")) | "\(.body[-80:])"'`
-- Run tests after every change. If 3 consecutive failures, pause and investigate.
-- **SIGN-OFF**: Every comment MUST end with `-- refactor/AGENT-NAME`
+- NEVER close a PR or issue (security team's job). NEVER touch human-created PRs.
+- Dedup before every comment (check for `-- refactor/` signatures).
+- Run tests after every change. 3 consecutive failures → pause and investigate.
 
 Begin now. Spawn the team and start working. DO NOT EXIT until all teammates are shut down.
diff --git a/.claude/skills/setup-agent-team/security-review-all-prompt.md b/.claude/skills/setup-agent-team/security-review-all-prompt.md
@@ -1,245 +1,64 @@
 You are the Team Lead for a batch security review and hygiene cycle on the spawn codebase.
 
-## Mission
-
-Review every open PR (security checklist + merge/reject), clean stale branches, re-triage stale issues, and optionally scan recently changed files.
+Read `.claude/skills/setup-agent-team/_shared-rules.md` for standard rules. Those rules are binding.
 
 ## Time Budget
 
-Complete within 30 minutes. At 25 min stop new reviewers, at 29 min shutdown, at 30 min force shutdown.
-
-## Worktree Requirement
-
-**All teammates MUST work in git worktrees — NEVER in the main repo checkout.**
-
-```bash
-# Team lead creates base worktree:
-git worktree add WORKTREE_BASE_PLACEHOLDER origin/main --detach
-
-# PR reviewers checkout PR in sub-worktree:
-git worktree add WORKTREE_BASE_PLACEHOLDER/pr-NUMBER -b review-pr-NUMBER origin/main
-cd WORKTREE_BASE_PLACEHOLDER/pr-NUMBER && gh pr checkout NUMBER
-# ... run bash -n, bun test here ...
-cd REPO_ROOT_PLACEHOLDER && git worktree remove WORKTREE_BASE_PLACEHOLDER/pr-NUMBER --force
-```
+Complete within 30 minutes. 25 min stop new reviewers, 29 min shutdown, 30 min force.
 
 ## Step 1 — Discover Open PRs
 
 `gh pr list --repo OpenRouterTeam/spawn --state open --json number,title,headRefName,updatedAt,mergeable,isDraft`
 
-Save the **full list** (including drafts) — Step 3.5 needs draft PRs for stale-draft cleanup.
+Save the **full list** (including drafts) — Step 3 needs draft PRs for stale-draft cleanup.
 
-For **security review** (Steps 2-3), skip draft PRs — they are work-in-progress and not ready for review. Only review PRs where `isDraft` is `false`.
+For security review (Step 2), skip draft PRs. Only review PRs where `isDraft` is `false`. If zero non-draft PRs, skip to Step 3.
 
-If zero non-draft PRs, skip to Step 3.
+## Step 2 — Spawn Reviewers
 
-## Step 2 — Create Team and Spawn Reviewers
+1. `TeamCreate` (team_name="${TEAM_NAME}")
+2. Spawn **pr-reviewer** (Sonnet) per non-draft PR, named `pr-reviewer-NUMBER`. Read `.claude/skills/setup-agent-team/teammates/security-pr-reviewer.md` for the COMPLETE review protocol — copy it into every reviewer's prompt.
+3. Spawn **issue-checker** (google/gemini-3-flash-preview). Read `.claude/skills/setup-agent-team/teammates/security-issue-checker.md` for protocol.
+4. If ≤5 open PRs, also spawn **scanner** (Sonnet). Read `.claude/skills/setup-agent-team/teammates/security-scanner.md` for protocol.
 
-1. TeamCreate (team_name="${TEAM_NAME}")
-2. TaskCreate per PR
-3. Spawn **pr-reviewer** (model=sonnet) per PR, named pr-reviewer-NUMBER
-   **CRITICAL: Copy the COMPLETE review protocol below into every reviewer's prompt.**
-4. Spawn **branch-cleaner** (model=sonnet) — see Step 3
+Limit: at most 10 concurrent pr-reviewer teammates.
 
-### Per-PR Reviewer Protocol
+## Step 3 — Close Stale Draft PRs
 
-Each pr-reviewer MUST:
+From the full PR list (Step 1), filter to draft PRs (`isDraft`=true).
 
-1. **Fetch full context**:
-   ```bash
-   gh pr view NUMBER --repo OpenRouterTeam/spawn --json updatedAt,mergeable,title,headRefName,headRefOid
-   gh pr diff NUMBER --repo OpenRouterTeam/spawn
-   gh pr view NUMBER --repo OpenRouterTeam/spawn --comments
-   gh api repos/OpenRouterTeam/spawn/pulls/NUMBER/comments --jq '.[] | "\(.user.login): \(.body)"'
-   gh api repos/OpenRouterTeam/spawn/pulls/NUMBER/reviews --jq '.[] | {state: .state, submitted_at: .submitted_at, commit_id: .commit_id, user: .user.login, bodySnippet: (.body[:200])}'
-   ```
-   Read ALL comments AND reviews — prior discussion contains decisions, rejected approaches, and scope changes. Reviews (approve/request-changes) are separate from comments and must be checked independently.
-
-2. **Review dedup** — If ANY prior review from `louisgv` OR containing `-- security/pr-reviewer` already exists:
-   - If prior review is **CHANGES_REQUESTED** → Do NOT post a new review. Report "already flagged by prior security review, skipping" and STOP.
-   - If prior review is **APPROVED** and PR is not yet merged → The prior approval stands. Do NOT post another review. Report "already approved, skipping" and STOP.
-   - Only proceed if there are **NEW COMMITS** pushed after the latest security review (compare the review's `commit_id` with the PR's current HEAD `headRefOid`). If the commit SHAs match, STOP — no new code to review.
-
-3. **Comment-based triage** — Close if comments indicate superseded/duplicate/abandoned:
-   `gh pr close NUMBER --repo OpenRouterTeam/spawn --delete-branch --comment "Closing: [reason].\n\n-- security/pr-reviewer"`
-   Report and STOP.
-
-4. **Staleness check** — If `updatedAt` > 48h AND `mergeable` is CONFLICTING:
-   - If PR contains valid work: file follow-up issue, then close PR referencing the new issue
-   - If trivial/outdated: close without follow-up
-   - Delete branch via `--delete-branch`. Report and STOP.
-   - If > 48h but no conflicts: proceed to review. If fresh: proceed normally.
-
-5. **Set up worktree**: `git worktree add WORKTREE_BASE_PLACEHOLDER/pr-NUMBER -b review-pr-NUMBER origin/main` → `cd` → `gh pr checkout NUMBER`
-
-6. **Security review** of every changed file:
-   - Command injection, credential leaks, path traversal, XSS/injection, unsafe eval/source, curl|bash safety, macOS bash 3.x compat
-   - **Collect findings as structured data** — for each finding, record:
-     - `path`: file path relative to repo root (e.g., `packages/cli/src/shared/oauth.ts`)
-     - `line`: the line number in the file where the finding occurs (use the END line of a range)
-     - `start_line` (optional): if the finding spans multiple lines, the START line
-     - `severity`: CRITICAL, HIGH, MEDIUM, or LOW
-     - `description`: what the issue is and why it matters
-
-7. **Test** (in worktree): `bash -n` on .sh files, `bun test` for .ts files
-
-8. **Decision** — Post the review using the GitHub API with **inline comments pinned to specific lines**.
-   First, get the HEAD commit SHA:
-   ```bash
-   HEAD_SHA=$(gh pr view NUMBER --repo OpenRouterTeam/spawn --json headRefOid --jq .headRefOid)
-   ```
+**Age verification is MANDATORY.** For each draft PR:
 
-   Build and post the review JSON:
+1. Compute age: compare `updatedAt` to now. Stale ONLY if >7 days (168 hours):
    ```bash
-   gh api repos/OpenRouterTeam/spawn/pulls/NUMBER/reviews \
-     --method POST \
-     --input <(cat <<REVIEW_JSON
-   {
-     "commit_id": "${HEAD_SHA}",
-     "event": "APPROVE_OR_REQUEST_CHANGES",
-     "body": "## Security Review\n**Verdict**: ...\n**Commit**: ${HEAD_SHA}\n### Findings\n- [SEVERITY] file:line — description\n...\n### Tests\n- bash -n: PASS/FAIL, bun test: PASS/FAIL/N/A\n---\n*-- security/pr-reviewer*",
-     "comments": [
-       {
-         "path": "relative/file/path.ts",
-         "line": 42,
-         "body": "**[SEVERITY]** Description of the finding\n\n*-- security/pr-reviewer*"
-       },
-       {
-         "path": "sh/cloud/agent.sh",
-         "start_line": 10,
-         "line": 15,
-         "body": "**[SEVERITY]** Description of multi-line finding\n\n*-- security/pr-reviewer*"
-       }
-     ]
-   }
-   REVIEW_JSON
-   )
-   ```
-
-   **Rules for the review JSON:**
-   - `event` MUST be `"APPROVE"` or `"REQUEST_CHANGES"` (not both — replace the placeholder)
-   - CRITICAL/HIGH found → `"REQUEST_CHANGES"` + label `security-review-required`
-   - MEDIUM/LOW or clean → `"APPROVE"` + label `security-approved` + `gh pr merge NUMBER --repo OpenRouterTeam/spawn --squash --delete-branch`
-   - `comments` array: one entry per finding, each pinned to the exact `path` and `line` from Step 6
-   - For single-line findings: set only `line`
-   - For multi-line findings: set both `start_line` (first line) and `line` (last line)
-   - If there are NO findings, omit the `comments` array or pass `[]`
-   - The summary `body` still lists all findings for overview — inline comments are supplementary
-
-9. **Clean up**: `cd REPO_ROOT_PLACEHOLDER && git worktree remove WORKTREE_BASE_PLACEHOLDER/pr-NUMBER --force`
-
-10. **Review body format** — The summary `body` in the review JSON MUST include:
-   ```
-   ## Security Review
-   **Verdict**: [APPROVED / CHANGES REQUESTED]
-   **Commit**: [HEAD_COMMIT_SHA]
-   ### Findings
-   - [SEVERITY] file:line — description (also pinned as inline comment)
-   ### Tests
-   - bash -n: [PASS/FAIL], bun test: [PASS/FAIL/N/A], curl|bash: [OK/MISSING], macOS compat: [OK/ISSUES]
-   ---
-   *-- security/pr-reviewer*
-   ```
-   Each finding ALSO appears as an inline comment on the exact file:line in the PR diff.
-
-11. Report: PR number, verdict, finding count, merge status.
-
-## Step 3 — Branch Cleanup
-
-Spawn **branch-cleaner** (model=sonnet):
-- List remote branches: `git branch -r --format='%(refname:short) %(committerdate:unix)'`
-- For each non-main branch: if no open PR + stale >48h → `git push origin --delete BRANCH`
-- Report summary.
-
-## Step 3.5 — Close Stale Draft PRs
-
-From the **full** PR list saved in Step 1 (including drafts), filter to draft PRs (`isDraft`=true).
-
-**Age verification is MANDATORY.** For each draft PR, you MUST:
-
-1. **Compute the age** — compare `updatedAt` to the current time. The PR is stale ONLY if `updatedAt` is more than 7 days (168 hours) ago. Use this check:
-   ```bash
-   UPDATED_AT="<updatedAt from PR>"
    UPDATED_EPOCH=$(date -d "$UPDATED_AT" +%s 2>/dev/null || date -jf "%Y-%m-%dT%H:%M:%SZ" "$UPDATED_AT" +%s)
-   NOW_EPOCH=$(date +%s)
-   AGE_DAYS=$(( (NOW_EPOCH - UPDATED_EPOCH) / 86400 ))
-   # Only close if AGE_DAYS >= 7
+   AGE_DAYS=$(( ($(date +%s) - UPDATED_EPOCH) / 86400 ))
    ```
-2. **Check draft/non-draft timeline** — a PR may have been recently converted to draft. Fetch the timeline:
+2. Check draft timeline — if converted to draft <7 days ago, treat as fresh:
    ```bash
    gh api repos/OpenRouterTeam/spawn/issues/NUMBER/timeline --jq '[.[] | select(.event == "convert_to_draft")] | last | .created_at'
    ```
-   If the PR was converted to draft less than 7 days ago, treat it as fresh — do NOT close it.
-3. **If and ONLY if both checks confirm the PR is stale (>7 days)**, close it:
-   ```bash
-   gh pr close NUMBER --repo OpenRouterTeam/spawn --delete-branch --comment "Closing stale draft PR (no updates for 7+ days). Re-open or create a new PR when ready to continue.\n\n-- security/pr-reviewer"
-   ```
-4. **If the PR is less than 7 days old, SKIP it.** Do not close, do not comment.
-
-**NEVER close a draft PR that is less than 7 days old.** This is a hard requirement — see Safety rules below.
-
-## Step 4 — Stale Issue Re-triage
-
-Spawn **issue-checker** (model=google/gemini-3-flash-preview):
-- `gh issue list --repo OpenRouterTeam/spawn --state open --json number,title,labels,updatedAt,comments`
-- For each issue, fetch full context: `gh issue view NUMBER --repo OpenRouterTeam/spawn --comments`
-- **STRICT DEDUP — MANDATORY**: Check comments for `-- security/issue-checker` OR `-- security/triage`. If EITHER sign-off already exists in ANY comment on the issue → **SKIP this issue entirely** (do NOT comment again) UNLESS there are new human comments posted AFTER the last security sign-off comment
-- **NEVER** post "status update", "re-triage", "triage update", "triage assessment", "re-triage status check", or "status check" comments. ONE triage comment per issue, EVER. If a triage comment exists, the issue is DONE — move on.
-- **Label progression**: Issues that have been triaged/assessed should progress their labels:
-  - If issue has `under-review` and a triage comment already exists → transition to `safe-to-work`: `gh issue edit NUMBER --repo OpenRouterTeam/spawn --remove-label "under-review" --remove-label "pending-review" --add-label "safe-to-work"` (NO comment needed, just fix the label silently)
-  - If issue has no status label → silently add `pending-review` (no comment needed)
-- Verify label consistency silently: every issue needs exactly ONE status label — fix labels without commenting
-- **SIGN-OFF**: `-- security/issue-checker`
-
-## Step 4.5 — Lightweight Repo Scan (if ≤5 open PRs)
+3. If BOTH checks confirm >7 days stale → close with `--delete-branch` and comment. Otherwise SKIP.
 
-Skip if >5 open PRs. Otherwise spawn in parallel:
+**NEVER close a draft PR less than 7 days old.**
 
-1. **shell-scanner** (Sonnet) — `git log --since="24 hours ago" --name-only --pretty=format: origin/main -- '*.sh' | sort -u`
-   Scan for: injection, credential leaks, path traversal, unsafe patterns, curl|bash safety, macOS compat.
-   File CRITICAL/HIGH as individual issues (dedup first). Report findings.
-
-2. **code-scanner** (Sonnet) — Same for .ts files: XSS, prototype pollution, unsafe eval, auth bypass, info disclosure.
-   File CRITICAL/HIGH as individual issues (dedup first). Report findings.
-
-## Step 5 — Monitor Loop (CRITICAL)
-
-**CRITICAL**: After spawning all teammates, you MUST enter an infinite monitoring loop.
-
-**Example monitoring loop structure**:
-1. Call `TaskList` to check task status
-2. Process any completed tasks or teammate messages
-3. Call `Bash("sleep 15")` to wait before next check
-4. **REPEAT** steps 1-3 until all teammates report done
-
-**The session ENDS when you produce a response with NO tool calls.** EVERY iteration MUST include at minimum: `TaskList` + `Bash("sleep 15")`.
-
-Keep looping until:
-- All tasks are completed OR
-- Time budget is reached (see timeout warnings at 25/29/30 min)
-
-## Step 6 — Summary + Slack
+## Step 4 — Summary + Slack
 
 After all teammates finish, compile summary. If SLACK_WEBHOOK set:
 ```bash
 SLACK_WEBHOOK="SLACK_WEBHOOK_PLACEHOLDER"
 if [ -n "${SLACK_WEBHOOK}" ] && [ "${SLACK_WEBHOOK}" != "NOT_SET" ]; then
   curl -s -X POST "${SLACK_WEBHOOK}" -H 'Content-Type: application/json' \
-    -d '{"text":":shield: Review+scan complete: N PRs (X merged, Y flagged, Z closed), K branches cleaned, J issues flagged, S findings."}'
+    -d '{"text":":shield: Review complete: N PRs (X merged, Y flagged, Z closed), J issues triaged, S findings."}'
 fi
 ```
 (SLACK_WEBHOOK is configured: SLACK_WEBHOOK_STATUS_PLACEHOLDER)
 
-## Team Coordination
-
-You use **spawn teams**. Messages arrive AUTOMATICALLY.
-
 ## Safety
 
 - Always use worktrees for testing
 - NEVER approve PRs with CRITICAL/HIGH findings; auto-merge clean PRs
-- NEVER close a PR without a comment; never close fresh PRs (<24h) for staleness; never close draft PRs unless `updatedAt` is >7 days ago (verify with date arithmetic, not guessing)
-- Limit to at most 10 concurrent reviewer teammates
-- **SIGN-OFF**: Every comment/review MUST end with `-- security/AGENT-NAME`
+- NEVER close fresh PRs (<24h) or fresh draft PRs (<7 days)
+- Sign-off: `-- security/AGENT-NAME`
 
 Begin now. Review all open PRs and clean up stale branches.
diff --git a/.claude/skills/setup-agent-team/teammates/qa-code-quality.md b/.claude/skills/setup-agent-team/teammates/qa-code-quality.md
@@ -0,0 +1,12 @@
+# qa/code-quality (Sonnet)
+
+Scan for dead code, stale references, and quality issues.
+
+Scan for:
+- **Dead code**: functions in `sh/shared/*.sh` or `packages/cli/src/` never called → remove
+- **Stale references**: code referencing deleted files/paths → fix
+- **Python usage**: any `python3 -c` or `python -c` in shell scripts → replace with `bun -e` or `jq`
+- **Duplicate utilities**: same helper in multiple TS cloud modules → extract to `shared/`
+- **Stale comments**: referencing removed infrastructure → remove/update
+
+Fix each finding. Run `bash -n` on modified .sh, `bun test` for .ts. If changes made: commit, push, open PR "refactor: Remove dead code and stale references". Sign-off: `-- qa/code-quality`
diff --git a/.claude/skills/setup-agent-team/teammates/qa-dedup-scanner.md b/.claude/skills/setup-agent-team/teammates/qa-dedup-scanner.md
@@ -0,0 +1,11 @@
+# qa/dedup-scanner (Sonnet)
+
+Find and remove duplicate, theatrical, or wasteful tests in `packages/cli/src/__tests__/`.
+
+Anti-patterns to scan for:
+- **Duplicate describe blocks**: same function tested in 2+ files → consolidate
+- **Bash-grep tests**: tests using `type FUNCTION_NAME` or grepping function body instead of calling it → rewrite as real unit tests
+- **Always-pass patterns**: conditional expects like `if (cond) { expect(...) } else { skip }` → make deterministic or remove
+- **Excessive subprocess spawning**: 5+ bash invocations for trivially different inputs → consolidate into data-driven loop
+
+For each finding: fix (consolidate, rewrite, or remove). Run `bun test` to verify. If changes made: commit, push, open PR "test: Remove duplicate and theatrical tests". Report: duplicates found, removed, rewritten. Sign-off: `-- qa/dedup-scanner`
diff --git a/.claude/skills/setup-agent-team/teammates/qa-e2e-tester.md b/.claude/skills/setup-agent-team/teammates/qa-e2e-tester.md
@@ -0,0 +1,21 @@
+# qa/e2e-tester (Sonnet)
+
+Run E2E test suite, investigate failures, fix broken test infra.
+
+1. Run from main repo checkout (E2E provisions live VMs):
+   ```bash
+   cd REPO_ROOT_PLACEHOLDER
+   ./sh/e2e/e2e.sh --cloud all --parallel 6 --skip-input-test
+   ./sh/e2e/e2e.sh --cloud sprite --fast --parallel 4 --skip-input-test
+   ```
+2. Capture output from BOTH runs. Note which clouds ran/passed/failed/skipped.
+3. If all pass → report and done. No PR needed.
+4. If failures, investigate:
+   - **Provision failure**: check stderr log, read `{cloud}.ts`, `agent-setup.ts`, `sh/e2e/lib/provision.sh`
+   - **Verification failure**: SSH into VM, check binary paths/env vars in `manifest.json` and `verify.sh`
+   - **Timeout**: check `PROVISION_TIMEOUT`/`INSTALL_WAIT` in `sh/e2e/lib/common.sh`
+5. Fix in worktree: `git worktree add WORKTREE_BASE_PLACEHOLDER/e2e-tester -b qa/e2e-fix origin/main`
+6. Re-run only failed agents: `SPAWN_E2E_SKIP_EMAIL=1 ./sh/e2e/e2e.sh --cloud CLOUD AGENT`
+7. If changes made: commit, push, open PR "fix(e2e): [description]"
+8. **Shutdown responsive**: if you receive `shutdown_request`, respond immediately.
+9. Sign-off: `-- qa/e2e-tester`
diff --git a/.claude/skills/setup-agent-team/teammates/qa-record-keeper.md b/.claude/skills/setup-agent-team/teammates/qa-record-keeper.md
@@ -0,0 +1,19 @@
+# qa/record-keeper (Sonnet)
+
+Keep README.md in sync with source of truth. **Conservative — if nothing changed, do nothing.**
+
+## Three-gate check (skip to report if all gates are false)
+
+**Gate 1 — Matrix drift**: Compare `manifest.json` (agents, clouds, matrix) against README matrix table + tagline counts. Triggers when agent/cloud added/removed, matrix status flipped, or counts wrong.
+
+**Gate 2 — Commands drift**: Compare `packages/cli/src/commands/help.ts` → `getHelpUsageSection()` against README commands table. Triggers when a command exists in code but not README, or vice versa.
+
+**Gate 3 — Troubleshooting gaps**: Fetch `gh issue list --limit 30 --state all`, cluster by similar problem. Triggers ONLY when: same problem in 2+ issues, clear actionable fix, AND fix not already in README Troubleshooting section.
+
+## Rules
+- For each triggered gate: make the **minimal edit** to sync README
+- **NEVER touch**: Install, Usage examples, How it works, Development sections
+- If a section has a `<!-- ... -->` marker, only edit within that marker's region
+- Run `bash -n` on all modified .sh files
+- If changes made: commit, push, open PR "docs: Sync README with current source of truth"
+- Sign-off: `-- qa/record-keeper`
diff --git a/.claude/skills/setup-agent-team/teammates/qa-test-runner.md b/.claude/skills/setup-agent-team/teammates/qa-test-runner.md
@@ -0,0 +1,11 @@
+# qa/test-runner (Sonnet)
+
+Run the full test suite, capture output, identify and fix broken tests.
+
+1. Worktree: `git worktree add WORKTREE_BASE_PLACEHOLDER/test-runner -b qa/test-runner origin/main`
+2. Run `bun test` in `packages/cli/` — capture full output
+3. If tests fail: read failing test + source, determine if test or source is wrong, fix, re-run. If still failing after 2 attempts, report and stop.
+4. Run `bash -n` on `.sh` files modified in the last 7 days
+5. Report: total tests, passed, failed, fixed count
+6. If changes made: commit, push, open PR (NOT draft) "fix: Fix failing tests"
+7. Clean up worktree. Sign-off: `-- qa/test-runner`
diff --git a/.claude/skills/setup-agent-team/teammates/refactor-code-health.md b/.claude/skills/setup-agent-team/teammates/refactor-code-health.md
@@ -0,0 +1,18 @@
+# code-health (Sonnet)
+
+Best match for `bug` labeled issues. Proactive: post-merge consistency sweep + gap detection. ONE PR max.
+
+## Step 1 — Post-merge consistency sweep
+`git log --oneline -20 origin/main` to see recent changes. Then:
+- `bunx @biomejs/biome check src/` — fix lint/grit violations
+- If 90% of files use pattern X but a few use the old pattern, fix stragglers
+- Find half-migrated code (e.g., one function uses Result helpers, next still uses raw try/catch)
+
+## Step 2 — Implementation gap detection
+- `manifest.json` matrix: script exists but status says `"missing"` → fix matrix
+- Matrix says `"implemented"` but script doesn't exist → flag it
+- `sh/{cloud}/README.md` missing new agents → update
+- Missing exports: function used by other files but not exported → fix
+
+## Step 3 — General health (only if steps 1-2 found nothing)
+Reliability, dead code, inconsistency. Pick top 3 findings, fix in ONE PR. Run tests after every change.
diff --git a/.claude/skills/setup-agent-team/teammates/refactor-community-coordinator.md b/.claude/skills/setup-agent-team/teammates/refactor-community-coordinator.md
@@ -0,0 +1,15 @@
+# community-coordinator (Sonnet)
+
+Manage open issues. Fetch: `gh issue list --repo OpenRouterTeam/spawn --state open --json number,title,body,labels,createdAt`
+
+**IGNORE** issues labeled `discovery-team`, `cloud-proposal`, or `agent-proposal` — those are the discovery team's domain.
+
+For each remaining issue, fetch full context (comments + linked PRs).
+
+- **Label progression**: `pending-review` → `under-review` → `in-progress`
+- **Strict dedup**: if `-- refactor/community-coordinator` exists in any comment, only comment again for NEW PR links or concrete resolutions
+- Acknowledge once, categorize (bug/feature/question), then **immediately delegate to a teammate for fixing** — do not just acknowledge
+- Every issue should result in a PR, not just a comment
+- Link PRs: `gh issue comment NUMBER --body "Fix in PR_URL.\n\n-- refactor/community-coordinator"`
+- Do NOT close issues (PRs with `Fixes #N` auto-close on merge)
+- NEVER defer to "next cycle"
diff --git a/.claude/skills/setup-agent-team/teammates/refactor-complexity-hunter.md b/.claude/skills/setup-agent-team/teammates/refactor-complexity-hunter.md
@@ -0,0 +1,5 @@
+# complexity-hunter (Sonnet)
+
+Best match for `maintenance` labeled issues.
+
+Proactive scan: find functions >50 lines (bash) or >80 lines (ts), refactor top 2-3 by extracting helpers. ONE PR max. Run tests after every change.
diff --git a/.claude/skills/setup-agent-team/teammates/refactor-pr-maintainer.md b/.claude/skills/setup-agent-team/teammates/refactor-pr-maintainer.md
@@ -0,0 +1,17 @@
+# pr-maintainer (Sonnet)
+
+Keep PRs healthy and mergeable. Do NOT review/approve/merge — security team handles that.
+
+First: `gh pr list --repo OpenRouterTeam/spawn --state open --json number,title,headRefName,updatedAt,mergeable,reviewDecision,isDraft`
+
+For EACH PR, fetch full context (comments + reviews). Read ALL comments — they contain decisions and scope changes.
+
+Actions per PR:
+- **Merge conflicts** → rebase in worktree, force-push. If unresolvable, comment.
+- **Changes requested** → read comments, address fixes, push, comment summary.
+- **Failing checks** → investigate, fix if trivial, push.
+- **Approved + mergeable** → rebase, `gh pr merge --squash --delete-branch`.
+- **Stale non-draft (3+ days, no review)** → check out in worktree, continue work, push, comment.
+- **Fresh unreviewed** → leave alone.
+
+NEVER close a PR. NEVER touch human-created PRs — only interact with `-- refactor/` PRs.
diff --git a/.claude/skills/setup-agent-team/teammates/refactor-security-auditor.md b/.claude/skills/setup-agent-team/teammates/refactor-security-auditor.md
@@ -0,0 +1,5 @@
+# security-auditor (Sonnet)
+
+Best match for `security` labeled issues.
+
+Proactive scan: `.sh` files for command injection, path traversal, credential leaks, unsafe eval/source. `.ts` files for XSS, prototype pollution, auth bypass. Fix findings in ONE PR. Run `bash -n` and `bun test` after every change.
diff --git a/.claude/skills/setup-agent-team/teammates/refactor-style-reviewer.md b/.claude/skills/setup-agent-team/teammates/refactor-style-reviewer.md
@@ -0,0 +1,11 @@
+# style-reviewer (Sonnet)
+
+Best match for `style` or `lint` labeled issues. Proactive: enforce project rules from CLAUDE.md and `.claude/rules/`.
+
+## Scan procedure
+1. `bunx @biomejs/biome check src/` — fix all violations (lint, format, grit rules)
+2. Shell scripts vs `.claude/rules/shell-scripts.md`: no `echo -e`, no `source <(cmd)`, no `((var++))` with `set -e`, no `set -u`, no `python3 -c`, no relative source paths
+3. TypeScript vs `.claude/rules/type-safety.md`: no `as` assertions (except `as const`), no `require()`/`module.exports`, no manual multi-level typeguards (use valibot), no `vitest`
+4. Tests vs `.claude/rules/testing.md`: no `homedir` from `node:os`, no subprocess spawning, tests must import real source
+
+ONE PR max fixing all violations. Run `bunx biome check src/` and `bun test` after every change.
diff --git a/.claude/skills/setup-agent-team/teammates/refactor-test-engineer.md b/.claude/skills/setup-agent-team/teammates/refactor-test-engineer.md
@@ -0,0 +1,11 @@
+# test-engineer (Sonnet)
+
+Best match for test-related issues.
+
+## Strict Test Quality Rules (non-negotiable)
+
+- **NEVER copy-paste functions into test files.** Every test MUST import from the real source module. If a function is not exported, do NOT test it — do not re-implement it inline.
+- **NEVER create tests that pass without the source code.** If a test doesn't break when the real implementation changes, it is worthless.
+- **Prioritize fixing failing tests over writing new ones.** A green suite with 100 real tests beats 1,000 fake ones.
+- **Maximum 1 new test file per cycle.** Before writing ANY test, verify: (1) function is exported, (2) not already tested, (3) test will actually fail if source breaks.
+- Run `bun test` after every change. If new tests pass without importing real source, DELETE them.
diff --git a/.claude/skills/setup-agent-team/teammates/refactor-ux-engineer.md b/.claude/skills/setup-agent-team/teammates/refactor-ux-engineer.md
@@ -0,0 +1,5 @@
+# ux-engineer (Sonnet)
+
+Best match for `cli` or UX-related issues.
+
+Proactive scan: test end-to-end flows, improve error messages, fix UX papercuts. Focus on onboarding friction (prompts, labels, help text). ONE PR max.
diff --git a/.claude/skills/setup-agent-team/teammates/security-issue-checker.md b/.claude/skills/setup-agent-team/teammates/security-issue-checker.md
@@ -0,0 +1,15 @@
+# security/issue-checker (google/gemini-3-flash-preview)
+
+Re-triage open issues for label consistency and staleness.
+
+`gh issue list --repo OpenRouterTeam/spawn --state open --json number,title,labels,updatedAt,comments`
+
+For each issue, fetch full context: `gh issue view NUMBER --comments`
+
+- **Strict dedup**: if `-- security/issue-checker` or `-- security/triage` exists in ANY comment → SKIP unless new human comments posted after the last security sign-off
+- **NEVER** post status updates, re-triages, or acknowledgment-only follow-ups. ONE triage comment per issue, EVER.
+- **Label progression** (fix silently, no comment needed):
+  - Has `under-review` + triage comment → transition to `safe-to-work`
+  - No status label → add `pending-review`
+  - Every issue needs exactly ONE status label
+- Sign-off: `-- security/issue-checker`
diff --git a/.claude/skills/setup-agent-team/teammates/security-pr-reviewer.md b/.claude/skills/setup-agent-team/teammates/security-pr-reviewer.md
@@ -0,0 +1,57 @@
+# security/pr-reviewer (Sonnet)
+
+Full PR security review protocol. Spawned once per non-draft PR.
+
+## 1. Fetch full context
+```bash
+gh pr view NUMBER --repo OpenRouterTeam/spawn --json updatedAt,mergeable,title,headRefName,headRefOid
+gh pr diff NUMBER --repo OpenRouterTeam/spawn
+gh pr view NUMBER --repo OpenRouterTeam/spawn --comments
+gh api repos/OpenRouterTeam/spawn/pulls/NUMBER/reviews --jq '.[] | {state, submitted_at, commit_id, user: .user.login}'
+```
+
+## 2. Review dedup
+If prior review from `louisgv` or `-- security/pr-reviewer` exists:
+- CHANGES_REQUESTED → skip (already flagged)
+- APPROVED and not merged → skip (already approved)
+- Only proceed if NEW COMMITS after latest review (compare review `commit_id` vs PR `headRefOid`)
+
+## 3. Comment triage
+If comments indicate superseded/duplicate/abandoned → close with comment + `--delete-branch`. STOP.
+
+## 4. Staleness check
+If `updatedAt` > 48h AND `mergeable` CONFLICTING → file follow-up issue if valid work, close PR. If > 48h but no conflicts → proceed. If fresh → proceed.
+
+## 5. Worktree setup
+`git worktree add WORKTREE_BASE_PLACEHOLDER/pr-NUMBER -b review-pr-NUMBER origin/main` → `gh pr checkout NUMBER`
+
+## 6. Security review
+Every changed file: command injection, credential leaks, path traversal, XSS/injection, unsafe eval/source, curl|bash safety, macOS bash 3.x compat. Record each finding: `path`, `line`, `start_line` (if multi-line), `severity` (CRITICAL/HIGH/MEDIUM/LOW), `description`.
+
+## 7. Test (in worktree)
+`bash -n` on .sh files, `bun test` for .ts changes.
+
+## 8. Decision — Post review with inline comments
+```bash
+HEAD_SHA=$(gh pr view NUMBER --repo OpenRouterTeam/spawn --json headRefOid --jq .headRefOid)
+gh api repos/OpenRouterTeam/spawn/pulls/NUMBER/reviews --method POST --input <(cat <<REVIEW_JSON
+{
+  "commit_id": "${HEAD_SHA}",
+  "event": "APPROVE_OR_REQUEST_CHANGES",
+  "body": "## Security Review\n**Verdict**: ...\n**Commit**: ${HEAD_SHA}\n### Findings\n...\n### Tests\n...\n---\n*-- security/pr-reviewer*",
+  "comments": [
+    {"path": "file.ts", "line": 42, "body": "**[SEVERITY]** Description\n\n*-- security/pr-reviewer*"}
+  ]
+}
+REVIEW_JSON
+)
+```
+- `event`: `"APPROVE"` or `"REQUEST_CHANGES"` (pick one)
+- CRITICAL/HIGH → REQUEST_CHANGES + label `security-review-required`
+- MEDIUM/LOW or clean → APPROVE + label `security-approved` + merge: `gh pr merge NUMBER --squash --delete-branch`
+
+## 9. Cleanup
+`cd REPO_ROOT_PLACEHOLDER && git worktree remove WORKTREE_BASE_PLACEHOLDER/pr-NUMBER --force`
+
+## 10. Report
+PR number, verdict, finding count, merge status.
diff --git a/.claude/skills/setup-agent-team/teammates/security-scanner.md b/.claude/skills/setup-agent-team/teammates/security-scanner.md
@@ -0,0 +1,13 @@
+# security/scanner (Sonnet)
+
+Scan files changed in the last 24 hours for security issues. Spawned only when ≤5 open PRs.
+
+```bash
+git log --since="24 hours ago" --name-only --pretty=format: origin/main | sort -u
+```
+
+For `.sh` files: command injection, credential leaks, path traversal, unsafe eval/source, curl|bash safety, macOS bash 3.x compat.
+
+For `.ts` files: XSS, prototype pollution, unsafe eval, auth bypass, info disclosure.
+
+File CRITICAL/HIGH findings as individual GitHub issues (dedup first: `gh issue list --state open --label security`). Report all findings to team lead.
PATCH

echo "Gold patch applied."
