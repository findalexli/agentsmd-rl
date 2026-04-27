#!/usr/bin/env bash
# Gold solution for prisma/prisma#29327.
# Patches packages/client-engine-runtime/src/interpreter/render-query.ts so
# that DateTime placeholder string values are coerced to Date objects.

set -euo pipefail

cd /workspace/prisma

TARGET="packages/client-engine-runtime/src/interpreter/render-query.ts"

# Idempotency guard — distinctive line introduced by the fix.
if grep -q "arg.prisma__value.type === 'DateTime'" "$TARGET"; then
    echo "Patch already applied to $TARGET"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/client-engine-runtime/src/interpreter/render-query.ts b/packages/client-engine-runtime/src/interpreter/render-query.ts
--- a/packages/client-engine-runtime/src/interpreter/render-query.ts
+++ b/packages/client-engine-runtime/src/interpreter/render-query.ts
@@ -48,7 +48,17 @@ export function evaluateArg(arg: unknown, scope: ScopeBindings, generators: Gene
       if (found === undefined) {
         throw new Error(`Missing value for query variable ${arg.prisma__value.name}`)
       }
-      arg = found
+      if (arg.prisma__value.type === 'DateTime' && typeof found === 'string') {
+        // Convert input datetime strings to Date objects. This is done to prevent issues that
+        // arise when query input values end up being directly compared to values retrieved from
+        // the database. One example of this is a query containing a DateTime cursor value being
+        // used against a DATE MySQL column. The pagination logic doesn't have parameter type
+        // information, therefore it ends up comparing the two datetimes as strings and would yield
+        // false even if the two date datetime strings represent the same Date.
+        arg = new Date(found)
+      } else {
+        arg = found
+      }
     } else if (isPrismaValueGenerator(arg)) {
       const { name, args } = arg.prisma__value
       const generator = generators[name]
PATCH

echo "Patch applied to $TARGET"
