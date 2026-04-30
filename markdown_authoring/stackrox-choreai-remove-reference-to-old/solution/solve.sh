#!/usr/bin/env bash
set -euo pipefail

cd /workspace/stackrox

# Idempotency guard
if grep -qF "AGENTS.md" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -3,7 +3,6 @@ This file provides guidance when working with code in this repository.
 ## Repository Information
 
 **Upstream Repository**: https://github.com/stackrox/stackrox
-**Legacy Upstream Repository**: https://github.com/stackrox/rox - archived, but may contain valuable past information
 
 ## Workflow
 
PATCH

echo "Gold patch applied."
