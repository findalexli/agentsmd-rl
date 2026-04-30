#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "1. **Verify before claiming** \u2014 When the brainstorm touches checkable infrastruc" "plugins/compound-engineering/skills/ce-brainstorm/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-brainstorm/SKILL.md b/plugins/compound-engineering/skills/ce-brainstorm/SKILL.md
@@ -87,7 +87,11 @@ Scan the repo before substantive brainstorming. Match depth to scope:
 
 *Topic Scan* — Search for relevant terms. Read the most relevant existing artifact if one exists (brainstorm, plan, spec, skill, feature doc). Skim adjacent examples covering similar behavior.
 
-If nothing obvious appears after a short scan, say so and continue. Do not drift into technical planning — avoid inspecting tests, migrations, deployment, or low-level architecture unless the brainstorm is itself about a technical decision.
+If nothing obvious appears after a short scan, say so and continue. Two rules govern technical depth during the scan:
+
+1. **Verify before claiming** — When the brainstorm touches checkable infrastructure (database tables, routes, config files, dependencies, model definitions), read the relevant source files to confirm what actually exists. Any claim that something is absent — a missing table, an endpoint that doesn't exist, a dependency not in the Gemfile, a config option with no current support — must be verified against the codebase first; if not verified, label it as an unverified assumption. This applies to every brainstorm regardless of topic.
+
+2. **Defer design decisions to planning** — Implementation details like schemas, migration strategies, endpoint structure, or deployment topology belong in planning, not here — unless the brainstorm is itself about a technical or architectural decision, in which case those details are the subject of the brainstorm and should be explored.
 
 #### 1.2 Product Pressure Test
 
@@ -263,6 +267,7 @@ Before finalizing, check:
 - Do any requirements depend on something claimed to be out of scope?
 - Are any unresolved items actually product decisions rather than planning questions?
 - Did implementation details leak in when they shouldn't have?
+- Do any requirements claim that infrastructure is absent without that claim having been verified against the codebase? If so, verify now or label as an unverified assumption.
 - Is there a low-cost change that would make this materially more useful?
 - Would a visual aid (flow diagram, comparison table, relationship diagram) help a reader grasp the requirements faster than prose alone?
 
PATCH

echo "Gold patch applied."
