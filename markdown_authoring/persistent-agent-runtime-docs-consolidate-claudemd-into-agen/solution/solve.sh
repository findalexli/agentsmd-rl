#!/usr/bin/env bash
set -euo pipefail

cd /workspace/persistent-agent-runtime

# Idempotency guard
if grep -qF "**Non-negotiable when installed.** At conversation start, invoke `using-superpow" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,21 +1,17 @@
 # AGENTS.md — Project Navigation
 
 ## Project
-Cloud-Native Persistent Agent Runtime — durable execution for AI agents. See [ARCHITECTURE.md](./ARCHITECTURE.md) for key decisions and tech stack.
+Cloud-Native Persistent Agent Runtime — durable execution for AI agents.
+
+**Stack:** Java + Spring Boot (API) · Python (worker) · TypeScript + React 19 + Vite (Console) · PostgreSQL · LangGraph. See [ARCHITECTURE.md](./ARCHITECTURE.md) for full stack and rationale.
 
 ## Documentation Map
 - `docs/product-specs/` — What the system should do (vision, user stories, core concepts)
-- `docs/design-docs/` — How to build it (phase-based design documents)
-  - `docs/design-docs/core-beliefs.md` — Key architectural invariants
-  - `docs/design-docs/phase-N/design.md` — Primary design doc per phase
-  - `docs/design-docs/langfuse/` — Langfuse customer integration design
-  - `docs/design-docs/agent-capabilities/` — Sandbox, artifacts, and file input design
-  - `docs/design-docs/phase-3-plus/` — Forward-looking design notes
-- `docs/exec-plans/` — Implementation plans
-  - `docs/exec-plans/active/` — Plans currently being executed
-  - `docs/exec-plans/completed/` — Archived completed plans
-- `docs/references/` — External docs (placeholder, currently empty)
-- `docs/generated/` — Auto-generated documentation (placeholder, currently empty)
+- `docs/design-docs/` — How to build it
+  - `core-beliefs.md` — Architectural invariants
+  - `phase-N/design.md` — Primary design doc per phase
+  - `langfuse/`, `agent-capabilities/`, `phase-3-plus/` — Cross-cutting and forward-looking
+- `docs/exec-plans/active/` and `docs/exec-plans/completed/` — Implementation plans
 - `docs/LOCAL_DEVELOPMENT.md` — Local setup and environment
 
 ## Services
