#!/usr/bin/env bash
# Gold patch: applies the fix to generics.rs that resolves the invariant
# matching of formal-union vs inferable-typevar in SpecializationBuilder.
set -euo pipefail

cd /workspace/ruff

# Idempotency: a distinctive phrase from the patch's added comment block.
if grep -q "probing individual union elements below can leave spurious" \
        crates/ty_python_semantic/src/types/generics.rs; then
    echo "solve.sh: gold patch already applied, skipping"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/crates/ty_python_semantic/src/types/generics.rs b/crates/ty_python_semantic/src/types/generics.rs
index c9c42f08f084d1..e3d45861a833e1 100644
--- a/crates/ty_python_semantic/src/types/generics.rs
+++ b/crates/ty_python_semantic/src/types/generics.rs
@@ -1992,6 +1992,20 @@ impl<'db, 'c> SpecializationBuilder<'db, 'c> {
                 self.add_type_mapping(*formal_bound_typevar, remaining_actual, polarity, f);
             }
             (Type::Union(union_formal), _) => {
+                // If the formal is a union and the actual is a bare inferable TypeVar in an
+                // invariant position, record the whole union as the mapping. Invariant matching is
+                // equality-like; probing individual union elements below can leave spurious
+                // partial mappings from non-matching elements. For example, while comparing
+                // `ClassSelector[T]` with `ClassSelector[CT | None]`, descending into `None`
+                // would map `T` to `None` before `CT` is solved from another argument.
+                if let Type::TypeVar(actual_typevar) = actual
+                    && actual_typevar.is_inferable(self.db, self.inferable)
+                    && matches!(polarity, TypeVarVariance::Invariant)
+                {
+                    self.add_type_mapping(actual_typevar, formal, polarity, f);
+                    return Ok(());
+                }
+
                 // Second, if the formal is a union, and the actual type is assignable to precisely
                 // one union element, then we don't add any type mapping. This handles a case like
                 //
PATCH

echo "solve.sh: gold patch applied"
