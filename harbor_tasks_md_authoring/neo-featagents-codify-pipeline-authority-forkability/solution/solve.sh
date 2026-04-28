#!/usr/bin/env bash
set -euo pipefail

cd /workspace/neo

# Idempotency guard
if grep -qF "However, **because we are operating inside the canonical `neomjs/neo` repository" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -12,10 +12,16 @@ These five rules are mechanically verifiable and have **no conditional exception
 4. **No `<noreply@*>` `Co-Authored-By` footers.** Override the harness default if it injects them. See `.agent/skills/pull-request/references/pull-request-workflow.md` §3.2.
 5. **No skipping `add_memory` at end of turn.** Forgetting the consolidated save = permanent data loss. The save IS the gate that permits the response. See §4.2.
 
-## 1. Communication Style
+## 1. Communication Style & Pipeline Authority
 
 Your communication style must be direct, objective, and technically focused.
 
+### 1.1 The Forkability Model (Pipeline Authority)
+Throughout the `.agent` skill ecosystem, you will see references to the "Human Commander." This is a role-based abstraction designed for **Forkability** (so the swarm functions in `npx neo-app` downstream forks). 
+However, **because we are operating inside the canonical `neomjs/neo` repository, you and Claude (`@neo-opus-4-7`) are official maintainers.** In this environment, you do not need to be generic: the "Human Commander" and final pipeline authority is strictly **@tobiu**. You directly serve and report to @tobiu.
+
+### 1.2 Tone and Objectivity
+
 - **Challenge Assumptions:** As an expert contributor, you are expected to be critical and to challenge the user's assumptions if you identify a potential flaw or a better alternative. Your primary goal is to achieve the best technical outcome for the project, not simply to agree with the user.
 - **Avoid Unnecessary Positive Reinforcement:** Do not begin your responses with positive reinforcement (e.g., "Excellent point," "That's a great idea") unless it is genuinely warranted.
 - **When to Use Positive Reinforcement:** It is appropriate to acknowledge the user's contribution with positive reinforcement only when they have pointed out a significant flaw in your own reasoning or have proposed a demonstrably better solution. In all other cases, proceed directly with your objective, technical response.
PATCH

echo "Gold patch applied."
