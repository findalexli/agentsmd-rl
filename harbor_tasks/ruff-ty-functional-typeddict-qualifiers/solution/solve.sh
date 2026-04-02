#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotency check: if functional_typed_dict_field already takes qualifiers param, skip
if grep -q 'qualifiers: TypeQualifiers' \
    crates/ty_python_semantic/src/types/typed_dict.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/typed_dict.md b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
index c1cb7adf3c89ff..caa871736281d7 100644
--- a/crates/ty_python_semantic/resources/mdtest/typed_dict.md
+++ b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
@@ -2178,6 +2178,17 @@ reveal_type(inline["x"])  # revealed: int
 inline_bad = TypedDict("InlineBad", {"x": int})(x="bad")
 ```
 
+Inline functional `TypedDict`s preserve `ReadOnly` qualifiers:
+
+```py
+from typing_extensions import TypedDict, ReadOnly
+
+inline_readonly = TypedDict("InlineReadOnly", {"id": ReadOnly[int]})(id=1)
+
+# error: [invalid-assignment] "Cannot assign to key "id" on TypedDict `InlineReadOnly`: key is marked read-only"
+inline_readonly["id"] = 2
+```
+
 Inline functional `TypedDict`s resolve string forward references to existing names:
 
 ```py
@@ -2214,6 +2225,38 @@ def f(total: bool) -> None:
     TotalDynamic = TypedDict("TotalDynamic", {"id": int}, total=total)
 ```
 
+## Function syntax with `Required` and `NotRequired`
+
+The `Required` and `NotRequired` wrappers can be used to override the default requiredness:
+
+```py
+from typing_extensions import TypedDict, Required, NotRequired
+
+# With total=True (default), all fields are required unless wrapped in NotRequired
+MovieWithOptional = TypedDict("MovieWithOptional", {"name": str, "year": NotRequired[int]})
+
+# name is required, year is optional
+# error: [missing-typed-dict-key] "Missing required key 'name' in TypedDict `MovieWithOptional` constructor"
+empty_movie = MovieWithOptional()
+movie_no_year = MovieWithOptional(name="The Matrix")
+reveal_type(movie_no_year)  # revealed: MovieWithOptional
+reveal_type(movie_no_year["name"])  # revealed: str
+reveal_type(movie_no_year["year"])  # revealed: int
+```
+
+```py
+from typing_extensions import TypedDict, Required, NotRequired
+
+# With total=False, all fields are optional unless wrapped in Required
+PartialWithRequired = TypedDict("PartialWithRequired", {"name": Required[str], "year": int}, total=False)
+
+# name is required, year is optional
+# error: [missing-typed-dict-key] "Missing required key 'name' in TypedDict `PartialWithRequired` constructor"
+empty_partial = PartialWithRequired()
+partial_no_year = PartialWithRequired(name="The Matrix")
+reveal_type(partial_no_year)  # revealed: PartialWithRequired
+```
+
 ## Function syntax with `closed`
 
 The `closed` keyword is accepted but not yet fully supported:
@@ -2267,7 +2310,7 @@ class Bar(TypedDict("TD3", {}, extra_items=ReadOnly[int])): ...
 Functional TypedDict supports forward references (string annotations):
 
 ```py
-from typing_extensions import TypedDict
+from typing_extensions import TypedDict, NotRequired
 
 # Forward reference to a class defined below
 MovieWithDirector = TypedDict("MovieWithDirector", {"title": str, "director": "Director"})
@@ -2277,6 +2320,39 @@ class Director:
 
 movie: MovieWithDirector = {"title": "The Matrix", "director": Director()}
 reveal_type(movie)  # revealed: MovieWithDirector