@@ -24,59 +20,71 @@ Cloud-Native Persistent Agent Runtime — durable execution for AI agents. See [
 - `services/worker-service/` — Python worker ([README](services/worker-service/README.md))
 - `services/model-discovery/` — Model discovery service
 
-## New Phase Workflow
+## Common Commands
+
+```bash
+make help        # list all targets with descriptions
+make init        # first-time setup
+make install     # install deps across services
+make test        # unit tests (fast, no infra)
+make e2e-test    # E2E on isolated infra (DB port 55433)
+make test-all    # unit + E2E
+make start       # live stack: Console :5173, API :8080
+make stop        # stop live stack
+make status      # background-target status
 
-When starting a new phase (e.g., Phase 3), follow this order:
+# Python (worker) — always use the pinned venv:
+services/worker-service/.venv/bin/python ...
+```
+
+## New Phase Workflow
 
-1. **Spec first** → Add Phase 3 sections to the existing files in `docs/product-specs/` (vision.md, user-stories.md, core-concepts.md). Tracks are subsections within those files.
-2. **Design second** → Create `docs/design-docs/phase-3/design.md` as the primary design doc
-3. **Plan third** → Create `docs/exec-plans/active/phase-3/` with plan.md, progress.md, and agent_tasks/
-4. **Execute** → Implement per the task specs in agent_tasks/
+1. **Spec** → Add phase sections to `docs/product-specs/` (vision.md, user-stories.md, core-concepts.md)
+2. **Design** → Create `docs/design-docs/phase-N/design.md`
+3. **Plan** → Create `docs/exec-plans/active/phase-N/` with plan.md, progress.md, agent_tasks/
+4. **Execute** → Implement per the task specs
+5. **Archive** → Move `active/phase-N/` → `completed/phase-N/`
+6. **Update status** → Update [STATUS.md](./STATUS.md)
 
 ### Task spec detail level
 
-Task specs in `agent_tasks/` define **what** to build, not **how** to build it. They are contracts, not implementation blueprints.
+Task specs in `agent_tasks/` are contracts, not implementation blueprints. They define **what**, not **how**.
 
-**Include:** inputs, outputs, API contracts, schema changes, affected files, dependency graph, constraints (what NOT to do), existing code to reference as patterns, and acceptance criteria as observable behaviors.
+**Include:** inputs, outputs, API contracts, schema changes, affected files, dependency graph, constraints, existing code to reference as patterns, acceptance criteria as observable behaviors.
 
-**Do NOT include:** full source code, copy-paste SQL/Java/Python/TypeScript blocks, or line-by-line implementation. The implementing agent should read existing code, understand patterns, and write the implementation itself. Over-specified plans produce copy-paste work that misses integration bugs and becomes stale if the codebase evolves.
-5. **Archive** → When done, move `docs/exec-plans/active/phase-3/` → `docs/exec-plans/completed/phase-3/`
-6. **Update status** → Update [STATUS.md](./STATUS.md) to reflect the phase/track state
+**Exclude:** full source code or paste-ready SQL/Java/Python/TypeScript. The implementing agent reads existing code and writes the implementation itself — over-specified plans produce copy-paste work that misses integration bugs.
 
 ### Tracks (chunking large phases)
 
-When a phase contains too much work for a single planning cycle (e.g., 40+ tasks), split it into sequential tracks of ~7-10 tasks each. Tracks break a phase into manageable batches.
+When a phase exceeds ~40 tasks, split into sequential tracks of ~7-10 tasks each. Tracks are spec subsections, may add `track-N-<name>.md` design docs, and each get their own `exec-plans/` subdirectory. Archive per-track; a phase is complete when all tracks are archived. See `exec-plans/completed/phase-2/` for a worked example.
 
-- **Spec**: Phase sections within the global files in `docs/product-specs/` — tracks are subsections
-- **Design**: One `design.md` per phase as the overview. Add `track-N-<name>.md` alongside for track-specific design detail
-- **Exec plans**: Each track gets its own subdirectory with plan.md, progress.md, and agent_tasks/
-- **Archiving**: Move each track to `completed/` as it finishes. A phase is complete when all its tracks are archived.
+## Agent Skills (Superpowers)
 
-Example (Phase 2 has 3 tracks):
-- Spec: Phase 2 sections in `product-specs/vision.md`, `product-specs/user-stories.md`, etc.
-- Design: `design-docs/phase-2/design.md` + `design-docs/phase-2/track-1-agent-control-plane.md` + `design-docs/phase-2/track-3-scheduler-and-budgets.md` + `design-docs/phase-2/track-4-custom-tool-runtime.md`
-- Cross-cutting: `design-docs/agent-capabilities/design.md` + `design-docs/langfuse/design.md`
-- Plans: `exec-plans/completed/phase-2/track-1/` · `exec-plans/completed/phase-2/track-2/` · `exec-plans/completed/phase-2/track-3/` · `exec-plans/completed/phase-2/track-4/`
+**Non-negotiable when installed.** At conversation start, invoke `using-superpowers` via the `Skill` tool before any other action — including reading files or asking clarifying questions. Before every task, invoke any relevant skill (debugging, TDD, brainstorming, code review). If there's even a 1% chance a skill applies, invoke it. "This is a simple question" and "let me explore first" are not valid reasons to skip — the skill tells you *how* to explore.
 
-## Current Status
+Priority: user instructions > skills > default behavior.
 
-See [STATUS.md](./STATUS.md) for phase-level tracking and links to each track's progress.
+## Boundaries
 
-## Agent Skills (Superpowers)
+**Never:**
+- Use bare `python3` or `uv run` for worker code — always the pinned venv at `services/worker-service/.venv/` (§Local Validation Notes)
+- Point tests at the dev DB (port 55432) — tests use `par-e2e-postgres` on 55433 (§Local Validation Notes)
+- Link to PRs in third-party repos from commits or PR descriptions (§External Pull Request References)
+- Commit or open a PR with unverified Console UI (§Browser Verification (Console Changes))
+- Merge without running the narrowest-scope tests that cover your change (§Testing (Mandatory))
 
-**Non-negotiable:** If superpowers skills are installed, agents MUST use them.
+**Ask first:**
+- Force-push to `main`/`master`, destructive DB operations, shared CI/infra changes, anything that deletes data
 
-1. **At conversation start**, invoke the `using-superpowers` skill via the `Skill` tool. This is mandatory before any other action — including reading files, exploring the codebase, or asking clarifying questions.
-2. **Before every task**, check if a relevant skill applies (debugging, TDD, brainstorming, code review, etc.) and invoke it via the `Skill` tool. If there is even a 1% chance a skill is relevant, invoke it.
-3. **Priority order**: User instructions > Superpowers skills > Default system behavior.
-4. **Do not rationalize skipping skills.** "This is just a simple question" or "Let me explore first" are not valid reasons. The skill tells you *how* to explore or answer.
+**Always:**
+- Invoke relevant superpowers skills (§Agent Skills (Superpowers))
+- Use `isolation: "worktree"` when parallel subagents could touch overlapping files (§Parallel Subagent Safety)
 
 ## Parallel Subagent Safety
 
 When orchestrating parallel subagents via the Agent tool, **always use `isolation: "worktree"`** if there is any chance two agents modify the same file — even different methods in the same file. Without worktrees, concurrent Edit tool calls on the same file can clobber each other (last writer wins, or `old_string` match fails silently).
 
-- Before launching parallel agents, check "Affected Component / File paths" for overlap.
-- If ANY file appears in both agents' scope, use `isolation: "worktree"` on at least one agent.
+- Before launching, check "Affected Component / File paths" for overlap — if any file appears in both scopes, use `isolation: "worktree"` on at least one agent.
 - After worktree agents complete, merge their branches into the main working tree.
 - Only skip worktrees when agents have truly zero file overlap (e.g., Python worker vs React console).
 
@@ -89,43 +97,33 @@ When orchestrating parallel subagents via the Agent tool, **always use `isolatio
 
 ## External Pull Request References
 
-**Do not link to pull requests in other people's repositories** from commit messages or PR descriptions. GitHub creates a cross-reference timeline event on the target PR, which typically surfaces as a notification to its author — unsolicited noise once the upstream work has shipped.
+**Do not link to PRs in other people's repositories** from commits or PR descriptions — GitHub creates a cross-reference notification to the upstream author. Allowed: PRs/commits in this repo, or PRs *you* authored anywhere.
 
-Allowed references:
-- PRs and commits in this repository
-- PRs that *you* authored on any repository
+For upstream fixes in OSS dependencies, cite the released **version** (e.g., "`ddgs 9.12.1` replaced the shared executor with a per-call one"), not the PR URL. The version pin is the technical guarantee; summarize the *why* inline.
 
-When citing an upstream fix from an OSS dependency, refer to the released **version** that contains it (e.g., "`ddgs 9.12.1` replaced the shared executor with a per-call one") rather than the PR URL. The version pin in `pyproject.toml` / `build.gradle` / `package.json` is the technical guarantee; the URL is just provenance and can be dropped. If the *why* matters, summarize it inline in prose rather than linking out.
-
-If an external PR reference slips in, rewrite the commit message and update the PR description before merge. Force-push is acceptable here — the rewrite is process hygiene, not content change.
+If an external PR reference slips in, rewrite the commit / PR description before merge (force-push is acceptable — process hygiene, not content change).
 
 ## Local Validation Notes
 
-- For local testing, follow `README.md` and `docs/LOCAL_DEVELOPMENT.md`.
-- The `Makefile` has wrapper targets for setup and testing (`make init`, `make install`, `make test`, `make start`, `make stop`, `make status`). Use these as the primary entry point.
+- See `README.md` and `docs/LOCAL_DEVELOPMENT.md` for setup details.
 - When validating background `Makefile` targets (`make start`, `make status`, `make stop`), prefer an interactive shell / PTY.
-- **Python:** Always use the worker virtualenv at `services/worker-service/.venv/`. Run Python commands via `services/worker-service/.venv/bin/python` or activate with `source services/worker-service/.venv/bin/activate`. Do NOT use bare `python3` or `uv run` — the venv has all dependencies pinned.
-- **Test isolation:** All tests (worker integration, E2E) use a dedicated test database on port **55433** (`par-e2e-postgres`), never the local dev database on port 55432. This is enforced by `make worker-test` (passes `E2E_DB_DSN`) and `make e2e-test` (passes `E2E_DB_*` vars). Do NOT add tests that default to the dev DB — they will corrupt local development data.
+- **Python venv:** the worker venv at `services/worker-service/.venv/` has all deps pinned. Activate with `source services/worker-service/.venv/bin/activate` or call `services/worker-service/.venv/bin/python` directly.
+- **Test DB isolation:** `par-e2e-postgres` on port **55433** is the tests' DB; the dev DB on 55432 is off-limits for tests (it corrupts local state). `make worker-test` passes `E2E_DB_DSN`; `make e2e-test` passes `E2E_DB_*` vars.
 
 ## Testing (Mandatory)
 
-**Every code change must be tested before it is considered done.** No exceptions. See [LOCAL_DEVELOPMENT.md](./docs/LOCAL_DEVELOPMENT.md) for full details on test locations, single-test commands, and conventions.
+**Every code change must be tested before it is considered done.** No exceptions. See [LOCAL_DEVELOPMENT.md](./docs/LOCAL_DEVELOPMENT.md) for test locations, single-test commands, and conventions.
 
-- **Write tests** for every code change. Cover all use cases and failure scenarios.
-- `make test` — unit tests (fast, no infra). **Required after every change.**
-- `make e2e-test` — E2E on isolated infra. **Required after DB/schema or cross-service changes.**
-- `make test-all` — both combined.
-- Run the **narrowest scope** that covers your change. If tests fail — including pre-existing failures — fix them before moving on.
-- **CI maintenance:** When adding database migrations, new service containers, or infrastructure dependencies, verify `.github/workflows/ci.yml` picks them up. Migrations use a glob pattern (`[0-9][0-9][0-9][0-9]_*.sql`) so new migrations are auto-applied, but new services (e.g., LocalStack) must be added as CI service containers manually.
+- Write tests covering the change, including failure scenarios.
+- Run the **narrowest scope** that covers your change (a single test file or package is fine — you don't need to run the whole `make test` suite if it doesn't touch your change). Run `make e2e-test` after DB/schema or cross-service changes. If tests fail — including pre-existing failures — fix them before moving on.
+- **CI maintenance:** when adding DB migrations, new service containers, or infra deps, verify `.github/workflows/ci.yml` picks them up. Migrations auto-apply via glob (`[0-9][0-9][0-9][0-9]_*.sql`); new services (e.g., LocalStack) must be added as CI service containers manually.
 
 ### Browser Verification (Console Changes) — BLOCKING
 
-**Console changes are not done until verified in a real browser.** This is a blocking gate, not a suggestion. Unit tests with mocked data cannot catch cross-origin issues, encoding problems, stale data display, or broken download flows. Skip this and users will find the bugs instead.
+**Console changes are not done until verified in a real browser.** Unit tests with mocked data cannot catch cross-origin issues, encoding problems, stale data, or broken downloads.
+
+Verify with Playwright MCP tools against `make start` (Console at `localhost:5173`, API at `localhost:8080`). Run Scenario 1 (Navigation Smoke Test) plus the feature scenario covering your change. If your UI isn't covered, add a new scenario. See [CONSOLE_BROWSER_TESTING.md](./docs/CONSOLE_BROWSER_TESTING.md) for scenarios and the selection matrix.
 
-After any change that affects the Console UI, verify it works using Playwright MCP tools (`browser_navigate`, `browser_snapshot`, `browser_click`, etc.). See [CONSOLE_BROWSER_TESTING.md](./docs/CONSOLE_BROWSER_TESTING.md) for standard scenarios and the scenario-selection matrix.
+---
 
-1. **Start the stack:** `make start` must be running (Console at `localhost:5173`, API at `localhost:8080`)
-2. **Run Scenario 1** (Navigation Smoke Test) for all console changes
-3. **Run the feature scenario** that covers the UI you changed — exercise the actual user flow end-to-end (submit data, wait for results, click buttons, verify downloads work)
-4. **New features:** If your change adds UI not covered by existing scenarios, **add a new scenario** to the doc
-5. **Mark done only after browser verification passes** — do not commit or create a PR with untested Console UI
+**Status:** See [STATUS.md](./STATUS.md) for phase-level tracking and per-track progress.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,3 +0,0 @@
-**MANDATORY FIRST STEP:** Read `AGENTS.md` in full before doing anything else — before reading other files, before exploring the codebase, before answering questions. `AGENTS.md` contains project navigation, workflow rules, skill requirements, and testing instructions that govern all work in this repository.
-
-If superpowers skills are installed, invoke the `using-superpowers` skill at the start of every conversation before taking any action.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
