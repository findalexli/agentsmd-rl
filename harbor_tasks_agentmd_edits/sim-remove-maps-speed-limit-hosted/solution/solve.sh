#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sim

# Idempotent: skip if already applied
if grep -q "value: 'speed_limits', not: true" apps/sim/blocks/blocks/google_maps.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.cursor/skills/add-hosted-key/SKILL.md b/.cursor/skills/add-hosted-key/SKILL.md
index 2a5888c5f11..a6e0f07052d 100644
--- a/.cursor/skills/add-hosted-key/SKILL.md
+++ b/.cursor/skills/add-hosted-key/SKILL.md
@@ -194,6 +194,45 @@ In the block config (`blocks/blocks/{service}.ts`), add `hideWhenHosted: true` t

 The visibility is controlled by `isSubBlockHiddenByHostedKey()` in `lib/workflows/subblocks/visibility.ts`, which checks the `isHosted` feature flag.

+### Excluding Specific Operations from Hosted Key Support
+
+When a block has multiple operations but some operations should **not** use a hosted key (e.g., the underlying API is deprecated, unsupported, or too expensive), use the **duplicate apiKey subblock** pattern. This is the same pattern Exa uses for its `research` operation:
+
+1. **Remove the `hosting` config** from the tool definition for that operation — it must not have a `hosting` object at all.
+2. **Duplicate the `apiKey` subblock** in the block config with opposing conditions:
+
+```typescript
+// API Key — hidden when hosted for operations with hosted key support
+{
+  id: 'apiKey',
+  title: 'API Key',
+  type: 'short-input',
+  placeholder: 'Enter your API key',
+  password: true,
+  required: true,
+  hideWhenHosted: true,
+  condition: { field: 'operation', value: 'unsupported_op', not: true },
+},
+// API Key — always visible for unsupported_op (no hosted key support)
+{
+  id: 'apiKey',
+  title: 'API Key',
+  type: 'short-input',
+  placeholder: 'Enter your API key',
+  password: true,
+  required: true,
+  condition: { field: 'operation', value: 'unsupported_op' },
+},
+```
+
+Both subblocks share the same `id: 'apiKey'`, so the same value flows to the tool. The conditions ensure only one is visible at a time. The first has `hideWhenHosted: true` and shows for all hosted operations; the second has no `hideWhenHosted` and shows only for the excluded operation — meaning users must always provide their own key for that operation.
+
+To exclude multiple operations, use an array: `{ field: 'operation', value: ['op_a', 'op_b'] }`.
+
+**Reference implementations:**
+- **Exa** (`blocks/blocks/exa.ts`): `research` operation excluded from hosting — lines 309-329
+- **Google Maps** (`blocks/blocks/google_maps.ts`): `speed_limits` operation excluded from hosting (deprecated Roads API)
+
 ## Step 5: Add to the BYOK Settings UI

  Add an entry to the `PROVIDERS` array in the BYOK settings component so users can bring their own key. You need the service icon from `components/icons.tsx`:
diff --git a/apps/sim/blocks/blocks/google_maps.ts b/apps/sim/blocks/blocks/google_maps.ts
index 53a0fcf25ae..5a582250e86 100644
--- a/apps/sim/blocks/blocks/google_maps.ts
+++ b/apps/sim/blocks/blocks/google_maps.ts
@@ -36,7 +36,7 @@ export const GoogleMapsBlock: BlockConfig = {
       value: () => 'geocode',
     },

-    // API Key
+    // API Key — hidden when hosted for operations with hosted key support
     {
       id: 'apiKey',
       title: 'API Key',
@@ -45,6 +45,17 @@ export const GoogleMapsBlock: BlockConfig = {
       placeholder: 'Enter your Google Maps API key',
       required: true,
       hideWhenHosted: true,
+      condition: { field: 'operation', value: 'speed_limits', not: true },
+    },
+    // API Key — always visible for Speed Limits (deprecated API, no hosted key support)
+    {
+      id: 'apiKey',
+      title: 'API Key',
+      type: 'short-input',
+      password: true,
+      placeholder: 'Enter your Google Maps API key',
+      required: true,
+      condition: { field: 'operation', value: 'speed_limits' },
     },

     // ========== Geocode ==========
diff --git a/apps/sim/tools/google_maps/speed_limits.ts b/apps/sim/tools/google_maps/speed_limits.ts
index 581baf50538..b0fdc2e49f4 100644
--- a/apps/sim/tools/google_maps/speed_limits.ts
+++ b/apps/sim/tools/google_maps/speed_limits.ts
@@ -34,20 +34,6 @@ export const googleMapsSpeedLimitsTool: ToolConfig<
     },
   },

-  hosting: {
-    envKeyPrefix: 'GOOGLE_CLOUD_API_KEY',
-    apiKeyParam: 'apiKey',
-    byokProviderId: 'google_cloud',
-    pricing: {
-      type: 'per_request',
-      cost: 0.02,
-    },
-    rateLimit: {
-      mode: 'per_request',
-      requestsPerMinute: 60,
-    },
-  },
-
   request: {
     url: (params) => {
       const hasPath = params.path && params.path.trim().length > 0

PATCH

echo "Patch applied successfully."
