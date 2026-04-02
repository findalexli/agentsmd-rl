#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff 2>/dev/null || cd /repo

# Idempotency: check if the fix is already applied
if grep -q 'Type::Dynamic(DynamicType::Divergent(_)) => self' crates/ty_python_semantic/src/types.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_python_semantic/src/types.rs b/crates/ty_python_semantic/src/types.rs
index 7c4b4df370459..32db314e75cf9 100644
--- a/crates/ty_python_semantic/src/types.rs
+++ b/crates/ty_python_semantic/src/types.rs
@@ -5586,9 +5586,17 @@ impl<'db> Type<'db> {
                 TypeMapping::ReplaceParameterDefaults |
                 TypeMapping::EagerExpansion |
                 TypeMapping::RescopeReturnCallables(_) => self,
-                TypeMapping::Materialize(materialization_kind) => match materialization_kind {
-                    MaterializationKind::Top => Type::object(),
-                    MaterializationKind::Bottom => Type::Never,
+                TypeMapping::Materialize(materialization_kind) => match self {
+                    // `Divergent` is an internal cycle marker rather than a gradual type like
+                    // `Any` or `Unknown`. Materializing it away would destroy the marker we rely
+                    // on for recursive alias convergence.
+                    // TODO: We elsewhere treat `Divergent` as a dynamic type, so failing to
+                    // materialize it away here could lead to odd behavior.
+                    Type::Dynamic(DynamicType::Divergent(_)) => self,
+                    _ => match materialization_kind {
+                        MaterializationKind::Top => Type::object(),
+                        MaterializationKind::Bottom => Type::Never,
+                    },
                 }
             }

PATCH

echo "Patch applied successfully."
