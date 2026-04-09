#!/usr/bin/env bash
set -euo pipefail
cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'get_or_infer_expression' crates/ty_python_semantic/src/types/infer/builder.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/typed_dict.md b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
index 169cd41bd0316..e3ec14919f1de 100644
--- a/crates/ty_python_semantic/resources/mdtest/typed_dict.md
+++ b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
@@ -408,8 +408,7 @@ accepts_person({"name": "Alice", "age": 30})
 house.owner = {"name": "Alice", "age": 30}
 ```
 
-Known issue: speculative `TypedDict` constructor validation currently duplicates diagnostics that
-were already emitted by the initial inference pass:
+TypedDict constructor validation should not duplicate diagnostics emitted by argument inference:
 
 ```py
 from typing import TypedDict
@@ -417,12 +416,54 @@ from typing import TypedDict
 class TD(TypedDict):
     x: int
 
-# TODO: This should only emit a single `unresolved-reference` diagnostic.
-# error: [unresolved-reference] "Name `missing` used when not defined"
 # error: [unresolved-reference] "Name `missing` used when not defined"
 TD(x=missing)
 ```
 
+TypedDict constructor validation should respect string-valued constants used as keys in positional
+dict literals:
+
+```py
+from typing import Final, TypedDict
+
+VALUE_KEY: Final = "value"
+
+class Record(TypedDict):
+    value: str
+
+Record({VALUE_KEY: "x"})
+```
+
+TypedDict constructor validation should combine positional dict literals with keyword arguments:
+
+```py
+from typing import TypedDict
+
+class TD(TypedDict):
+    x: int
+    y: str
+
+# error: [invalid-argument-type] "Invalid argument to key "x" with declared type `int` on TypedDict `TD`: value of type `Literal["foo"]`"
+TD({"x": "foo"}, y="bar")
+```
+
+TypedDict constructor validation should preserve string-valued constant keys in mixed calls:
+
+```py
+from typing import Final, TypedDict
+
+VALUE_KEY: Final = "value"
+
+class Record(TypedDict):
+    value: str
+    count: int
+
+Record({VALUE_KEY: "x"}, count=1)
+
+# error: [invalid-argument-type] "Invalid argument to key "value" with declared type `str` on TypedDict `Record`: value of type `Literal[1]`"
+Record({VALUE_KEY: 1}, count=1)
+```
+
 All of these are missing the required `age` field:
 
 ```py
diff --git a/crates/ty_python_semantic/src/types/infer/builder.rs b/crates/ty_python_semantic/src/types/infer/builder.rs
index 769a21bbfdf11..3d713a129fe4f 100644
--- a/crates/ty_python_semantic/src/types/infer/builder.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder.rs
@@ -563,6 +563,11 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             .or(self.fallback_type())
     }
 
