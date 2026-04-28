#!/usr/bin/env bash
set -euo pipefail

cd /workspace/datadog-agent

# Idempotency guard
if grep -qF "# install dda on mac OS" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -41,7 +41,11 @@ The Datadog Agent is a comprehensive monitoring and observability agent written
 ### Common Commands
 
 #### Building
+
 ```bash
+# install dda on mac OS
+brew install --cask dda
+
 # Install development tools
 dda inv install-tools
 
PATCH

echo "Gold patch applied."
