#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-rules

# Idempotency guard
if grep -qF "docs/swift-observation.mdc" "docs/swift-observation.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/docs/swift-observation.mdc b/docs/swift-observation.mdc

PATCH

echo "Gold patch applied."
