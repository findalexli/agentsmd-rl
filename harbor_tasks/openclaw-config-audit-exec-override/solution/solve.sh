#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openclaw

# Idempotency check: if the exec override test case already exists, skip
if grep -q 'newly denied exec override' src/security/audit.test.ts 2>/dev/null; then
  echo "Patch already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/src/security/audit.test.ts b/src/security/audit.test.ts
index 8397ebd02ba2..b66531b71fcf 100644
--- a/src/security/audit.test.ts
+++ b/src/security/audit.test.ts
@@ -650,6 +650,17 @@ description: test skill
         },
         expectedSeverity: "critical",
       },
+      {
+        name: "newly denied exec override",
+        cfg: {
+          gateway: {
+            bind: "lan",
+            auth: { token: "secret" },
+            tools: { allow: ["exec"] },
+          },
+        },
+        expectedSeverity: "critical",
+      },
     ];
     await runConfigAuditCases(
       cases,

PATCH

echo "Patch applied successfully."
