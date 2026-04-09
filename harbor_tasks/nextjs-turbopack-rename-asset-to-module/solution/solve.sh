#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nextjs

# Idempotent: skip if already applied
if grep -q 'module: ResolvedVc<Box<dyn Module>>' turbopack/crates/turbopack-core/src/reference/mod.rs 2>/dev/null && \
   ! grep -q 'asset: ResolvedVc<Box<dyn Module>>,' turbopack/crates/turbopack-core/src/reference/mod.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/turbopack/crates/turbopack-core/src/reference/mod.rs b/turbopack/crates/turbopack-core/src/reference/mod.rs
index 4be4f4d86b0f91..b364f97c01d307 100644
--- a/turbopack/crates/turbopack-core/src/reference/mod.rs
+++ b/turbopack/crates/turbopack-core/src/reference/mod.rs
@@ -61,7 +61,7 @@ impl ModuleReferences {
 #[derive(ValueToString)]
 #[value_to_string(self.description)]
 pub struct SingleModuleReference {
-    asset: ResolvedVc<Box<dyn Module>>,
+    module: ResolvedVc<Box<dyn Module>>,
     description: RcStr,
 }

@@ -69,22 +69,19 @@ pub struct SingleModuleReference {
 impl ModuleReference for SingleModuleReference {
     #[turbo_tasks::function]
     fn resolve_reference(&self) -> Vc<ModuleResolveResult> {
-        *ModuleResolveResult::module(self.asset)
+        *ModuleResolveResult::module(self.module)
     }
 }

 #[turbo_tasks::value_impl]
 impl SingleModuleReference {
-    /// Create a new instance that resolves to the given asset.
-    #[turbo_tasks::function]
-    pub fn new(asset: ResolvedVc<Box<dyn Module>>, description: RcStr) -> Vc<Self> {
-        Self::cell(SingleModuleReference { asset, description })
-    }
-
-    /// The [`Vc<Box<dyn Module>>`][Module] that this reference resolves to.
+    /// Create a new instance that resolves to the given module.
     #[turbo_tasks::function]
-    pub fn asset(&self) -> Vc<Box<dyn Module>> {
-        *self.asset
+    pub fn new(module: ResolvedVc<Box<dyn Module>>, description: RcStr) -> Vc<Self> {
+        Self::cell(SingleModuleReference {
+            module,
+            description,
+        })
     }
 }

PATCH

echo "Patch applied successfully."
