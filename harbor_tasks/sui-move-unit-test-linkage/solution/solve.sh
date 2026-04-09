#!/bin/bash
set -e

cd /workspace/sui

# Apply the gold patch from PR #26139
patch -p1 <<'PATCH'
diff --git a/external-crates/move/crates/move-unit-test/src/test_runner.rs b/external-crates/move/crates/move-unit-test/src/test_runner.rs
index caa2b9ae595d5..3fbe3b634ce33 100644
--- a/external-crates/move/crates/move-unit-test/src/test_runner.rs
+++ b/external-crates/move/crates/move-unit-test/src/test_runner.rs
@@ -35,7 +35,10 @@ use move_trace_format::{
     format::{MoveTraceBuilder, TRACE_FILE_EXTENSION},
     tracers::function_only::FunctionOnlyTracer,
 };
-use move_vm_runtime::{dev_utils::storage::StoredPackage, shared::gas::GasMeter};
+use move_vm_runtime::{
+    dev_utils::storage::StoredPackage,
+    shared::{gas::GasMeter, linkage_context},
+};
 use move_vm_runtime::{
     dev_utils::{
         in_memory_test_adapter::InMemoryTestAdapter, storage::InMemoryStorage,
@@ -91,8 +94,17 @@ fn setup_test_storage<'a>(
             .or_insert_with(Vec::new);
         entry.push(module.clone());
     }
+
+    let linkage_table = packages.keys().copied().map(|addr| (addr, addr)).collect();
+    let linkage_context = linkage_context::LinkageContext::new(linkage_table).unwrap();
+
     for (addr, modules) in packages {
-        let package = StoredPackage::from_modules_for_testing(addr, modules).unwrap();
+        let package = StoredPackage::from_module_for_testing_with_linkage(
+            addr,
+            linkage_context.clone(),
+            modules,
+        )
+        .unwrap();
         adapter.insert_package_into_storage(package);
     }
     Ok(())
PATCH

# Idempotency check: verify distinctive line exists
if ! grep -q "from_module_for_testing_with_linkage" external-crates/move/crates/move-unit-test/src/test_runner.rs; then
    echo "ERROR: Patch not applied correctly"
    exit 1
fi

echo "Patch applied successfully"
