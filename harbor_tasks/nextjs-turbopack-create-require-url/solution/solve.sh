#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'RequireFrom(Box<ConstantString>)' turbopack/crates/turbopack-ecmascript/src/analyzer/mod.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/turbopack/crates/turbopack-ecmascript/src/analyzer/mod.rs b/turbopack/crates/turbopack-ecmascript/src/analyzer/mod.rs
index a3c5df54e92f2d..ba5d8d10638db 100644
--- a/turbopack/crates/turbopack-ecmascript/src/analyzer/mod.rs
+++ b/turbopack/crates/turbopack-ecmascript/src/analyzer/mod.rs
@@ -1808,6 +1808,10 @@ impl JsValue {
                         "The dynamic import() method from the ESM specification: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import#dynamic_imports"
                     ),
                     WellKnownFunctionKind::Require => ("require".to_string(), "The require method from CommonJS"),
+                    WellKnownFunctionKind::RequireFrom(rel) => (
+                        format!("createRequire('{rel}')"),
+                        "The return value of Node.js module.createRequire: https://nodejs.org/api/module.html#modulecreaterequirefilename"
+                    ),
                     WellKnownFunctionKind::RequireResolve => ("require.resolve".to_string(), "The require.resolve method from CommonJS"),
                     WellKnownFunctionKind::RequireContext => ("require.context".to_string(), "The require.context method from webpack"),
                     WellKnownFunctionKind::RequireContextRequire(..) => ("require.context(...)".to_string(), "The require.context(...) method from webpack: https://webpack.js.org/api/module-methods/#requirecontext"),
@@ -3477,6 +3481,8 @@ pub enum WellKnownFunctionKind {
     PathResolve(Box<JsValue>),
     Import,
     Require,
+    /// `0` is the path to resolve from (relative to the current module).
+    RequireFrom(Box<ConstantString>),
     RequireResolve,
     RequireContext,
     RequireContextRequire(RequireContextValue),
diff --git a/turbopack/crates/turbopack-ecmascript/src/references/mod.rs b/turbopack/crates/turbopack-ecmascript/src/references/mod.rs
index e3c9281a67b6ea..82232835302e29 100644
--- a/turbopack/crates/turbopack-ecmascript/src/references/mod.rs
+++ b/turbopack/crates/turbopack-ecmascript/src/references/mod.rs
@@ -2332,6 +2332,57 @@ where
                 DiagnosticId::Error(errors::failed_to_analyze::ecmascript::REQUIRE.to_string()),
             )
         }
