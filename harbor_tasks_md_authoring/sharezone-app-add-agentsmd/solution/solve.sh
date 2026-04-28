#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sharezone-app

# Idempotency guard
if grep -qF "Please refer to our [contribution guidelines](./CONTRIBUTING.md) for information" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,7 @@
+# Agents
+
+Please refer to our [contribution guidelines](./CONTRIBUTING.md) for information on topics such as:
+
+- How to run the app
+- How to run tests
+- How to add multi-language strings
PATCH

echo "Gold patch applied."
