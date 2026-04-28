#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "After successful login, the user will have to restart codex. You should finish y" "skills/.curated/figma-code-connect-components/SKILL.md" && grep -qF "After successful login, the user will have to restart codex. You should finish y" "skills/.curated/figma-create-design-system-rules/SKILL.md" && grep -qF "After successful login, the user will have to restart codex. You should finish y" "skills/.curated/figma-implement-design/SKILL.md" && grep -qF "- `reference/` \u2014 database schemas and templates (e.g., `team-wiki-database.md`, " "skills/.curated/notion-knowledge-capture/SKILL.md" && grep -qF "- `reference/` \u2014 template picker and meeting templates (e.g., `template-selectio" "skills/.curated/notion-meeting-intelligence/SKILL.md" && grep -qF "- `reference/` \u2014 search tactics, format selection, templates, and citation rules" "skills/.curated/notion-research-documentation/SKILL.md" && grep -qF "- Create the plan via `Notion:notion-create-pages`, include: overview, linked sp" "skills/.curated/notion-spec-to-implementation/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/.curated/figma-code-connect-components/SKILL.md b/skills/.curated/figma-code-connect-components/SKILL.md
@@ -2,7 +2,7 @@
 name: figma-code-connect-components
 description: Connects Figma design components to code components using Code Connect. Use when user says "code connect", "connect this component to code", "connect Figma to code", "map this component", "link component to code", "create code connect mapping", "add code connect", "connect design to code", or wants to establish mappings between Figma designs and code implementations. Requires Figma MCP server connection.
 metadata:
-  short-description: Map Figma components to code
+  short-description: Connect Figma components to local code
 ---
 
 # Code Connect Components
@@ -24,6 +24,19 @@ This skill helps you connect Figma design components to their corresponding code
 
 **Follow these steps in order. Do not skip steps.**
 
+### Step 0: Set up Figma MCP (if not already configured)
+
+If any MCP call fails because Figma MCP is not connected, pause and set it up:
+
+1. Add the Figma MCP:
+   - `codex mcp add figma --url https://mcp.figma.com/mcp`
+2. Enable remote MCP client:
+   - Set `[features].rmcp_client = true` in `config.toml` **or** run `codex --enable rmcp_client`
+3. Log in with OAuth:
+   - `codex mcp login figma`
+
+After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.
+
 ### Step 1: Get Node ID and Extract Metadata
 
 #### Option A: Parse from Figma URL
diff --git a/skills/.curated/figma-create-design-system-rules/SKILL.md b/skills/.curated/figma-create-design-system-rules/SKILL.md
@@ -2,7 +2,7 @@
 name: figma-create-design-system-rules
 description: Generates custom design system rules for the user's codebase. Use when user says "create design system rules", "generate rules for my project", "set up design rules", "customize design system guidelines", or wants to establish project-specific conventions for Figma-to-code workflows. Requires Figma MCP server connection.
 metadata:
-  short-description: Create Figma design system rules
+  short-description: Update AGENTS.md with design system rules
 ---
 
 # Create Design System Rules
@@ -44,6 +44,19 @@ Use this skill when:
 
 **Follow these steps in order. Do not skip steps.**
 
+### Step 0: Set up Figma MCP (if not already configured)
+
+If any MCP call fails because Figma MCP is not connected, pause and set it up:
+
+1. Add the Figma MCP:
+   - `codex mcp add figma --url https://mcp.figma.com/mcp`
+2. Enable remote MCP client:
+   - Set `[features].rmcp_client = true` in `config.toml` **or** run `codex --enable rmcp_client`
+3. Log in with OAuth:
+   - `codex mcp login figma`
+
+After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.
+
 ### Step 1: Run the Create Design System Rules Tool
 
 Call the Figma MCP server's `create_design_system_rules` tool to get the foundational prompt and template.
diff --git a/skills/.curated/figma-implement-design/SKILL.md b/skills/.curated/figma-implement-design/SKILL.md
@@ -24,6 +24,19 @@ This skill provides a structured workflow for translating Figma designs into pro
 
 **Follow these steps in order. Do not skip steps.**
 
