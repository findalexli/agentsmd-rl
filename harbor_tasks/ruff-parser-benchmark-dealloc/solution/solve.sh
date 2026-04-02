#!/usr/bin/env bash
set -euo pipefail

cd /repo 2>/dev/null || cd /workspace/ruff

TARGET="crates/ruff_benchmark/benches/parser.rs"

# Idempotency: check if already fixed
if grep -q 'iter_with_large_drop' "$TARGET" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ruff_benchmark/benches/parser.rs b/crates/ruff_benchmark/benches/parser.rs
index d5e086eb505cc..8aa633224a5d1 100644
--- a/crates/ruff_benchmark/benches/parser.rs
+++ b/crates/ruff_benchmark/benches/parser.rs
@@ -6,8 +6,6 @@ use criterion::{
 use ruff_benchmark::{
     LARGE_DATASET, NUMPY_CTYPESLIB, NUMPY_GLOBALS, PYDANTIC_TYPES, TestCase, UNICODE_PYPINYIN,
 };
-use ruff_python_ast::Stmt;
-use ruff_python_ast::statement_visitor::{StatementVisitor, walk_stmt};
 use ruff_python_parser::parse_module;

 #[cfg(target_os = "windows")]
@@ -37,17 +35,6 @@ fn create_test_cases() -> Vec<TestCase> {
     ]
 }

-struct CountVisitor {
-    count: usize,
-}
-
-impl<'a> StatementVisitor<'a> for CountVisitor {
-    fn visit_stmt(&mut self, stmt: &'a Stmt) {
-        walk_stmt(self, stmt);
-        self.count += 1;
-    }
-}
-
 fn benchmark_parser(criterion: &mut Criterion<WallTime>) {
     let test_cases = create_test_cases();
     let mut group = criterion.benchmark_group("parser");
@@ -58,14 +45,8 @@ fn benchmark_parser(criterion: &mut Criterion<WallTime>) {
             BenchmarkId::from_parameter(case.name()),
             &case,
             |b, case| {
-                b.iter(|| {
-                    let parsed = parse_module(case.code())
-                        .expect("Input should be a valid Python code")
-                        .into_suite();
-
-                    let mut visitor = CountVisitor { count: 0 };
-                    visitor.visit_body(&parsed);
-                    visitor.count
+                b.iter_with_large_drop(|| {
+                    parse_module(case.code()).expect("Input should be a valid Python code")
                 });
             },
         );

PATCH

echo "Patch applied successfully."
