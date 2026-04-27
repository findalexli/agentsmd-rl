#!/usr/bin/env bash
# Gold patch for biome PR #9344: fix(noShadow): detect destructured patterns
# in sibling scopes.
set -euo pipefail

cd /workspace/biome

# Idempotency guard: if the distinctive line is already present, the patch
# was applied. Bail successfully.
if grep -q "parent_binding_pattern_declaration" \
   crates/biome_js_analyze/src/lint/nursery/no_shadow.rs; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch to no_shadow.rs. The patch is inlined below as a
# HEREDOC — never fetched from network.
git apply --whitespace=nowarn <<'PATCH'
diff --git a/crates/biome_js_analyze/src/lint/nursery/no_shadow.rs b/crates/biome_js_analyze/src/lint/nursery/no_shadow.rs
index a77051690d6e..c62ce0e2ccd8 100644
--- a/crates/biome_js_analyze/src/lint/nursery/no_shadow.rs
+++ b/crates/biome_js_analyze/src/lint/nursery/no_shadow.rs
@@ -6,8 +6,8 @@ use biome_diagnostics::Severity;
 use biome_js_semantic::{Binding, SemanticModel};
 use biome_js_syntax::{
     JsClassExpression, JsFunctionExpression, JsIdentifierBinding, JsParameterList,
-    JsVariableDeclarator, TsIdentifierBinding, TsPropertySignatureTypeMember,
-    TsTypeAliasDeclaration, TsTypeParameter, TsTypeParameterName,
+    TsIdentifierBinding, TsPropertySignatureTypeMember, TsTypeParameter, TsTypeParameterName,
+    binding_ext::AnyJsBindingDeclaration,
 };
 use biome_rowan::{AstNode, SyntaxNodeCast, TokenText, declare_node_union};
 use biome_rule_options::no_shadow::NoShadowOptions;
@@ -218,9 +218,14 @@ declare_node_union! {
 /// var a = function() { function a() {} };
 /// ```
 fn is_on_initializer(a: &Binding, b: &Binding) -> bool {
-    if let Some(b_initializer_expression) = b
-        .tree()
-        .parent::<JsVariableDeclarator>()
+    let b_declarator = b.tree().declaration().and_then(|decl| {
+        let decl = decl.parent_binding_pattern_declaration().unwrap_or(decl);
+        match decl {
+            AnyJsBindingDeclaration::JsVariableDeclarator(d) => Some(d),
+            _ => None,
+        }
+    });
+    if let Some(b_initializer_expression) = b_declarator
         .and_then(|d| d.initializer())
         .and_then(|i| i.expression().ok())
         && let Some(a_parent) = a.tree().parent::<AnyIdentifiableExpression>()
@@ -232,17 +237,26 @@ fn is_on_initializer(a: &Binding, b: &Binding) -> bool {
     false
 }

-/// Whether the binding is a declaration or not.
+/// Whether the binding is a variable or type alias declaration.
 ///
-/// Examples of declarations:
+/// This also handles bindings inside destructuring patterns, e.g.:
 /// ```js
 /// var a;
 /// let b;
 /// const c;
+/// const { d } = obj;
+/// const [e] = arr;
 /// ```
 fn is_declaration(binding: &Binding) -> bool {
-    binding.tree().parent::<JsVariableDeclarator>().is_some()
-        || binding.tree().parent::<TsTypeAliasDeclaration>().is_some()
+    let Some(decl) = binding.tree().declaration() else {
+        return false;
+    };
+    let decl = decl.parent_binding_pattern_declaration().unwrap_or(decl);
+    matches!(
+        decl,
+        AnyJsBindingDeclaration::JsVariableDeclarator(_)
+            | AnyJsBindingDeclaration::TsTypeAliasDeclaration(_)
+    )
 }

 fn is_inside_type_parameter(binding: &Binding) -> bool {
PATCH

echo "Gold patch applied."
