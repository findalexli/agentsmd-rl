#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "- **Rigor probes fire before Phase 2 and are prose, not menus.** Narrowing is le" "plugins/compound-engineering/skills/ce-brainstorm/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-brainstorm/SKILL.md b/plugins/compound-engineering/skills/ce-brainstorm/SKILL.md
@@ -128,28 +128,38 @@ If nothing obvious appears after a short scan, say so and continue. Two rules go
 
 #### 1.2 Product Pressure Test
 
-Before generating approaches, challenge the request to catch misframing. Match depth to scope:
+Before generating approaches, scan the user's opening for rigor gaps. Match depth to scope.
+
+This is agent-internal analysis, not a user-facing checklist. Read the opening, note which gaps actually exist, and raise only those as questions during Phase 1.3 — folded into the normal flow of dialogue, not fired as a pre-flight gauntlet. A fuzzy opening may earn three or four probes; a concrete, well-framed one may earn zero because no scope-appropriate gaps were found.
 
 **Lightweight:**
 - Is this solving the real user problem?
 - Are we duplicating something that already covers this?
 - Is there a clearly better framing with near-zero extra cost?
 
-**Standard:**
-- Is this the right problem, or a proxy for a more important one?
-- What user or business outcome actually matters here?
-- What happens if we do nothing?
+**Standard — scan for these gaps:**
+
+- **Evidence gap.** The opening asserts want or need, but doesn't point to anything the would-be user has already done — time spent, money paid, workarounds built — that would make the want observable. When present, ask for the most concrete thing someone has already done about this.
+
+- **Specificity gap.** The opening describes the beneficiary at a level of abstraction where the agent couldn't design without silently inventing who they are and what changes for them. When present, ask the user to name a specific person or narrow segment, and what changes for that person when this ships.
+
+- **Counterfactual gap.** The opening doesn't make visible what users do today when this problem arises, nor what changes if nothing ships. When present, ask what the current workaround is, even if it's messy — and what it costs them.
+
+- **Attachment gap.** The opening treats a particular solution shape as the thing being built, rather than the value that shape is supposed to deliver, and hasn't been examined against smaller forms that might deliver the same value. When present, ask what the smallest version that still delivers real value would look like.
+
+Plus these synthesis questions — not gap lenses, product-judgment the agent weighs in its own reasoning:
 - Is there a nearby framing that creates more user value without more carrying cost? If so, what complexity does it add?
 - Given the current project state, user goal, and constraints, what is the single highest-leverage move right now: the request as framed, a reframing, one adjacent addition, a simplification, or doing nothing?
-- Favor moves that compound value, reduce future carrying cost, or make the product meaningfully more useful or compelling
-- Use the result to sharpen the conversation, not to bulldoze the user's intent
 
-**Deep** — Standard questions plus:
-- What durable capability should this create in 6-12 months?
-- Does this move the product toward that, or is it only a local patch?
+Favor moves that compound value, reduce future carrying cost, or make the product meaningfully more useful or compelling. Use the result to sharpen the conversation, not to bulldoze the user's intent.
+
+**Deep** — Standard lenses and synthesis questions plus:
+- Is this a local patch, or does it move the broader system toward where it wants to be?
+
+**Deep — product** — Deep plus:
+
+- **Durability gap.** The opening's value proposition rests on a current state of the world that may shift in predictable ways within the horizon the user cares about. When present, ask how the idea fares under the most plausible near-term shifts — and push past rising-tide answers every competitor could make.
 
-**Deep — product** — Deep questions plus:
-- What's the single sharpest user outcome this earns, and what evidence or assumption supports that outcome?
 - What adjacent product could we accidentally build instead, and why is that the wrong one?
 - What would have to be true in the world for this to fail?
 
@@ -162,6 +172,7 @@ Follow the Interaction Rules above. Use the platform's blocking question tool wh
 **Guidelines:**
 - Ask what the user is already thinking before offering your own ideas. This surfaces hidden context and prevents fixation on AI-generated framings.
 - Start broad (problem, users, value) then narrow (constraints, exclusions, edge cases)
+- **Rigor probes fire before Phase 2 and are prose, not menus.** Narrowing is legitimate, but Phase 1 cannot end with un-probed rigor gaps. Each scope-appropriate gap from Phase 1.2 fires as a **separate** direct prose probe — one probe satisfies one gap, not multiple. Standard brainstorms scan four gap lenses (evidence, specificity, counterfactual, attachment); Deep-product adds durability (five total), but only the gaps actually present in the opening must be probed. Surface those probes progressively across the conversation — interleaving with narrowing moves is fine, as long as every scope-appropriate gap that was found in Phase 1.2 has been probed in prose before Phase 2. Rigor probes map to Interaction Rule 5(b): a 4-option menu signals which kinds of evidence count and lets the user pick rather than produce. Prose forces them to produce real observation or surface their uncertainty. Examples (one per gap): *evidence — "What's the most concrete thing someone's already done about this — paid, built a workaround, quit a tool over it?"* / *specificity — "Can you name a team you've actually watched hit this, or are you reasoning?"* / *counterfactual — "What do teams do today when this breaks — who reconciles?"* / *attachment — "Before we move to shapes or approaches — what's the smallest version that would still prove the bet right, and what's excluded?"* — **attachment is the final rigor probe before Phase 2 when the attachment gap is present. Fire it regardless of whether a specific shape has emerged through narrowing; its job is to pressure-test the user's implicit framing of the product before Phase 2 inherits it** / *durability — "Under the most plausible near-term shifts, how does this bet hold?"* If the answer reveals genuine uncertainty, record it as an explicit assumption in the requirements document rather than skipping the probe.
 - Clarify the problem frame, validate assumptions, and ask about success criteria
 - Make requirements concrete enough that planning will not need to invent behavior
 - Surface dependencies or prerequisites only when they materially affect scope
PATCH

echo "Gold patch applied."
