#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mattermost

# Idempotency guard
if grep -qF "Never run `go mod tidy` directly. Always run `make modules-tidy` instead \u2014 it ex" "server/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/server/AGENTS.md b/server/AGENTS.md
@@ -0,0 +1,5 @@
+# AGENTS.md
+
+Never run `go mod tidy` directly. Always run `make modules-tidy` instead — it excludes private enterprise imports that would otherwise break the tidy.
+
+After editing `i18n/en.json`, always run `make i18n-extract` — it regenerates the file with strings in the required order.
PATCH

echo "Gold patch applied."
