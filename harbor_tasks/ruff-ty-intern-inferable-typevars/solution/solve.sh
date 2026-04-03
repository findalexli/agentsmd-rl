#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if InferableTypeVarsInner already exists, patch is applied
if grep -q 'struct InferableTypeVarsInner' crates/ty_python_semantic/src/types/generics.rs; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_python_semantic/src/types.rs b/crates/ty_python_semantic/src/types.rs
index f490e097a55748..7cea85b6682b08 100644
--- a/crates/ty_python_semantic/src/types.rs
+++ b/crates/ty_python_semantic/src/types.rs
@@ -1645,7 +1645,7 @@ impl<'db> Type<'db> {
         self,
         db: &'db dyn Db,
         target: Type<'db>,
-        inferable: InferableTypeVars<'_, 'db>,
+        inferable: InferableTypeVars<'db>,
     ) -> Type<'db> {
         let constraints = ConstraintSetBuilder::new();
         self.filter_union(db, |elem| {
diff --git a/crates/ty_python_semantic/src/types/call/bind.rs b/crates/ty_python_semantic/src/types/call/bind.rs
index d3f7e61f601bcd..472a1a7469b80e 100644
--- a/crates/ty_python_semantic/src/types/call/bind.rs
+++ b/crates/ty_python_semantic/src/types/call/bind.rs
@@ -56,7 +56,7 @@ use crate::types::{
     TypeVarBoundOrConstraints, TypeVarVariance, UnionBuilder, UnionType, WrapperDescriptorKind,
     enums, list_members,
 };
-use crate::{DisplaySettings, Program};
+use crate::{DisplaySettings, FxOrderSet, Program};
 use ruff_db::diagnostic::{Annotation, Diagnostic, SubDiagnostic, SubDiagnosticSeverity};
 use ruff_python_ast::{self as ast, ArgOrKeyword, PythonVersion};
 use ty_module_resolver::KnownModule;
@@ -1882,21 +1882,22 @@ impl<'db> Bindings<'db> {
                         let extract_inferable = |instance: &NominalInstanceType<'db>| {
                             if instance.has_known_class(db, KnownClass::NoneType) {
                                 // Caller explicitly passed None, so no typevars are inferable.
-                                return Some(FxHashSet::default());
+                                return Some(InferableTypeVars::None);
                             }
-                            instance
+                            let typevars: Option<FxOrderSet<_>> = instance
                                 .tuple_spec(db)?
                                 .fixed_elements()
                                 .map(|ty| {
                                     ty.as_typevar()
                                         .map(|bound_typevar| bound_typevar.identity(db))
                                 })
-                                .collect()
+                                .collect();
+                            typevars.map(|typevars| InferableTypeVars::from_typevars(db, typevars))
                         };

                         let inferable = match overload.parameter_types() {
                             // Caller did not provide argument, so no typevars are inferable.
-                            [None] => FxHashSet::default(),
+                            [None] => InferableTypeVars::None,
                             [Some(Type::NominalInstance(instance))] => {
                                 match extract_inferable(instance) {
                                     Some(inferable) => inferable,
@@ -1908,11 +1909,7 @@ impl<'db> Bindings<'db> {

                         let constraints = ConstraintSetBuilder::new();
                         let set = constraints.load(db, tracked.constraints(db));
-                        let result = set.satisfied_by_all_typevars(
-                            db,
-                            &constraints,
-                            InferableTypeVars::One(&inferable),
-                        );
+                        let result = set.satisfied_by_all_typevars(db, &constraints, inferable);
                         overload.set_return_type(Type::bool_literal(result));
                     }

@@ -3672,7 +3669,7 @@ struct ArgumentTypeChecker<'a, 'db> {
     return_ty: Type<'db>,
     errors: &'a mut Vec<BindingError<'db>>,

-    inferable_typevars: InferableTypeVars<'db, 'db>,
+    inferable_typevars: InferableTypeVars<'db>,
     specialization: Option<Specialization<'db>>,

     /// Argument indices for which specialization inference has already produced a sufficiently
@@ -4430,7 +4427,7 @@ impl<'a, 'db> ArgumentTypeChecker<'a, 'db> {
     fn finish(
         self,
     ) -> (
-        InferableTypeVars<'db, 'db>,
+        InferableTypeVars<'db>,
         Option<Specialization<'db>>,
         Type<'db>,
     ) {
@@ -4503,7 +4500,7 @@ pub(crate) struct Binding<'db> {
     return_ty: Type<'db>,

     /// The inferable typevars in this signature.
-    inferable_typevars: InferableTypeVars<'db, 'db>,
+    inferable_typevars: InferableTypeVars<'db>,

     /// The specialization that was inferred from the argument types, if the callable is generic.
     specialization: Option<Specialization<'db>>,
@@ -4780,7 +4777,7 @@ impl<'db> Binding<'db> {
 #[derive(Clone, Debug)]
 struct BindingSnapshot<'db> {
     return_ty: Type<'db>,
-    inferable_typevars: InferableTypeVars<'db, 'db>,
+    inferable_typevars: InferableTypeVars<'db>,
     specialization: Option<Specialization<'db>>,
     argument_matches: Box<[MatchedArgument<'db>]>,
     parameter_tys: Box<[Option<Type<'db>>]>,
diff --git a/crates/ty_python_semantic/src/types/constraints.rs b/crates/ty_python_semantic/src/types/constraints.rs
index 308bd1479ad52e..7e410aea6f8367 100644
--- a/crates/ty_python_semantic/src/types/constraints.rs
+++ b/crates/ty_python_semantic/src/types/constraints.rs
@@ -341,11 +341,7 @@ impl<'db, 'c> ConstraintSet<'db, 'c> {
         self.is_cyclic_impl(db, None)
     }

-    fn is_cyclic_impl(
-        self,
-        db: &'db dyn Db,
-        inferable: Option<InferableTypeVars<'_, 'db>>,
-    ) -> bool {
+    fn is_cyclic_impl(self, db: &'db dyn Db, inferable: Option<InferableTypeVars<'db>>) -> bool {
         #[derive(Default)]
         struct CollectReachability<'db> {
             reachable_typevars: RefCell<FxHashSet<BoundTypeVarIdentity<'db>>>,
@@ -422,7 +418,7 @@ impl<'db, 'c> ConstraintSet<'db, 'c> {
             .for_each_constraint(self.builder, &mut |constraint, _| {
                 let constraint = self.builder.constraint_data(constraint);
                 let identity = constraint.typevar.identity(db);
-                if inferable.is_some_and(|inferable| !identity.is_inferable(inferable)) {
+                if inferable.is_some_and(|inferable| !identity.is_inferable(db, inferable)) {
                     return;
                 }
                 let visitor = CollectReachability::default();
@@ -434,7 +430,7 @@ impl<'db, 'c> ConstraintSet<'db, 'c> {
                     entry.extend(
                         reachable
                             .into_iter()
-                            .filter(|tv| tv.is_inferable(inferable)),
+                            .filter(|tv| tv.is_inferable(db, inferable)),
                     );
                 } else {
                     entry.extend(reachable);
@@ -488,7 +484,7 @@ impl<'db, 'c> ConstraintSet<'db, 'c> {
         &self,
         db: &'db dyn Db,
         builder: &'c ConstraintSetBuilder<'db>,
-        inferable: InferableTypeVars<'_, 'db>,
+        inferable: InferableTypeVars<'db>,
     ) -> bool {
         self.verify_builder(builder);
         self.node.satisfied_by_all_typevars(db, builder, inferable)
@@ -647,7 +643,7 @@ impl<'db, 'c> ConstraintSet<'db, 'c> {
         self,
         db: &'db dyn Db,
         builder: &'c ConstraintSetBuilder<'db>,
-        inferable: InferableTypeVars<'_, 'db>,
+        inferable: InferableTypeVars<'db>,
         choose: impl FnMut(
             BoundTypeVarInstance<'db>,
             TypeVarVariance,
@@ -2118,7 +2114,7 @@ impl NodeId {
         self,
         db: &'db dyn Db,
         builder: &ConstraintSetBuilder<'db>,
-        inferable: InferableTypeVars<'_, 'db>,
+        inferable: InferableTypeVars<'db>,
     ) -> bool {
         match self.node() {
             Node::AlwaysTrue => return true,
diff --git a/crates/ty_python_semantic/src/types/generics.rs b/crates/ty_python_semantic/src/types/generics.rs
index b6cdd3f17be1e1..4df1ebcd2e2e79 100644
--- a/crates/ty_python_semantic/src/types/generics.rs
+++ b/crates/ty_python_semantic/src/types/generics.rs
@@ -207,83 +207,79 @@ pub(crate) fn typing_self<'db>(
     )
 }

-#[derive(Clone, Copy, Debug)]
-pub(crate) enum InferableTypeVars<'a, 'db> {
+#[derive(Clone, Copy, Debug, Hash, Eq, PartialEq, get_size2::GetSize, salsa::Update)]
+pub(crate) enum InferableTypeVars<'db> {
     None,
-    One(&'a FxHashSet<BoundTypeVarIdentity<'db>>),
-    Two(
-        &'a InferableTypeVars<'a, 'db>,
-        &'a InferableTypeVars<'a, 'db>,
-    ),
+    Some(InferableTypeVarsInner<'db>),
 }

+impl<'db> InferableTypeVars<'db> {
+    pub(crate) fn from_typevars(
+        db: &'db dyn Db,
+        typevars: FxOrderSet<BoundTypeVarIdentity<'db>>,
+    ) -> Self {
+        if typevars.is_empty() {
+            return InferableTypeVars::None;
+        }
+        Self::Some(InferableTypeVarsInner::new_internal(db, typevars))
+    }
+}
+
+#[salsa::interned(debug, constructor=new_internal, heap_size=ruff_memory_usage::heap_size)]
+pub(crate) struct InferableTypeVarsInner<'db> {
+    #[returns(ref)]
+    inferable: FxOrderSet<BoundTypeVarIdentity<'db>>,
+}
+
+// The Salsa heap is tracked separately.
+impl get_size2::GetSize for InferableTypeVarsInner<'_> {}
+
 impl<'db> BoundTypeVarIdentity<'db> {
-    pub(crate) fn is_inferable(self, inferable: InferableTypeVars<'_, 'db>) -> bool {
+    pub(crate) fn is_inferable(self, db: &'db dyn Db, inferable: InferableTypeVars<'db>) -> bool {
         match inferable {
             InferableTypeVars::None => false,
-            InferableTypeVars::One(typevars) => typevars.contains(&self),
-            InferableTypeVars::Two(left, right) => {
-                self.is_inferable(*left) || self.is_inferable(*right)
-            }
+            InferableTypeVars::Some(inner) => inner.inferable(db).contains(&self),
         }
     }
 }

 impl<'db> BoundTypeVarInstance<'db> {
-    pub(crate) fn is_inferable(
-        self,
-        db: &'db dyn Db,
-        inferable: InferableTypeVars<'_, 'db>,
-    ) -> bool {
-        self.identity(db).is_inferable(inferable)
+    pub(crate) fn is_inferable(self, db: &'db dyn Db, inferable: InferableTypeVars<'db>) -> bool {
+        self.identity(db).is_inferable(db, inferable)
     }
 }

-impl<'a, 'db> InferableTypeVars<'a, 'db> {
-    pub(crate) fn merge(&'a self, other: &'a InferableTypeVars<'a, 'db>) -> Self {
+#[salsa::tracked]
+impl<'db> InferableTypeVars<'db> {
+    #[salsa::tracked(heap_size=ruff_memory_usage::heap_size)]
+    pub(crate) fn merge(self, db: &'db dyn Db, other: Self) -> Self {
         match (self, other) {
-            (InferableTypeVars::None, other) | (other, InferableTypeVars::None) => *other,
-            _ => InferableTypeVars::Two(self, other),
+            (InferableTypeVars::None, other) | (other, InferableTypeVars::None) => other,
+            (InferableTypeVars::Some(self_inner), InferableTypeVars::Some(other_inner)) => {
+                let merged = self_inner.inferable(db) | other_inner.inferable(db);
+                Self::Some(InferableTypeVarsInner::new_internal(db, merged))
+            }
         }
     }

     // This is not an IntoIterator implementation because I have no desire to try to name the
     // iterator type.
-    pub(crate) fn iter(self) -> impl Iterator<Item = BoundTypeVarIdentity<'db>> {
+    pub(crate) fn iter(
+        self,
+        db: &'db dyn Db,
+    ) -> impl Iterator<Item = BoundTypeVarIdentity<'db>> + 'db {
         match self {
-            InferableTypeVars::None => Either::Left(Either::Left(std::iter::empty())),
-            InferableTypeVars::One(typevars) => Either::Right(typevars.iter().copied()),
-            InferableTypeVars::Two(left, right) => {
-                let chained: Box<dyn Iterator<Item = BoundTypeVarIdentity<'db>>> =
-                    Box::new(left.iter().chain(right.iter()));
-                Either::Left(Either::Right(chained))
-            }
+            InferableTypeVars::None => Either::Left(std::iter::empty()),
+            InferableTypeVars::Some(inner) => Either::Right(inner.inferable(db).iter().copied()),
         }
     }

     // Keep this around for debugging purposes
     #[expect(dead_code)]
     pub(crate) fn display(&self, db: &'db dyn Db) -> impl Display {
-        fn find_typevars<'db>(
-            result: &mut FxHashSet<BoundTypeVarIdentity<'db>>,
-            inferable: &InferableTypeVars<'_, 'db>,
-        ) {
-            match inferable {
-                InferableTypeVars::None => {}
-                InferableTypeVars::One(typevars) => result.extend(typevars.iter().copied()),
-                InferableTypeVars::Two(left, right) => {
-                    find_typevars(result, left);
-                    find_typevars(result, right);
-                }
-            }
-        }
-
-        let mut typevars = FxHashSet::default();
-        find_typevars(&mut typevars, self);
         format!(
             "[{}]",
-            typevars
-                .into_iter()
+            self.iter(db)
                 .map(|identity| identity.display(db))
                 .format(", ")
         )
@@ -391,10 +387,10 @@ impl<'db> GenericContext<'db> {
     /// In this example, `method`'s generic context binds `Self` and `T`, but its inferable set
     /// also includes `A@C`. This is needed because at each call site, we need to infer the
     /// specialized class instance type whose method is being invoked.
-    pub(crate) fn inferable_typevars(self, db: &'db dyn Db) -> InferableTypeVars<'db, 'db> {
+    pub(crate) fn inferable_typevars(self, db: &'db dyn Db) -> InferableTypeVars<'db> {
         #[derive(Default)]
         struct CollectTypeVars<'db> {
-            typevars: RefCell<FxHashSet<BoundTypeVarIdentity<'db>>>,
+            typevars: RefCell<FxOrderSet<BoundTypeVarIdentity<'db>>>,
             recursion_guard: TypeCollector<'db>,
         }

@@ -423,25 +419,21 @@ impl<'db> GenericContext<'db> {
         }

         #[salsa::tracked(
-            returns(ref),
-            cycle_initial=|_, _, _| FxHashSet::default(),
+            cycle_initial=|_, _, _| InferableTypeVars::None,
             heap_size=ruff_memory_usage::heap_size,
         )]
         fn inferable_typevars_inner<'db>(
             db: &'db dyn Db,
             generic_context: GenericContext<'db>,
-        ) -> FxHashSet<BoundTypeVarIdentity<'db>> {
+        ) -> InferableTypeVars<'db> {
             let visitor = CollectTypeVars::default();
             for bound_typevar in generic_context.variables(db) {
                 visitor.visit_bound_type_var_type(db, bound_typevar);
             }
-            visitor.typevars.into_inner()
+            InferableTypeVars::from_typevars(db, visitor.typevars.into_inner())
         }

-        // This ensures that salsa caches the FxHashSet, not the InferableTypeVars that wraps it.
-        // (That way InferableTypeVars can contain references, and doesn't need to impl
-        // salsa::Update.)
-        InferableTypeVars::One(inferable_typevars_inner(db, self))
+        inferable_typevars_inner(db, self)
     }

     pub(crate) fn variables(
@@ -1273,7 +1265,7 @@ impl<'db> Specialization<'db> {
         db: &'db dyn Db,
         other: Self,
         constraints: &'c ConstraintSetBuilder<'db>,
-        inferable: InferableTypeVars<'_, 'db>,
+        inferable: InferableTypeVars<'db>,
     ) -> ConstraintSet<'db, 'c> {
         let relation_visitor = HasRelationToVisitor::default(constraints);
         let disjointness_visitor = IsDisjointVisitor::default(constraints);
@@ -1628,7 +1620,7 @@ impl<'db> ApplySpecialization<'_, 'db> {
 pub(crate) struct SpecializationBuilder<'db, 'c> {
     db: &'db dyn Db,
     constraints: &'c ConstraintSetBuilder<'db>,
-    inferable: InferableTypeVars<'db, 'db>,
+    inferable: InferableTypeVars<'db>,
     types: FxHashMap<BoundTypeVarIdentity<'db>, Type<'db>>,
 }

@@ -1640,7 +1632,7 @@ impl<'db, 'c> SpecializationBuilder<'db, 'c> {
     pub(crate) fn new(
         db: &'db dyn Db,
         constraints: &'c ConstraintSetBuilder<'db>,
-        inferable: InferableTypeVars<'db, 'db>,
+        inferable: InferableTypeVars<'db>,
     ) -> Self {
         Self {
             db,
diff --git a/crates/ty_python_semantic/src/types/relation.rs b/crates/ty_python_semantic/src/types/relation.rs
index 58dfb5e087909a..565a5926378651 100644
--- a/crates/ty_python_semantic/src/types/relation.rs
+++ b/crates/ty_python_semantic/src/types/relation.rs
@@ -302,7 +302,7 @@ impl<'db> Type<'db> {
         db: &'db dyn Db,
         target: Type<'db>,
         constraints: &'c ConstraintSetBuilder<'db>,
-        inferable: InferableTypeVars<'_, 'db>,
+        inferable: InferableTypeVars<'db>,
     ) -> ConstraintSet<'db, 'c> {
         self.has_relation_to(db, target, constraints, inferable, TypeRelation::Subtyping)
     }
@@ -317,7 +317,7 @@ impl<'db> Type<'db> {
         target: Type<'db>,
         assuming: ConstraintSet<'db, 'c>,
         constraints: &'c ConstraintSetBuilder<'db>,
-        inferable: InferableTypeVars<'_, 'db>,
+        inferable: InferableTypeVars<'db>,
     ) -> ConstraintSet<'db, 'c> {
         let checker = TypeRelationChecker {
             constraints,
@@ -355,7 +355,7 @@ impl<'db> Type<'db> {
         db: &'db dyn Db,
         target: Type<'db>,
         constraints: &'c ConstraintSetBuilder<'db>,
-        inferable: InferableTypeVars<'_, 'db>,
+        inferable: InferableTypeVars<'db>,
     ) -> ConstraintSet<'db, 'c> {
         self.has_relation_to(
             db,
@@ -414,7 +414,7 @@ impl<'db> Type<'db> {
         db: &'db dyn Db,
         target: Type<'db>,
         constraints: &'c ConstraintSetBuilder<'db>,
-        inferable: InferableTypeVars<'_, 'db>,
+        inferable: InferableTypeVars<'db>,
         relation: TypeRelation,
     ) -> ConstraintSet<'db, 'c> {
         let checker = TypeRelationChecker {
@@ -486,7 +486,7 @@ impl<'db> Type<'db> {
         db: &'db dyn Db,
         other: Type<'db>,
         constraints: &'c ConstraintSetBuilder<'db>,
-        inferable: InferableTypeVars<'_, 'db>,
+        inferable: InferableTypeVars<'db>,
     ) -> ConstraintSet<'db, 'c> {
         let checker = DisjointnessChecker {
             constraints,
@@ -524,7 +524,7 @@ impl<'db, 'c> IsDisjointVisitor<'db, 'c> {
 #[derive(Clone)]
 pub(super) struct TypeRelationChecker<'a, 'c, 'db> {
     pub(super) constraints: &'c ConstraintSetBuilder<'db>,
-    pub(super) inferable: InferableTypeVars<'a, 'db>,
+    pub(super) inferable: InferableTypeVars<'db>,
     pub(super) relation: TypeRelation,
     given: ConstraintSet<'db, 'c>,

@@ -541,7 +541,7 @@ pub(super) struct TypeRelationChecker<'a, 'c, 'db> {
 impl<'a, 'c, 'db> TypeRelationChecker<'a, 'c, 'db> {
     pub(super) fn subtyping(
         constraints: &'c ConstraintSetBuilder<'db>,
-        inferable: InferableTypeVars<'a, 'db>,
+        inferable: InferableTypeVars<'db>,
         relation_visitor: &'a HasRelationToVisitor<'db, 'c>,
         disjointness_visitor: &'a IsDisjointVisitor<'db, 'c>,
     ) -> Self {
@@ -570,7 +570,7 @@ impl<'a, 'c, 'db> TypeRelationChecker<'a, 'c, 'db> {
         }
     }

-    pub(super) fn with_inferable_typevars(&self, inferable: InferableTypeVars<'a, 'db>) -> Self {
+    pub(super) fn with_inferable_typevars(&self, inferable: InferableTypeVars<'db>) -> Self {
         Self {
             inferable,
             ..self.clone()
@@ -1576,7 +1576,7 @@ impl<'c, 'db> EquivalenceChecker<'_, 'c, 'db> {

 pub(super) struct DisjointnessChecker<'a, 'c, 'db> {
     pub(super) constraints: &'c ConstraintSetBuilder<'db>,
-    pub(super) inferable: InferableTypeVars<'a, 'db>,
+    pub(super) inferable: InferableTypeVars<'db>,
     given: ConstraintSet<'db, 'c>,

     // N.B. these fields are private to reduce the risk of
@@ -1592,7 +1592,7 @@ pub(super) struct DisjointnessChecker<'a, 'c, 'db> {
 impl<'a, 'c, 'db> DisjointnessChecker<'a, 'c, 'db> {
     pub(super) fn new(
         constraints: &'c ConstraintSetBuilder<'db>,
-        inferable: InferableTypeVars<'a, 'db>,
+        inferable: InferableTypeVars<'db>,
         relation_visitor: &'a HasRelationToVisitor<'db, 'c>,
         disjointness_visitor: &'a IsDisjointVisitor<'db, 'c>,
     ) -> Self {
diff --git a/crates/ty_python_semantic/src/types/signatures.rs b/crates/ty_python_semantic/src/types/signatures.rs
index 66fbde4600fb94..d5b40ae6a569aa 100644
--- a/crates/ty_python_semantic/src/types/signatures.rs
+++ b/crates/ty_python_semantic/src/types/signatures.rs
@@ -715,7 +715,7 @@ impl<'db> Signature<'db> {
         }
     }

-    fn inferable_typevars(&self, db: &'db dyn Db) -> InferableTypeVars<'db, 'db> {
+    fn inferable_typevars(&self, db: &'db dyn Db) -> InferableTypeVars<'db> {
         match self.generic_context {
             Some(generic_context) => generic_context.inferable_typevars(db),
             None => InferableTypeVars::None,
@@ -1093,8 +1093,8 @@ impl<'c, 'db> TypeRelationChecker<'_, 'c, 'db> {
         //         return t
         let source_inferable = source.inferable_typevars(db);
         let target_inferable = target.inferable_typevars(db);
-        let inferable = self.inferable.merge(&source_inferable);
-        let inferable = inferable.merge(&target_inferable);
+        let inferable = source_inferable.merge(db, target_inferable);
+        let inferable = self.inferable.merge(db, inferable);

         // `inner` will create a constraint set that references these newly inferable typevars.
         let checker = self.with_inferable_typevars(inferable);
@@ -1107,7 +1107,7 @@ impl<'c, 'db> TypeRelationChecker<'_, 'c, 'db> {
         when.reduce_inferable(
             db,
             self.constraints,
-            source_inferable.iter().chain(target_inferable.iter()),
+            source_inferable.iter(db).chain(target_inferable.iter(db)),
         )
     }

PATCH
