#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "- **Unchanged invariants:** [Existing APIs, interfaces, or behaviors that this p" "plugins/compound-engineering/skills/ce-plan/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-plan/SKILL.md b/plugins/compound-engineering/skills/ce-plan/SKILL.md
@@ -311,6 +311,7 @@ Before detailing implementation units, decide whether an overview would help a r
 | Data pipeline or transformation | Data flow sketch |
 | State-heavy lifecycle | State diagram |
 | Complex branching logic | Flowchart |
+| Mode/flag combinations or multi-input behavior | Decision matrix (inputs -> outcomes) |
 | Single-component with non-obvious shape | Pseudo-code sketch |
 
 **When to skip it:**
@@ -508,10 +509,13 @@ deepened: YYYY-MM-DD  # optional, set when the confidence check substantively st
 - **State lifecycle risks:** [Partial-write, cache, duplicate, or cleanup concerns]
 - **API surface parity:** [Other interfaces that may require the same change]
 - **Integration coverage:** [Cross-layer scenarios unit tests alone will not prove]
+- **Unchanged invariants:** [Existing APIs, interfaces, or behaviors that this plan explicitly does not change — and how the new work relates to them. Include when the change touches shared surfaces and reviewers need blast-radius assurance]
 
 ## Risks & Dependencies
 
-- [Meaningful risk, dependency, or sequencing concern]
+| Risk | Mitigation |
+|------|------------|
+| [Meaningful risk] | [How it is addressed or accepted] |
 
 ## Documentation / Operational Notes
 
@@ -542,7 +546,9 @@ For larger `Deep` plans, extend the core template only when useful with sections
 
 ## Risk Analysis & Mitigation
 
-- [Risk]: [Mitigation]
+| Risk | Likelihood | Impact | Mitigation |
+|------|-----------|--------|------------|
+| [Risk] | [Low/Med/High] | [Low/Med/High] | [How addressed] |
 
 ## Phased Delivery
 
PATCH

echo "Gold patch applied."
