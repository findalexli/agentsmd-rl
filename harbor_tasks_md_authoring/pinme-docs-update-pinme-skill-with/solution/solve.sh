#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pinme

# Idempotency guard
if grep -qF "- AppKey configuration (use `pinme set-appkey`)" "skills/pinme/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/pinme/SKILL.md b/skills/pinme/SKILL.md
@@ -22,6 +22,10 @@ keywords:
 
 Use PinMe CLI to deploy static files to IPFS and get a preview URL.
 
+## System Requirements
+
+- Node.js version 16.13.0 or higher required
+
 ## When to Use
 
 - User requests deployment of a frontend project
@@ -133,4 +137,28 @@ pinme ls -l 5
 
 # Remove uploaded file
 pinme rm <hash>
+
+# Configure authentication
+pinme set-appkey
+
+# Display available domains
+pinme my-domains
+
+# End session
+pinme logout
 ```
+
+## File Size Limits
+
+| Type | Limit |
+|------|-------|
+| Single file | 200MB maximum |
+| Total directory | 1GB maximum |
+
+## Fixed Domain Binding
+
+Format: `https://<name>.pinit.eth.limo`
+
+**Requirements:**
+- Plus membership
+- AppKey configuration (use `pinme set-appkey`)
PATCH

echo "Gold patch applied."
