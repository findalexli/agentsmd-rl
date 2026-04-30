#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

if grep -q 'must match the name of the variable it is assigned to' \
        crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs; then
    echo "Patch already applied; rebuilding only."
else
    patch -p1 <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/typed_dict.md b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
index 246bb956bf4cd..8d3e17e26b768 100644
--- a/crates/ty_python_semantic/resources/mdtest/typed_dict.md
+++ b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
@@ -2513,6 +2513,9 @@ from typing_extensions import TypedDict
 # error: [invalid-argument-type] "Invalid argument to parameter `typename` of `TypedDict()`"
 Bad1 = TypedDict(123, {"name": str})

+# error: [invalid-argument-type] "The name of a `TypedDict` (`WrongName`) must match the name of the variable it is assigned to (`BadTypedDict3`)"
+BadTypedDict3 = TypedDict("WrongName", {"name": str})
+
 # error: [invalid-argument-type] "Expected a dict literal for parameter `fields` of `TypedDict()`"
 Bad2 = TypedDict("Bad2", "not a dict")

diff --git a/crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs b/crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs
index 81f0d27152e22..2928633a22b35 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs
@@ -159,7 +159,19 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
         }

         let name = if let Some(literal) = name_type.as_string_literal() {
-            Name::new(literal.value(db))
+            let name = literal.value(db);
+
+            if let Some(assigned_name) = definition.and_then(|definition| definition.name(db))
+                && name != assigned_name
+                && let Some(builder) = self.context.report_lint(&INVALID_ARGUMENT_TYPE, name_arg)
+            {
+                builder.into_diagnostic(format_args!(
+                    "The name of a `TypedDict` (`{name}`) must match \
+                    the name of the variable it is assigned to (`{assigned_name}`)"
+                ));
+            }
+
+            Name::new(name)
         } else {
             if !name_type.is_assignable_to(db, KnownClass::Str.to_instance(db))
                 && let Some(builder) = self.context.report_lint(&INVALID_ARGUMENT_TYPE, name_arg)
PATCH
fi

cargo build --release --bin ty -p ty
