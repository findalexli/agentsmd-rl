#!/usr/bin/env bash
set -euo pipefail

FILE="test/e2e/app-dir/typed-routes/typed-routes.test.ts"

# Idempotency: check if fix is already applied
if grep -q '}, 30000)' "$FILE" 2>/dev/null; then
  echo "Fix already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/test/e2e/app-dir/typed-routes/typed-routes.test.ts b/test/e2e/app-dir/typed-routes/typed-routes.test.ts
index eda2a140f71a8e..405e8f19260ff8 100644
--- a/test/e2e/app-dir/typed-routes/typed-routes.test.ts
+++ b/test/e2e/app-dir/typed-routes/typed-routes.test.ts
@@ -23,13 +23,21 @@ describe('typed-routes', () => {
   }

   it('should generate route types correctly', async () => {
+    // Route type generation happens after the "Ready" log fires; give it time.
     await retry(async () => {
       const dts = await next.readFile(`${next.distDir}/types/routes.d.ts`)
       expect(dts).toContain(expectedDts)
-    })
+    }, 30000)
   })

   it('should have passing tsc after start', async () => {
+    // Wait for routes.d.ts before stopping the server; route type generation
+    // happens after the "Ready" log fires and tsc may run before it completes.
+    await retry(async () => {
+      const dts = await next.readFile(`${next.distDir}/types/routes.d.ts`)
+      expect(dts).toContain(expectedDts)
+    }, 30000)
+
     await next.stop()
     try {
       const { stdout, stderr } = await execa('pnpm', ['tsc', '--noEmit'], {
@@ -47,6 +55,7 @@ describe('typed-routes', () => {
   })

   it('should correctly convert custom route patterns from path-to-regexp to bracket syntax', async () => {
+    // Route type generation happens after the "Ready" log fires; give it time.
     await retry(async () => {
       const dts = await next.readFile(`${next.distDir}/types/routes.d.ts`)

@@ -59,7 +68,7 @@ describe('typed-routes', () => {
       // Test catch-all zero-or-more: :slug* -> [[...slug]]
       expect(dts).toContain('"/blog/[category]/[[...slug]]"')
       expect(dts).toContain('"/api-legacy/[version]/[[...endpoint]]"')
-    })
+    }, 30000)
   })

   if (isNextDev) {

PATCH

echo "Patch applied successfully."