+
+# Forward reference to a class defined above
+MovieWithDirector2 = TypedDict("MovieWithDirector2", {"title": str, "director": NotRequired["Director"]})
+
+movie2: MovieWithDirector2 = {"title": "The Matrix"}
+reveal_type(movie2)  # revealed: MovieWithDirector2
+```
+
+String annotations can also wrap the entire `Required` or `NotRequired` qualifier:
+
+```py
+from typing_extensions import TypedDict, Required, NotRequired
+
+# NotRequired as a string annotation
+TD = TypedDict("TD", {"required": str, "optional": "NotRequired[int]"})
+
+# 'required' is required, 'optional' is not required
+td1: TD = {"required": "hello"}  # Valid - optional is not required
+td2: TD = {"required": "hello", "optional": 42}  # Valid - all keys provided
+reveal_type(td1)  # revealed: TD
+reveal_type(td1["required"])  # revealed: Literal["hello"]
+reveal_type(td1["optional"])  # revealed: int
+
+# error: [missing-typed-dict-key] "Missing required key 'required' in TypedDict `TD` constructor"
+bad_td: TD = {"optional": 42}
+
+# Also works with Required in total=False TypedDicts
+TD2 = TypedDict("TD2", {"required": "Required[str]", "optional": int}, total=False)
+
+# 'required' is required, 'optional' is not required
+td3: TD2 = {"required": "hello"}  # Valid
+# error: [missing-typed-dict-key] "Missing required key 'required' in TypedDict `TD2` constructor"
+bad_td2: TD2 = {"optional": 42}
 ```
 
 ## Recursive functional `TypedDict` (unstringified forward reference)
diff --git a/crates/ty_python_semantic/src/types/infer.rs b/crates/ty_python_semantic/src/types/infer.rs
index 5a2ee4441422a2..265d1176c81493 100644
--- a/crates/ty_python_semantic/src/types/infer.rs
+++ b/crates/ty_python_semantic/src/types/infer.rs
@@ -54,7 +54,8 @@ use crate::types::function::{FunctionDecorators, FunctionType};
 use crate::types::generics::Specialization;
 use crate::types::unpacker::{UnpackResult, Unpacker};
 use crate::types::{
-    ClassLiteral, KnownClass, StaticClassLiteral, Type, TypeAndQualifiers, declaration_type,
+    ClassLiteral, KnownClass, StaticClassLiteral, Type, TypeAndQualifiers, TypeQualifiers,
+    declaration_type,
 };
 use crate::unpack::Unpack;
 use builder::TypeInferenceBuilder;
@@ -737,6 +738,10 @@ struct DefinitionInferenceExtra<'db> {
 
     /// For function definitions, the undecorated type of the function.
     undecorated_type: Option<Type<'db>>,
+
+    /// Type qualifiers (`Required`, `NotRequired`, etc.) for annotation expressions.
+    /// Only populated for expressions that have non-empty qualifiers.
+    qualifiers: FxHashMap<ExpressionNodeKey, TypeQualifiers>,
 }
 
 impl<'db> DefinitionInference<'db> {
@@ -810,6 +815,14 @@ impl<'db> DefinitionInference<'db> {
             .or_else(|| self.fallback_type())
     }
 
+    /// Get qualifiers for an annotation expression, if any.
+    pub(crate) fn qualifiers(&self, expression: impl Into<ExpressionNodeKey>) -> TypeQualifiers {
+        self.extra
+            .as_ref()
+            .and_then(|extra| extra.qualifiers.get(&expression.into()).copied())
+            .unwrap_or_default()
+    }
+
     #[track_caller]
     pub(crate) fn binding_type(&self, definition: Definition<'db>) -> Type<'db> {
         self.bindings
diff --git a/crates/ty_python_semantic/src/types/infer/builder.rs b/crates/ty_python_semantic/src/types/infer/builder.rs
index 53c9bc6c15acff..3b79203d3928e9 100644
--- a/crates/ty_python_semantic/src/types/infer/builder.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder.rs
@@ -223,6 +223,10 @@ pub(super) struct TypeInferenceBuilder<'db, 'ast> {
     /// The types of every expression in this region.
     expressions: FxHashMap<ExpressionNodeKey, Type<'db>>,
 
+    /// Type qualifiers (`Required`, `NotRequired`, etc.) for annotation expressions.
+    /// Only populated for expressions that have non-empty qualifiers.
+    qualifiers: FxHashMap<ExpressionNodeKey, TypeQualifiers>,
+
     /// Expressions that are string annotations
     string_annotations: FxHashSet<ExpressionNodeKey>,
 
@@ -333,6 +337,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             deferred_state: DeferredExpressionState::None,
             inferring_vararg_annotation: false,
             expressions: FxHashMap::default(),
+            qualifiers: FxHashMap::default(),
             string_annotations: FxHashSet::default(),
             bindings: VecMap::default(),
             declarations: VecMap::default(),
@@ -383,6 +388,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             self.deferred.extend(extra.deferred.iter().copied());
             self.string_annotations
                 .extend(extra.string_annotations.iter().copied());
+            self.qualifiers.extend(extra.qualifiers.iter());
         }
     }
 
@@ -533,6 +539,13 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             .or(self.fallback_type())
     }
 
+    /// Store qualifiers for an annotation expression.
+    fn store_qualifiers(&mut self, expr: &ast::Expr, qualifiers: TypeQualifiers) {
+        if !qualifiers.is_empty() {
+            self.qualifiers.insert(expr.into(), qualifiers);
+        }
+    }
+
     /// Get the type of an expression from any scope in the same file.
     ///
     /// If the expression is in the current scope, and we are inferring the entire scope, just look
@@ -3029,7 +3042,8 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
     }
 
     fn infer_assignment_deferred(&mut self, target: &ast::Expr, value: &'ast ast::Expr) {
-        // Infer deferred bounds/constraints/defaults of a legacy TypeVar / ParamSpec / NewType.
+        // Infer deferred bounds/constraints/defaults of a legacy TypeVar / ParamSpec / NewType,
+        // and field types for functional TypedDict.
         let ast::Expr::Call(ast::ExprCall {
             func, arguments, ..
         }) = value
@@ -8971,6 +8985,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         let Self {
             context,
             mut expressions,
+            qualifiers: _,
             string_annotations,
             scope,
             bindings,
@@ -9077,6 +9092,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             region: _,
             cycle_recovery: _,
             all_definitely_bound: _,
+            qualifiers: _,
         } = self;
         let diagnostics = context.finish();
 
@@ -9098,6 +9114,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         let Self {
             context,
             mut expressions,
+            mut qualifiers,
             string_annotations,
             scope,
             bindings,
@@ -9126,8 +9143,10 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             || cycle_recovery.is_some()
             || undecorated_type.is_some()
             || !deferred.is_empty()
-            || !called_functions.is_empty())
+            || !called_functions.is_empty()
+            || !qualifiers.is_empty())
         .then(|| {
+            qualifiers.shrink_to_fit();
             Box::new(DefinitionInferenceExtra {
                 string_annotations,
                 called_functions: called_functions
@@ -9138,6 +9157,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                 deferred: deferred.into_boxed_slice(),
                 diagnostics,
                 undecorated_type,
+                qualifiers,
             })
         });
 
@@ -9183,6 +9203,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             deferred: _,
             bindings: _,
             declarations: _,
+            qualifiers: _,
 
             // Ignored; only relevant to definition regions
             undecorated_type: _,
@@ -9247,6 +9268,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             called_functions: _,
             undecorated_type: _,
             all_definitely_bound: _,
+            qualifiers: _,
         } = *self;
 
         let mut builder = TypeInferenceBuilder::new(self.db(), region, index, self.module());
@@ -9296,6 +9318,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             index: _,
             region: _,
             return_types_and_ranges: _,
+            qualifiers: _,
         } = other;
 
         let diagnostics = context.finish();
@@ -9823,7 +9846,7 @@ impl<'db, 'ast> AddBinding<'db, 'ast> {
     /// necessarily guarantee that the passed-in value for `__setitem__` is stored and
     /// can be retrieved unmodified via `__getitem__`. Therefore, we currently only
     /// perform assignment-based narrowing on a few built-in classes (`list`, `dict`,
-    /// `bytesarray`, `TypedDict` and `collections` types) where we are confident that
+    /// `bytesarray`, `TypedDict`, and `collections` types) where we are confident that
     /// this kind of narrowing can be performed soundly. This is the same approach as
     /// pyright. TODO: Other standard library classes may also be considered safe. Also,
     /// subclasses of these safe classes that do not override `__getitem__/__setitem__`
diff --git a/crates/ty_python_semantic/src/types/infer/builder/annotation_expression.rs b/crates/ty_python_semantic/src/types/infer/builder/annotation_expression.rs
index c2a61281105248..0da1a370cce5c6 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/annotation_expression.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/annotation_expression.rs
@@ -409,6 +409,8 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
         };
 
         self.store_expression_type(annotation, annotation_ty.inner_type());
+        self.store_qualifiers(annotation, annotation_ty.qualifiers());
+
         annotation_ty
     }
 
diff --git a/crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs b/crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs
index d04db97fd85131..d759ac9889aec9 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs
@@ -271,7 +271,11 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
 
             schema.insert(
                 Name::new(key_literal.value(db)),
-                functional_typed_dict_field(annotation.inner_type(), total),
+                functional_typed_dict_field(
+                    annotation.inner_type(),
+                    annotation.qualifiers(),
+                    total,
+                ),
             );
         }
 
diff --git a/crates/ty_python_semantic/src/types/typed_dict.rs b/crates/ty_python_semantic/src/types/typed_dict.rs
index b9c003f723dc43..356fa000f865da 100644
--- a/crates/ty_python_semantic/src/types/typed_dict.rs
+++ b/crates/ty_python_semantic/src/types/typed_dict.rs
@@ -18,8 +18,8 @@ use super::diagnostic::{
 };
 use super::infer::infer_deferred_types;
 use super::{
-    ApplyTypeMappingVisitor, IntersectionBuilder, Type, TypeMapping, definition_expression_type,
-    visitor,
+    ApplyTypeMappingVisitor, IntersectionBuilder, Type, TypeMapping, TypeQualifiers,
+    definition_expression_type, visitor,
 };
 use crate::Db;
 use crate::semantic_index::definition::Definition;
@@ -76,10 +76,20 @@ impl get_size2::GetSize for FunctionalTypedDictSpec<'_> {}
 
 pub(super) fn functional_typed_dict_field(
     declared_ty: Type<'_>,
+    qualifiers: TypeQualifiers,
     total: bool,
 ) -> TypedDictField<'_> {
+    let required = if qualifiers.contains(TypeQualifiers::REQUIRED) {
+        true
+    } else if qualifiers.contains(TypeQualifiers::NOT_REQUIRED) {
+        false
+    } else {
+        total
+    };
+
     TypedDictFieldBuilder::new(declared_ty)
-        .required(total)
+        .required(required)
+        .read_only(qualifiers.contains(TypeQualifiers::READ_ONLY))
         .build()
 }
 
@@ -587,10 +597,11 @@ pub(super) fn deferred_functional_typed_dict_spec<'db>(
             let field_ty = deferred_inference
                 .try_expression_type(&item.value)
                 .unwrap_or(Type::unknown());
+            let qualifiers = deferred_inference.qualifiers(&item.value);
 
             schema.insert(
                 Name::new(key_lit.value(db)),
-                functional_typed_dict_field(field_ty, total),
+                functional_typed_dict_field(field_ty, qualifiers, total),
             );
         }
 
@@ -610,10 +621,11 @@ pub(super) fn deferred_functional_typed_dict_spec<'db>(
                 let field_ty = deferred_inference
                     .try_expression_type(&keyword.value)
                     .unwrap_or(Type::unknown());
+                let qualifiers = deferred_inference.qualifiers(&keyword.value);
 
                 schema.insert(
                     Name::new(field_name),
-                    functional_typed_dict_field(field_ty, total),
+                    functional_typed_dict_field(field_ty, qualifiers, total),
                 );
             }
         }

PATCH

echo "Patch applied successfully."
