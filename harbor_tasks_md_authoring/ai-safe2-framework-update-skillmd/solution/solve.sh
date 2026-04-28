#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ai-safe2-framework

# Idempotency guard
if grep -qF "skill.md" "skill.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skill.md b/skill.md
@@ -916,16 +916,6 @@ Before finalizing any response, verify:
 
 ## 🏁 End of SKILL.md
 
-**You are now ready to be the AI SAFE² Secure Build Copilot.**
-
-When a user engages with you:
-1. Activate immediately if they mention AI agents, security, or compliance
-2. Ground all responses in the 5 pillars (S-A-F-E-E)
-3. Provide actionable, code-level recommendations
-4. Generate before/after metrics to prove value
-5. Map everything to ISO 42001, NIST AI RMF, SOC 2, and other frameworks
-6. Be concise, opinionated, and helpful
-
 **Remember:** Security is not a checklist — it's a mindset. Help users build AI systems they can trust, audit, and defend.
 
 Let's make AI safe, together. 🛡️
PATCH

echo "Gold patch applied."
