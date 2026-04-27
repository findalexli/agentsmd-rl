#!/usr/bin/env bash
# Gold solution: apply the fix from astral-sh/ruff#24699 to expand class bases
# in per-base lint checks, then rebuild ty (incremental).
set -euo pipefail

cd /workspace/ruff

# Idempotency: if the patch is already applied, skip re-applying.
if grep -q 'expanded_class_base_entries(db, class.known(db), class_node, class_definition);' \
     crates/ty_python_semantic/src/types/infer/builder/post_inference/static_class.rs \
   && grep -q 'class InheritsFromFinalViaStarred' \
     crates/ty_python_semantic/resources/mdtest/mro.md; then
  echo "Patch already applied, skipping git apply."
else
  git apply --whitespace=nowarn <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/mro.md b/crates/ty_python_semantic/resources/mdtest/mro.md
index b0811a78cfe90c..4a53db7a9d45c5 100644
--- a/crates/ty_python_semantic/resources/mdtest/mro.md
+++ b/crates/ty_python_semantic/resources/mdtest/mro.md
@@ -614,6 +614,35 @@ reveal_mro(NameDuplicateBases)  # revealed: (<class 'NameDuplicateBases'>, Unkno
 class StarredInvalidBases(*invalid_bases): ...
 ```

+Per-base lint checks also see the unpacked entries:
+
+```py
+from typing import Generic, NamedTuple, Protocol
+
+# error: [inconsistent-mro]
+# error: [subclass-of-final-class]
+class InheritsFromFinalViaStarred(*(int, bool)): ...
+
+final_bases = (int, bool)
+
+# error: [inconsistent-mro]
+# error: [subclass-of-final-class]
+class InheritsFromFinalViaNamedStarred(*final_bases): ...
+
+# error: [instance-layout-conflict]
+# error: [invalid-named-tuple]
+# error: [invalid-named-tuple]
+class NamedTupleWithStarredBases(NamedTuple, *(int, str)): ...
+
+# error: [inconsistent-mro]
+# error: [invalid-protocol]
+# error: [invalid-protocol]
+class ProtocolWithStarredBases(Protocol, *(int, str)): ...
+
+# error: [invalid-base]
+class BareGenericInStarred(*(int, Generic)): ...
+```
+
 ## Inline tuple-literal starred bases point diagnostics at unpacked elements

 <!-- snapshot-diagnostics -->
diff --git a/crates/ty_python_semantic/src/types/infer/builder/post_inference/static_class.rs b/crates/ty_python_semantic/src/types/infer/builder/post_inference/static_class.rs
index 682fdfcace95c8..63690e3275b4de 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/post_inference/static_class.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/post_inference/static_class.rs
@@ -210,34 +210,42 @@ pub(crate) fn check_static_class_definitions<'db>(
     }

     let mut disjoint_bases = IncompatibleBases::default();
-    let mut protocol_base_with_generic_context = None;
+    let mut protocol_base_with_generic_context: Option<(&ast::Expr, _)> = None;
     let mut direct_typed_dict_bases = vec![];

+    let class_definition = index.expect_single_definition(class_node);
+
     // Iterate through the class's explicit bases to check for various possible errors:
     //     - Check for inheritance from plain `Generic`,
     //     - Check for inheritance from a `@final` classes
     //     - If the class is a protocol class: check for inheritance from a non-protocol class
     //     - If the class is a NamedTuple class: check for multiple inheritance that isn't `Generic[]`
-    for (i, base_class) in class.explicit_bases(db).iter().enumerate() {
+    let expanded_base_entries =
+        expanded_class_base_entries(db, class.known(db), class_node, class_definition);
+    for (i, entry) in expanded_base_entries.iter().enumerate() {
+        let source_node = entry.source_node();
+        let base_class = entry.ty();
+
         if class_kind == Some(CodeGeneratorKind::NamedTuple)
             && !matches!(
                 base_class,
                 Type::SpecialForm(SpecialFormType::NamedTuple)
                     | Type::KnownInstance(KnownInstanceType::SubscriptedGeneric(_))
             )
+            && let Some(node) = source_node
+            && let Some(builder) = context.report_lint(&INVALID_NAMED_TUPLE, node)
         {
-            if let Some(builder) = context.report_lint(&INVALID_NAMED_TUPLE, &class_node.bases()[i])
-            {
-                builder.into_diagnostic(format_args!(
-                    "NamedTuple class `{}` cannot use multiple inheritance except with `Generic[]`",
-                    class.name(db),
-                ));
-            }
+            builder.into_diagnostic(format_args!(
+                "NamedTuple class `{}` cannot use multiple inheritance except with `Generic[]`",
+                class.name(db),
+            ));
         }

         let base_class = match base_class {
             Type::SpecialForm(SpecialFormType::Generic) => {
-                if let Some(builder) = context.report_lint(&INVALID_BASE, &class_node.bases()[i]) {
+                if let Some(node) = source_node
+                    && let Some(builder) = context.report_lint(&INVALID_BASE, node)
+                {
                     // Unsubscripted `Generic` can appear in the MRO of many classes,
                     // but it is never valid as an explicit base class in user code.
                     builder.into_diagnostic("Cannot inherit from plain `Generic`");
@@ -245,25 +253,25 @@ pub(crate) fn check_static_class_definitions<'db>(
                 continue;
             }
             Type::KnownInstance(KnownInstanceType::SubscriptedGeneric(new_context)) => {
-                let Some((previous_index, previous_context)) = protocol_base_with_generic_context
+                let Some((previous_node, previous_context)) = protocol_base_with_generic_context
                 else {
                     continue;
                 };
-                let prior_node = &class_node.bases()[previous_index];
-                let Some(builder) = context.report_lint(&INVALID_GENERIC_CLASS, prior_node) else {
+                let Some(builder) = context.report_lint(&INVALID_GENERIC_CLASS, previous_node)
+                else {
                     continue;
                 };
                 let mut diagnostic = builder.into_diagnostic(
                     "Cannot both inherit from subscripted `Protocol` \
                                 and subscripted `Generic`",
                 );
-                if let ast::Expr::Subscript(prior_node) = prior_node
+                if let ast::Expr::Subscript(previous_node) = previous_node
                     && new_context == previous_context
                 {
                     diagnostic.help("Remove the type parameters from the `Protocol` base");
                     diagnostic.set_fix(Fix::unsafe_edit(Edit::range_deletion(TextRange::new(
-                        prior_node.value.end(),
-                        prior_node.end(),
+                        previous_node.value.end(),
+                        previous_node.end(),
                     ))));
                 }
                 continue;
@@ -273,16 +281,17 @@ pub(crate) fn check_static_class_definitions<'db>(
             // but it is semantically invalid.
             Type::KnownInstance(KnownInstanceType::SubscriptedProtocol(generic_context)) => {
                 if let Some(type_params) = class_node.type_params.as_deref() {
-                    let Some(builder) =
-                        context.report_lint(&INVALID_GENERIC_CLASS, &class_node.bases()[i])
-                    else {
+                    let Some(node) = source_node else {
+                        continue;
+                    };
+                    let Some(builder) = context.report_lint(&INVALID_GENERIC_CLASS, node) else {
                         continue;
                     };
                     let mut diagnostic = builder.into_diagnostic(
                         "Cannot both inherit from subscripted `Protocol` \
                             and use PEP 695 type variables",
                     );
-                    if let ast::Expr::Subscript(node) = &class_node.bases()[i] {
+                    if let ast::Expr::Subscript(node) = node {
                         let source = source_text(db, context.file());
                         let type_params_range = TextRange::new(
                             type_params.start().saturating_add(TextSize::new(1)),
@@ -295,13 +304,15 @@ pub(crate) fn check_static_class_definitions<'db>(
                             )));
                         }
                     }
-                } else if protocol_base_with_generic_context.is_none() {
-                    protocol_base_with_generic_context = Some((i, generic_context));
+                } else if let Some(node) = source_node
+                    && protocol_base_with_generic_context.is_none()
+                {
+                    protocol_base_with_generic_context = Some((node, generic_context));
                 }
                 continue;
             }
-            Type::ClassLiteral(class) => ClassType::NonGeneric(*class),
-            Type::GenericAlias(class) => ClassType::Generic(*class),
+            Type::ClassLiteral(class) => ClassType::NonGeneric(class),
+            Type::GenericAlias(class) => ClassType::Generic(class),
             _ => continue,
         };

@@ -312,8 +323,8 @@ pub(crate) fn check_static_class_definitions<'db>(
         if is_protocol {
             if !base_class.is_protocol(db)
                 && !base_class.is_object(db)
-                && let Some(builder) =
-                    context.report_lint(&INVALID_PROTOCOL, &class_node.bases()[i])
+                && let Some(node) = source_node
+                && let Some(builder) = context.report_lint(&INVALID_PROTOCOL, node)
             {
                 builder.into_diagnostic(format_args!(
                     "Protocol class `{}` cannot inherit from non-protocol class `{}`",
@@ -323,8 +334,8 @@ pub(crate) fn check_static_class_definitions<'db>(
             }
         } else if class_kind == Some(CodeGeneratorKind::TypedDict) {
             if !base_class.class_literal(db).is_typed_dict(db)
-                && let Some(builder) =
-                    context.report_lint(&INVALID_TYPED_DICT_HEADER, &class_node.bases()[i])
+                && let Some(node) = source_node
+                && let Some(builder) = context.report_lint(&INVALID_TYPED_DICT_HEADER, node)
             {
                 let mut diagnostic = builder.into_diagnostic(format_args!(
                     "TypedDict class `{}` can only inherit from TypedDict classes",
@@ -344,16 +355,15 @@ pub(crate) fn check_static_class_definitions<'db>(
             }
         }

-        if base_class.is_final(db) {
-            if let Some(builder) =
-                context.report_lint(&SUBCLASS_OF_FINAL_CLASS, &class_node.bases()[i])
-            {
-                builder.into_diagnostic(format_args!(
-                    "Class `{}` cannot inherit from final class `{}`",
-                    class.name(db),
-                    base_class.name(db),
-                ));
-            }
+        if base_class.is_final(db)
+            && let Some(node) = source_node
+            && let Some(builder) = context.report_lint(&SUBCLASS_OF_FINAL_CLASS, node)
+        {
+            builder.into_diagnostic(format_args!(
+                "Class `{}` cannot inherit from final class `{}`",
+                class.name(db),
+                base_class.name(db),
+            ));
         }

         if let Some((base_class_literal, _)) = base_class.static_class_literal(db)
@@ -362,20 +372,20 @@ pub(crate) fn check_static_class_definitions<'db>(
                 class.is_frozen_dataclass(db),
             )
             && base_is_frozen != class_is_frozen
+            && let Some(node) = source_node
         {
             report_bad_frozen_dataclass_inheritance(
                 context,
                 class,
                 class_node,
                 base_class_literal,
-                &class_node.bases()[i],
+                node,
                 base_is_frozen,
             );
         }
     }

     // Check for starred variable-length tuples that cannot be unpacked
-    let class_definition = index.expect_single_definition(class_node);
     for base in class_node.bases() {
         if let ast::Expr::Starred(starred) = base
             && let starred_ty = definition_expression_type(db, class_definition, &starred.value)
@@ -390,15 +400,11 @@ pub(crate) fn check_static_class_definitions<'db>(
     match class.try_mro(db, None) {
         Err(mro_error) => match mro_error.reason() {
             StaticMroErrorKind::DuplicateBases(duplicates) => {
-                let expanded_base_entries =
-                    expanded_class_base_entries(db, class.known(db), class_node, class_definition);
                 for duplicate in duplicates {
                     report_duplicate_bases(context, class, duplicate, &expanded_base_entries);
                 }
             }
             StaticMroErrorKind::InvalidBases(bases) => {
-                let expanded_base_entries =
-                    expanded_class_base_entries(db, class.known(db), class_node, class_definition);
                 for (index, base_ty) in bases {
                     if let Some(base_node) = expanded_base_entries[*index].source_node() {
                         report_invalid_or_unsupported_base(context, base_node, *base_ty, class);
PATCH
fi

# Rebuild ty (incremental) so the test invocation picks up the fix.
cargo build --bin ty 2>&1 | tail -5
