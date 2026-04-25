#!/bin/bash
set -e

# Clone fresh (not from volume) - sparse checkout for speed
# Remove existing directory if present (from base image)
rm -rf /workspace/backstage
git clone --filter=blob:none --depth=50 \
    --branch=master \
    https://github.com/backstage/backstage.git \
    /workspace/backstage

cd /workspace/backstage

# Checkout the base commit (parent of merge)
git checkout 5b1ba4ee3ece1f6a33b2b4c6c8ad77cdc2b52a83

# Apply the fix patch
cat << 'PATCH' > /tmp/fix.patch
diff --git a/packages/cli-module-build/src/lib/runner/startEmbeddedDb.ts b/packages/cli-module-build/src/lib/runner/startEmbeddedDb.ts
index c94a5a7f..334f7687 100644
--- a/packages/cli-module-build/src/lib/runner/startEmbeddedDb.ts
+++ b/packages/cli-module-build/src/lib/runner/startEmbeddedDb.ts
@@ -78,8 +78,6 @@ export async function startEmbeddedDb() {
   const port = await getPortPromise();
   const tmpDir = await fs.mkdtemp(resolvePath(os.tmpdir(), TEMP_DIR_PREFIX));

-  await fs.writeFile(resolvePath(tmpDir, PID_FILE), String(process.pid));
-
   const pg = new EmbeddedPostgres({
     databaseDir: tmpDir,
     user,
@@ -94,6 +92,7 @@ export async function startEmbeddedDb() {

   try {
     await pg.initialise();
+    await fs.writeFile(resolvePath(tmpDir, PID_FILE), String(process.pid));
     await pg.start();
   } catch (error) {
     await pg.stop().catch(() => {});
PATCH

git apply /tmp/fix.patch

# Idempotency check - find the distinctive line
grep -q "await pg.initialise();" packages/cli-module-build/src/lib/runner/startEmbeddedDb.ts && echo "IDEMPOTENCY_CHECK_PASSED"