+### Step 0: Set up Figma MCP (if not already configured)
+
+If any MCP call fails because Figma MCP is not connected, pause and set it up:
+
+1. Add the Figma MCP:
+   - `codex mcp add figma --url https://mcp.figma.com/mcp`
+2. Enable remote MCP client:
+   - Set `[features].rmcp_client = true` in `config.toml` **or** run `codex --enable rmcp_client`
+3. Log in with OAuth:
+   - `codex mcp login figma`
+
+After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.
+
 ### Step 1: Get Node ID
 
 #### Option A: Parse from Figma URL
diff --git a/skills/.curated/notion-knowledge-capture/SKILL.md b/skills/.curated/notion-knowledge-capture/SKILL.md
@@ -1,14 +1,56 @@
 ---
 name: notion-knowledge-capture
-description: Capture conversations and discussions into structured Notion pages; use when asked to save, document, or capture knowledge to Notion wiki or database.
+description: Capture conversations and decisions into structured Notion pages; use when turning chats/notes into wiki entries, how-tos, decisions, or FAQs with proper linking.
 metadata:
-  short-description: Capture knowledge into Notion pages
+  short-description: Capture conversations into structured Notion pages
 ---
 
 # Knowledge Capture
 
-- Extract key information from conversation context
-- Structure into appropriate format (concept, how-to, decision record, FAQ)
-- Save to Notion using `Notion:notion-create-pages`
-- Link from hub pages to ensure discoverability
-- See reference/ for database schemas and content type templates
+Convert conversations and notes into structured, linkable Notion pages for easy reuse.
+
+## Quick start
+1) Clarify what to capture (decision, how-to, FAQ, learning, documentation) and target audience.
+2) Identify the right database/template in `reference/` (team wiki, how-to, FAQ, decision log, learning, documentation).
+3) Pull any prior context from Notion with `Notion:notion-search` → `Notion:notion-fetch` (existing pages to update/link).
+4) Draft the page with `Notion:notion-create-pages` using the database’s schema; include summary, context, source links, and tags/owners.
+5) Link from hub pages and related records; update status/owners with `Notion:notion-update-page` as the source evolves.
+
+## Workflow
+### 0) If any MCP call fails because Notion MCP is not connected, pause and set it up:
+1. Add the Notion MCP:
+   - `codex mcp add notion --url https://mcp.notion.com/mcp`
+2. Enable remote MCP client:
+   - Set `[features].rmcp_client = true` in `config.toml` **or** run `codex --enable rmcp_client`
+3. Log in with OAuth:
+   - `codex mcp login notion`
+
+After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.
+
+### 1) Define the capture
+- Ask purpose, audience, freshness, and whether this is new or an update.
+- Determine content type: decision, how-to, FAQ, concept/wiki entry, learning/note, documentation page.
+
+### 2) Locate destination
+- Pick the correct database using `reference/*-database.md` guides; confirm required properties (title, tags, owner, status, date, relations).
+- If multiple candidate databases, ask the user which to use; otherwise, create in the primary wiki/documentation DB.
+
+### 3) Extract and structure
+- Extract facts, decisions, actions, and rationale from the conversation.
+- For decisions, record alternatives, rationale, and outcomes.
+- For how-tos/docs, capture steps, pre-reqs, links to assets/code, and edge cases.
+- For FAQs, phrase as Q&A with concise answers and links to deeper docs.
+
+### 4) Create/update in Notion
+- Use `Notion:notion-create-pages` with the correct `data_source_id`; set properties (title, tags, owner, status, dates, relations).
+- Use templates in `reference/` to structure content (section headers, checklists).
+- If updating an existing page, fetch then edit via `Notion:notion-update-page`.
+
+### 5) Link and surface
+- Add relations/backlinks to hub pages, related specs/docs, and teams.
+- Add a short summary/changelog for future readers.
+- If follow-up tasks exist, create tasks in the relevant database and link them.
+
+## References and examples
+- `reference/` — database schemas and templates (e.g., `team-wiki-database.md`, `how-to-guide-database.md`, `faq-database.md`, `decision-log-database.md`, `documentation-database.md`, `learning-database.md`, `database-best-practices.md`).
+- `examples/` — capture patterns in practice (e.g., `decision-capture.md`, `how-to-guide.md`, `conversation-to-faq.md`).
diff --git a/skills/.curated/notion-meeting-intelligence/SKILL.md b/skills/.curated/notion-meeting-intelligence/SKILL.md
@@ -1,15 +1,60 @@
 ---
 name: notion-meeting-intelligence
