#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotency check: see if the fix is already applied
if grep -q 'DynamicTypedDict(typeddict)' crates/ty_python_semantic/src/types/class/static_literal.rs 2>/dev/null \
   && grep -q 'fn is_typed_dict.*bool' crates/ty_python_semantic/src/types/class.rs 2>/dev/null; then
    echo "Fix already applied, skipping."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/typed_dict.md b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
index f775adf2f1bd1c..c1cb7adf3c89ff 100644
--- a/crates/ty_python_semantic/resources/mdtest/typed_dict.md
+++ b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
@@ -1949,6 +1949,33 @@ emp_invalid1 = Employee(department="HR")
 emp_invalid2 = Employee(id=3)
 ```

+## Class-based inheritance from functional `TypedDict`
+
+Class-based TypedDicts can inherit from functional TypedDicts:
+
+```py
+from typing import TypedDict
+
+Base = TypedDict("Base", {"a": int}, total=False)
+
+class Child(Base):
+    b: str
+    c: list[int]
+
+child1 = Child(b="hello", c=[1, 2, 3])
+child2 = Child(a=1, b="world", c=[])
+
+reveal_type(child1["a"])  # revealed: int
+reveal_type(child1["b"])  # revealed: str
+reveal_type(child1["c"])  # revealed: list[int]
+
+# error: [missing-typed-dict-key] "Missing required key 'b' in TypedDict `Child` constructor"
+bad_child1 = Child(c=[1])
+
+# error: [missing-typed-dict-key] "Missing required key 'c' in TypedDict `Child` constructor"
+bad_child2 = Child(b="test")
+```
+
 ## Generic `TypedDict`

 `TypedDict`s can also be generic.
@@ -2551,6 +2578,9 @@ def f():

 # fine
 MyFunctionalTypedDict = TypedDict("MyFunctionalTypedDict", {"not-an-identifier": Required[int]})
+
+class FunctionalTypedDictSubclass(MyFunctionalTypedDict):
+    y: NotRequired[int]  # fine
 ```

 ### Nested `Required` and `NotRequired`
