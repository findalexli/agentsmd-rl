#!/bin/bash
set -euo pipefail

cd /workspace/effect

if grep -q 'if (self === null || that === null) {' packages/effect/src/Equal.ts; then
    echo "patch already applied"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/fix-equal-null-guard.md b/.changeset/fix-equal-null-guard.md
new file mode 100644
index 00000000000..7876fb12e5d
--- /dev/null
+++ b/.changeset/fix-equal-null-guard.md
@@ -0,0 +1,5 @@
+---
+"effect": patch
+---
+
+Fix `Equal.equals` crash when comparing `null` values inside `structuralRegion`. Added null guard before `Object.getPrototypeOf` calls to prevent `TypeError: Cannot convert undefined or null to object`.
diff --git a/packages/effect/src/Equal.ts b/packages/effect/src/Equal.ts
index 5e2738d95f9..e6ca6d8ba23 100644
--- a/packages/effect/src/Equal.ts
+++ b/packages/effect/src/Equal.ts
@@ -60,6 +60,9 @@ function compareBoth(self: unknown, that: unknown): boolean {
       }
     }
     if (structuralRegionState.enabled) {
+      if (self === null || that === null) {
+        return false
+      }
       if (Array.isArray(self) && Array.isArray(that)) {
         return self.length === that.length && self.every((v, i) => compareBoth(v, that[i]))
       }
PATCH

echo "patch applied"
