#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'FsReadDir =>' turbopack/crates/turbopack-ecmascript/src/analyzer/well_known.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/turbopack/crates/turbopack-ecmascript/src/analyzer/mod.rs b/turbopack/crates/turbopack-ecmascript/src/analyzer/mod.rs
index a3c5df54e92f2..c8747e2de23d5 100644
--- a/turbopack/crates/turbopack-ecmascript/src/analyzer/mod.rs
+++ b/turbopack/crates/turbopack-ecmascript/src/analyzer/mod.rs
@@ -1818,6 +1818,10 @@ impl JsValue {
                         format!("fs.{name}"),
                         "A file reading method from the Node.js fs module: https://nodejs.org/api/fs.html",
                     ),
+                    WellKnownFunctionKind::FsReadDir => (
+                        "fs.readdir".to_string(),
+                        "The Node.js fs.readdir method: https://nodejs.org/api/fs.html",
+                    ),
                     WellKnownFunctionKind::PathToFileUrl => (
                         "url.pathToFileURL".to_string(),
                         "The Node.js url.pathToFileURL method: https://url/html#urlpathtofileurlpath",
@@ -3484,6 +3488,7 @@ pub enum WellKnownFunctionKind {
     RequireContextRequireResolve(RequireContextValue),
     Define,
     FsReadMethod(Atom),
+    FsReadDir,
     PathToFileUrl,
     CreateRequire,
     ChildProcessSpawnMethod(Atom),
diff --git a/turbopack/crates/turbopack-ecmascript/src/analyzer/well_known.rs b/turbopack/crates/turbopack-ecmascript/src/analyzer/well_known.rs
index 53311f2966a4d..c8400d6b946ca 100644
--- a/turbopack/crates/turbopack-ecmascript/src/analyzer/well_known.rs
+++ b/turbopack/crates/turbopack-ecmascript/src/analyzer/well_known.rs
@@ -721,6 +721,9 @@ fn fs_module_member(kind: WellKnownObjectKind, prop: JsValue) -> JsValue {
                     word.into(),
                 ));
             }
+            (.., "readdir" | "readdirSync") => {
+                return JsValue::WellKnownFunction(WellKnownFunctionKind::FsReadDir);
+            }
             (WellKnownObjectKind::FsModule | WellKnownObjectKind::FsModuleDefault, "promises") => {
                 return JsValue::WellKnownObject(WellKnownObjectKind::FsModulePromises);
             }
diff --git a/turbopack/crates/turbopack-ecmascript/src/references/mod.rs b/turbopack/crates/turbopack-ecmascript/src/references/mod.rs
index e3c9281a67b6e..a88ecc6a0716c 100644
--- a/turbopack/crates/turbopack-ecmascript/src/references/mod.rs
+++ b/turbopack/crates/turbopack-ecmascript/src/references/mod.rs
@@ -2460,7 +2460,41 @@ where
                 DiagnosticId::Error(errors::failed_to_analyze::ecmascript::FS_METHOD.to_string()),
             )
         }
-
+        WellKnownFunctionKind::FsReadDir if analysis.analyze_mode.is_tracing_assets() => {
+            let args = linked_args().await?;
+            if !args.is_empty() {
+                let pat = js_value_to_pattern(&args[0]);
+                if !pat.has_constant_parts() {
+                    let (args, hints) = explain_args(args);
+                    handler.span_warn_with_code(
+                        span,
+                        &format!("fs.readdir({args}) is very dynamic{hints}"),
+                        DiagnosticId::Lint(
+                            errors::failed_to_analyze::ecmascript::FS_METHOD.to_string(),
+                        ),
+                    );
+                    if ignore_dynamic_requests {
+                        return Ok(());
+                    }
+                }
+                analysis.add_reference(
+                    DirAssetReference::new(
+                        get_traced_project_dir().await?,
+                        Pattern::new(pat),
+                        get_issue_source(),
+                    )
+                    .to_resolved()
+                    .await?,
+                );
+                return Ok(());
+            }
+            let (args, hints) = explain_args(args);
+            handler.span_warn_with_code(
+                span,
+                &format!("fs.readdir({args}) is not statically analyze-able{hints}"),
+                DiagnosticId::Error(errors::failed_to_analyze::ecmascript::FS_METHOD.to_string()),
+            )
+        }
         WellKnownFunctionKind::PathResolve(..) if analysis.analyze_mode.is_tracing_assets() => {
             let parent_path = origin.origin_path().owned().await?.parent();
             let args = linked_args().await?;
@@ -2504,7 +2538,6 @@ where
             );
             return Ok(());
         }