+    fn get_or_infer_expression(&mut self, expr: &ast::Expr, tcx: TypeContext<'db>) -> Type<'db> {
+        self.try_expression_type(expr)
+            .unwrap_or_else(|| self.infer_expression(expr, tcx))
+    }
+
     /// Store qualifiers for an annotation expression.
     fn store_qualifiers(&mut self, expr: &ast::Expr, qualifiers: TypeQualifiers) {
         if !qualifiers.is_empty() {
@@ -6566,6 +6571,65 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         call_arguments
     }
 
+    fn infer_typed_dict_constructor_values<'expr>(
+        &mut self,
+        typed_dict: TypedDictType<'db>,
+        arguments: &'expr ast::Arguments,
+        error_node: AnyNodeRef<'expr>,
+    ) {
+        if arguments.args.len() == 1 && arguments.keywords.is_empty() {
+            let target_ty = Type::TypedDict(typed_dict);
+            let argument = &arguments.args[0];
+            self.get_or_infer_expression(argument, TypeContext::new(Some(target_ty)));
+            if argument.is_dict_expr() {
+                return;
+            }
+        } else if arguments.args.len() == 1
+            && let ast::Expr::Dict(dict_expr) = &arguments.args[0]
+        {
+            self.infer_typed_dict_constructor_dict_literal_values(typed_dict, dict_expr);
+        }
+
+        let items = typed_dict.items(self.db());
+        for keyword in &arguments.keywords {
+            let value_tcx = keyword
+                .arg
+                .as_ref()
+                .and_then(|arg_name| items.get(arg_name.id.as_str()))
+                .map(|field| TypeContext::new(Some(field.declared_ty)))
+                .unwrap_or_default();
+            self.get_or_infer_expression(&keyword.value, value_tcx);
+        }
+
+        validate_typed_dict_constructor(
+            &self.context,
+            typed_dict,
+            arguments,
+            error_node,
+            |expr, _| self.expression_type(expr),
+        );
+    }
+
+    fn infer_typed_dict_constructor_dict_literal_values(
+        &mut self,
+        typed_dict: TypedDictType<'db>,
+        dict_expr: &ast::ExprDict,
+    ) {
+        let items = typed_dict.items(self.db());
+
+        for item in &dict_expr.items {
+            let value_tcx = item
+                .key
+                .as_ref()
+                .map(|key| self.get_or_infer_expression(key, TypeContext::default()))
+                .and_then(Type::as_string_literal)
+                .and_then(|key| items.get(key.value(self.db())))
+                .map(|field| TypeContext::new(Some(field.declared_ty)))
+                .unwrap_or_default();
+            self.get_or_infer_expression(&item.value, value_tcx);
+        }
+    }
+
     fn infer_call_expression(
         &mut self,
         call_expression: &ast::ExprCall,
@@ -6876,32 +6940,37 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             &bindings,
         );
 
+        let is_typed_dict_constructor = class.is_some_and(|class| class.is_typed_dict(self.db()));
+        let has_mixed_typed_dict_literal_argument = is_typed_dict_constructor
+            && arguments.args.len() == 1
+            && arguments.args[0].is_dict_expr()
+            && !arguments.keywords.is_empty();
+
+        // Validate `TypedDict` constructor calls before general argument inference so the field
+        // type context becomes the canonical inference for constructor values.
+        if let Some(class) = class
+            && is_typed_dict_constructor
+        {
+            let typed_dict = TypedDictType::new(class);
+            self.infer_typed_dict_constructor_values(typed_dict, arguments, func.as_ref().into());
+        }
+
         let bindings_result = self.infer_and_check_argument_types(
             ArgumentsIter::from_ast(arguments),
             &mut call_arguments,
-            &mut |builder, (_, expr, tcx)| builder.infer_expression(expr, tcx),
+            &mut |builder, (_, expr, tcx)| {
+                if has_mixed_typed_dict_literal_argument && expr.is_dict_expr() {
+                    builder.try_expression_type(expr).unwrap_or(Type::unknown())
+                } else if is_typed_dict_constructor {
+                    builder.get_or_infer_expression(expr, tcx)
+                } else {
+                    builder.infer_expression(expr, tcx)
+                }
+            },
             &mut bindings,
             call_expression_tcx,
         );
 
-        // Validate `TypedDict` constructor calls after argument type inference.
-        if let Some(class) = class
-            && class.is_typed_dict(self.db())
-        {
-            let mut speculative = self.speculate();
-            validate_typed_dict_constructor(
-                &self.context,
-                TypedDictType::new(class),
-                arguments,
-                func.as_ref().into(),
-                |expr, tcx| speculative.infer_expression(expr, tcx),
-            );
-            // TODO: Merging speculative inference preserves TypedDict-specific diagnostics, but it
-            // can also duplicate diagnostics that were already emitted during the initial
-            // type-context-free argument inference.
-            self.extend(speculative);
-        }
-
         let mut bindings = match bindings_result {
             Ok(()) => bindings,
             Err(_) => {
diff --git a/crates/ty_python_semantic/src/types/typed_dict.rs b/crates/ty_python_semantic/src/types/typed_dict.rs
index 0d0dcefc6fa94..1a83e54977825 100644
--- a/crates/ty_python_semantic/src/types/typed_dict.rs
+++ b/crates/ty_python_semantic/src/types/typed_dict.rs
@@ -934,13 +934,24 @@ pub(super) fn validate_typed_dict_constructor<'db, 'ast>(
         arguments.args.len() == 1 && arguments.keywords.is_empty() && !has_positional_dict_literal;
 
     if has_positional_dict_literal {
-        let provided_keys = validate_from_dict_literal(
+        let mut provided_keys = validate_from_dict_literal(
             context,
             typed_dict,
             arguments,
             error_node,
             &mut expression_type_fn,
         );
+
+        for key in validate_from_keywords(
+            context,
+            typed_dict,
+            arguments,
+            error_node,
+            &mut expression_type_fn,
+        ) {
+            provided_keys.insert(key);
+        }
+
         validate_typed_dict_required_keys(context, typed_dict, &provided_keys, error_node);
     } else if is_single_positional_arg {
         // Single positional argument: check if assignable to the target TypedDict.
@@ -988,11 +999,10 @@ fn validate_from_dict_literal<'db, 'ast>(
         // Validate dict entries
         for dict_item in &dict_expr.items {
             if let Some(ref key_expr) = dict_item.key
-                && let ast::Expr::StringLiteral(ast::ExprStringLiteral {
-                    value: key_value, ..
-                }) = key_expr
+                && let Some(key_value) =
+                    expression_type_fn(key_expr, TypeContext::default()).as_string_literal()
             {
-                let key = key_value.to_str();
+                let key = key_value.value(context.db());
                 provided_keys.insert(Name::new(key));
 
                 let value_tcx = items

PATCH

# Rebuild ty with the fix applied (incremental — only changed files recompile).
cargo build --bin ty

echo "Patch applied successfully."