@@ -3590,6 +3620,18 @@ class Child(Base):
     y: str
 ```

+The functional `TypedDict` syntax also triggers this error:
+
+```py
+from dataclasses import dataclass
+from typing import TypedDict
+
+@dataclass
+# error: [invalid-dataclass]
+class Foo(TypedDict("Foo", {"x": int, "y": str})):
+    pass
+```
+
 ## Class header validation

 <!-- snapshot-diagnostics -->
diff --git a/crates/ty_python_semantic/src/types/class.rs b/crates/ty_python_semantic/src/types/class.rs
index b4266c20c5aac7..805c303d2d1eba 100644
--- a/crates/ty_python_semantic/src/types/class.rs
+++ b/crates/ty_python_semantic/src/types/class.rs
@@ -907,6 +907,11 @@ impl<'db> ClassType<'db> {
         self.is_known(db, KnownClass::Object)
     }

+    /// Return `true` if this class is a `TypedDict`.
+    pub(crate) fn is_typed_dict(self, db: &'db dyn Db) -> bool {
+        self.class_literal(db).is_typed_dict(db)
+    }
+
     pub(super) fn apply_type_mapping_impl<'a>(
         self,
         db: &'db dyn Db,
diff --git a/crates/ty_python_semantic/src/types/class/static_literal.rs b/crates/ty_python_semantic/src/types/class/static_literal.rs
index e49dfc2868f985..95e2491885a74d 100644
--- a/crates/ty_python_semantic/src/types/class/static_literal.rs
+++ b/crates/ty_python_semantic/src/types/class/static_literal.rs
@@ -34,9 +34,9 @@ use crate::{
         call::{CallError, CallErrorKind},
         callable::CallableTypeKind,
         class::{
-            ClassMemberResult, CodeGeneratorKind, DisjointBase, Field, FieldKind,
-            InstanceMemberResult, MetaclassError, MetaclassErrorKind, MethodDecorator, MroLookup,
-            NamedTupleField, SlotsKind, synthesize_namedtuple_class_member,
+            ClassMemberResult, CodeGeneratorKind, DisjointBase, DynamicTypedDictLiteral, Field,
+            FieldKind, InstanceMemberResult, MetaclassError, MetaclassErrorKind, MethodDecorator,
+            MroLookup, NamedTupleField, SlotsKind, synthesize_namedtuple_class_member,
         },
         context::InferContext,
         declaration_type, definition_expression_type, determine_upper_bound,
@@ -54,7 +54,10 @@ use crate::{
         mro::{Mro, MroIterator},
         signatures::CallableSignature,
         tuple::{Tuple, TupleSpec, TupleType},
-        typed_dict::{TypedDictField, TypedDictParams, typed_dict_params_from_class_def},
+        typed_dict::{
+            TypedDictField, TypedDictParams, dynamic_typed_dict_schema,
+            typed_dict_params_from_class_def,
+        },
         variance::VarianceInferable,
         visitor::{TypeCollector, TypeVisitor, walk_type_with_recursion_guard},
     },
@@ -1670,25 +1673,64 @@ impl<'db> StaticClassLiteral<'db> {
         specialization: Option<Specialization<'db>>,
         field_policy: CodeGeneratorKind<'db>,
     ) -> FxIndexMap<Name, Field<'db>> {
+        enum FieldSource<'db> {
+            Static(StaticClassLiteral<'db>, Option<Specialization<'db>>),
+            DynamicTypedDict(DynamicTypedDictLiteral<'db>),
+        }
+
         if field_policy == CodeGeneratorKind::NamedTuple {
             // NamedTuples do not allow multiple inheritance, so it is sufficient to enumerate the
             // fields of this class only.
             return self.own_fields(db, specialization, field_policy);
         }

-        self.iter_mro(db, specialization)
-            .rev()
+        let matching_classes_in_mro: Vec<FieldSource<'db>> = self
+            .iter_mro(db, specialization)
             .filter_map(|superclass| {
                 let class = superclass.into_class()?;
-                // Dynamic classes don't have fields (no class body).
-                let (class_literal, specialization) = class.static_class_literal(db)?;
-                if field_policy.matches(db, class_literal.into(), specialization) {
-                    Some((class_literal, specialization))
-                } else {
-                    None
+
+                if let Some((class_literal, specialization)) = class.static_class_literal(db) {
+                    if field_policy.matches(db, class_literal.into(), specialization) {
+                        return Some(FieldSource::Static(class_literal, specialization));
+                    }
+                }
+
+                if field_policy == CodeGeneratorKind::TypedDict
+                    && let ClassLiteral::DynamicTypedDict(typeddict) = class.class_literal(db)
+                {
+                    return Some(FieldSource::DynamicTypedDict(typeddict));
+                }
+
+                None
+            })
+            .collect();
+
+        matching_classes_in_mro
+            .into_iter()
+            .rev()
+            .flat_map(|source| match source {
+                FieldSource::Static(class, specialization) => {
+                    class.own_fields(db, specialization, field_policy)
+                }
+                FieldSource::DynamicTypedDict(typeddict) => {
+                    dynamic_typed_dict_schema(db, typeddict)
+                        .iter()
+                        .map(|(name, td_field)| {
+                            (
+                                name.clone(),
+                                Field {
+                                    declared_ty: td_field.declared_ty,
+                                    kind: FieldKind::TypedDict {
+                                        is_required: td_field.is_required(),
+                                        is_read_only: td_field.is_read_only(),
+                                    },
+                                    first_declaration: td_field.first_declaration(),
+                                },
+                            )
+                        })
+                        .collect()
                 }
             })
-            .flat_map(|(class, specialization)| class.own_fields(db, specialization, field_policy))
             // KW_ONLY sentinels are markers, not real fields. Exclude them so
             // they cannot shadow an inherited field with the same name.
             .filter(|(_, field)| !field.is_kw_only_sentinel(db))
diff --git a/crates/ty_python_semantic/src/types/infer/builder.rs b/crates/ty_python_semantic/src/types/infer/builder.rs
index 93ec1c7729a933..53c9bc6c15acff 100644
--- a/crates/ty_python_semantic/src/types/infer/builder.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder.rs
@@ -4112,13 +4112,8 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                 TypeQualifiers::REQUIRED | TypeQualifiers::NOT_REQUIRED | TypeQualifiers::READ_ONLY,
             ) {
                 let in_typed_dict = current_scope.kind() == ScopeKind::Class
-                    && nearest_enclosing_class(self.db(), self.index, self.scope()).is_some_and(
-                        |class| {
-                            class
-                                .iter_mro(self.db(), None)
-                                .contains(&ClassBase::TypedDict)
-                        },
-                    );
+                    && nearest_enclosing_class(self.db(), self.index, self.scope())
+                        .is_some_and(|class| class.is_typed_dict(self.db()));
                 if !in_typed_dict {
                     for qualifier in [
                         TypeQualifiers::REQUIRED,
@@ -7322,7 +7317,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {

         // Validate `TypedDict` constructor calls after argument type inference.
         if let Some(class) = class
-            && class.class_literal(self.db()).is_typed_dict(self.db())
+            && class.is_typed_dict(self.db())
         {
             validate_typed_dict_constructor(
                 &self.context,

PATCH

echo "Patch applied successfully."
