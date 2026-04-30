#!/usr/bin/env bash
set -euo pipefail

cd /workspace/purchases-ios

# Idempotency guard
if grep -qF "When creating a pull request, **always add one of these labels** to categorize t" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -155,6 +155,21 @@ For snapshot testing, sample applications, pre-commit hooks, and release process
 - `CI.xcconfig` - CI-specific configuration
 - `api/*.swiftinterface` - Public API surface tracking
 
+### Pull Request Labels
+
+When creating a pull request, **always add one of these labels** to categorize the change. These labels determine automatic version bumps and changelog generation:
+
+| Label | When to Use |
+|-------|-------------|
+| `pr:feat` | New user-facing features or enhancements |
+| `pr:fix` | Bug fixes |
+| `pr:other` | Internal changes, refactors, CI, docs, or anything that shouldn't trigger a release |
+
+**Additional scope labels** (add alongside the primary label above):
+- `pr:RevenueCatUI` — Changes specific to the RevenueCatUI module (paywalls, customer center)
+- `feat:Paywalls_V2` — Changes related to Paywalls V2 (requires `pr:RevenueCatUI` as well)
+- `feat:Customer Center` — Changes related to Customer Center (requires `pr:RevenueCatUI` as well)
+
 ## When the Task is Ambiguous
 
 1. Search for similar existing implementation in this repo first
PATCH

echo "Gold patch applied."
