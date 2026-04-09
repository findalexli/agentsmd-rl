#!/usr/bin/env bash
set -euo pipefail
cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'is_outer_block_in_type_checking || clause_in_type_checking' crates/ty_python_semantic/src/semantic_index/builder.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/overloads.md b/crates/ty_python_semantic/resources/mdtest/overloads.md
index c38d640f01b730..a64f12940e478f 100644
--- a/crates/ty_python_semantic/resources/mdtest/overloads.md
+++ b/crates/ty_python_semantic/resources/mdtest/overloads.md
@@ -497,6 +497,17 @@ if TYPE_CHECKING:
     @overload
     def b(x: int) -> int: ...

+if TYPE_CHECKING:
+    import sys
+
+    if sys.platform == "win32":
+        pass
+    else:
+        @overload
+        def d() -> bytes: ...
+        @overload
+        def d(x: int) -> int: ...
+
 if TYPE_CHECKING:
     @overload
     # not all overloads are in a `TYPE_CHECKING` block, so this is an error
diff --git a/crates/ty_python_semantic/src/semantic_index/builder.rs b/crates/ty_python_semantic/src/semantic_index/builder.rs
index daaaece1f0207f..ec11cf3ab045e6 100644
--- a/crates/ty_python_semantic/src/semantic_index/builder.rs
+++ b/crates/ty_python_semantic/src/semantic_index/builder.rs
@@ -2392,7 +2392,9 @@ impl<'ast> Visitor<'ast> for SemanticIndexBuilder<'_, 'ast> {
                         is_in_not_type_checking_chain
                     };

-                    self.in_type_checking_block = clause_in_type_checking;
+                    // Nested conditional clauses inherit an enclosing TYPE_CHECKING context.
+                    self.in_type_checking_block =
+                        is_outer_block_in_type_checking || clause_in_type_checking;

                     self.visit_body(clause_body);
                 }

PATCH

# Rebuild ty with the fix applied (incremental — only changed files recompile).
cargo build --bin ty

echo "Patch applied successfully."
