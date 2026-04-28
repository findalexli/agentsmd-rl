#!/usr/bin/env bash
set -euo pipefail

cd /workspace/neo

# Idempotency guard
if grep -qF "**Problem:** Without commentId-scoped fetch, every review cycle N+1 incurs **cum" ".agent/skills/pr-review/references/pr-review-guide.md" && grep -qF "**Pre-Flight Check (operational reflex)** \u2014 mirrors `AGENTS.md \u00a73 / \u00a74.2` proven" ".agent/skills/pull-request/references/pull-request-workflow.md" && grep -qF "| `pr-review` | Reviewing a PR (yours or peer's) \u2014 structured eval metrics, grap" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agent/skills/pr-review/references/pr-review-guide.md b/.agent/skills/pr-review/references/pr-review-guide.md
@@ -258,7 +258,9 @@ PR #10155 shipped `.agent/skills/epic-review/` with the claim "runs *before* `ti
 
 ## 9. A2A Comment-ID Hand-off Protocol (#10272)
 
-**Problem:** Each review cycle N+1 costs context-fetch cost proportional to cumulative thread size. By cycle three of an Architectural Pillar review, fetching the full conversation via `get_conversation({pr_number: N})` burns more tokens reading prior rounds than the new substance justifies.
+**Problem:** Without commentId-scoped fetch, every review cycle N+1 incurs **cumulative-thread context cost** — full-thread fetch reads all prior cycles, not just the delta. This breaks linear-cost scaling: by cycle three of an Architectural Pillar review, fetching the full conversation burns more tokens on prior rounds than on the new substance. Compounds silently across the swarm — every reviewer pays the cumulative cost per cycle, not just once. **Treat as invariant discipline, not optional optimization** — the cost asymmetry diverges with thread length, and missed pings cascade across reviewers.
+
+**Empirical anchor (PR #10371, 2026-04-26):** Cycle 3 thread reached ~8KB markdown across 6 prior comments. Full-thread fetch by Cycle 4 reviewer reads all 8KB to extract the ~1KB delta from one new comment — **~8× context-budget waste per cycle, ratio diverging with thread length**. CommentId-scoped fetch reads ~1KB. Reviewer-side §9 + author-side `pull-request-workflow §8.1` discipline together close the loop.
 
 **Solution:** `manage_issue_comment` action:`create` returns `{message, commentId, url, createdAt}`. The reviewer captures `commentId` from that response and relays it to the next reviewer (peer or author) via A2A mailbox — the recipient fetches just-this-comment via `get_conversation({pr_number: N, comment_id: COMMENT_ID})`, scaling linearly with new-comment volume rather than cumulative thread size.
 
@@ -288,4 +290,33 @@ PR #10155 shipped `.agent/skills/epic-review/` with the claim "runs *before* `ti
 - **Full-conversation-fetch-per-cycle when commentId is available.** If the A2A message carries a commentId, use it. Otherwise the propagation discipline is broken.
 - **Mailbox DM without commentId when the message is pointing at a specific comment.** Forces recipient to fetch full thread and grep for the intended passage — negates the efficiency gain.
 - **Passing all three selectors at once expecting a merge.** First-match semantics; excess selectors are ignored.
+- **Rigidly applying commentId-scoped fetch in a cold-cache case** (e.g., fresh session bootstrap, Cycle 1 review). Lands one isolated comment in a void without the prior context it depends on. See §9.5 below.
+- **Skipping the Pre-Flight Check (§9.4) before yielding turn after `manage_issue_comment`.** Empirically the dominant failure mode — agents read this guide, draft the comment, post it, and forget to capture commentId + send A2A ping. Proven mitigation: explicit reasoning-statement mirroring the `AGENTS.md §3 / §4.2` Pre-Flight pattern.
+
+### 9.4 Pre-Flight Check (operational reflex)
+
+The §9 hand-off protocol is mechanical — but reviewers empirically miss it across cycles even after reading this guide (PR #10371 + #10375, 2026-04-26: 5+ missed pings before @tobiu surfaced the gap explicitly). The discipline is reflex-application, not knowledge.
+
+**Pre-Flight Check shape** (mirrors `AGENTS.md §3 / §4.2` proven primitives). After every `manage_issue_comment` create, before yielding turn, you MUST explicitly state in your internal reasoning:
+
+> *"Pre-Flight: I posted review commentId `<ID>` for cycle K. I have (or will) send an A2A ping to `<recipient>` via `add_message` with the literal commentId in the body so they can call `get_conversation({pr_number, comment_id})` for scoped fetch."*
+
+This commitment-statement is the gate that permits yielding turn. The §0.5 `add_memory` discipline already proves this Pre-Flight pattern works as a reflex enforcement primitive when paired with explicit pre-action reasoning. Skipping forces the next cycle's actor to re-read the full thread — the empirical-anchor ~8× cost ratio quantifies the cost.
+
+Cold-cache exception applies when the recipient lacks prior-cycle context — see §9.5 below for when full-thread fetch is the right call instead.
+
+### 9.5 Cold-Cache Exception
+
+CommentId-scoped fetch is the **warm-cache** path — the reviewer or author has continuous prior-cycle context loaded in the current context window. **Cold-cache cases require a different fetch shape:**
+
+| Cold-cache case | Fetch shape | Reason |
+|---|---|---|
+| **Fresh session bootstrap** | Full-thread fetch + `query_summaries` / `query_raw_memories` for Memory Core grounding | No prior cycle context loaded; commentId-scoped fetch lands one comment in a void |
+| **Cycle 1 review** | Full-thread fetch | First ramp on the PR; no prior cycle exists; need full diff + body for grounding |
+| **Cross-agent handoff** | Full-thread fetch + memory query against the prior agent's session-id | Different reviewer/author than prior cycle; no shared mental model |
+| **Missed/lost A2A ping** | `since_comment_id` from last-known anchor, OR `last_n: 3-5`, OR full-thread fallback | No commentId pointer to scope from |
+
+The dichotomy mirrors the boot-pull-vs-sunset-pull lifecycle distinction (`AGENTS_STARTUP §0` vs `session-sunset` skill body Step 1): **warm path** optimizes for incremental context; **cold path** grounds from scratch. They are NOT symmetric operations — they fill different lifecycle gaps. Don't confuse them: rigidly applying commentId-scoped fetch in a cold-cache case lands one isolated comment without the context it depends on; over-fetching on principle in a warm-cache case defeats the linear-cost scaling.
+
+**The right reflex** — before fetching, ask: *"do I have prior cycle context loaded in this context window?"* If yes → commentId-scoped fetch (or `since_comment_id` for incremental polling across stale-anchor recovery). If no → full-thread fetch + memory query for grounding.
 
diff --git a/.agent/skills/pull-request/references/pull-request-workflow.md b/.agent/skills/pull-request/references/pull-request-workflow.md
@@ -251,6 +251,10 @@ Symmetric with `pr-review §9` (reviewer side). When YOU (as author) post a resp
 
 Rationale: §9 of `pr-review-guide.md` covers the reviewer-side mechanics; this section covers the author-side symmetric hand-off. The selector precedence (`comment_id > since_comment_id > last_n > full`) and anti-patterns (full-fetch-when-commentId-available, mailbox-without-commentId, all-three-selectors-at-once) apply identically here.
 
+**Pre-Flight Check (operational reflex)** — mirrors `AGENTS.md §3 / §4.2` proven primitive. After every author-side `manage_issue_comment` create, before yielding turn, explicitly state in your reasoning: *"Pre-Flight: I posted response commentId `<ID>` addressing reviewer feedback. I have (or will) send an A2A ping to reviewer `<handle>` with the literal commentId in the body."* This commitment-statement is the gate that permits yielding turn. Skipping is empirically the dominant failure mode (PR #10371 + #10375, 2026-04-26: 5+ missed pings before @tobiu surfaced the gap). See `pr-review-guide §9.4 Pre-Flight Check` for the full reasoning template; single source of truth lives there, this section inherits.
+
+**Cold-cache exception:** When picking up a PR after a fresh session bootstrap, opening Cycle 1 of a PR, taking a cross-agent handoff, or recovering from a missed/lost reviewer ping, full-thread fetch (or `since_comment_id` from the last-known anchor) is the right call instead — the warm-cache reflex would land one comment in a void without prior-cycle grounding. See `pr-review-guide §9.5 Cold-Cache Exception` for the warm-vs-cold-cache dichotomy and per-case fetch shape; single source of truth lives there, this section inherits.
+
 ## 9. PR Body Hygiene
 
 Do not blindly copy the entire ticket body into the PR description. The ticket holds the original context; the PR body summarizes the implementation delta.
diff --git a/AGENTS.md b/AGENTS.md
@@ -449,8 +449,8 @@ The lifecycle skills below carry the discipline that this file's invariants (esp
 | `ticket-create` | Before `create_issue` MCP invocation — duplicate sweep, Fat Ticket body, label rules, 5-stage challenge chain |
 | `ticket-intake` | Picking up an existing assigned ticket — validation sweep, ROI calculation, branch-before-code gate |
 | `epic-review` | Before picking up a sub of an unreviewed epic — 5-stage roadmap-fit / approach-elegance / sub-coherence chain |
-| `pull-request` | Code modifications complete; before opening PR — stepping-back reflection, commit format, cross-family review mandate |
-| `pr-review` | Reviewing a PR (yours or peer's) — structured eval metrics, graph ingestion tags, severity ladder, restates §0 merge gate |
+| `pull-request` | Code modifications complete; before opening PR — stepping-back reflection, commit format, cross-family review mandate, post-comment A2A commentId hand-off (author→reviewer) per workflow §8.1 |
+| `pr-review` | Reviewing a PR (yours or peer's) — structured eval metrics, graph ingestion tags, severity ladder, restates §0 merge gate, post-comment A2A commentId hand-off (reviewer→author) per guide §9 + §9.4 cold-cache exception |
 | `ideation-sandbox` | Before creating a Discussion for architectural exploration — speculative-thought routing, OQ tracking |
 | `memory-mining` | On regression / non-obvious-architecture / decision-points — historical context retrieval ("what was decided here?") |
 | `tech-debt-radar` | During PR review for fundamental architectural shifts — semantic sweep against historical issues + Memory Core |
PATCH

echo "Gold patch applied."
