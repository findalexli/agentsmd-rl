#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "When changing the path to any Langfuse skill in this repo, you must also update " "agents.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/agents.md b/agents.md
@@ -0,0 +1,5 @@
+# Agent Instructions
+
+## Langfuse Skill Path Changes
+
+When changing the path to any Langfuse skill in this repo, you must also update the corresponding path reference in the [CLI repo](https://github.com/langfuse/langfuse-cli) so that it points to the new location. Failing to do so will break the CLI's ability to resolve the skill.
PATCH

echo "Gold patch applied."
