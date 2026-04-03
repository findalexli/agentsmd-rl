#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prql

# Idempotent: skip if already applied
if grep -q 'column references a table not accessible in this context' prqlc/prqlc/src/semantic/lowering.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index 1fbdffa282b8..48045e636c38 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -100,6 +100,14 @@ Run all lints with
 task lint
 ```

+## Error Handling
+
+Never panic on user input or recoverable errors. Use proper error returns:
+
+- ❌ `.unwrap()` on operations that can fail with user input
+- ✅ `?` operator or `return Err(Error::new_simple("message"))`
+- ✅ `.expect("reason")` or `unreachable!()` only for compiler-bug invariants
+
 ## Error Messages

 Error messages should avoid 2nd person (you/your). Use softer modal verbs like
diff --git a/prqlc/prqlc/src/semantic/lowering.rs b/prqlc/prqlc/src/semantic/lowering.rs
index 708b67ee71ed..b9ce5135e931 100644
--- a/prqlc/prqlc/src/semantic/lowering.rs
+++ b/prqlc/prqlc/src/semantic/lowering.rs
@@ -680,7 +680,12 @@ impl Lowerer {
                     columns.push((RelationColumn::Single(name), cid));
                 }
                 LineageColumn::All { input_id, except } => {
-                    let input = lineage.find_input(*input_id).unwrap();
+                    let Some(input) = lineage.find_input(*input_id) else {
+                        return Err(Error::new_simple(
+                            "column references a table not accessible in this context",
+                        )
+                        .push_hint("join is not supported inside group"));
+                    };

                     match &self.node_mapping[&input.id] {
                         LoweredTarget::Compute(_cid) => unreachable!(),
diff --git a/prqlc/prqlc/src/semantic/module.rs b/prqlc/prqlc/src/semantic/module.rs
index a5ba34481413..08fe6fbce490 100644
--- a/prqlc/prqlc/src/semantic/module.rs
+++ b/prqlc/prqlc/src/semantic/module.rs
@@ -255,17 +255,20 @@ impl Module {
             // insert column decl
             match column {
                 LineageColumn::All { input_id, .. } => {
-                    let input = lineage.find_input(*input_id).unwrap();
-
-                    let kind = DeclKind::Infer(Box::new(DeclKind::Column(input.id)));
-                    let declared_at = Some(input.id);
-                    let decl = Decl {
-                        kind,
-                        declared_at,
-                        order: col_index + 1,
-                        ..Default::default()
-                    };
-                    ns.names.insert(NS_INFER.to_string(), decl);
+                    // Input might not exist if lineage references an outer scope
+                    // (e.g., join inside group). This is an error caught during
+                    // lowering - skip here to avoid panic during resolution.
+                    if let Some(input) = lineage.find_input(*input_id) {
+                        let kind = DeclKind::Infer(Box::new(DeclKind::Column(input.id)));
+                        let declared_at = Some(input.id);
+                        let decl = Decl {
+                            kind,
+                            declared_at,
+                            order: col_index + 1,
+                            ..Default::default()
+                        };
+                        ns.names.insert(NS_INFER.to_string(), decl);
+                    }
                 }
                 LineageColumn::Single {
                     name: Some(name),
diff --git a/prqlc/prqlc/src/semantic/resolver/inference.rs b/prqlc/prqlc/src/semantic/resolver/inference.rs
index 336d5ade30b6..f429ac15c3af 100644
--- a/prqlc/prqlc/src/semantic/resolver/inference.rs
+++ b/prqlc/prqlc/src/semantic/resolver/inference.rs
@@ -49,6 +49,9 @@ impl Resolver<'_> {
                     1 => {
                         let (input_id, _) = wildcard_inputs.into_iter().next().unwrap();

+                        // input_id comes from LineageColumn::All in frame.columns.
+                        // Should be valid, but if this panics, see #5280 and lowering.rs
+                        // for the pattern where columns reference out-of-scope inputs.
                         let input = frame.find_input(*input_id).unwrap();
                         let table_ident = input.table.clone();
                         self.infer_table_column(&table_ident, col_name)?;
diff --git a/prqlc/prqlc/src/semantic/resolver/transforms.rs b/prqlc/prqlc/src/semantic/resolver/transforms.rs
index a568d73ace94..3052559e63ee 100644
--- a/prqlc/prqlc/src/semantic/resolver/transforms.rs
+++ b/prqlc/prqlc/src/semantic/resolver/transforms.rs
@@ -876,6 +876,10 @@ impl Lineage {
                                 LineageColumn::Single {
                                     name: Some(name), ..
                                 } => {
+                                    // input_id comes from LineageColumn::All in self.columns,
+                                    // which should reference valid inputs in self.inputs.
+                                    // If this panics, it may indicate a scope issue similar to
+                                    // #5280 (join inside group) - see lowering.rs for the fix pattern.
                                     let input = self.find_input(input_id).unwrap();
                                     let ex_input_name = name.iter().next().unwrap();
                                     if ex_input_name == &input.name {
@@ -891,6 +895,7 @@ impl Lineage {
                                         // The two `All`s match and will erase each other.
                                         // The only remaining columns are those from the first wildcard
                                         // that are not excluded, but are excluded in the second wildcard.
+                                        // Same assumption as above - input_id should be valid here.
                                         let input = self.find_input(input_id).unwrap();
                                         let input_name = input.name.clone();
                                         for remaining in e_e.difference(&except).sorted() {
diff --git a/prqlc/prqlc/src/sql/gen_query.rs b/prqlc/prqlc/src/sql/gen_query.rs
index d26636caa596..0d6dd35ef6ae 100644
--- a/prqlc/prqlc/src/sql/gen_query.rs
+++ b/prqlc/prqlc/src/sql/gen_query.rs
@@ -843,4 +843,22 @@ mod test {
           table_0
         ");
     }
+
+    #[test]
+    fn test_join_with_inaccessible_table() {
+        // issue #5280: join referencing table not accessible in current scope
+        let query = r#"
+        from c = companies
+        join ca = companies_addresses (c.tax_code == ca.company)
+        group c.tax_code (
+          join a = addresses (a.id == ca.address)
+          sort {-ca.created_at}
+          take 2..
+        )
+        sort tax_code
+        "#;
+
+        let err = crate::tests::compile(query).unwrap_err();
+        assert!(err.to_string().contains("not accessible in this context"));
+    }
 }

PATCH

echo "Patch applied successfully."
