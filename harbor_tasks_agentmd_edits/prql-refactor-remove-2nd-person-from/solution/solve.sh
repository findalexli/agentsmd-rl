#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prql

# Idempotent: skip if already applied
if grep -q 'self-equality operator requires a column name' prqlc/prqlc/src/semantic/ast_expand.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index 75033478072f..2002061084db 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -70,6 +70,18 @@ Run all lints with
 task lint
 ```

+## Error Messages
+
+Error messages should avoid 2nd person (you/your). Use softer modal verbs like
+"might" for a friendlier tone:
+
+- ❌ "are you missing `from` statement?" → ✅ "`from` statement might be
+  missing?"
+- ❌ "did you forget to specify the column name?" → ✅ "column name might be
+  missing?"
+- ❌ "you can only use X" → ✅ "X requires Y" (for hard constraints)
+- ❌ "Have you forgotten an argument?" → ✅ "Argument might be missing?"
+
 ## Documentation

 For Claude to view crate documentation:
diff --git a/prqlc/prqlc/src/semantic/ast_expand.rs b/prqlc/prqlc/src/semantic/ast_expand.rs
index 8ddf77d14129..07871b1988fe 100644
--- a/prqlc/prqlc/src/semantic/ast_expand.rs
+++ b/prqlc/prqlc/src/semantic/ast_expand.rs
@@ -142,12 +142,12 @@ fn expand_unary(pr::UnaryExpr { op, expr }: pr::UnaryExpr) -> Result<pl::ExprKin
         EqSelf => {
             let pl::ExprKind::Ident(ident) = expr.kind else {
                 return Err(Error::new_simple(
-                    "you can only use column names with self-equality operator",
+                    "self-equality operator requires a column name",
                 ));
             };
             if !ident.path.is_empty() {
                 return Err(Error::new_simple(
-                    "you cannot use namespace prefix with self-equality operator",
+                    "self-equality operator does not support namespace prefix",
                 ));
             }

diff --git a/prqlc/prqlc/src/semantic/lowering.rs b/prqlc/prqlc/src/semantic/lowering.rs
index 3cfb75891610..06ecf3259f59 100644
--- a/prqlc/prqlc/src/semantic/lowering.rs
+++ b/prqlc/prqlc/src/semantic/lowering.rs
@@ -416,7 +416,7 @@ impl Lowerer {
                     expected: "a pipeline that resolves to a table".to_string(),
                     found: format!("`{}`", write_pl(expr.clone())),
                 })
-                .push_hint("are you missing `from` statement?")
+                .push_hint("`from` statement might be missing?")
                 .with_span(expr.span))
             }
         })
@@ -917,7 +917,7 @@ impl Lowerer {
             pl::ExprKind::Tuple(_) => {
                 return Err(
                     Error::new_simple("table instance cannot be referenced directly")
-                        .push_hint("did you forget to specify the column name?")
+                        .push_hint("column name might be missing?")
                         .with_span(span),
                 );
             }
diff --git a/prqlc/prqlc/src/semantic/resolver/types.rs b/prqlc/prqlc/src/semantic/resolver/types.rs
index f8212f8d0e06..1b1d3ec91a58 100644
--- a/prqlc/prqlc/src/semantic/resolver/types.rs
+++ b/prqlc/prqlc/src/semantic/resolver/types.rs
@@ -218,7 +218,7 @@ where
             .map(|n| format!("to function {n}"))
             .unwrap_or_else(|| "in this function call?".to_string());

-        e = e.push_hint(format!("Have you forgotten an argument {to_what}?"));
+        e = e.push_hint(format!("Argument might be missing {to_what}?"));
     }

     if is_join && found_ty.kind.is_tuple() && !expected.kind.is_tuple() {
diff --git a/prqlc/prqlc/tests/integration/bad_error_messages.rs b/prqlc/prqlc/tests/integration/bad_error_messages.rs
index 28ee62960026..b7ca0398eddd 100644
--- a/prqlc/prqlc/tests/integration/bad_error_messages.rs
+++ b/prqlc/prqlc/tests/integration/bad_error_messages.rs
@@ -32,7 +32,7 @@ fn test_bad_error_messages() {
        │     ──┬──
        │       ╰──── main expected type `relation`, but found type `func transform relation -> relation`
        │
-       │ Help: Have you forgotten an argument to function std.group?
+       │ Help: Argument might be missing to function std.group?
        │
        │ Note: Type `relation` expands to `[{..}]`
     ───╯
@@ -74,7 +74,7 @@ fn test_bad_error_messages() {
     sort -name
     "###).unwrap_err(), @r"
     Error: expected a pipeline that resolves to a table, but found `internal std.sub`
-    ↳ Hint: are you missing `from` statement?
+    ↳ Hint: `from` statement might be missing?
     ");
 }

@@ -165,7 +165,7 @@ fn invalid_lineage_in_transform() {
   )
   "###).unwrap_err(), @r"
     Error: expected a pipeline that resolves to a table, but found `internal std.sub`
-    ↳ Hint: are you missing `from` statement?
+    ↳ Hint: `from` statement might be missing?
     ");
 }

diff --git a/prqlc/prqlc/tests/integration/sql.rs b/prqlc/prqlc/tests/integration/sql.rs
index e003a8b1bcca..4a66f8999d4c 100644
--- a/prqlc/prqlc/tests/integration/sql.rs
+++ b/prqlc/prqlc/tests/integration/sql.rs
@@ -4035,7 +4035,7 @@ fn test_direct_table_references() {
        │               ┬
        │               ╰── table instance cannot be referenced directly
        │
-       │ Help: did you forget to specify the column name?
+       │ Help: column name might be missing?
     ───╯
     "#);

PATCH

echo "Patch applied successfully."
