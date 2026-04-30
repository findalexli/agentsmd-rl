#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cube

# Idempotency guard
if grep -qF "- Semantic Model IDE (short: \"IDE\")" ".cursor/rules/namings-rule.mdc" && grep -qF "Our cloud product codebase is located in ~/code/cubejs-enterprise (at least that" ".cursor/rules/writing-documentation.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/namings-rule.mdc b/.cursor/rules/namings-rule.mdc
@@ -1,7 +1,6 @@
 ---
-description: Product naming conventions for Cube documentation
 globs: docs-mintlify/**
-alwaysApply: false
+alwaysApply: true
 ---
 
 # Product Naming Conventions
@@ -16,3 +15,29 @@ alwaysApply: false
 - **Development** — development deployment type (legacy: "Development instance")
 - **Production** — production deployment type (legacy: "Production cluster")
 - **Multi-cluster** — multi-cluster production deployment type (legacy: "Production multi-cluster")
+
+# Product Taxonomy
+Make sure to use correct terms.
+
+- **Account**
+  - **Deployment**
+    - **Analytics Chat**
+    - **Workbook**
+      - Tab
+      - Dashboard builder
+    - **Dashboard**
+      - Scheduled refresh
+    - **Semantic Model**
+      - Semantic Model IDE (short: "IDE")
+      - Semantic Model Agent
+    - **Explore**
+      - Explorations
+    - **API**
+      - Embed APIs
+      - Core Data APIs
+      - Management APIs
+        - Orchestration API
+  - **Embedding**
+    - Private embedding
+    - Signed embedding
+    - Creator Mode
diff --git a/.cursor/rules/writing-documentation.mdc b/.cursor/rules/writing-documentation.mdc
@@ -0,0 +1,9 @@
+---
+alwaysApply: true
+globs: docs-mintlify/**
+---
+
+This repo only contains code for Cube Core and documentation.
+Our cloud product codebase is located in ~/code/cubejs-enterprise (at least that is where it is located on Artyom's mac). Research the cloud product codebase when documenting new features.
+Our documenation is built with https://www.mintlify.com. Make sure you follow Mintlify best practices when designing documentation.
+Our competitors are [Omni](https://omni.co/) and [Hex](https://hex.tech/). We use their documentation sometimes as a reference.
\ No newline at end of file
PATCH

echo "Gold patch applied."
