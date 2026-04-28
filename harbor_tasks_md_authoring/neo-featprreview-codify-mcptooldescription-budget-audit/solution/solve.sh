#!/usr/bin/env bash
set -euo pipefail

cd /workspace/neo

# Idempotency guard
if grep -qF "*(Required per guide \u00a75.3 when the PR touches `ai/mcp/server/*/openapi.yaml` \u2014 a" ".agent/skills/pr-review/assets/pr-review-template.md" && grep -qF "**Empirical anchor:** PR #10340's initial `task` parameter description on `mailb" ".agent/skills/pr-review/references/pr-review-guide.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agent/skills/pr-review/assets/pr-review-template.md b/.agent/skills/pr-review/assets/pr-review-template.md
@@ -63,6 +63,22 @@ For every issue named as close-target, verify it does NOT carry the `epic` label
 
 ---
 
+### 📡 MCP-Tool-Description Budget Audit
+
+*(Required per guide §5.3 when the PR touches `ai/mcp/server/*/openapi.yaml` — adds a new `description:`, modifies an existing block-literal `description:`, or introduces a new tool path or operation. Mark N/A for PRs that don't touch OpenAPI surfaces.)*
+
+For every modified or added OpenAPI tool description:
+
+- [ ] Single-line preferred — block-literal (`|`) descriptions justified by content, not authorial habit
+- [ ] No internal cross-refs (no ticket numbers, Phase sequencing, session IDs, or memory anchor names in the description payload)
+- [ ] No architectural narrative — descriptions describe call-site usage (what + when-to-use + when-not-to-use)
+- [ ] External standard URLs OK — citing canonical specs (e.g., `https://a2a-protocol.org/...`) is acceptable
+- [ ] 1024-char hard cap respected — approaching it is a red flag (see `McpServerToolLimits` test)
+
+**Findings:** [Pass / specific descriptions flagged / N/A]
+
+---
+
 ### 🔗 Cross-Skill Integration Audit
 
 *(Required per guide §8.1 when the PR touches skill files, conventions, MCP tool surfaces, `AGENTS_STARTUP.md` / `AGENTS.md`, or architectural primitives. Mark N/A for routine code changes that don't introduce cross-substrate conventions.)*
diff --git a/.agent/skills/pr-review/references/pr-review-guide.md b/.agent/skills/pr-review/references/pr-review-guide.md
@@ -115,6 +115,56 @@ When reviewing a PR, audit every issue named as a close-target via GitHub's magi
 - Sub-issues with their own children (rare but legitimate) — same risk class as leaf; not flagged.
 - `Related: #N` / `Refs #N` / `Part of #N` references — these don't trigger GitHub's magic-close, so they're not subject to this audit.
 
+### 5.3 MCP-Tool-Description Budget Audit
+
+When a PR touches `ai/mcp/server/*/openapi.yaml`, audit each modified or added tool description for budget compliance. Tool descriptions are loaded into every consuming agent's context window when the tool surface is enumerated; bloat compounds across the tool surface and competes with reasoning budget at runtime.
+
+**The Rule:** OpenAPI tool-parameter and operation descriptions are runtime payload, not source-code documentation. Their audience is the agent enumerating the tool surface — not the developer reading the source. Treat them as terse, usage-focused contracts; relegate architectural narrative to JSDoc on the corresponding service method or to the PR / ticket body.
+
+**Three audiences, three verbosity budgets:**
+
+| Surface | Audience | Verbosity budget | Acceptable content |
+|---|---|---|---|
+| **OpenAPI YAML** (`openapi.yaml`) | MCP-consuming agents at runtime (every tool-surface enumeration) | **Terse, single-line, usage-focused** | What it is + when to use + when NOT to use |
+| **JSDoc** (source code) | Developers reading source | Verbose; framing OK | Architectural rationale, design history, cross-refs |
+| **PR body / ticket body** | Reviewers + Retrospective daemon | Full Fat Ticket | Narrative, deltas, test evidence, post-merge validation |
+
+Conflating budgets — bloating YAML with what should have stayed in JSDoc — has empirical cost. It also conflates audience: an agent calling `add_message` doesn't need to know about Phase 1/Phase 2 sequencing; it needs to know whether to populate the param.
+
+**Trigger conditions** (fire if any apply):
+
+1. PR adds a new `description:` to an OpenAPI tool param or operation.
+2. PR modifies an existing `description:` block-literal (`|` form).
+3. PR introduces a new OpenAPI tool path or operation.
+
+**Audit checks:**
+
+1. **Single-line preferred** — multi-line block-literal (`|`) descriptions warrant scrutiny. Block-literal is acceptable for genuinely complex contracts (e.g., transport-substrate observability blocks) but must be justified by content, not authorial habit.
+2. **No internal cross-refs** — descriptions should not cite ticket numbers, internal Phase sequencing, session IDs, or memory anchors (those belong in JSDoc + PR / ticket bodies).
+3. **No architectural narrative** — descriptions should describe call-site usage (what + when-to-use + when-not-to-use), not implementation history.
+4. **External standard URLs OK** — citing `https://a2a-protocol.org/...` or other canonical specs is acceptable when the param adopts an external standard; agents can navigate canonical docs.
+5. **Mind the 1024-char hard cap** — MCP protocol enforces a per-tool-description limit; approaching it is a red flag (see `McpServerToolLimits` test for the empirical bound).
+
+**Required Action template when violated:**
+
+> *"OpenAPI description on param `X` of tool `Y` exceeds budget — multi-line block-literal + internal ticket references. Tighten to single-line usage-focused description; move architectural narrative to JSDoc on the corresponding service method or to the PR body."*
+
+**Author response options** when this Required Action fires:
+- Tighten the description to single-line usage-focused form; relocate the architectural narrative to JSDoc or the PR body.
+- Defend the block-literal with a content-justification (e.g., transport-substrate observability that genuinely requires multi-clause framing) — reviewer can accept with rationale logged.
+- Push back on a specific check if the audit misfires (e.g., a multi-line description that legitimately enumerates an external spec's nuances).
+
+**Distinction from JSDoc audit:** JSDoc on service-method source is a separate audience (developers reading code). Verbosity is acceptable there. The §5.3 audit fires only on the OpenAPI YAML surface that becomes runtime tool-description payload.
+
+**Empirical anchor:** PR #10340's initial `task` parameter description on `mailbox/messages` was a ~600-char block-literal with internal Phase 1/Phase 2 framing and ticket cross-refs (#10334/#10313/#10338). Cycle 1 review challenge ("these directly map to mcp server tools — they must be short and meaningful") tightened it to a ~155-char single-line description in one follow-up commit. The post-fix form (`"Optional A2A Task envelope (https://...) for structured agent coordination. Omit for free-form markdown messages."`) preserves usage signal without architectural narrative — a 4× reduction with no information loss for the consuming agent. The §5.3 audit codifies that reviewer-side discipline so the tightening fires pre-Approval, not post-Approval.
+
+**Out of scope for this audit:**
+- Auto-tooling for description-bloat detection (mechanical-layer enforcement after discipline-layer proves insufficient).
+- Migration sweep of legacy verbose descriptions in existing OpenAPI files (forward-only via this discipline + opportunistic refactoring during ongoing PR work).
+- JSDoc verbosity (different audience, different budget).
+- PR body verbosity (reviewers + Retrospective daemon legitimately consume Fat Ticket framing).
+- OpenAPI/JS contract drift (e.g., `enum` values diverging from runtime validators, `required` arrays diverging from JS-side implementation) — adjacent discipline gap; warrants separate codification if recurrent. The §5.3 audit is budget-focused; correctness drift is a different audit shape.
+
 ## 6. The Review Template
 When drafting your review, use the `view_file` tool to load the exact markdown template from:
 `.agent/skills/pr-review/assets/pr-review-template.md`
@@ -178,6 +228,7 @@ If a qualifying PR lacks a provenance declaration, or if it merely ports externa
 | Style-calibrating toward the other model family's tone | §7.2 — the floor keeps rigor universal, not style convergence |
 | Ignoring Chain of Custody | §7.3 Provenance Audit violated on a major abstraction |
 | PR names an epic as close-target without flagging | §5.2 Close-Target Audit violated; risks epic auto-close-with-open-subs (see #9999 sabotage chain) |
+| PR adds bloated multi-line OpenAPI tool description without flagging | §5.3 MCP-Tool-Description Budget Audit violated; bloat compounds across the tool surface and competes with agent reasoning budget at runtime |
 
 ## 8. Cross-Skill Integration Audit
 
PATCH

echo "Gold patch applied."
