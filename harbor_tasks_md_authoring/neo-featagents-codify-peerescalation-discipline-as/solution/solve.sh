#!/usr/bin/env bash
set -euo pipefail

cd /workspace/neo

# Idempotency guard
if grep -qF "7. **Peer Escalation Protocol (Swarm Strength Primitive):** *\"Stuck is data, not" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -213,8 +213,9 @@ To maintain repository hygiene and improve test coverage, you MUST adhere to the
 2. **No Throwaway Scripts:** You are strictly **FORBIDDEN** from using `run_shell_command` (e.g., `cat << EOF > test.js`) to create temporary testing scripts on the filesystem.
 3. **Permanent Coverage:** If you are testing or validating Neo.mjs framework logic, behavior, or regressions, you MUST add the validation logic as a permanent test case inside the appropriate Playwright test file (e.g., `test/playwright/unit/data/Store.spec.mjs`). Use the `replace` or `write_file` tools to do this. A task is not complete unless its framework logic is permanently verifiable.
 4. **Live VDOM Simulation (Neural Link):** For **frontend tasks**, during tactical debugging, you **MUST** prioritize **direct** Neural Link agent introspection (e.g., `inspect_component_render_tree` via the `neural-link` skill) over the repetitive execution of Whitebox E2E test suites. Validate mathematically that the VDOM generates the correct payload individually before falling back to full browser framework suites.
-5. **Productive Failure Loop (The Tripwire):** If the same verification strategy (e.g., E2E test) fails 3 to 5 times for the same logical hypothesis, STOP execution. Do not panic. Instead, step back and challenge your architectural assumptions. You **MUST** document the paradox locally (e.g., in `walkthrough.md` or a `scratch` artifact), invoke `add_memory`, and ask the user for guidance. Only escalate to creating an R&D ticket or GH Discussion if the blocker is systemic and requires asynchronous external review.
-6. **Global Turn Limit (25-Turn Guardrail):** If you reach 25 turns on a single task without resolution, you MUST perform a hard cut. Stop coding, invoke `add_memory`, and provide a comprehensive status report to the user detailing the blockage.
+5. **Productive Failure Loop (The Tripwire):** If the same verification strategy (e.g., E2E test) fails 3 to 5 times for the same logical hypothesis, STOP execution. Do not panic. Instead, step back and challenge your architectural assumptions. You **MUST** document the paradox locally (e.g., in `walkthrough.md` or a `scratch` artifact), invoke `add_memory`, and ask the user for guidance — but **first consider #7 (Peer Escalation Protocol) below**: cross-family peer escalation is lower-cost than user-tier escalation and frequently resolves the paradox without reaching this rule's user-tier hand-off. Only escalate to creating an R&D ticket or GH Discussion if the blocker is systemic and requires asynchronous external review.
+6. **Global Turn Limit (25-Turn Guardrail):** If you reach 25 turns on a single task without resolution, you MUST perform a hard cut. Stop coding, invoke `add_memory`, and provide a comprehensive status report to the user detailing the blockage. **Earlier peer escalation per #7 below is the discipline that prevents reaching this hard cut** — by turn 25, the cost of context-recovery typically exceeds the cost of asking your peer at turn 5-10.
+7. **Peer Escalation Protocol (Swarm Strength Primitive):** *"Stuck is data, not failure. Asking is discipline."* When you encounter friction that resists multiple debugging hypotheses (substrate-edge ambiguity, cross-family-knowledge gap, multi-turn diminishing returns), your cross-family peer (e.g., `@neo-opus-4-7` ↔ `@neo-gemini-3-1-pro`) is often the lowest-cost source of fresh-perspective unblock. Send an A2A message via `add_message` with: empirical state (what you tested, what passed/failed) + hypothesis enumeration (what you've ruled out and why) + specific ask (not "help me solve this" but "have you seen this pattern? / what would you check next?") + explicit *"I'm escalating per §10.7"* framing. Peer escalation is a sign of structural awareness, not weakness — it fires earlier and lower-cost than the user-tier rules above (#5, #6), and frequently resolves friction that would otherwise reach them. The cost stratification is explicit: peer-tier (low — async A2A, peer responds when convenient) → user-tier #5 (medium — interrupts user attention) → user-tier #6 (high — comprehensive status report, hard work-stop). **Do NOT defer escalating because** *"my peer might be busy"* (A2A is async; their response timing is theirs), *"I should figure this out solo"* (solo loops on substrate-edge cases waste compute), or *"asking is admitting failure"* (wrong framing — earlier escalation IS the wisdom that prevents reaching #6's 25-turn hard-cut). Empirical anchor: session `aaf22f06-cc5c-4dff-aa2f-7d5efb3a6343` (2026-04-26) — an agent encountered a Playwright/ES-module load-order paradox; substantial turn budget burned on solo debugging before user-triggered escalation surfaced cross-family contribution that unblocked in a single A2A response. The substrate worked when invoked; this rule codifies the reflex to invoke it proactively.
 
 ## 11. File Editing Tool Selection (The "Append Gap")
 
PATCH

echo "Gold patch applied."
