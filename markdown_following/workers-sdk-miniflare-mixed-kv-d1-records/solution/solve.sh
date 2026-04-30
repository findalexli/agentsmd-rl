#!/usr/bin/env bash
# Apply the gold patch fixing the kvNamespaces and d1Databases Zod schema unions
# so that records may freely mix string values and object values.
set -euo pipefail

REPO=/workspace/workers-sdk
cd "$REPO"

# Idempotency guard - if already patched, skip
if grep -q "z.union(\[$" packages/miniflare/src/plugins/kv/index.ts \
   && grep -q "z.union(\[$" packages/miniflare/src/plugins/d1/index.ts; then
    # Heuristic: the inner z.union (multi-line) is only present after the fix
    if ! grep -A1 "kvNamespaces: z" packages/miniflare/src/plugins/kv/index.ts | grep -q "\.union"; then
        :
    fi
fi

# Patch KV plugin schema
git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/miniflare/src/plugins/kv/index.ts b/packages/miniflare/src/plugins/kv/index.ts
--- a/packages/miniflare/src/plugins/kv/index.ts
+++ b/packages/miniflare/src/plugins/kv/index.ts
@@ -34,14 +34,16 @@ import {
 export const KVOptionsSchema = z.object({
 	kvNamespaces: z
 		.union([
-			z.record(z.string()),
 			z.record(
-				z.object({
-					id: z.string(),
-					remoteProxyConnectionString: z
-						.custom<RemoteProxyConnectionString>()
-						.optional(),
-				})
+				z.union([
+					z.string(),
+					z.object({
+						id: z.string(),
+						remoteProxyConnectionString: z
+							.custom<RemoteProxyConnectionString>()
+							.optional(),
+					}),
+				])
 			),
 			z.string().array(),
 		])
PATCH

# Patch D1 plugin schema
git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/miniflare/src/plugins/d1/index.ts b/packages/miniflare/src/plugins/d1/index.ts
--- a/packages/miniflare/src/plugins/d1/index.ts
+++ b/packages/miniflare/src/plugins/d1/index.ts
@@ -27,14 +27,16 @@ import {
 export const D1OptionsSchema = z.object({
 	d1Databases: z
 		.union([
-			z.record(z.string()),
 			z.record(
-				z.object({
-					id: z.string(),
-					remoteProxyConnectionString: z
-						.custom<RemoteProxyConnectionString>()
-						.optional(),
-				})
+				z.union([
+					z.string(),
+					z.object({
+						id: z.string(),
+						remoteProxyConnectionString: z
+							.custom<RemoteProxyConnectionString>()
+							.optional(),
+					}),
+				])
 			),
 			z.string().array(),
 		])
PATCH

# Add changesets that record the user-facing patch notes
mkdir -p .changeset
cat > .changeset/fix-mixed-kv-namespaces.md <<'EOF'
---
"miniflare": patch
---

fix: allow mixed `kvNamespaces` records containing both string and object entries

Previously, passing a `kvNamespaces` config that mixed plain string values and object entries (e.g. `{ MY_NS: "ns-name", OTHER_NS: { id: "...", remoteProxyConnectionString: ... } }`) would cause Miniflare to throw an error. Both forms are now accepted and normalised correctly.
EOF

cat > .changeset/fix-mixed-d1-databases.md <<'EOF'
---
"miniflare": patch
---

fix: allow mixed `d1Databases` records containing both string and object entries

Previously, passing a `d1Databases` config that mixed plain string values and object entries (e.g. `{ MY_DB: "db-name", OTHER_DB: { id: "...", remoteProxyConnectionString: ... } }`) would cause Miniflare to throw an error. Both forms are now accepted and normalised correctly.
EOF

# Re-build miniflare so dist/src/index.js reflects the patched schemas
pnpm --filter miniflare run build

echo "[solve.sh] patched and rebuilt miniflare"
