#!/usr/bin/env bash
set -euo pipefail

cd /workspace/neo

# Idempotency guard
if grep -qF "*(Required when the PR carries substantive architectural prose \u2014 PR description " ".agent/skills/pr-review/assets/pr-review-template.md" && grep -qF "A review can hit every structural metric, document its search, pass \u00a77.1-\u00a77.3 \u2014 " ".agent/skills/pr-review/references/pr-review-guide.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agent/skills/pr-review/assets/pr-review-template.md b/.agent/skills/pr-review/assets/pr-review-template.md
@@ -30,6 +30,19 @@ OR
 
 *A peer-review with neither a challenge nor a documented search fails the Depth Floor regardless of structural compliance elsewhere.*
 
+**Rhetorical-Drift Audit (per guide §7.4):**
+
+*(Required when the PR carries substantive architectural prose — PR description framing, Anchor & Echo JSDoc additions, `[RETROSPECTIVE]` tags, or linked-anchor citations. Mark N/A for routine code with no architectural prose.)*
+
+Verify symmetry between stated framing and mechanical implementation:
+
+- [ ] PR description: framing matches what the diff substantiates (no overshoot)
+- [ ] Anchor & Echo summaries: precise codebase terminology, no metaphor that overshoots the implementation
+- [ ] `[RETROSPECTIVE]` tag: accurately characterizes what shipped (no inflation of architectural significance)
+- [ ] Linked anchors: cited tickets/PRs actually establish the claimed pattern (no borrowed authority)
+
+**Findings:** [Pass / specific drift flagged with Required Action / N/A]
+
 ---
 
 ### 🧠 Graph Ingestion Notes
@@ -107,7 +120,7 @@ To proceed with merging, please address the following:
 
 No required actions — eligible for human merge.
 
-*Do NOT use pre-ticked placeholder items like `- [x] All checks pass and no required changes identified.` — that reads as box-checking, not genuine review. Per guide §5 Zero-Issue PR Semantics + §7.3 anti-patterns table.*
+*Do NOT use pre-ticked placeholder items like `- [x] All checks pass and no required changes identified.` — that reads as box-checking, not genuine review. Per guide §5 Zero-Issue PR Semantics + §7.5 anti-patterns table.*
 
 ---
 
diff --git a/.agent/skills/pr-review/references/pr-review-guide.md b/.agent/skills/pr-review/references/pr-review-guide.md
@@ -217,7 +217,45 @@ When a PR introduces a major new architectural abstraction or core subsystem, it
 
 If a qualifying PR lacks a provenance declaration, or if it merely ports external framework code rather than solving the abstracted friction natively, the reviewer MUST flag it as a Required Action.
 
-### 7.4 Anti-Patterns
+### 7.4 Rhetorical-Drift Audit
+
+A review can hit every structural metric, document its search, pass §7.1-§7.3 — and still let through prose that drifts away from mechanical reality. **Rhetorical Drift** is the divergence of stated framing from substrate truth: PR descriptions, Anchor & Echo summaries, docstrings, or `[RETROSPECTIVE]` tags that conceptually overshoot what the code actually does (e.g., framing a JSON-schema constraint as an "air-gapped substrate boundary", or claiming a radar ingests "SOTA" when it explicitly filters out industry standards).
+
+Unaudited rhetorical drift poisons the `ask_knowledge_base` ingestion pipeline. Future agents query the synthesized answer and inherit the metaphor, building on a flawed premise rather than a factual constraint. The semantic knowledge base diverges from mechanical reality one PR at a time.
+
+#### Audit task
+
+Reviewers MUST verify symmetry between **stated framing** and **mechanical implementation**:
+
+1. **PR description** — does the architectural narrative accurately describe the boundaries and capabilities of the code? Or does the prose claim more than the diff substantiates?
+2. **Anchor & Echo summaries** (`AGENTS.md §15.2`) — does new JSDoc reuse precise codebase terminology, or does it lean on metaphor that overshoots the implementation?
+3. **`[RETROSPECTIVE]` tags** (§4) — does the takeaway accurately characterize what shipped, or does it inflate the architectural significance of a routine change?
+4. **Linked-anchor accuracy** — when prose claims "implements pattern X from #N" or "similar to PR #M", does the cited reference actually establish that pattern, or is it being cited for borrowed authority?
+
+#### What this audit is NOT
+
+- **Not style-policing of metaphor itself.** Metaphors that accurately bridge a complex concept to a familiar one are fine; metaphors that overstate or misframe are not.
+- **Not a redundant Provenance Audit (§7.3).** Provenance audits the *origin* of an abstraction; this audit checks whether the *description* matches the *implementation*. A PR can have legitimate provenance and still drift rhetorically.
+- **Not a replacement for Score Justification (§3.2).** Score justifications target reviewer prose; this audit targets author prose.
+
+#### Required Action template
+
+> *"Rhetorical drift detected: the [PR description / anchor summary / `[RETROSPECTIVE]` tag / linked-anchor citation] claims [specific framing], but the code [specific mechanical reality]. Tighten the framing to match the implementation, or scope the implementation to match the framing."*
+
+**Author response options:**
+
+- **Tighten the prose** — rewrite the framing to match the substrate.
+- **Expand the implementation** — if the framing reflects intended substrate that the diff doesn't yet deliver, scope-expand or file a follow-up ticket.
+- **Defend the metaphor** — argue why the framing accurately bridges to the mechanical reality (reviewer judges).
+
+#### Empirical anchors
+
+- **PR #10298** (`industry-friction-radar`, 2026-04-24): initial framing claimed the radar ingests "SOTA" patterns when the implementation explicitly filters out industry standards (rationale: industry-standard adoption defeats Neo's friction-as-signal heuristic). Caught at review; tightened to "abstracted friction patterns" — no information loss, mechanical accuracy restored.
+- **PR #10371** review (2026-04-26): initial Cycle 1 framing of Step 6 (A2A self-ping) and Step 7 (Sandman memory) as "redundant push-pull substrates" drifted from the mechanical reality that the substrates serve distinct lifecycle gaps (push-inbox vs pull-memory-graph). Caught via author calibration; reviewer posted Cycle 2.5 follow-up withdrawing the redundancy challenge with substrate-grounded reasoning.
+
+Two empirical anchors confirm the pattern: rhetorical drift fires both at author-side (PR description framing) and reviewer-side (challenge framing). The §7.4 mandate applies to both surfaces.
+
+### 7.5 Anti-Patterns
 
 | Anti-pattern | Why it fails the Depth Floor |
 |---|---|
@@ -227,6 +265,7 @@ If a qualifying PR lacks a provenance declaration, or if it merely ports externa
 | Approval without cross-skill integration check on PRs introducing new workflow conventions | §8 Cross-Skill Integration Audit violated |
 | Style-calibrating toward the other model family's tone | §7.2 — the floor keeps rigor universal, not style convergence |
 | Ignoring Chain of Custody | §7.3 Provenance Audit violated on a major abstraction |
+| Approval without rhetorical-drift audit on a PR carrying substantive architectural prose | §7.4 Rhetorical-Drift Audit violated; framing drifts from mechanical reality, poisons `ask_knowledge_base` ingestion |
 | PR names an epic as close-target without flagging | §5.2 Close-Target Audit violated; risks epic auto-close-with-open-subs (see #9999 sabotage chain) |
 | PR adds bloated multi-line OpenAPI tool description without flagging | §5.3 MCP-Tool-Description Budget Audit violated; bloat compounds across the tool surface and competes with agent reasoning budget at runtime |
 
PATCH

echo "Gold patch applied."
