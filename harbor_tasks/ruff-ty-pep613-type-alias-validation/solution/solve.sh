#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'pep_613_alias' crates/ty_python_semantic/src/types/infer/builder/post_inference/mod.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/annotations/literal.md b/crates/ty_python_semantic/resources/mdtest/annotations/literal.md
index 1e36725340df0..bd74a89438220 100644
--- a/crates/ty_python_semantic/resources/mdtest/annotations/literal.md
+++ b/crates/ty_python_semantic/resources/mdtest/annotations/literal.md
@@ -48,6 +48,10 @@ invalid1: Literal[3 + 4]
 invalid2: Literal[4 + 3j]
 # error: [invalid-type-form]
 invalid3: Literal[(3, 4)]
+# error: [invalid-type-form]
+invalid4: Literal[-3.14]
+# error: [invalid-type-form]
+invalid5: Literal[-3j]

 hello = "hello"
 invalid4: Literal[
diff --git a/crates/ty_python_semantic/resources/mdtest/pep613_type_aliases.md b/crates/ty_python_semantic/resources/mdtest/pep613_type_aliases.md
index bfa1966a2bb77..d2ef7fb1bb2bf 100644
--- a/crates/ty_python_semantic/resources/mdtest/pep613_type_aliases.md
+++ b/crates/ty_python_semantic/resources/mdtest/pep613_type_aliases.md
@@ -440,8 +440,7 @@ Empty: TypeAlias

 ## Simple syntactic validation

-We don't yet do full validation for the right-hand side of a `TypeAlias` assignment, but we do
-simple syntactic validation:
+We do full validation of the right-hand side of a type alias.

 ```toml
 [environment]
@@ -454,6 +453,9 @@ from typing_extensions import Annotated, Literal, TypeAlias
 GoodTypeAlias: TypeAlias = Annotated[int, (1, 3.14, lambda x: x)]
 GoodTypeAlias: TypeAlias = tuple[int, *tuple[str, ...]]

+var1 = 3
+
+# typing conformance cases:
 BadTypeAlias1: TypeAlias = eval("".join(map(chr, [105, 110, 116])))  # error: [invalid-type-form]
 BadTypeAlias2: TypeAlias = [int, str]  # error: [invalid-type-form]
 BadTypeAlias3: TypeAlias = ((int, str),)  # error: [invalid-type-form]
@@ -462,15 +464,24 @@ BadTypeAlias5: TypeAlias = {"a": "b"}  # error: [invalid-type-form]
 BadTypeAlias6: TypeAlias = (lambda: int)()  # error: [invalid-type-form]
 BadTypeAlias7: TypeAlias = [int][0]  # error: [invalid-type-form]
 BadTypeAlias8: TypeAlias = int if 1 < 3 else str  # error: [invalid-type-form]
+BadTypeAlias9: TypeAlias = var1  # error: [invalid-type-form]
 BadTypeAlias10: TypeAlias = True  # error: [invalid-type-form]
 BadTypeAlias11: TypeAlias = 1  # error: [invalid-type-form]
 BadTypeAlias12: TypeAlias = list or set  # error: [invalid-type-form]
 BadTypeAlias13: TypeAlias = f"{'int'}"  # error: [invalid-type-form]
-BadTypeAlias14: TypeAlias = Literal[-3.14]  # error: [invalid-type-form]

+# bonus ones from Alex:
+#
+# TODO should be just one error for both of these (we currently validate type-form subscripts
+# twice, once when inferring as a value expression and again when inferring as a
+# type expression in post-inference)
+#
+# error:[invalid-type-form]
+# error:[invalid-type-form]
+BadTypeAlias14: TypeAlias = Literal[3.14]
 # error: [invalid-type-form]
 # error: [invalid-type-form]
-BadTypeAlias14: TypeAlias = Literal[3.14]
+BadTypeAlias15: TypeAlias = Literal[-3.14]
 ```

 ## No type qualifiers
diff --git a/crates/ty_python_semantic/src/types/infer/builder.rs b/crates/ty_python_semantic/src/types/infer/builder.rs
index 0250f53377d1b..3ca82e1def142 100644
--- a/crates/ty_python_semantic/src/types/infer/builder.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder.rs
@@ -7,7 +7,7 @@ use ruff_db::diagnostic::{Annotation, DiagnosticId, Severity};
 use ruff_db::files::File;
 use ruff_db::parsed::ParsedModuleRef;
 use ruff_db::source::source_text;
-use ruff_python_ast::helpers::{is_dotted_name, map_subscript};
+use ruff_python_ast::helpers::is_dotted_name;
 use ruff_python_ast::name::Name;
 use ruff_python_ast::{
     self as ast, AnyNodeRef, ArgOrKeyword, ArgumentsSourceOrder, ExprContext, HasNodeIndex,
@@ -676,19 +676,19 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             let mut seen_overloaded_places = FxHashSet::default();
             let mut seen_public_functions = FxHashSet::default();

-            for (definition, ty_and_quals) in &self.declarations {
+            for (&definition, ty_and_quals) in &self.declarations {
                 let ty = ty_and_quals.inner_type();
                 match definition.kind(self.db()) {
                     DefinitionKind::Function(function) => {
                         post_inference::function::check_function_definition(
                             &self.context,
-                            *definition,
+                            definition,
                             &|expr| self.file_expression_type(expr),
                         );
                         post_inference::overloaded_function::check_overloaded_function(
                             &self.context,
                             ty,
-                            *definition,
+                            definition,
                             self.scope.scope(self.db()).node(),
                             self.index,
                             &mut seen_overloaded_places,
@@ -710,6 +710,15 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                             &|expr| self.file_expression_type(expr),
                         );
                     }
+                    DefinitionKind::AnnotatedAssignment(assignment) => {
+                        if let Some(diagnostics) =
+                            post_inference::pep_613_alias::check_pep_613_alias(
+                                assignment, definition, self,
+                            )
+                        {
+                            self.context.extend(&diagnostics);
+                        }
+                    }
                     _ => {}
                 }
             }
@@ -4002,85 +4011,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         assignment: &'db AnnotatedAssignmentDefinitionKind,
         definition: Definition<'db>,
     ) {
-        /// Simple syntactic validation for the right-hand sides of PEP-613 type aliases.
-        ///
-        /// TODO: this is far from exhaustive and should be improved.
-        const fn alias_syntax_validation(expr: &ast::Expr) -> bool {
-            const fn inner(expr: &ast::Expr, allow_context_dependent: bool) -> bool {
-                match expr {
-                    ast::Expr::Name(_)
-                    | ast::Expr::StringLiteral(_)
-                    | ast::Expr::NoneLiteral(_) => true,
-                    ast::Expr::Attribute(ast::ExprAttribute {
-                        value,
-                        attr: _,
-                        node_index: _,
-                        range: _,
-                        ctx: _,
-                    }) => inner(value, allow_context_dependent),
-                    ast::Expr::Subscript(ast::ExprSubscript {
-                        value,
-                        slice,
-                        node_index: _,
-                        range: _,
-                        ctx: _,
-                    }) => {
-                        if !inner(value, allow_context_dependent) {
-                            return false;
-                        }
-                        match &**slice {
-                            ast::Expr::Tuple(ast::ExprTuple { elts, .. }) => {
-                                match elts.as_slice() {
-                                    [first, ..] => inner(first, true),
-                                    _ => true,
-                                }
-                            }
-                            _ => inner(slice, true),
-                        }
-                    }
-                    ast::Expr::BinOp(ast::ExprBinOp {
-                        left,
-                        op,
-                        right,
-                        range: _,
-                        node_index: _,
-                    }) => {
-                        op.is_bit_or()
-                            && inner(left, allow_context_dependent)
-                            && inner(right, allow_context_dependent)
-                    }
-                    ast::Expr::UnaryOp(ast::ExprUnaryOp {
-                        op,
-                        operand,
-                        range: _,
-                        node_index: _,
-                    }) => {
-                        allow_context_dependent
-                            && matches!(op, ast::UnaryOp::UAdd | ast::UnaryOp::USub)
-                            && matches!(
-                                &**operand,
-                                ast::Expr::NumberLiteral(ast::ExprNumberLiteral {
-                                    value: ast::Number::Int(_),
-                                    ..
-                                })
-                            )
-                    }
-                    ast::Expr::NumberLiteral(ast::ExprNumberLiteral {
-                        value,
-                        node_index: _,
-                        range: _,
-                    }) => allow_context_dependent && value.is_int(),
-                    ast::Expr::EllipsisLiteral(_)
-                    | ast::Expr::BytesLiteral(_)
-                    | ast::Expr::BooleanLiteral(_)
-                    | ast::Expr::Starred(_)
-                    | ast::Expr::List(_) => allow_context_dependent,
-                    _ => false,
-                }
-            }
-            inner(expr, false)
-        }
-
         let annotation = assignment.annotation(self.module());
         let target = assignment.target(self.module());
         let value = assignment.value(self.module());
@@ -4132,22 +4062,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {

         let is_pep_613_type_alias = declared.inner_type().is_typealias_special_form();

-        if is_pep_613_type_alias
-            && let Some(value) = value
-            && !alias_syntax_validation(value)
-            && let Some(builder) = self.context.report_lint(
-                &INVALID_TYPE_FORM,
-                definition.full_range(self.db(), self.module()),
-            )
-        {
-            // TODO: better error message; full type-expression validation; etc.
-            let mut diagnostic = builder
-                .into_diagnostic("Invalid right-hand side for `typing.TypeAlias` assignment");
-            diagnostic.help(
-                "See https://typing.python.org/en/latest/spec/annotations.html#type-and-annotation-expressions",
-            );
-        }
-
         if !declared.qualifiers.is_empty() {
             for qualifier in TypeQualifier::iter() {
                 if !declared
@@ -4338,19 +4252,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             };

             if is_pep_613_type_alias {
-                let is_invalid = matches!(
-                    self.expression_type(map_subscript(value)),
-                    Type::SpecialForm(SpecialFormType::TypeQualifier(_))
-                );
-
-                if is_invalid
-                    && let Some(builder) = self.context.report_lint(&INVALID_TYPE_FORM, value)
-                {
-                    builder.into_diagnostic(
-                        "Type qualifiers are not allowed in type alias definitions",
-                    );
-                }
-
                 let inferred_ty =
                     if let Type::KnownInstance(KnownInstanceType::TypeVar(typevar)) = inferred_ty {
                         let identity = TypeVarIdentity::new(
diff --git a/crates/ty_python_semantic/src/types/infer/builder/post_inference/mod.rs b/crates/ty_python_semantic/src/types/infer/builder/post_inference/mod.rs
index 09bc583400bdd..622520ad72a2a 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/post_inference/mod.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/post_inference/mod.rs
@@ -5,6 +5,7 @@ pub(super) mod dynamic_class;
 pub(super) mod final_variable;
 pub(super) mod function;
 pub(super) mod overloaded_function;
+pub(super) mod pep_613_alias;
 pub(super) mod static_class;
 pub(super) mod type_param_validation;
 pub(super) mod typeguard;
diff --git a/crates/ty_python_semantic/src/types/infer/builder/post_inference/pep_613_alias.rs b/crates/ty_python_semantic/src/types/infer/builder/post_inference/pep_613_alias.rs
new file mode 100644
index 0000000000000..3e067a9c1dfbe
--- /dev/null
+++ b/crates/ty_python_semantic/src/types/infer/builder/post_inference/pep_613_alias.rs
@@ -0,0 +1,32 @@
+use crate::{
+    semantic_index::definition::{AnnotatedAssignmentDefinitionKind, Definition},
+    types::{
+        TypeCheckDiagnostics,
+        infer::{InferenceFlags, TypeInferenceBuilder},
+    },
+};
+
+pub(crate) fn check_pep_613_alias<'db>(
+    assignment: &AnnotatedAssignmentDefinitionKind,
+    definition: Definition<'db>,
+    builder: &TypeInferenceBuilder<'db, '_>,
+) -> Option<TypeCheckDiagnostics> {
+    let context = &builder.context;
+
+    let value = assignment.value(context.module())?;
+
+    let annotation = assignment.annotation(context.module());
+    if !builder
+        .file_expression_type(annotation)
+        .is_typealias_special_form()
+    {
+        return None;
+    }
+
+    let mut speculative = builder.speculate();
+
+    speculative.typevar_binding_context = Some(definition);
+    speculative.inference_flags |= InferenceFlags::IN_TYPE_ALIAS;
+    speculative.infer_type_expression(value);
+    Some(speculative.context.finish())
+}
diff --git a/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs b/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs
index cd70240a19b37..9d8df992a75b3 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs
@@ -2308,11 +2308,17 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
             }

             // for negative and positive numbers
-            ast::Expr::UnaryOp(u)
-                if matches!(u.op, ast::UnaryOp::USub | ast::UnaryOp::UAdd)
-                    && u.operand.is_number_literal_expr() =>
+            ast::Expr::UnaryOp(unary @ ast::ExprUnaryOp { op, operand, .. })
+                if matches!(op, ast::UnaryOp::USub | ast::UnaryOp::UAdd)
+                    && matches!(
+                        &**operand,
+                        ast::Expr::NumberLiteral(ast::ExprNumberLiteral {
+                            value: ast::Number::Int(_),
+                            ..
+                        })
+                    ) =>
             {
-                let ty = self.infer_unary_expression(u);
+                let ty = self.infer_unary_expression(unary);
                 self.store_expression_type(parameters, ty);
                 ty
             }

PATCH

echo "Patch applied successfully."
