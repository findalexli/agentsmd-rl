#!/bin/bash
set -e

cd /workspace/prisma

# Apply the fix to PrismaPgAdapterFactory to accept a string connection URL
cat > /tmp/fix.patch << 'PATCH'
diff --git a/packages/adapter-pg/src/pg.ts b/packages/adapter-pg/src/pg.ts
index 8d01ee593875..481b94415213 100644
--- a/packages/adapter-pg/src/pg.ts
+++ b/packages/adapter-pg/src/pg.ts
@@ -278,12 +278,15 @@ export class PrismaPgAdapterFactory implements SqlMigrationAwareDriverAdapterFac
   private externalPool: pg.Pool | null

   constructor(
-    poolOrConfig: pg.Pool | pg.PoolConfig,
+    poolOrConfig: pg.Pool | pg.PoolConfig | string,
     private readonly options?: PrismaPgOptions,
   ) {
     if (poolOrConfig instanceof pg.Pool) {
       this.externalPool = poolOrConfig
       this.config = poolOrConfig.options
+    } else if (typeof poolOrConfig === 'string') {
+      this.externalPool = null
+      this.config = { connectionString: poolOrConfig }
     } else {
       this.externalPool = null
       this.config = poolOrConfig
PATCH

git apply /tmp/fix.patch

# Rebuild adapter-pg so the compiled dist/ reflects the fix
pnpm --filter @prisma/adapter-pg build

# Verify the distinctive line is present (idempotency check)
grep -q "typeof poolOrConfig === 'string'" packages/adapter-pg/src/pg.ts && echo "Patch applied and rebuilt successfully"