#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotency check: if tcx is already passed to infer_await_expression call, skip
if grep -q 'infer_await_expression(await_expression, tcx)' \
    crates/ty_python_semantic/src/types/infer/builder.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/bidirectional.md b/crates/ty_python_semantic/resources/mdtest/bidirectional.md
index db8fe891d7305..c6d255ba0a096 100644
--- a/crates/ty_python_semantic/resources/mdtest/bidirectional.md
+++ b/crates/ty_python_semantic/resources/mdtest/bidirectional.md
@@ -542,6 +542,27 @@ def _(x: Intersection[X, Y]):
     x |= reveal_type({"bar": [1, None]})  # revealed: dict[str, list[int | None]]
 ```

+## `await` expressions
+
+Type context is also propagated through `await` expressions:
+
+```py
+from typing import Literal
+
+async def make_lst[T](x: T) -> list[T]:
+    return [x]
+
+async def _():
+    x1 = await make_lst(1)
+    reveal_type(x1)  # revealed: list[int]
+
+    x2: list[Literal[1]] = await make_lst(1)
+    reveal_type(x2)  # revealed: list[Literal[1]]
+
+    x3: list[int | None] = await make_lst(1)
+    reveal_type(x3)  # revealed: list[int | None]
+```
+
 ## Multi-inference diagnostics

 Diagnostics unrelated to the type-context are only reported once:
diff --git a/crates/ty_python_semantic/src/types/infer/builder.rs b/crates/ty_python_semantic/src/types/infer/builder.rs
index 52ba391e4ca07..f01689d32cc20 100644
--- a/crates/ty_python_semantic/src/types/infer/builder.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder.rs
@@ -5528,7 +5528,9 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             ast::Expr::Starred(starred) => self.infer_starred_expression(starred, tcx),
             ast::Expr::Yield(yield_expression) => self.infer_yield_expression(yield_expression),
             ast::Expr::YieldFrom(yield_from) => self.infer_yield_from_expression(yield_from),
-            ast::Expr::Await(await_expression) => self.infer_await_expression(await_expression),
+            ast::Expr::Await(await_expression) => {
+                self.infer_await_expression(await_expression, tcx)
+            }
             ast::Expr::Named(named) => self.infer_named_expression(named),
             ast::Expr::IpyEscapeCommand(_) => {
                 todo_type!("Ipy escape command support")
@@ -7626,13 +7628,22 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             .unwrap_or_else(Type::unknown)
     }

-    fn infer_await_expression(&mut self, await_expression: &ast::ExprAwait) -> Type<'db> {
+    fn infer_await_expression(
+        &mut self,
+        await_expression: &ast::ExprAwait,
+        tcx: TypeContext<'db>,
+    ) -> Type<'db> {
         let ast::ExprAwait {
             range: _,
             node_index: _,
             value,
         } = await_expression;
-        let expr_type = self.infer_expression(value, TypeContext::default());
+
+        let expr_type = self.infer_expression(
+            value,
+            tcx.map(|tcx| KnownClass::Awaitable.to_specialized_instance(self.db(), &[tcx])),
+        );
+
         expr_type.try_await(self.db()).unwrap_or_else(|err| {
             err.report_diagnostic(&self.context, expr_type, value.as_ref().into());
             Type::unknown()
diff --git a/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs b/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs
index 24253a943fa3c..af5dbca09ab44 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs
@@ -550,7 +550,7 @@ impl<'db> TypeInferenceBuilder<'db, '_> {

             ast::Expr::Await(await_expression) => {
                 if !self.deferred_state.in_string_annotation() {
-                    self.infer_await_expression(await_expression);
+                    self.infer_await_expression(await_expression, TypeContext::default());
                 }
                 self.report_invalid_type_expression(
                     expression,

PATCH

echo "Patch applied successfully."