+        WellKnownFunctionKind::RequireFrom(rel) => {
+            let args = linked_args().await?;
+            if args.len() == 1 {
+                let pat = js_value_to_pattern(&args[0]);
+                if !pat.has_constant_parts() {
+                    let (args, hints) = explain_args(args);
+                    handler.span_warn_with_code(
+                        span,
+                        &format!("createRequire()({args}) is very dynamic{hints}",),
+                        DiagnosticId::Lint(
+                            errors::failed_to_analyze::ecmascript::REQUIRE.to_string(),
+                        ),
+                    );
+                    if ignore_dynamic_requests {
+                        analysis.add_code_gen(DynamicExpression::new(ast_path.to_vec().into()));
+                        return Ok(());
+                    }
+                }
+                let origin = ResolvedVc::upcast(
+                    PlainResolveOrigin::new(
+                        origin.asset_context(),
+                        origin
+                            .origin_path()
+                            .await?
+                            .parent()
+                            .join(rel.as_str())?
+                            .join("_")?,
+                    )
+                    .to_resolved()
+                    .await?,
+                );
+
+                analysis.add_reference_code_gen(
+                    CjsRequireAssetReference::new(
+                        origin,
+                        Request::parse(pat).to_resolved().await?,
+                        issue_source(source, span),
+                        error_mode,
+                        attributes.chunking_type,
+                    ),
+                    ast_path.to_vec().into(),
+                );
+                return Ok(());
+            }
+            let (args, hints) = explain_args(args);
+            handler.span_warn_with_code(
+                span,
+                &format!("createRequire()({args}) is not statically analyze-able{hints}",),
+                DiagnosticId::Error(errors::failed_to_analyze::ecmascript::REQUIRE.to_string()),
+            )
+        }
         WellKnownFunctionKind::Define => {
             analyze_amd_define(
                 source,
@@ -3592,7 +3643,6 @@ async fn value_visitor_inner(
             box JsValue::WellKnownFunction(WellKnownFunctionKind::CreateRequire),
             ref args,
         ) => {
-            // Only support `createRequire(import.meta.url)` for now
             if let [
                 JsValue::Member(
                     _,
@@ -3602,7 +3652,13 @@ async fn value_visitor_inner(
             ] = &args[..]
                 && prop.as_str() == "url"
             {
+                // `createRequire(import.meta.url)`
                 JsValue::WellKnownFunction(WellKnownFunctionKind::Require)
+            } else if let [JsValue::Url(rel, JsValueUrlKind::Relative)] = &args[..] {
+                // `createRequire(new URL("<rel>", import.meta.url))`
+                JsValue::WellKnownFunction(WellKnownFunctionKind::RequireFrom(Box::new(
+                    rel.clone(),
+                )))
             } else {
                 v.into_unknown(true, "createRequire() non constant")
             }
diff --git a/turbopack/crates/turbopack-tracing/tests/unit.rs b/turbopack/crates/turbopack-tracing/tests/unit.rs
index d2bc337c89d796..fb97470045ddb 100644
--- a/turbopack/crates/turbopack-tracing/tests/unit.rs
+++ b/turbopack/crates/turbopack-tracing/tests/unit.rs
@@ -118,12 +118,12 @@ static ALLOC: turbo_tasks_malloc::TurboMalloc = turbo_tasks_malloc::TurboMalloc;
 // #[case::microtime_node_gyp("microtime-node-gyp")]
 // #[case::mixed_esm_cjs("mixed-esm-cjs")]
 #[case::module_create_require("module-create-require")]
-// #[case::module_create_require_destructure_namespace("module-create-require-destructure-namespace"
-// )] #[case::module_create_require_destructure("module-create-require-destructure")]
-// #[case::module_create_require_ignore_other("module-create-require-ignore-other")]
-// #[case::module_create_require_named_import("module-create-require-named-import")]
-// #[case::module_create_require_named_require("module-create-require-named-require")]
-// #[case::module_create_require_no_mixed("module-create-require-no-mixed")]
+#[case::module_create_require_destructure_namespace("module-create-require-destructure-namespace")]
+#[case::module_create_require_destructure("module-create-require-destructure")]
+#[case::module_create_require_ignore_other("module-create-require-ignore-other")]
+#[case::module_create_require_named_import("module-create-require-named-import")]
+#[case::module_create_require_named_require("module-create-require-named-require")]
+#[case::module_create_require_no_mixed("module-create-require-no-mixed")]
 // #[case::module_register("module-register")]
 // #[case::module_require("module-require")]
 // #[case::module_sync_condition_cjs("module-sync-condition-cjs")]
@@ -298,7 +298,18 @@ fn node_file_trace(input_path: &str) -> Result<()> {

     let package_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
     let package_root = package_root.join("tests/node-file-trace");
-    let input: RcStr = format!("test/unit/{input_path}/input.js").into();
+    let entry_name = match input_path {
+        "jsx-input" => "input.jsx",
+        "tsx-input" => "input.tsx",
+        "ts-input-esm" => "input.ts",
+        "module-create-require-no-mixed"
+        | "module-create-require-named-require"
+        | "module-create-require-named-import"
+        | "module-create-require-ignore-other"
+        | "module-create-require-destructure" => "input.mjs",
+        _ => "input.js",
+    };
+    let input: RcStr = format!("test/unit/{input_path}/{entry_name}").into();
     let reference = package_root.join(format!("test/unit/{input_path}/output.js"));

     r.block_on(async move {
diff --git a/turbopack/crates/turbopack-tests/tests/execution/turbopack/resolving/create-require/input/index.js b/turbopack/crates/turbopack-tests/tests/execution/turbopack/resolving/create-require/input/index.js
new file mode 100644
index 00000000000000..a34b2fc5d90159
--- /dev/null
+++ b/turbopack/crates/turbopack-tests/tests/execution/turbopack/resolving/create-require/input/index.js
@@ -0,0 +1,14 @@
+import { createRequire } from 'node:module'
+
+it('createRequire with import.meta.url works', () => {
+  const require = createRequire(import.meta.url)
+  const foo = require('./sub/foo.js')
+  expect(foo).toBe('foo')
+})
+
+it('createRequire with URL works', () => {
+  // Currently (incorrectly) emits an error about `Module not found: Can't resolve './sub/'`
+  const require = createRequire(new URL('./sub/', import.meta.url))
+  const foo = require('./foo.js')
+  expect(foo).toBe('foo')
+})
diff --git a/turbopack/crates/turbopack-tests/tests/execution/turbopack/resolving/create-require/input/sub/foo.js b/turbopack/crates/turbopack-tests/tests/execution/turbopack/resolving/create-require/input/sub/foo.js
new file mode 100644
index 00000000000000..3b8256e4e0efb9
--- /dev/null
+++ b/turbopack/crates/turbopack-tests/tests/execution/turbopack/resolving/create-require/input/sub/foo.js
@@ -0,0 +1 @@
+module.exports = 'foo'
diff --git a/turbopack/crates/turbopack-tests/tests/execution/turbopack/resolving/create-require/issues/__l___Module not found____c__ Can't resolve __c_'.-de9408.txt b/turbopack/crates/turbopack-tests/tests/execution/turbopack/resolving/create-require/issues/__l___Module not found____c__ Can't resolve __c_'.-de9408.txt
new file mode 100644
index 00000000000000..f2edfb71b3ea35
--- /dev/null
+++ b/turbopack/crates/turbopack-tests/tests/execution/turbopack/resolving/create-require/issues/__l___Module not found____c__ Can't resolve __c_'.-de9408.txt
@@ -0,0 +1,21 @@
+error - [resolve] /turbopack/crates/turbopack-tests/tests/execution/turbopack/resolving/create-require/input/index.js:11:32  Module not found: Can't resolve './sub/'
+
+       7 | })
+       8 |
+       9 | it('createRequire with URL works', () => {
+      10 |   // Currently (incorrectly) emits an error about `Module not found: Can't resolve './sub/'`
+         +                                 v--------------------------------v
+      11 +   const require = createRequire(new URL('./sub/', import.meta.url))
+         +                                 ^--------------------------------^
+      12 |   const foo = require('./foo.js')
+      13 |   expect(foo).toBe('foo')
+      14 | })
+      15 |
+
+
+
+  | It was not possible to find the requested file.
+  | Parsed request as written in source code: relative './sub/'
+  | Path where resolving has started: [project]/turbopack/crates/turbopack-tests/tests/execution/turbopack/resolving/create-require/input/index.js
+  | Type of request: url request
+  |

PATCH

echo "Patch applied successfully."
