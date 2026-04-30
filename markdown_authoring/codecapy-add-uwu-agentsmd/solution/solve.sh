#!/usr/bin/env bash
set -euo pipefail

cd /workspace/codecapy

# Idempotency guard
if grep -qF "Important: always respond to the user in an UwU voice" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1 @@
+Important: always respond to the user in an UwU voice
PATCH

echo "Gold patch applied."
