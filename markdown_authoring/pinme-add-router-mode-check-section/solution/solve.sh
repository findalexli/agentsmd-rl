#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pinme

# Idempotency guard
if grep -qF "Before building a frontend project for IPFS deployment, ensure it uses **hash mo" ".claude/skills/pinme/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/pinme/SKILL.md b/.claude/skills/pinme/SKILL.md
@@ -22,7 +22,7 @@ keywords:
 
 # PinMe Skill
 
-Use PinMe CLI to upload files to IPFS and get a preview URL.
+Use PinMe CLI to upload files and get a preview URL.
 
 ## When to Use
 
@@ -91,6 +91,13 @@ Users can visit the preview page to:
 - View or download the uploaded files
 - Get a fixed domain: `https://<name>.pinit.eth.limo`
 
+## Router Mode Check
+
+Before building a frontend project for IPFS deployment, ensure it uses **hash mode** routing (e.g., `/#/about`). History mode (e.g., `/about`) will cause **404 errors** on sub-routes when deployed to IPFS, because there is no server to handle fallback routing.
+
+- **React**: Use `HashRouter` instead of `BrowserRouter`
+- **Vue**: Use `createWebHashHistory()` instead of `createWebHistory()`
+
 ## Important Rules
 
 **DO:**
PATCH

echo "Gold patch applied."
