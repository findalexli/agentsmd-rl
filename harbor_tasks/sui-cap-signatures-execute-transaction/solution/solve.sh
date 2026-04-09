#!/bin/bash
set -e

cd /workspace/sui

# Check if fix is already applied
if grep -q "MAX_NUMBER_OF_SIGNATURES" crates/sui-rpc-api/src/grpc/v2/transaction_execution_service/mod.rs; then
    echo "Fix already applied, skipping"
    exit 0
fi

# Apply the fix
cat > /tmp/patch.txt << 'PATCH'
--- a/crates/sui-rpc-api/src/grpc/v2/transaction_execution_service/mod.rs
+++ b/crates/sui-rpc-api/src/grpc/v2/transaction_execution_service/mod.rs
@@ -52,6 +52,9 @@ impl TransactionExecutionService for RpcService {
 }

 pub const EXECUTE_TRANSACTION_READ_MASK_DEFAULT: &str = "effects";
+// Current maximum number of supported UserSignature's,
+// one for the sender and one for an optional sponsor
+const MAX_NUMBER_OF_SIGNATURES: usize = 2;

 #[tracing::instrument(skip(service, executor))]
 pub async fn execute_transaction(
@@ -70,6 +73,17 @@ pub async fn execute_transaction(
                 .with_reason(ErrorReason::FieldInvalid)
         })?;

+    if request.signatures.len() > MAX_NUMBER_OF_SIGNATURES {
+        return Err(FieldViolation::new("signatures")
+            .with_description(format!(
+                "{} provided signatures exceeds the maximum allowed of {}",
+                request.signatures.len(),
+                MAX_NUMBER_OF_SIGNATURES
+            ))
+            .with_reason(ErrorReason::FieldInvalid)
+            .into());
+    }
+
     let signatures = request
         .signatures
         .iter()
PATCH

git apply /tmp/patch.txt

echo "Fix applied successfully"
