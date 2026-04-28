#!/bin/bash
set -euo pipefail

cd /workspace/ruff

# Idempotency guard: check if the fast-path code already exists
if grep -q "Fast path: if the target accepts positional calls that the source cannot accept" crates/ty_python_semantic/src/types/signatures.rs; then
    echo "Patch already applied, skipping."
    exit 0
fi

git apply <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/type_properties/is_subtype_of.md b/crates/ty_python_semantic/resources/mdtest/type_properties/is_subtype_of.md
--- a/crates/ty_python_semantic/resources/mdtest/type_properties/is_subtype_of.md
+++ b/crates/ty_python_semantic/resources/mdtest/type_properties/is_subtype_of.md
@@ -2196,6 +2196,51 @@ static_assert(is_subtype_of(RegularCallableTypeOf[overload_ab], RegularCallableT
 static_assert(is_subtype_of(RegularCallableTypeOf[overload_ba], RegularCallableTypeOf[overload_ab]))
 ```

+#### Overloaded callable with many arity-incompatible overloads
+
+When an overloaded source callable has many overloads with different arities, overloads whose
+positional parameter count is less than the target's should be quickly rejected without expensive
+per-parameter type comparisons.
+
+`many_overloads.pyi`:
+
+```pyi
+from typing import overload
+
+@overload
+def many(a: int) -> int: ...
+@overload
+def many(a: int, b: int) -> int: ...
+@overload
+def many(a: int, b: int, c: int) -> int: ...
+@overload
+def many(a: int, b: int, c: int, d: int) -> int: ...
+@overload
+def many(a: int, b: int, c: int, d: int, e: int) -> int: ...
+```
+
+```py
+from ty_extensions import RegularCallableTypeOf, is_subtype_of, static_assert
+from many_overloads import many
+
+def two_args(a: int, b: int) -> int:
+    return 0
+
+def five_args(a: int, b: int, c: int, d: int, e: int) -> int:
+    return 0
+
+def six_args(a: int, b: int, c: int, d: int, e: int, f: int) -> int:
+    return 0
+
+def variadic_args(*args: int) -> int:
+    return 0
+
+static_assert(is_subtype_of(RegularCallableTypeOf[many], RegularCallableTypeOf[two_args]))
+static_assert(is_subtype_of(RegularCallableTypeOf[many], RegularCallableTypeOf[five_args]))
+static_assert(not is_subtype_of(RegularCallableTypeOf[many], RegularCallableTypeOf[six_args]))
+static_assert(not is_subtype_of(RegularCallableTypeOf[many], RegularCallableTypeOf[variadic_args]))
+```
+
 ### Generic callables

 A generic callable can be considered equivalent to an intersection of all of its possible
diff --git a/crates/ty_python_semantic/src/types/signatures.rs b/crates/ty_python_semantic/src/types/signatures.rs
--- a/crates/ty_python_semantic/src/types/signatures.rs
+++ b/crates/ty_python_semantic/src/types/signatures.rs
@@ -1234,6 +1234,36 @@ impl<'c, 'db> TypeRelationChecker<'_, 'c, 'db> {
             }
         }

+        // Fast path: if the target accepts positional calls that the source cannot accept, reject
+        // without checking return types or individual parameter types. The full parameter
+        // comparison below reaches the same result, but only after doing work that is expensive for
+        // large overload sets.
+        if source.parameters.is_standard()
+            && target.parameters.is_standard()
+            && source.parameters.variadic().is_none()
+        {
+            let source_positional = source.parameters.positional().count();
+            let target_positional = target.parameters.positional().count();
+            let target_accepts_extra_positionals =
+                target_positional > source_positional || target.parameters.variadic().is_some();
+
+            if target_accepts_extra_positionals {
+                if target_positional > source_positional
+                    && let Some(ParameterKind::KeywordOnly { name, .. }) = source
+                        .parameters
+                        .iter()
+                        .nth(source_positional)
+                        .map(Parameter::kind)
+                {
+                    self.provide_context(|| ErrorContext::ParameterMustAcceptPositionalArguments {
+                        name: name.clone(),
+                    });
+                }
+
+                return self.never();
+            }
+        }
+
         let mut result = self.always();

         // Avoid returning early after checking the return types in case there is a `ParamSpec` type
@@ -2592,6 +2622,12 @@ impl<'db> Parameters<'db> {
         matches!(self.kind, ParametersKind::Top)
     }

+    /// Returns `true` if the parameters are a standard parameter list (not gradual, top,
+    /// `ParamSpec`, or `Concatenate`).
+    pub(crate) const fn is_standard(&self) -> bool {
+        matches!(self.kind, ParametersKind::Standard)
+    }
+
     /// Returns the bound `ParamSpec` type variable if the parameter list is exactly `P`.
     ///
     /// For either `P` or `Concatenate[<prefix-params>, P]`, use [`as_paramspec_with_prefix`].
PATCH

echo "Patch applied successfully."
