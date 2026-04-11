#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prql

# Idempotent: skip if already applied
if grep -q 'When we have DISTINCT ON, we must have at least a wildcard' prqlc/prqlc/src/sql/gen_query.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index 2002061084db..1fbdffa282b8 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -47,6 +47,36 @@ insta::assert_snapshot!(result, @"");

 The test commands above with `--accept` will fill in the result automatically.

+### Test Strategy
+
+**Prefer small inline `insta` snapshot tests** over full integration tests:
+
+- **Use inline tests** for most bug fixes and small features
+  - Add `#[test]` functions in a `#[cfg(test)]` module at the end of the file
+  - Use `insta::assert_snapshot!` for compact, readable test assertions
+  - Fast to run, easy to review in PRs
+
+- **Use integration tests** (`prqlc/tests/integration/queries/*.prql`) only
+  when:
+  - Developing large, complex features that need comprehensive testing
+  - Testing end-to-end behavior across multiple compilation stages
+  - The test requires external resources or multi-file scenarios
+
+Example of a good inline test:
+
+```rust
+#[cfg(test)]
+mod test {
+    use insta::assert_snapshot;
+
+    #[test]
+    fn test_my_feature() {
+        let query = "from employees | filter country == 'USA'";
+        assert_snapshot!(crate::tests::compile(query).unwrap(), @"");
+    }
+}
+```
+
 ## Running the CLI

 For viewing `prqlc` output, for any stage of the compilation process:
diff --git a/prqlc/prqlc/src/sql/gen_query.rs b/prqlc/prqlc/src/sql/gen_query.rs
index a2728afb0176..d26636caa596 100644
--- a/prqlc/prqlc/src/sql/gen_query.rs
+++ b/prqlc/prqlc/src/sql/gen_query.rs
@@ -110,7 +110,7 @@ fn translate_select_pipeline(
         .exactly_one()
         .unwrap();
     let projection = translate_wildcards(&ctx.anchor, projection);
-    let projection = translate_select_items(projection.0, projection.1, ctx)?;
+    let mut projection = translate_select_items(projection.0, projection.1, ctx)?;

     let order_by = pipeline.pluck(|t| t.into_sort());
     let takes = pipeline.pluck(|t| t.into_take());
@@ -132,6 +132,24 @@ fn translate_select_pipeline(
         None
     };

+    // When we have DISTINCT ON, we must have at least a wildcard in the projection
+    // (PostgreSQL requires DISTINCT ON to have a non-empty SELECT list)
+    // Replace NULL placeholder with wildcard if present, or add wildcard if empty
+    if matches!(distinct, Some(sql_ast::Distinct::On(_))) {
+        if projection.len() == 1 {
+            if let SelectItem::UnnamedExpr(sql_ast::Expr::Value(ref v)) = projection[0] {
+                if matches!(v.value, sql_ast::Value::Null) {
+                    projection[0] =
+                        SelectItem::Wildcard(sql_ast::WildcardAdditionalOptions::default());
+                }
+            }
+        } else if projection.is_empty() {
+            projection.push(SelectItem::Wildcard(
+                sql_ast::WildcardAdditionalOptions::default(),
+            ));
+        }
+    }
+
     // Split the pipeline into before & after the aggregate
     let (mut before_agg, mut after_agg) =
         pipeline.break_up(|t| matches!(t, Transform::Aggregate { .. } | Transform::Union { .. }));
@@ -800,4 +818,29 @@ mod test {
           _expr_0 > 3
         ");
     }
+
+    #[test]
+    fn test_distinct_on_with_aggregate() {
+        // #5556: DISTINCT ON with aggregate should include wildcard
+        let query = &r#"
+        prql target:sql.postgres
+
+        from t1
+        group {id, name} (take 1)
+        aggregate {c=count this}
+        "#;
+
+        assert_snapshot!(crate::tests::compile(query).unwrap(), @r"
+        WITH table_0 AS (
+          SELECT
+            DISTINCT ON (id, name) *
+          FROM
+            t1
+        )
+        SELECT
+          COUNT(*) AS c
+        FROM
+          table_0
+        ");
+    }
 }
diff --git a/prqlc/prqlc/tests/integration/sql.rs b/prqlc/prqlc/tests/integration/sql.rs
index 4a66f8999d4c..a27087b97ed6 100644
--- a/prqlc/prqlc/tests/integration/sql.rs
+++ b/prqlc/prqlc/tests/integration/sql.rs
@@ -2592,7 +2592,7 @@ fn test_distinct_on_03() {
     "###).unwrap()), @r"
     WITH table_0 AS (
       SELECT
-        DISTINCT ON (col1) NULL
+        DISTINCT ON (col1) *
       FROM
         tab1
     )

PATCH

echo "Patch applied successfully."