-description: Prepare meeting materials with Notion context and Codex research; use when prepping meetings, creating agendas, or gathering meeting context.
+description: Prepare meeting materials with Notion context and Codex research; use when gathering context, drafting agendas/pre-reads, and tailoring materials to attendees.
 metadata:
-  short-description: Prep meetings with Notion context
+  short-description: Prep meetings with Notion context and tailored agendas
 ---
 
 # Meeting Intelligence
 
-- Search Notion for related pages using `Notion:notion-search`
-- Fetch details with `Notion:notion-fetch`
-- Enrich with Codex research (industry insights, best practices)
-- Create internal pre-read for attendees
-- Create external agenda for all participants
-- See reference/template-selection-guide.md for meeting templates
+Prep meetings by pulling Notion context, tailoring agendas/pre-reads, and enriching with Codex research.
+
+## Quick start
+1) Confirm meeting goal, attendees, date/time, and decisions needed.
+2) Gather context: search with `Notion:notion-search`, then fetch with `Notion:notion-fetch` (prior notes, specs, OKRs, decisions).
+3) Pick the right template via `reference/template-selection-guide.md` (status, decision, planning, retro, 1:1, brainstorming).
+4) Draft agenda/pre-read in Notion with `Notion:notion-create-pages`, embedding source links and owner/timeboxes.
+5) Enrich with Codex research (industry insights, benchmarks, risks) and update the page with `Notion:notion-update-page` as plans change.
+
+## Workflow
+### 0) If any MCP call fails because Notion MCP is not connected, pause and set it up:
+1. Add the Notion MCP:
+   - `codex mcp add notion --url https://mcp.notion.com/mcp`
+2. Enable remote MCP client:
+   - Set `[features].rmcp_client = true` in `config.toml` **or** run `codex --enable rmcp_client`
+3. Log in with OAuth:
+   - `codex mcp login notion`
+
+After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.
+
+### 1) Gather inputs
+- Ask for objective, desired outcomes/decisions, attendees, duration, date/time, and prior materials.
+- Search Notion for relevant docs, past notes, specs, and action items (`Notion:notion-search`), then fetch key pages (`Notion:notion-fetch`).
+- Capture blockers/risks and open questions up front.
+
+### 2) Choose format
+- Status/update → status template.
+- Decision/approval → decision template.
+- Planning (sprint/project) → planning template.
+- Retro/feedback → retrospective template.
+- 1:1 → one-on-one template.
+- Ideation → brainstorming template.
+- Use `reference/template-selection-guide.md` to confirm.
+
+### 3) Build the agenda/pre-read
+- Start from the chosen template in `reference/` and adapt sections (context, goals, agenda, owner/time per item, decisions, risks, prep asks).
+- Include links to pulled Notion pages and any required pre-reading.
+- Assign owners for each agenda item; call out timeboxes and expected outputs.
+
+### 4) Enrich with research
+- Add concise Codex research where helpful: market/industry facts, benchmarks, risks, best practices.
+- Keep claims cited with source links; separate fact from opinion.
+
+### 5) Finalize and share
+- Add next steps and owners for follow-ups.
+- If tasks arise, create/link tasks in the relevant Notion database.
+- Update the page via `Notion:notion-update-page` when details change; keep a brief changelog if multiple edits.
+
+## References and examples
+- `reference/` — template picker and meeting templates (e.g., `template-selection-guide.md`, `status-update-template.md`, `decision-meeting-template.md`, `sprint-planning-template.md`, `one-on-one-template.md`, `retrospective-template.md`, `brainstorming-template.md`).
+- `examples/` — end-to-end meeting preps (e.g., `executive-review.md`, `project-decision.md`, `sprint-planning.md`, `customer-meeting.md`).
diff --git a/skills/.curated/notion-research-documentation/SKILL.md b/skills/.curated/notion-research-documentation/SKILL.md
@@ -1,14 +1,59 @@
 ---
 name: notion-research-documentation
