#!/usr/bin/env bash
set -euo pipefail

cd /workspace/fizzy

# Idempotency guard
if grep -qF "Note: `beta` is a template requiring `BETA_NUMBER` env var; typical targets are " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -50,6 +50,14 @@ bin/jobs                     # Manage Solid Queue jobs
 bin/kamal deploy             # Deploy (requires 1Password CLI for secrets)
 ```
 
+## Deploy
+
+Default branch: `main`
+Pre-deploy: `bin/rails saas:enable`
+Deploy: `bin/kamal deploy -d <destination>`
+Destinations: production, staging, beta, beta1, beta2, beta3, beta4
+Note: `beta` is a template requiring `BETA_NUMBER` env var; typical targets are `beta1`-`beta4`.
+
 ## Architecture Overview
 
 ### Multi-Tenancy (URL-Based)
PATCH

echo "Gold patch applied."
