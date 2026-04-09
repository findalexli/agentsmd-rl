#!/bin/bash
set -e

REPO_DIR="/workspace/sui"
cd "$REPO_DIR"

# Apply the gold patch for argument checking in Move VM
cat << 'PATCH' | git apply -
diff --git a/external-crates/move/crates/move-vm-runtime/src/execution/vm.rs b/external-crates/move/crates/move-vm-runtime/src/execution/vm.rs
index 31748a70002f..f701fef740dd 100644
--- a/external-crates/move/crates/move-vm-runtime/src/execution/vm.rs
+++ b/external-crates/move/crates/move-vm-runtime/src/execution/vm.rs
@@ -351,6 +351,28 @@ impl<'extensions> MoveVM<'extensions> {
                     return_type: _,
                 } = self.find_function(original_id, function_name, &type_arguments)?;

+                if args.len() != function.to_ref().parameters.len() {
+                    return Err(partial_vm_error!(
+                        NUMBER_OF_ARGUMENTS_MISMATCH,
+                        "argument length mismatch: expected {} got {}",
+                        function.to_ref().parameters.len(),
+                        args.len(),
+                    )
+                    .finish(Location::Module(function.module_id(&self.interner))));
+                }
+
+                // Internal type error if we get here -- `find_function` should have already
+                // verified the type arguments as part of the type resolution that it performs.
+                if type_arguments.len() != function.to_ref().type_parameters().len() {
+                    return Err(partial_vm_error!(
+                        INTERNAL_TYPE_ERROR,
+                        "type argument length mismatch: expected {} got {}.",
+                        function.to_ref().type_parameters().len(),
+                        type_arguments.len(),
+                    )
+                    .finish(Location::Module(function.module_id(&self.interner))));
+                }
+
                 if !bypass_declared_entry_check && !function.to_ref().is_entry {
                     return Err(partial_vm_error!(EXECUTE_ENTRY_FUNCTION_CALLED_ON_NON_ENTRY_FUNCTION)
                     .finish(Location::Module(function.module_id(&self.interner))));
PATCH

# Verify the patch was applied by checking for the distinctive line
grep -q "argument length mismatch: expected" external-crates/move/crates/move-vm-runtime/src/execution/vm.rs || {
    echo "ERROR: Patch was not applied successfully"
    exit 1
}

echo "Gold patch applied successfully"