-description: Research across Notion and synthesize into structured documentation; use when asked to research topics, create reports, or analyze information from Notion.
+description: Research across Notion and synthesize into structured documentation; use when gathering info from multiple Notion sources to produce briefs, comparisons, or reports with citations.
 metadata:
-  short-description: Research Notion content into reports
+  short-description: Research Notion content and produce briefs/reports
 ---
 
 # Research & Documentation
 
-- Search for content using `Notion:notion-search`
-- Fetch pages with `Notion:notion-fetch`
-- Synthesize findings from multiple sources
-- Create structured output with `Notion:notion-create-pages`
-- See reference/format-selection-guide.md for output formats
+Pull relevant Notion pages, synthesize findings, and publish clear briefs or reports (with citations and links to sources).
+
+## Quick start
+1) Find sources with `Notion:notion-search` using targeted queries; confirm scope with the user.
+2) Fetch pages via `Notion:notion-fetch`; note key sections and capture citations (`reference/citations.md`).
+3) Choose output format (brief, summary, comparison, comprehensive report) using `reference/format-selection-guide.md`.
+4) Draft in Notion with `Notion:notion-create-pages` using the matching template (quick, summary, comparison, comprehensive).
+5) Link sources and add a references/citations section; update as new info arrives with `Notion:notion-update-page`.
+
+## Workflow
+### 0) If any MCP call fails because Notion MCP is not connected, pause and set it up:
+1. Add the Notion MCP:
+   - `codex mcp add notion --url https://mcp.notion.com/mcp`
+2. Enable remote MCP client:
+   - Set `[features].rmcp_client = true` in `config.toml` **or** run `codex --enable rmcp_client`
+3. Log in with OAuth:
+   - `codex mcp login notion`
+
+After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.
+
+### 1) Gather sources
+- Search first (`Notion:notion-search`); refine queries, and ask the user to confirm if multiple results appear.
+- Fetch relevant pages (`Notion:notion-fetch`), skim for facts, metrics, claims, constraints, and dates.
+- Track each source URL/ID for later citation; prefer direct quotes for critical facts.
+
+### 2) Select the format
+- Quick readout → quick brief.
+- Single-topic dive → research summary.
+- Option tradeoffs → comparison.
+- Deep dive / exec-ready → comprehensive report.
+- See `reference/format-selection-guide.md` for when to pick each.
+
+### 3) Synthesize
+- Outline before writing; group findings by themes/questions.
+- Note evidence with source IDs; flag gaps or contradictions.
+- Keep user goal in view (decision, summary, plan, recommendation).
+
+### 4) Create the doc
+- Pick the matching template in `reference/` (brief, summary, comparison, comprehensive) and adapt it.
+- Create the page with `Notion:notion-create-pages`; include title, summary, key findings, supporting evidence, and recommendations/next steps when relevant.
+- Add citations inline and a references section; link back to source pages.
+
+### 5) Finalize & handoff
+- Add highlights, risks, and open questions.
+- If the user needs follow-ups, create tasks or a checklist in the page; link any task database entries if applicable.
+- Share a short changelog or status using `Notion:notion-update-page` when updating.
+
+## References and examples
+- `reference/` — search tactics, format selection, templates, and citation rules (e.g., `advanced-search.md`, `format-selection-guide.md`, `research-summary-template.md`, `comparison-template.md`, `citations.md`).
+- `examples/` — end-to-end walkthroughs (e.g., `competitor-analysis.md`, `technical-investigation.md`, `market-research.md`, `trip-planning.md`).
diff --git a/skills/.curated/notion-spec-to-implementation/SKILL.md b/skills/.curated/notion-spec-to-implementation/SKILL.md
@@ -1,15 +1,58 @@
 ---
 name: notion-spec-to-implementation
