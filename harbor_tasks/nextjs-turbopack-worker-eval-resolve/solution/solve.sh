#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotency: check if the fix is already applied
if grep -q 'JsConstantValue::True' turbopack/crates/turbopack-ecmascript/src/references/mod.rs 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/turbopack/crates/turbopack-core/src/resolve/parse.rs b/turbopack/crates/turbopack-core/src/resolve/parse.rs
index 15f58172c845c1..e8af9e865d0c59 100644
--- a/turbopack/crates/turbopack-core/src/resolve/parse.rs
+++ b/turbopack/crates/turbopack-core/src/resolve/parse.rs
@@ -293,7 +293,12 @@ impl Request {
                 Request::Unknown { path } => {
                     path.push(item);
                 }
-                Request::DataUri { .. } | Request::Uri { .. } | Request::Dynamic => {
+                Request::DataUri { .. } | Request::Uri { .. } => {
+                    return Request::Dynamic;
+                }
+                Request::Dynamic => {
+                    // A dynamic prefix is essentially impossible to resolve so we don't try.  We
+                    // would have to scan the entire repo for suffix matches.
                     return Request::Dynamic;
                 }
                 Request::Alternatives { .. } => unreachable!(),
diff --git a/turbopack/crates/turbopack-ecmascript/src/references/mod.rs b/turbopack/crates/turbopack-ecmascript/src/references/mod.rs
index 6da5f4f39a2d68..a6b1c3e3e2b8fa 100644
--- a/turbopack/crates/turbopack-ecmascript/src/references/mod.rs
+++ b/turbopack/crates/turbopack-ecmascript/src/references/mod.rs
@@ -2167,6 +2167,58 @@ where
             WellKnownFunctionKind::NodeWorkerConstructor => {
                 let args = linked_args().await?;
                 if !args.is_empty() {
+                    // When `{ eval: true }` is passed as the second argument,
+                    // the first argument is inline JS code, not a file path.
+                    // Skip creating a worker reference in that case.
+                    let mut dynamic_warning: Option<&str> = None;
+                    if let Some(opts) = args.get(1) {
+                        match opts {
+                            JsValue::Object { parts, .. } => {
+                                let eval_value = parts.iter().find_map(|part| match part {
+                                    ObjectPart::KeyValue(
+                                        JsValue::Constant(JsConstantValue::Str(key)),
+                                        value,
+                                    ) if key.as_str() == "eval" => Some(value),
+                                    _ => None,
+                                });
+                                if let Some(eval_value) = eval_value {
+                                    match eval_value {
+                                        // eval: true — first arg is code, not a
+                                        // path
+                                        JsValue::Constant(JsConstantValue::True) => {
+                                            return Ok(());
+                                        }
+                                        // eval: false — first arg is a path,
+                                        // continue normally
+                                        JsValue::Constant(JsConstantValue::False) => {}
+                                        // eval is set but not a literal boolean
+                                        _ => {
+                                            dynamic_warning = Some("has a dynamic `eval` option");
+                                        }
+                                    }
+                                }
+                            }
+                            // Options argument is not a static object literal —
+                            // we can't inspect it for `eval: true`
+                            _ => {
+                                dynamic_warning = Some("has a dynamic options argument");
+                            }
+                        }
+                    }
+                    if let Some(warning) = dynamic_warning {
+                        let (args, hints) = explain_args(args);
+                        handler.span_warn_with_code(
+                            span,
+                            &format!("new Worker({args}) {warning}{hints}"),
+                            DiagnosticId::Lint(
+                                errors::failed_to_analyze::ecmascript::NEW_WORKER.to_string(),
+                            ),
+                        );
+                        if ignore_dynamic_requests {
+                            return Ok(());
+                        }
+                    }
+
                     let pat = js_value_to_pattern(&args[0]);
                     if !pat.has_constant_parts() {
                         let (args, hints) = explain_args(args);
@@ -2208,7 +2260,7 @@ where
                     span,
                     &format!("new Worker({args}) is not statically analyze-able{hints}",),
                     DiagnosticId::Error(
-                        errors::failed_to_analyze::ecmascript::FS_METHOD.to_string(),
+                        errors::failed_to_analyze::ecmascript::NEW_WORKER.to_string(),
                     ),
                 );
                 // Ignore (e.g. dynamic parameter or string literal)

PATCH

echo "Fix applied successfully."
