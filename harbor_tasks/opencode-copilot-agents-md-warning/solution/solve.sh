#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency guard
if grep -q "THIS IS ONLY FOR GITHUB COPILOT" packages/opencode/src/provider/sdk/copilot/README.md 2>/dev/null; then
    echo "Solution already applied"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/opencode/src/provider/sdk/copilot/AGENTS.md b/packages/opencode/src/provider/sdk/copilot/AGENTS.md
new file mode 120000
index 000000000000..42061c01a1c7
--- /dev/null
+++ b/packages/opencode/src/provider/sdk/copilot/AGENTS.md
@@ -0,0 +1 @@
+README.md
\ No newline at end of file
diff --git a/packages/opencode/src/provider/sdk/copilot/README.md b/packages/opencode/src/provider/sdk/copilot/README.md
index 8ce03d614079..d1051a4da041 100644
--- a/packages/opencode/src/provider/sdk/copilot/README.md
+++ b/packages/opencode/src/provider/sdk/copilot/README.md
@@ -1,5 +1,5 @@
 This is a temporary package used primarily for GitHub Copilot compatibility.

-Avoid making changes to these files unless you only want to affect the Copilot provider.
+These DO NOT apply for openai-compatible providers or majority of providers supporting completions/responses apis. THIS IS ONLY FOR GITHUB COPILOT!!!

-Also, this should ONLY be used for the Copilot provider.
+Avoid making edits to these files
PATCH

echo "Solution applied"
