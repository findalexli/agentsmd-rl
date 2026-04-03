#!/usr/bin/env bash
set -euo pipefail

cd /workspace/biome

# Idempotent: skip if already applied
if grep -q 'parent_binding_pattern_declaration' crates/biome_js_analyze/src/lint/nursery/no_shadow.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.changeset/fix-no-shadow-destructuring.md b/.changeset/fix-no-shadow-destructuring.md
new file mode 100644
index 000000000000..1dd6ddb71934
--- /dev/null
+++ b/.changeset/fix-no-shadow-destructuring.md
@@ -0,0 +1,5 @@
+---
+"@biomejs/biome": patch
+---
+
+Fixed [#6921](https://github.com/biomejs/biome/issues/6921): `noShadow` no longer incorrectly flags destructured variable bindings in sibling scopes as shadowing. Object destructuring, array destructuring, nested patterns, and rest elements are now properly recognized as declarations.
diff --git a/.claude/skills/testing-codegen/SKILL.md b/.claude/skills/testing-codegen/SKILL.md
index 365b2c8779a3..8501a279b2b9 100644
--- a/.claude/skills/testing-codegen/SKILL.md
+++ b/.claude/skills/testing-codegen/SKILL.md
@@ -141,15 +141,31 @@ cargo test
 
 ### Create Test Files
 
-**Single file tests** - Place in `tests/specs/{group}/{rule}/`:
+**Single file tests** - Place in `tests/specs/{group}/{rule}/` under the appropriate `*_analyze` crate for the language:
 
 ```
 tests/specs/nursery/noVar/
-├── invalid.js           # Code that triggers the rule
-├── valid.js             # Code that doesn't trigger
+├── invalid.js           # Code that should generate diagnostics
+├── valid.js             # Code that should not generate diagnostics
 └── options.json         # Optional: rule configuration
 ```
 
+**File and folder naming conventions (IMPORTANT):**
+
+- Use `valid` or `invalid` in file names or parent folder names to indicate expected behaviour.
+- Files/folders with `valid` in the name (but not `invalid`) are expected to produce **no diagnostics**.
+- Files/folders with `invalid` in the name are expected to produce **diagnostics**.
+- When testing cases inside a folder, prefix the name of folder using `valid`/`invalid` e.g. `validResolutionReact`/`invalidResolutionReact`
+
+```
+tests/specs/nursery/noShadow/
+├── invalid.js                     # should generate diagnostics
+├── valid.js                       # should not generate diagnostics
+├── validResolutionReact/
+└───── file.js              # should generate diagnostics
+   └── file2.js             # should not generate diagnostics
+```
+
 **Multiple test cases** - Use `.jsonc` files with arrays:
 
 ```jsonc
@@ -182,27 +198,19 @@ tests/specs/nursery/noVar/
 
 ### Top-Level Comment Convention (REQUIRED)
 
-Every JS/TS test spec file **must** begin with a top-level comment declaring whether it expects diagnostics. The test runner (
-`assert_diagnostics_expectation_comment` in `biome_test_utils`) enforces this and panics if the rules are violated.
+Every test spec file **must** begin with a top-level comment declaring whether it expects diagnostics. The test runner
+(`assert_diagnostics_expectation_comment` in `biome_test_utils`) enforces this and panics if the rules are violated.
 
-**For files whose name contains "valid" (but not "invalid"):**
+Write the marker text using whatever comment syntax the language under test supports.
+For languages that do not support comments at all, rely on the file/folder naming convention (`valid`/`invalid`) instead.
 
-```js
-/* should not generate diagnostics */
-import {foo} from "./foo.js";
-```
+**For files whose name contains "valid" (but not "invalid"):**
 
-This is **enforced** — the test panics if the comment is absent.
+The comment is **mandatory** — the test panics if it is absent.
 
 **For files whose name contains "invalid" (or other names):**
 
-```js
-/* should generate diagnostics */
-var x = 1;
-var y = 2;
-```
-
-This is strongly recommended convention and is also enforced when present: if the comment says
+The comment is strongly recommended and is also enforced when present: if the comment says
 `should generate diagnostics` but no diagnostics appear, the test panics.
 
 **Rules enforced by the test runner:**
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
diff --git a/crates/biome_js_analyze/tests/specs/nursery/noShadow/invalidDestructuring.js b/crates/biome_js_analyze/tests/specs/nursery/noShadow/invalidDestructuring.js
new file mode 100644
index 000000000000..a2ea9c049659
--- /dev/null
+++ b/crates/biome_js_analyze/tests/specs/nursery/noShadow/invalidDestructuring.js
@@ -0,0 +1,43 @@
+/* should generate diagnostics */
+
+// Object destructuring shadowing outer variable
+const x = 1;
+function shadowObj() {
+    const { a: x } = { a: 2 };
+}
+
+// Array destructuring shadowing outer variable
+const y = 1;
+function shadowArr() {
+    const [y] = [2];
+}
+
+// Nested destructuring shadowing outer variable
+const z = 1;
+function shadowNested() {
+    const { a: { b: z } } = { a: { b: 2 } };
+}
+
+// Shorthand object destructuring shadowing outer variable
+const w = 1;
+function shadowShorthand() {
+    const { w } = { w: 2 };
+}
+
+// Mixed nested destructuring shadowing outer variable
+const m = 1;
+function shadowMixed() {
+    const [{ m }] = [{ m: 2 }];
+}
+
+// Rest in array destructuring shadowing outer variable
+const rest = 1;
+function shadowRestArr() {
+    const [, ...rest] = [1, 2, 3];
+}
+
+// Rest in object destructuring shadowing outer variable
+const other = 1;
+function shadowRestObj() {
+    const { a, ...other } = { a: 1, b: 2 };
+}
diff --git a/crates/biome_js_analyze/tests/specs/nursery/noShadow/validDestructuring.js b/crates/biome_js_analyze/tests/specs/nursery/noShadow/validDestructuring.js
new file mode 100644
index 000000000000..09ddf383d450
--- /dev/null
+++ b/crates/biome_js_analyze/tests/specs/nursery/noShadow/validDestructuring.js
@@ -0,0 +1,97 @@
+/* should not generate diagnostics */
+
+// Object destructuring in sibling scopes
+function objDestructuring(condition) {
+  if (condition) {
+    const str = 'this is a message';
+    const { str: destructuredStr } = { str: 'this is a message' };
+    const objStr = { str: 'this is a message' };
+    return { str, destructuredStr, objStr };
+  }
+
+  const str = 'this is a message';
+  const { str: destructuredStr } = { str: 'this is a different message' };
+  const objStr = { str: 'this is a different message' };
+  return { str, destructuredStr, objStr };
+}
+
+// Array destructuring in sibling scopes
+function arrDestructuring(condition) {
+  if (condition) {
+    const [first] = [1];
+    const [, second] = [1, 2];
+    return { first, second };
+  }
+
+  const [first] = [10];
+  const [, second] = [10, 20];
+  return { first, second };
+}
+
+// Shorthand object destructuring in sibling scopes
+function shorthandDestructuring(condition) {
+  if (condition) {
+    const { x } = { x: 1 };
+    return x;
+  }
+
+  const { x } = { x: 2 };
+  return x;
+}
+
+// Nested object destructuring in sibling scopes
+function nestedObjDestructuring(condition) {
+  if (condition) {
+    const { a: { b: nested } } = { a: { b: 1 } };
+    return nested;
+  }
+
+  const { a: { b: nested } } = { a: { b: 2 } };
+  return nested;
+}
+
+// Nested array destructuring in sibling scopes
+function nestedArrDestructuring(condition) {
+  if (condition) {
+    const [[inner]] = [[1]];
+    return inner;
+  }
+
+  const [[inner]] = [[2]];
+  return inner;
+}
+
+// Mixed nested destructuring in sibling scopes
+function mixedDestructuring(condition) {
+  if (condition) {
+    const { items: [first] } = { items: [1] };
+    const [{ name }] = [{ name: 'a' }];
+    return { first, name };
+  }
+
+  const { items: [first] } = { items: [2] };
+  const [{ name }] = [{ name: 'b' }];
+  return { first, name };
+}
+
+// Rest element in array destructuring in sibling scopes
+function restDestructuring(condition) {
+  if (condition) {
+    const [head, ...tail] = [1, 2, 3];
+    return { head, tail };
+  }
+
+  const [head, ...tail] = [4, 5, 6];
+  return { head, tail };
+}
+
+// Rest element in object destructuring in sibling scopes
+function restObjDestructuring(condition) {
+  if (condition) {
+    const { a, ...rest } = { a: 1, b: 2 };
+    return { a, rest };
+  }
+
+  const { a, ...rest } = { a: 3, b: 4 };
+  return { a, rest };
+}

PATCH

echo "Patch applied successfully."
