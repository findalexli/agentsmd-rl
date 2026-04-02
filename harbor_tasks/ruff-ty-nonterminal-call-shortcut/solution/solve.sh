#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Check if already applied (look for the new struct in predicate.rs)
if grep -q 'CallableAndCallExpr' crates/ty_python_semantic/src/semantic_index/predicate.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ruff_benchmark/benches/ty.rs b/crates/ruff_benchmark/benches/ty.rs
index edcfe4a6e0d7a..dbd06f9f33246 100644
--- a/crates/ruff_benchmark/benches/ty.rs
+++ b/crates/ruff_benchmark/benches/ty.rs
@@ -812,6 +812,28 @@ fn benchmark_large_isinstance_narrowing(criterion: &mut Criterion) {
     });
 }

+/// Regression benchmark for <https://github.com/astral-sh/ty/issues/3120>.
+///
+/// Sequential (`TypeIs`) narrowing on a large `Literal` union, combined with
+/// `match`/`assert_never` on another `Literal` union, caused a combinatorial
+/// explosion when the `PredicateNode::IsNonTerminalCall` optimization was
+/// removed.
+fn benchmark_typeis_narrowing(criterion: &mut Criterion) {
+    setup_rayon();
+
+    criterion.bench_function("ty_micro[typeis_narrowing]", |b| {
+        b.iter_batched_ref(
+            || setup_micro_case(include_str!("../resources/typeis_narrowing.py")),
+            |case| {
+                let Case { db, .. } = case;
+                let result = db.check();
+                assert_eq!(result.len(), 0);
+            },
+            BatchSize::SmallInput,
+        );
+    });
+}
+
 fn benchmark_pandas_tdd(criterion: &mut Criterion) {
     setup_rayon();

@@ -1009,6 +1031,7 @@ criterion_group!(
     benchmark_very_large_tuple,
     benchmark_large_union_narrowing,
     benchmark_large_isinstance_narrowing,
+    benchmark_typeis_narrowing,
     benchmark_pandas_tdd,
 );
 criterion_group!(project, anyio, attrs, hydra, datetype);
diff --git a/crates/ruff_benchmark/resources/typeis_narrowing.py b/crates/ruff_benchmark/resources/typeis_narrowing.py
new file mode 100644
index 0000000000000..dc8cd8cb820d1
--- /dev/null
+++ b/crates/ruff_benchmark/resources/typeis_narrowing.py
@@ -0,0 +1,297 @@
+"""Regression test for https://github.com/astral-sh/ty/issues/3120"""
+
+from typing import Any, Literal, assert_never
+from typing_extensions import TypeIs
+
+Kind = Literal[
+    "alpha_one",
+    "alpha_two",
+    "alpha_three",
+    "alpha_four",
+    "bravo_one",
+    "bravo_two",
+    "bravo_three",
+    "bravo_four",
+    "bravo_five",
+    "bravo_six",
+    "bravo_seven",
+    "bravo_eight",
+    "bravo_nine",
+    "bravo_ten",
+    "bravo_eleven",
+    "bravo_twelve",
+    "charlie_one",
+    "charlie_two",
+    "charlie_three",
+    "charlie_four",
+    "charlie_five",
+    "charlie_six",
+    "charlie_seven",
+    "charlie_eight",
+    "charlie_nine",
+    "charlie_ten",
+    "charlie_eleven",
+    "charlie_twelve",
+    "delta_one",
+    "delta_two",
+    "delta_three",
+    "delta_four",
+    "delta_five",
+    "delta_six",
+    "delta_seven",
+    "delta_eight",
+    "delta_nine",
+    "delta_ten",
+    "delta_eleven",
+    "delta_twelve",
+    "delta_thirteen",
+    "delta_fourteen",
+    "echo_one",
+    "echo_two",
+    "echo_three",
+    "echo_four",
+    "echo_five",
+    "echo_six",
+    "echo_seven",
+    "echo_eight",
+    "echo_nine",
+    "echo_ten",
+    "echo_eleven",
+    "echo_twelve",
+    "echo_thirteen",
+    "echo_fourteen",
+    "foxtrot_one",
+    "foxtrot_two",
+    "foxtrot_three",
+    "foxtrot_four",
+    "foxtrot_five",
+    "foxtrot_six",
+    "foxtrot_seven",
+    "foxtrot_eight",
+    "foxtrot_nine",
+    "foxtrot_ten",
+    "foxtrot_eleven",
+    "foxtrot_twelve",
+    "foxtrot_thirteen",
+    "foxtrot_fourteen",
+    "foxtrot_fifteen",
+    "foxtrot_sixteen",
+    "golf_one",
+    "golf_two",
+    "golf_three",
+    "golf_four",
+    "golf_five",
+    "golf_six",
+    "golf_seven",
+    "golf_eight",
+    "hotel_one",
+    "hotel_two",
+    "hotel_three",
+    "hotel_four",
+    "hotel_five",
+]
+
+CHARLIE = Literal[
+    "charlie_one",
+    "charlie_two",
+    "charlie_three",
+    "charlie_four",
+    "charlie_five",
+    "charlie_six",
+    "charlie_seven",
+]
+DELTA = Literal[
+    "delta_one", "delta_two", "delta_three", "delta_four", "delta_five", "delta_six"
+]
+ECHO = Literal[
+    "echo_one", "echo_two", "echo_three", "echo_four", "echo_five", "echo_six"
+]
+FOXTROT = Literal["foxtrot_one", "foxtrot_two"]
+CHARLIE_WIDE = Literal[
+    "charlie_one",
+    "charlie_two",
+    "charlie_three",
+    "charlie_four",
+    "charlie_five",
+    "charlie_six",
+    "charlie_seven",
+    "charlie_eight",
+    "charlie_nine",
+    "charlie_ten",
+    "charlie_eleven",
+    "charlie_twelve",
+]
+ALPHA = Literal[
+    "alpha_one",
+    "alpha_two",
+    "alpha_three",
+    "alpha_four",
+    "bravo_one",
+    "bravo_two",
+    "bravo_three",
+    "bravo_four",
+    "bravo_five",
+    "bravo_six",
+    "bravo_seven",
+    "bravo_eight",
+    "bravo_nine",
+    "bravo_ten",
+    "bravo_eleven",
+    "bravo_twelve",
+    "delta_seven",
+    "delta_eight",
+    "echo_seven",
+    "echo_eight",
+]
+GOLF = Literal[
+    "golf_one",
+    "golf_two",
+    "golf_three",
+    "golf_four",
+    "golf_five",
+    "golf_six",
+    "golf_seven",
+    "golf_eight",
+]
+
+
+def is_charlie(t: Kind) -> TypeIs[CHARLIE]:
+    return t.startswith("charlie")
+
+
+def is_delta(t: Kind) -> TypeIs[DELTA]:
+    return t.startswith("delta")
+
+
+def is_echo(t: Kind) -> TypeIs[ECHO]:
+    return t.startswith("echo")
+
+
+def is_foxtrot(t: Kind) -> TypeIs[FOXTROT]:
+    return t.startswith("foxtrot")
+
+
+def is_charlie_wide(t: Kind) -> TypeIs[CHARLIE_WIDE]:
+    return t.startswith("charlie")
+
+
+def is_alpha(t: Kind) -> TypeIs[ALPHA]:
+    return t.startswith("alpha") or t.startswith("bravo")
+
+
+def is_golf(t: Kind) -> TypeIs[GOLF]:
+    return t.startswith("golf")
+
+
+Action = Literal[
+    "act_one",
+    "act_two",
+    "act_three",
+    "act_four",
+    "act_five",
+    "act_six",
+    "act_seven",
+    "act_eight",
+    "act_nine",
+    "act_ten",
+    "act_eleven",
+    "act_twelve",
+    "act_thirteen",
+    "act_fourteen",
+    "act_fifteen",
+    "act_sixteen",
+    "act_seventeen",
+    "act_eighteen",
+    "act_nineteen",
+    "act_twenty",
+]
+
+
+def process(kind: Kind, action: Action | None, params: dict[str, Any]) -> str:
+    if is_golf(kind):
+        raise ValueError
+    if is_alpha(kind) and action not in ["act_two", "act_five"]:
+        raise ValueError
+
+    if action is None:
+        if is_foxtrot(kind):
+            return "foxtrot"
+        if is_echo(kind):
+            return "echo"
+        if is_delta(kind):
+            return "delta"
+        if is_charlie(kind):
+            return "charlie"
+        if kind == "bravo_one":
+            action = "act_one"
+        elif kind == "bravo_two":
+            action = "act_eight"
+        elif kind == "bravo_three":
+            action = "act_three"
+        elif kind == "alpha_one":
+            action = "act_six"
+        else:
+            action = "act_one"
+    else:
+        match action:
+            case "act_three":
+                if kind != "bravo_three":
+                    raise ValueError
+            case "act_one" | "act_two":
+                if kind not in ("alpha_one", "alpha_two", "alpha_three"):
+                    raise ValueError
+            case "act_four":
+                if kind not in ("alpha_one", "alpha_two", "alpha_three"):
+                    raise ValueError
+            case "act_five":
+                if kind not in ("alpha_one", "alpha_two", "alpha_three"):
+                    raise ValueError
+            case "act_six":
+                if kind not in ("alpha_one", "alpha_two", "alpha_three", "alpha_four"):
+                    raise ValueError
+            case "act_seven":
+                if kind != "bravo_one":
+                    raise ValueError
+            case "act_eight":
+                if kind != "bravo_two":
+                    raise ValueError
+            case "act_nine" | "act_ten":
+                if not is_charlie(kind):
+                    raise ValueError
+            case "act_eleven" | "act_twelve":
+                if not is_delta(kind):
+                    raise ValueError
+                if params.get("version") == "2.1":
+                    if kind in ("delta_nine", "delta_ten"):
+                        if action == "act_eleven":
+                            action = "act_thirteen"
+                        elif action == "act_twelve":
+                            action = "act_fourteen"
+                        else:
+                            assert_never(action)
+                    else:
+                        raise ValueError
+            case "act_thirteen" | "act_fourteen":
+                if not is_delta(kind):
+                    raise ValueError
+            case "act_fifteen" | "act_sixteen":
+                if not is_echo(kind):
+                    raise ValueError
+            case "act_seventeen":
+                if not is_charlie(kind):
+                    raise ValueError
+            case "act_eighteen":
+                if not is_delta(kind):
+                    raise ValueError
+            case "act_nineteen":
+                if not is_echo(kind):
+                    raise ValueError
+            case "act_twenty":
+                if not is_foxtrot(kind):
+                    raise ValueError
+            case _ as never:
+                assert_never(never)
+        if is_charlie_wide(kind):
+            pass
+
+    return kind
diff --git a/crates/ty_python_semantic/src/semantic_index/builder.rs b/crates/ty_python_semantic/src/semantic_index/builder.rs
index 17d90bb9ddedb..c05d52b0c7241 100644
--- a/crates/ty_python_semantic/src/semantic_index/builder.rs
+++ b/crates/ty_python_semantic/src/semantic_index/builder.rs
@@ -35,8 +35,8 @@ use crate::semantic_index::expression::{Expression, ExpressionKind};
 use crate::semantic_index::member::MemberExprBuilder;
 use crate::semantic_index::place::{PlaceExpr, PlaceTableBuilder, ScopedPlaceId};
 use crate::semantic_index::predicate::{
-    ClassPatternKind, PatternPredicate, PatternPredicateKind, Predicate, PredicateNode,
-    PredicateOrLiteral, ScopedPredicateId, StarImportPlaceholderPredicate,
+    CallableAndCallExpr, ClassPatternKind, PatternPredicate, PatternPredicateKind, Predicate,
+    PredicateNode, PredicateOrLiteral, ScopedPredicateId, StarImportPlaceholderPredicate,
 };
 use crate::semantic_index::re_exports::exported_names;
 use crate::semantic_index::reachability_constraints::{
@@ -2887,29 +2887,44 @@ impl<'ast> Visitor<'ast> for SemanticIndexBuilder<'_, 'ast> {
                 // We also only add these inside function scopes, since considering module-level
                 // constraints can affect the type of imported symbols, leading to a lot more
                 // work in third-party code.
-                let is_call = match value.as_ref() {
-                    ast::Expr::Call(_) => true,
-                    ast::Expr::Await(ast::ExprAwait { value: inner, .. }) => inner.is_call_expr(),
-                    _ => false,
+                let call_info = match value.as_ref() {
+                    ast::Expr::Call(ast::ExprCall { func, .. }) => {
+                        Some((func.as_ref(), value.as_ref(), false))
+                    }
+                    ast::Expr::Await(ast::ExprAwait { value: inner, .. }) => match inner.as_ref() {
+                        ast::Expr::Call(ast::ExprCall { func, .. }) => {
+                            Some((func.as_ref(), value.as_ref(), true))
+                        }
+                        _ => None,
+                    },
+                    _ => None,
                 };

-                if is_call && !self.source_type.is_stub() && self.in_function_scope() {
-                    let call_expr = self.add_standalone_expression(value.as_ref());
+                if let Some((func, expr, is_await)) = call_info {
+                    if !self.source_type.is_stub() && self.in_function_scope() {
+                        let callable = self.add_standalone_expression(func);
+                        let call_expr = self.add_standalone_expression(expr);
+
+                        let predicate = Predicate {
+                            node: PredicateNode::IsNonTerminalCall(CallableAndCallExpr {
+                                callable,
+                                call_expr,
+                                is_await,
+                            }),
+                            is_positive: true,
+                        };
+                        let constraint = self.record_reachability_constraint(
+                            PredicateOrLiteral::Predicate(predicate),
+                        );

-                    let predicate = Predicate {
-                        node: PredicateNode::IsNonTerminalCall(call_expr),
-                        is_positive: true,
-                    };
-                    let constraint = self
-                        .record_reachability_constraint(PredicateOrLiteral::Predicate(predicate));
-
-                    // Also gate narrowing by this constraint: if the call returns
-                    // `Never`, any narrowing in the current branch should be
-                    // invalidated (since this path is unreachable). This enables
-                    // narrowing to be preserved after if-statements where one branch
-                    // calls a `NoReturn` function like `sys.exit()`.
-                    self.current_use_def_map_mut()
-                        .record_narrowing_constraint_for_all_places(constraint);
+                        // Also gate narrowing by this constraint: if the call returns
+                        // `Never`, any narrowing in the current branch should be
+                        // invalidated (since this path is unreachable). This enables
+                        // narrowing to be preserved after if-statements where one branch
+                        // calls a `NoReturn` function like `sys.exit()`.
+                        self.current_use_def_map_mut()
+                            .record_narrowing_constraint_for_all_places(constraint);
+                    }
                 }
             }
             _ => {
diff --git a/crates/ty_python_semantic/src/semantic_index/predicate.rs b/crates/ty_python_semantic/src/semantic_index/predicate.rs
index 97481c909a660..70e3fffb3590a 100644
--- a/crates/ty_python_semantic/src/semantic_index/predicate.rs
+++ b/crates/ty_python_semantic/src/semantic_index/predicate.rs
@@ -98,6 +98,16 @@ impl PredicateOrLiteral<'_> {
     }
 }

+#[derive(Clone, Copy, Debug, Hash, PartialEq, Eq, salsa::Update, get_size2::GetSize)]
+pub(crate) struct CallableAndCallExpr<'db> {
+    pub(crate) callable: Expression<'db>,
+    pub(crate) call_expr: Expression<'db>,
+    /// Whether the call is wrapped in an `await` expression. If `true`, `call_expr` refers to the
+    /// `await` expression rather than the call itself. This is used to detect terminal `await`s of
+    /// async functions that return `Never`.
+    pub(crate) is_await: bool,
+}
+
 #[derive(Clone, Copy, Debug, Hash, PartialEq, Eq, salsa::Update, get_size2::GetSize)]
 pub(crate) enum PredicateNode<'db> {
     Expression(Expression<'db>),
@@ -118,7 +128,7 @@ pub(crate) enum PredicateNode<'db> {
     /// [`crate::types::Truthiness::Ambiguous`], even if the return type of the
     /// call is `Unknown`/`Any`, because that would result in too many false
     /// positives.
-    IsNonTerminalCall(Expression<'db>),
+    IsNonTerminalCall(CallableAndCallExpr<'db>),
     Pattern(PatternPredicate<'db>),
     StarImportPlaceholder(StarImportPlaceholderPredicate<'db>),
 }
diff --git a/crates/ty_python_semantic/src/semantic_index/reachability_constraints.rs b/crates/ty_python_semantic/src/semantic_index/reachability_constraints.rs
index b9c38181a52c9..2d096a3821f81 100644
--- a/crates/ty_python_semantic/src/semantic_index/reachability_constraints.rs
+++ b/crates/ty_python_semantic/src/semantic_index/reachability_constraints.rs
@@ -205,11 +205,12 @@ use crate::rank::RankBitBox;
 use crate::semantic_index::place::ScopedPlaceId;
 use crate::semantic_index::place_table;
 use crate::semantic_index::predicate::{
-    PatternPredicate, PatternPredicateKind, Predicate, PredicateNode, Predicates, ScopedPredicateId,
+    CallableAndCallExpr, PatternPredicate, PatternPredicateKind, Predicate, PredicateNode,
+    Predicates, ScopedPredicateId,
 };
 use crate::types::{
-    IntersectionBuilder, KnownClass, NarrowingConstraint, Truthiness, Type, TypeContext,
-    UnionBuilder, UnionType, infer_expression_type, infer_narrowing_constraint,
+    CallableTypes, IntersectionBuilder, KnownClass, NarrowingConstraint, Truthiness, Type,
+    TypeContext, UnionBuilder, UnionType, infer_expression_type, infer_narrowing_constraint,
 };

 /// A ternary formula that defines under what conditions a binding is visible. (A ternary formula
@@ -1089,12 +1090,62 @@ impl ReachabilityConstraints {
                     .bool(db)
                     .negate_if(!predicate.is_positive)
             }
-            PredicateNode::IsNonTerminalCall(call_expr) => {
-                let call_expr_ty = infer_expression_type(db, call_expr, TypeContext::default());
-                if call_expr_ty.is_equivalent_to(db, Type::Never) {
-                    Truthiness::AlwaysFalse
+            PredicateNode::IsNonTerminalCall(CallableAndCallExpr {
+                callable,
+                call_expr,
+                is_await,
+            }) => {
+                // We first infer just the type of the callable. In the most likely case that the
+                // function is not marked with `NoReturn`, or that it always returns `NoReturn`,
+                // doing so allows us to avoid the more expensive work of inferring the entire call
+                // expression (which could involve inferring argument types to possibly run the overload
+                // selection algorithm).
+                // Avoiding this on the happy-path is important because these constraints can be
+                // very large in number, since we add them on all statement level function calls.
+                let ty = infer_expression_type(db, callable, TypeContext::default());
+
+                // Short-circuit for well known types that are known not to return `Never` when called.
+                // Without the short-circuit, we've seen that threads keep blocking each other
+                // because they all try to acquire Salsa's `CallableType` lock that ensures each type
+                // is only interned once. The lock is so heavily congested because there are only
+                // very few dynamic types, in which case Salsa's sharding the locks by value
+                // doesn't help much.
+                // See <https://github.com/astral-sh/ty/issues/968>.
+                if matches!(ty, Type::Dynamic(_)) {
+                    return Truthiness::AlwaysTrue.negate_if(!predicate.is_positive);
+                }
+
+                let overloads_iterator = if let Some(callable) = ty
+                    .try_upcast_to_callable(db)
+                    .and_then(CallableTypes::exactly_one)
+                {
+                    callable.signatures(db).overloads.iter()
                 } else {
+                    return Truthiness::AlwaysTrue.negate_if(!predicate.is_positive);
+                };
+
+                let mut no_overloads_return_never = true;
+                let mut all_overloads_return_never = true;
+                let mut any_overload_is_generic = false;
+
+                for overload in overloads_iterator {
+                    let returns_never = overload.return_ty.is_equivalent_to(db, Type::Never);
+                    no_overloads_return_never &= !returns_never;
+                    all_overloads_return_never &= returns_never;
+                    any_overload_is_generic |= overload.return_ty.has_typevar(db);
+                }
+
+                if no_overloads_return_never && !any_overload_is_generic && !is_await {
                     Truthiness::AlwaysTrue
+                } else if all_overloads_return_never {
+                    Truthiness::AlwaysFalse
+                } else {
+                    let call_expr_ty = infer_expression_type(db, call_expr, TypeContext::default());
+                    if call_expr_ty.is_equivalent_to(db, Type::Never) {
+                        Truthiness::AlwaysFalse
+                    } else {
+                        Truthiness::AlwaysTrue
+                    }
                 }
                 .negate_if(!predicate.is_positive)
             }
diff --git a/crates/ty_python_semantic/src/types/narrow.rs b/crates/ty_python_semantic/src/types/narrow.rs
index 26dc13dd80193..d73aeee6ba7cc 100644
--- a/crates/ty_python_semantic/src/types/narrow.rs
+++ b/crates/ty_python_semantic/src/types/narrow.rs
@@ -3,7 +3,8 @@ use crate::semantic_index::expression::Expression;
 use crate::semantic_index::place::{PlaceExpr, PlaceTable, PlaceTableBuilder, ScopedPlaceId};
 use crate::semantic_index::place_table;
 use crate::semantic_index::predicate::{
-    ClassPatternKind, PatternPredicate, PatternPredicateKind, Predicate, PredicateNode,
+    CallableAndCallExpr, ClassPatternKind, PatternPredicate, PatternPredicateKind, Predicate,
+    PredicateNode,
 };
 use crate::semantic_index::scope::ScopeId;
 use crate::subscript::PyIndex;
@@ -761,7 +762,9 @@ impl<'db, 'ast> NarrowingConstraintsBuilder<'db, 'ast> {
         match self.predicate {
             PredicateNode::Expression(expression) => expression.scope(self.db),
             PredicateNode::Pattern(pattern) => pattern.scope(self.db),
-            PredicateNode::IsNonTerminalCall(call_expr) => call_expr.scope(self.db),
+            PredicateNode::IsNonTerminalCall(CallableAndCallExpr { callable, .. }) => {
+                callable.scope(self.db)
+            }
             PredicateNode::StarImportPlaceholder(definition) => definition.scope(self.db),
         }
     }

PATCH

echo "Patch applied successfully."
