#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sync-gateway

# Idempotency guard
if grep -qF "- Git: `main` branch is the current in-development version. Released versions an" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -4,6 +4,7 @@ Sync Gateway is a horizontally scalable web server that securely manages access
 
 ## Build & Test
 
+- Git: `main` branch is the current in-development version. Released versions and backports end up in `release/x.y.z` branches. Feature branches are typically just named `CBG-xxxx` after the Jira ticket.
 - Build: `go build -o bin/sync_gateway .`
 - Building or testing EE (requires private repo SSH access) must use the `cb_sg_enterprise, cb_sg_devmode` build tags for all Go commands. E.g: `go build -tags cb_sg_enterprise,cb_sg_devmode .`
 - Run all unit tests (Rosmar/in-memory, no Couchbase Server): `go test ./...`
PATCH

echo "Gold patch applied."
