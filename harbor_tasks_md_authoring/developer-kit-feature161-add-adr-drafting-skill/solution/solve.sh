#!/usr/bin/env bash
set -euo pipefail

cd /workspace/developer-kit

# Idempotency guard
if grep -qF "Use this skill when a user or agent has decided on a meaningful architectural ch" "plugins/developer-kit-core/skills/adr-drafting/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/developer-kit-core/skills/adr-drafting/SKILL.md b/plugins/developer-kit-core/skills/adr-drafting/SKILL.md
@@ -18,15 +18,7 @@ See `references/template.md` for the default ADR template and `references/exampl
 
 ## When to Use
 
-Use this skill when:
-
-- A user or agent has decided on a meaningful architectural change
-- The team wants to document the rationale behind a framework, database, infrastructure, or integration choice
-- A project needs a durable history of architectural decisions for onboarding and maintenance
-- Someone asks to "create an ADR", "document this architecture decision", or "write a decision record"
-- A new technical direction introduces important trade-offs that should be captured explicitly
-
-**Trigger phrases:** "create an ADR", "document the architecture decision", "write a decision record", "record this technical choice", "add an ADR"
+Use this skill when a user or agent has decided on a meaningful architectural change and needs to document the rationale, chosen direction, and trade-offs in a new Architecture Decision Record. It fits requests such as creating an ADR, documenting an architecture decision, writing a decision record, or preserving the project history behind an important technical choice.
 
 ## Instructions
 
@@ -39,12 +31,9 @@ Ask the user for the minimum information needed to draft a new ADR:
 3. Context: the problem, constraints, or forces driving the decision
 4. Decision: the chosen approach
 5. Consequences: what becomes easier, harder, riskier, or more expensive
-
-Also confirm:
-
-- This request is for a **new ADR**, not for editing an existing ADR
-- The desired repository language if documentation language is unclear
-- Whether any existing ADR naming convention must be preserved
+6. Confirm that this request is for a **new ADR**, not for editing an existing ADR
+7. Confirm the desired repository language if documentation language is unclear
+8. Confirm whether any existing ADR naming convention must be preserved
 
 If the user actually wants to update an existing ADR, change statuses in older ADRs, or manage supersession links, explain that this skill only drafts **new ADR documents** and ask whether they want to proceed with a new record instead.
 
PATCH

echo "Gold patch applied."
