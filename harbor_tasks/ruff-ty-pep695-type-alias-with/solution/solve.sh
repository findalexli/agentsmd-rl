#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'Type::TypeAlias(alias) => alias' crates/ty_python_semantic/src/types.rs 2>/dev/null; then
    # Check it's BEFORE no_instance_fallback (the actual fix position)
    lineno_alias=$(grep -n 'Type::TypeAlias(alias) => alias' crates/ty_python_semantic/src/types.rs | head -1 | cut -d: -f1)
    lineno_fallback=$(grep -n 'no_instance_fallback' crates/ty_python_semantic/src/types.rs | head -1 | cut -d: -f1)
    if [ "$lineno_alias" -lt "$lineno_fallback" ] 2>/dev/null; then
        echo "Patch already applied."
        exit 0
    fi
fi

git apply - <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/with/sync.md b/crates/ty_python_semantic/resources/mdtest/with/sync.md
index da383f065b6c9..3f9ff1b414849 100644
--- a/crates/ty_python_semantic/resources/mdtest/with/sync.md
+++ b/crates/ty_python_semantic/resources/mdtest/with/sync.md
@@ -40,6 +40,46 @@ def _(flag: bool):
         reveal_type(f)  # revealed: str | int
 ```

+## Type aliases preserve context manager behavior
+
+```toml
+[environment]
+python-version = "3.12"
+```
+
+```py
+from typing import Self, TypeAlias
+from typing_extensions import TypeAliasType
+
+class A:
+    def __enter__(self) -> Self:
+        return self
+
+    def __exit__(self, exc_type, exc_value, traceback) -> None: ...
+
+class B:
+    def __enter__(self) -> Self:
+        return self
+
+    def __exit__(self, exc_type, exc_value, traceback) -> None: ...
+
+UnionAB1: TypeAlias = A | B
+type UnionAB2 = A | B
+UnionAB3 = TypeAliasType("UnionAB3", A | B)
+
+def f1(x: UnionAB1) -> None:
+    with x as y:
+        reveal_type(y)  # revealed: A | B
+
+def f2(x: UnionAB2) -> None:
+    with x as y:
+        reveal_type(y)  # revealed: A | B
+
+def f3(x: UnionAB3) -> None:
+    with x as y:
+        reveal_type(y)  # revealed: A | B
+```
+
 ## Context manager without an `__enter__` or `__exit__` method

 ```py
diff --git a/crates/ty_python_semantic/src/types.rs b/crates/ty_python_semantic/src/types.rs
index a9f0771dcb715..a917199b9126d 100644
--- a/crates/ty_python_semantic/src/types.rs
+++ b/crates/ty_python_semantic/src/types.rs
@@ -3284,6 +3284,10 @@ impl<'db> Type<'db> {
                     .member_lookup_with_policy(db, name, policy)
             }

+            Type::TypeAlias(alias) => alias
+                .value_type(db)
+                .member_lookup_with_policy(db, name, policy),
+
             _ if policy.no_instance_fallback() => self.invoke_descriptor_protocol(
                 db,
                 name_str,
@@ -3292,10 +3296,6 @@ impl<'db> Type<'db> {
                 policy,
             ),

-            Type::TypeAlias(alias) => alias
-                .value_type(db)
-                .member_lookup_with_policy(db, name, policy),
-
             Type::LiteralValue(literal)
                 if literal.as_enum().is_some()
                     && matches!(name_str, "name" | "_name_" | "value" | "_value_") =>

PATCH

echo "Patch applied successfully."