-description: Turn specs into implementation tasks for Codex; use when implementing specifications, breaking down requirements, or creating task lists from PRDs.
+description: Turn Notion specs into implementation plans, tasks, and progress tracking; use when implementing PRDs/feature specs and creating Notion plans + tasks from them.
 metadata:
-  short-description: Turn specs into implementation tasks
+  short-description: Turn Notion specs into implementation plans, tasks, and progress tracking
 ---
 
 # Spec to Implementation
 
-- Find spec using `Notion:notion-search`
-- Fetch and analyze with `Notion:notion-fetch`
-- Create implementation plan with `Notion:notion-create-pages`
-- Create tasks in task database
-- Track progress with `Notion:notion-update-page`
-- See reference/spec-parsing.md for requirement extraction patterns
+Convert a Notion spec into linked implementation plans, tasks, and ongoing status updates.
+
+## Quick start
+1) Locate the spec with `Notion:notion-search`, then fetch it with `Notion:notion-fetch`.
+2) Parse requirements and ambiguities using `reference/spec-parsing.md`.
+3) Create a plan page with `Notion:notion-create-pages` (pick a template: quick vs. full).
+4) Find the task database, confirm schema, then create tasks with `Notion:notion-create-pages`.
+5) Link spec ↔ plan ↔ tasks; keep status current with `Notion:notion-update-page`.
+
+## Workflow
+
+### 0) If any MCP call fails because Notion MCP is not connected, pause and set it up:
+1. Add the Notion MCP:
+   - `codex mcp add notion --url https://mcp.notion.com/mcp`
+2. Enable remote MCP client:
+   - Set `[features].rmcp_client = true` in `config.toml` **or** run `codex --enable rmcp_client`
+3. Log in with OAuth:
+   - `codex mcp login notion`
+
+After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.
+
+### 1) Locate and read the spec
+- Search first (`Notion:notion-search`); if multiple hits, ask the user which to use.
+- Fetch the page (`Notion:notion-fetch`) and scan for requirements, acceptance criteria, constraints, and priorities. See `reference/spec-parsing.md` for extraction patterns.
+- Capture gaps/assumptions in a clarifications block before proceeding.
+
+### 2) Choose plan depth
+- Simple change → use `reference/quick-implementation-plan.md`.
+- Multi-phase feature/migration → use `reference/standard-implementation-plan.md`.
+- Create the plan via `Notion:notion-create-pages`, include: overview, linked spec, requirements summary, phases, dependencies/risks, and success criteria. Link back to the spec.
+
+### 3) Create tasks
+- Find the task database (`Notion:notion-search` → `Notion:notion-fetch` to confirm the data source and required properties). Patterns in `reference/task-creation.md`.
+- Size tasks to 1–2 days. Use `reference/task-creation-template.md` for content (context, objective, acceptance criteria, dependencies, resources).
+- Set properties: title/action verb, status, priority, relations to spec + plan, due date/story points/assignee if provided.
+- Create pages with `Notion:notion-create-pages` using the database’s `data_source_id`.
+
+### 4) Link artifacts
+- Plan links to spec; tasks link to both plan and spec.
+- Optionally update the spec with a short “Implementation” section pointing to the plan and tasks using `Notion:notion-update-page`.
+
+### 5) Track progress
+- Use the cadence in `reference/progress-tracking.md`.
+- Post updates with `reference/progress-update-template.md`; close phases with `reference/milestone-summary-template.md`.
+- Keep checklists and status fields in plan/tasks in sync; note blockers and decisions.
+
+## References and examples
+- `reference/` — parsing patterns, plan/task templates, progress cadence (e.g., `spec-parsing.md`, `standard-implementation-plan.md`, `task-creation.md`, `progress-tracking.md`).
+- `examples/` — end-to-end walkthroughs (e.g., `ui-component.md`, `api-feature.md`, `database-migration.md`).
PATCH

echo "Gold patch applied."
