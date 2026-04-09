#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q 'return defaultResultOrder();' src/js/node/dns.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the fix
git apply - <<'PATCH'
diff --git a/src/js/node/dns.ts b/src/js/node/dns.ts
index 03ea35aa8ba..98cf6114bc5 100644
--- a/src/js/node/dns.ts
+++ b/src/js/node/dns.ts
@@ -92,7 +92,7 @@ function setDefaultResultOrder(order) {
 }

 function getDefaultResultOrder() {
-  return defaultResultOrder;
+  return defaultResultOrder();
 }

 function setServersOn(servers, object) {
@@ -943,7 +943,9 @@ const promises = {
     }
   },

+  getDefaultResultOrder,
   setDefaultResultOrder,
+  getServers,
   setServers,
 };

PATCH

echo "Patch applied successfully."
