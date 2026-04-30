#!/usr/bin/env bash
# Gold-patch solver. Inlines the diff from PR tuist/tuist#10086 verbatim.
set -euo pipefail

cd /workspace/tuist

# Idempotency: bail out early if the patch is already applied.
if grep -q "cache-au-east.tuist.dev" infra/registry-router/src/index.ts; then
  echo "Gold patch already applied; nothing to do."
  exit 0
fi

git apply --ignore-whitespace --whitespace=nowarn <<'PATCH'
diff --git a/infra/AGENTS.md b/infra/AGENTS.md
index 30f910ea47d4..d48ff92da3d3 100644
--- a/infra/AGENTS.md
+++ b/infra/AGENTS.md
@@ -28,9 +28,12 @@ Cloudflare Worker that geo-routes requests to `registry.tuist.dev` to the neares
 - `cache-eu-central.tuist.dev`
 - `cache-eu-north.tuist.dev`
 - `cache-us-east.tuist.dev`
+- `cache-us-east-2.tuist.dev`
+- `cache-us-east-3.tuist.dev`
 - `cache-us-west.tuist.dev`
 - `cache-ap-southeast.tuist.dev`
 - `cache-sa-west.tuist.dev`
+- `cache-au-east.tuist.dev`

 **Health Checks:** Cron Trigger every 60s writes health state to Workers KV (TTL 120s). Missing keys are treated as healthy (fail-open).

diff --git a/infra/registry-router/src/index.ts b/infra/registry-router/src/index.ts
index 067da7e5f8e8..8b05025a7b13 100644
--- a/infra/registry-router/src/index.ts
+++ b/infra/registry-router/src/index.ts
@@ -15,10 +15,13 @@ const EARTH_RADIUS_KM = 6371;
 const ORIGINS: Origin[] = [
   { host: "cache-eu-central.tuist.dev",   lat:  50.11, lon:    8.68 }, // Frankfurt
   { host: "cache-eu-north.tuist.dev",     lat:  60.17, lon:   24.94 }, // Helsinki
-  { host: "cache-us-east.tuist.dev",      lat:  39.04, lon:  -77.49 }, // Virginia
+  { host: "cache-us-east.tuist.dev",      lat:  39.04, lon:  -77.49 }, // Ashburn
+  { host: "cache-us-east-2.tuist.dev",    lat:  39.04, lon:  -77.49 }, // Ashburn
+  { host: "cache-us-east-3.tuist.dev",    lat:  39.04, lon:  -77.49 }, // Ashburn
   { host: "cache-us-west.tuist.dev",      lat:  45.59, lon: -122.60 }, // Oregon
   { host: "cache-ap-southeast.tuist.dev", lat:   1.35, lon:  103.82 }, // Singapore
   { host: "cache-sa-west.tuist.dev",      lat: -33.45, lon:  -70.67 }, // Santiago
+  { host: "cache-au-east.tuist.dev",      lat: -33.87, lon:  151.21 }, // Sydney
 ];

 function toRadians(degrees: number): number {
PATCH

echo "Gold patch applied."
