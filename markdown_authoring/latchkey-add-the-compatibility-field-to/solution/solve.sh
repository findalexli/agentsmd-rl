#!/usr/bin/env bash
set -euo pipefail

cd /workspace/latchkey

# Idempotency guard
if grep -qF "compatibility: Requires node, curl, latchkey (npm install -g latchkey)." "integrations/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/integrations/SKILL.md b/integrations/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: latchkey
 description: Interact with third-party services (Slack, Discord, Dropbox, GitHub, Linear...) on user's behalf using their public APIs.
+compatibility: Requires node, curl, latchkey (npm install -g latchkey).
 ---
 
 # Latchkey
PATCH

echo "Gold patch applied."