-
         WellKnownFunctionKind::PathJoin if analysis.analyze_mode.is_tracing_assets() => {
             let context_path = source.ident().path().await?;
             // ignore path.join in `node-gyp`, it will includes too many files
diff --git a/turbopack/crates/turbopack-tracing/tests/node-file-trace/test/unit/wildcard/input.js b/turbopack/crates/turbopack-tracing/tests/node-file-trace/test/unit/wildcard/input.js
index 3e7a806e5ad59..9dd42daec3343 100644
--- a/turbopack/crates/turbopack-tracing/tests/node-file-trace/test/unit/wildcard/input.js
+++ b/turbopack/crates/turbopack-tracing/tests/node-file-trace/test/unit/wildcard/input.js
@@ -1,3 +1,4 @@
+const fs = require('fs')
 const path = require('path')

 fs.readFileSync(path.join(__dirname, 'assets', unknown) + '.txt')
diff --git a/turbopack/crates/turbopack-tracing/tests/node-file-trace/test/unit/wildcard3/input.js b/turbopack/crates/turbopack-tracing/tests/node-file-trace/test/unit/wildcard3/input.js
index e190847b39763..92d3586079e0a 100644
--- a/turbopack/crates/turbopack-tracing/tests/node-file-trace/test/unit/wildcard3/input.js
+++ b/turbopack/crates/turbopack-tracing/tests/node-file-trace/test/unit/wildcard3/input.js
@@ -1,3 +1,4 @@
+const fs = require('fs')
 const path = require('path')

 const num = Math.ceil(Math.random() * 3)
diff --git a/turbopack/crates/turbopack-tracing/tests/unit.rs b/turbopack/crates/turbopack-tracing/tests/unit.rs
index d2bc337c89d79..b0e842b02ecfd 100644
--- a/turbopack/crates/turbopack-tracing/tests/unit.rs
+++ b/turbopack/crates/turbopack-tracing/tests/unit.rs
@@ -86,8 +86,8 @@ static ALLOC: turbo_tasks_malloc::TurboMalloc = turbo_tasks_malloc::TurboMalloc;
 // #[case::depth_1("depth-1")]
 // #[case::depth_2("depth-2")]
 // #[case::depth_3("depth-3")]
-// #[case::dirname_emit("dirname-emit")]
-// #[case::dirname_emit_concat("dirname-emit-concat")]
+#[case::dirname_emit("dirname-emit")]
+#[case::dirname_emit_concat("dirname-emit-concat")]
 #[case::dirname_len("dirname-len")]
 #[case::dot_dot("dot-dot")]
 #[case::esm_dynamic_import("esm-dynamic-import")]
@@ -188,9 +188,9 @@ static ALLOC: turbo_tasks_malloc::TurboMalloc = turbo_tasks_malloc::TurboMalloc;
 // #[case::webpack_wrapper_strs_namespaces_large("webpack-wrapper-strs-namespaces-large")]
 // #[case::when_wrapper("when-wrapper")]
 #[case::wildcard("wildcard")]
-// #[case::wildcard_require("wildcard-require")]
+#[case::wildcard_require("wildcard-require")]
 // #[case::wildcard2("wildcard2")]
-// #[case::wildcard3("wildcard3")]
+#[case::wildcard3("wildcard3")]
 // #[case::yarn_workspace_esm("yarn-workspace-esm")]
 // #[case::yarn_workspaces("yarn-workspaces")]
 // #[case::zeromq_node_gyp("zeromq-node_gyp")]

PATCH

echo "Patch applied successfully."
