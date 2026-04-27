#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bria-skill

# Idempotency guard
if grep -qF "### Step 1: Check if the key exists (without printing the key)" "skills/bria-ai/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/bria-ai/SKILL.md b/skills/bria-ai/SKILL.md
@@ -19,10 +19,14 @@ Generate, edit, and create visual assets using Bria's commercially-safe AI model
 
 Before making any Bria API call, check for the API key and help the user set it up if missing:
 
-### Step 1: Check if the key exists
+### Step 1: Check if the key exists (without printing the key)
 
 ```bash
-echo $BRIA_API_KEY
+if [ -z "$BRIA_API_KEY" ]; then
+  echo "BRIA_API_KEY is not set"
+else
+  echo "BRIA_API_KEY is set"
+fi
 ```
 
 If the output is **not empty**, skip to the next section.
PATCH

echo "Gold patch applied."
