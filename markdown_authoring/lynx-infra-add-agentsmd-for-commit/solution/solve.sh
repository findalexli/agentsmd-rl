#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lynx

# Idempotency guard
if grep -qF "- Module or subsystem name (e.g., `Clay`, `Layout`, `Headers`, `Painting`, `Harm" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,22 @@
+## Conventions
+
+- All commit messages MUST be written in **English**.
+- Preferred format:
+
+  Header:
+  `[Type][Scope] Short imperative summary`
+
+  Body (details):
+  `- What changed`
+  `- Why it was needed`
+  `- How it was verified / impacts`
+
+  Footer (optional):
+  `issue: #12345`
+
+### Type
+- `Feature`, `BugFix`, `Optimize`, `Refactor`, `Infra`, `Docs`, `Test`, etc., using capitalized English.
+
+### Scope
+- Module or subsystem name (e.g., `Clay`, `Layout`, `Headers`, `Painting`, `Harmony`, `Android`, `iOS`, etc.), optional but recommended.
+
PATCH

echo "Gold patch applied."
