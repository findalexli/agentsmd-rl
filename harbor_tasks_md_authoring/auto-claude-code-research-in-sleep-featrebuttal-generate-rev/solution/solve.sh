#!/usr/bin/env bash
set -euo pipefail

cd /workspace/auto-claude-code-research-in-sleep

# Idempotency guard
if grep -qF "This document is the single source of truth for every paper revision promised (e" "skills/rebuttal/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/rebuttal/SKILL.md b/skills/rebuttal/SKILL.md
@@ -165,12 +165,47 @@ Hard rules:
 
 Also generate `rebuttal/PASTE_READY.txt` (plain text, exact character count).
 
+Also generate `rebuttal/REVISION_PLAN.md` — the **overall revision checklist**.
+
+This document is the single source of truth for every paper revision promised (explicitly or implicitly) in the rebuttal draft. It exists so the author can track follow-through after the rebuttal is submitted, and so the commitment gate in Phase 5 has a concrete artifact to validate against.
+
+Structure:
+
+1. **Header**
+   - Paper title, venue, character limit, rebuttal round
+   - Links back to `ISSUE_BOARD.md`, `STRATEGY_PLAN.md`, `REBUTTAL_DRAFT_v1.md`
+
+2. **Overall checklist** — a single flat GitHub-style checklist covering **every** revision item, so the author can tick items off as they land in the camera-ready / revised PDF:
+
+   ```markdown
+   ## Overall Checklist
+
+   - [ ] (R1-C2) Add assumption hierarchy table to Section 3.1 — commitment: `approved_for_rebuttal` — owner: author — status: pending
+   - [ ] (R2-C1) Clarify novelty delta vs. Smith'24 in Section 2 related work — commitment: `already_done` — status: verify wording
+   - [ ] (R3-C4) Add runtime breakdown figure to Appendix B — commitment: `future_work_only` — status: deferred, note in camera-ready
+   - ...
+   ```
+
+   Checklist items must be **atomic** (one paper edit per line) and each must reference its `issue_id` so it maps back to `ISSUE_BOARD.md`.
+
+3. **Grouped view** — the same items regrouped by (a) paper section/location and (b) severity, so the author can plan the revision pass efficiently.
+
+4. **Commitment summary** — counts of `already_done` / `approved_for_rebuttal` / `future_work_only`, plus any `needs_user_input` items that are blocking.
+
+5. **Out-of-scope log** — reviewer concerns that will **not** trigger a paper revision (e.g. `deferred_intentionally`, `narrow_concession` with no edit), with a one-line reason each. This keeps the checklist honest: nothing silently disappears.
+
+Rules for `REVISION_PLAN.md`:
+- Every checklist item must map to at least one `issue_id` from `ISSUE_BOARD.md`.
+- Every promise in `REBUTTAL_DRAFT_v1.md` that implies a paper edit must appear as a checklist item — if it is not in the plan, it is a commitment-gate violation.
+- Never add items that are not backed by the draft or by user-confirmed evidence.
+- On rerun / follow-up rounds, update checkbox state in place rather than regenerating from scratch.
+
 ### Phase 5: Safety Validation
 
 Run all lints:
 1. **Coverage** — every issue maps to draft anchor
 2. **Provenance** — every factual sentence has source
-3. **Commitment** — promises are approved
+3. **Commitment** — promises are approved AND every paper-edit promise in the draft appears as a checklist item in `REVISION_PLAN.md` (and vice versa — no orphan items in the plan)
 4. **Tone** — flag aggressive/submissive/evasive phrases
 5. **Consistency** — no contradictions across reviewer replies
 6. **Limit** — exact character count, compress if over (redundancy → friendly → opener → wording, never drop critical answers)
@@ -212,9 +247,11 @@ Produce **two outputs** for different purposes:
    - Useful for follow-up rounds — the extra material is pre-written
 
 3. Update `rebuttal/REBUTTAL_STATE.md`
-4. Present to user:
+4. Refresh `rebuttal/REVISION_PLAN.md` so the overall checklist matches the final draft (add items, mark `already_done` as checked, carry forward any `pending` items)
+5. Present to user:
    - `PASTE_READY.txt` character count vs venue limit
    - `REBUTTAL_DRAFT_rich.md` for review and manual editing
+   - `REVISION_PLAN.md` checklist — counts of pending / approved / deferred
    - Remaining risks + lines needing manual approval
 
 ### Phase 8: Follow-Up Rounds
@@ -224,9 +261,10 @@ When new reviewer comments arrive:
 1. Append verbatim to `rebuttal/FOLLOWUP_LOG.md`
 2. Link to existing issues or create new ones
 3. Draft **delta reply only** (not full rewrite)
-4. Re-run safety lints
-5. Use Codex MCP reply for continuity if useful
-6. Rules: escalate technically not rhetorically; concede if reviewer is correct; stop arguing if reviewer is immovable and no new evidence exists
+4. Update `rebuttal/REVISION_PLAN.md` in place — add any new checklist items introduced by the follow-up, tick off items the author has already completed, and keep existing items' status current
+5. Re-run safety lints
+6. Use Codex MCP reply for continuity if useful
+7. Rules: escalate technically not rhetorically; concede if reviewer is correct; stop arguing if reviewer is immovable and no new evidence exists
 
 ## Key Rules
 
PATCH

echo "Gold patch applied."
