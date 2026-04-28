#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "> AUTHORIZED USE ONLY: Use this skill only for authorized penetration testing en" "skills/ethical-hacking-methodology/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/ethical-hacking-methodology/SKILL.md b/skills/ethical-hacking-methodology/SKILL.md
@@ -1,12 +1,14 @@
 ---
 name: ethical-hacking-methodology
 description: "Master the complete penetration testing lifecycle from reconnaissance through reporting. This skill covers the five stages of ethical hacking methodology, essential tools, attack techniques, and professional reporting for authorized security assessments."
-risk: unknown
+risk: offensive
 source: community
 author: zebbern
 date_added: "2026-02-27"
 ---
 
+> AUTHORIZED USE ONLY: Use this skill only for authorized penetration testing engagements, defensive validation, or controlled educational environments.
+
 # Ethical Hacking Methodology
 
 ## Purpose
PATCH

echo "Gold patch applied."
