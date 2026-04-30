#!/usr/bin/env bash
set -euo pipefail

cd /workspace/marketingskills

# Idempotency guard
if grep -qF "3. What's the primary business goal? (Retention, activation, word-of-mouth, supp" "skills/community-marketing/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/community-marketing/SKILL.md b/skills/community-marketing/SKILL.md
@@ -141,3 +141,23 @@ Depending on what the user needs, produce one of:
 - **Health Audit Report** — Current metrics, diagnosis, top 3 priorities to fix
 
 Always be specific. Generic advice ("be consistent," "provide value") is not useful. Give the user something they can act on today.
+
+---
+
+## Task-Specific Questions
+
+1. What platform are you building on (or considering)?
+2. What stage is the community at? (Pre-launch, early, growing, established)
+3. What's the primary business goal? (Retention, activation, word-of-mouth, support deflection)
+4. Who is the ideal community member and what motivates them?
+5. Do you have existing users or customers to seed from?
+6. How much time can you dedicate to community management weekly?
+
+---
+
+## Related Skills
+
+- **referral-program**: For structured referral and ambassador incentive programs
+- **churn-prevention**: For retention strategies that complement community engagement
+- **social-content**: For content creation across social platforms
+- **customer-research**: For understanding your community members' needs and language
PATCH

echo "Gold patch applied."
