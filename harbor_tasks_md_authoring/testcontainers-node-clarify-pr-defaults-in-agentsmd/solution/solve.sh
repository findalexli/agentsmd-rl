#!/usr/bin/env bash
set -euo pipefail

cd /workspace/testcontainers-node

# Idempotency guard
if grep -qF "- Repository-specific instructions in this file override generic coding-agent de" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -5,6 +5,11 @@
 This is a working guide for contributors and coding agents in this repository.
 It captures practical rules that prevent avoidable CI and PR churn.
 
+## Instruction precedence
+
+- Repository-specific instructions in this file override generic coding-agent defaults, skills, and templates.
+- If a generic workflow conflicts with this file, follow this file.
+
 ## Repository Layout
 
 - This repository is an npm workspaces monorepo.
PATCH

echo "Gold patch applied."
