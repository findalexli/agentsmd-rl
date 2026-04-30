#!/usr/bin/env bash
set -euo pipefail

cd /workspace/calcite-design-system

# Idempotency guard
if grep -qF "- When helpful, prefix review comments with a label so intent is clear. Format: " ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -131,7 +131,11 @@ In descending order when rules conflict:
 - When drafting review comments or PR text, be direct, collaborative, and specific.
 - Avoid sounding absolute, dismissive, or overly corrective.
 - Prefer wording that explains what changed and why in concrete terms.
-- When helpful, label the type of review comment up front (for example, `fixme` or `suggestion`) so the intent is clear.
+- When helpful, prefix review comments with a label so intent is clear. Format: `<label>:`. Suggested labels:
+  - `blocking:` must be addressed before merge (correctness, accessibility, security, breaking API)
+  - `suggestion:` optional improvement; author may adopt or explain why not
+  - `nit:` minor polish; not worth back-and-forth
+  - `question:` asking for clarification or rationale
 
 ## Reference Docs
 
PATCH

echo "Gold patch applied."
