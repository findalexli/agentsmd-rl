#!/usr/bin/env bash
set -euo pipefail

cd /workspace/effect

# Idempotency check: if patched line already present, skip
if grep -q "Respect the proxy invariant" packages/sql-kysely/src/internal/patch.ts; then
    echo "Already patched"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/flat-wombats-smile.md b/.changeset/flat-wombats-smile.md
new file mode 100644
index 00000000000..96bbe7853c2
--- /dev/null
+++ b/.changeset/flat-wombats-smile.md
@@ -0,0 +1,5 @@
+---
+"@effect/sql-kysely": patch
+---
+
+Fix proxy get invariant violation in sql-kysely when hashing cached properties
diff --git a/packages/sql-kysely/src/internal/patch.ts b/packages/sql-kysely/src/internal/patch.ts
index 522c831ec95..fb4b0ddcac3 100644
--- a/packages/sql-kysely/src/internal/patch.ts
+++ b/packages/sql-kysely/src/internal/patch.ts
@@ -41,6 +41,12 @@ function effectifyWith(
   }
   return new Proxy(obj, {
     get(target, prop): any {
+      // Respect the proxy invariant: non-configurable, non-writable
+      // properties must return their actual value.
+      const desc = Object.getOwnPropertyDescriptor(target, prop)
+      if (desc && !desc.configurable && !desc.writable) {
+        return target[prop]
+      }
       const prototype = Object.getPrototypeOf(target)
       if (Effect.EffectTypeId in prototype && prop === "commit") {
         return commit.bind(target)
PATCH

echo "Patch applied"
