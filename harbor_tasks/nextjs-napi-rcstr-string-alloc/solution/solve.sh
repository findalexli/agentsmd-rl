#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

ENDPOINT_FILE="crates/next-napi-bindings/src/next_api/endpoint.rs"

# Idempotency check: if RcStr is already used for path field in NapiAssetPath, skip
if grep -q 'pub path: RcStr' "$ENDPOINT_FILE" 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/next-napi-bindings/src/next_api/endpoint.rs b/crates/next-napi-bindings/src/next_api/endpoint.rs
index a5a5684c77166..a46de5c045b7d 100644
--- a/crates/next-napi-bindings/src/next_api/endpoint.rs
+++ b/crates/next-napi-bindings/src/next_api/endpoint.rs
@@ -13,6 +13,7 @@ use next_api::{
     },
 };
 use tracing::Instrument;
+use turbo_rcstr::RcStr;
 use turbo_tasks::{Completion, Effects, OperationVc, ReadRef, Vc};
 use turbopack_core::{
     diagnostics::PlainDiagnostic,
@@ -31,15 +32,15 @@ pub struct NapiEndpointConfig {}
 #[napi(object)]
 #[derive(Default)]
 pub struct NapiAssetPath {
-    pub path: String,
-    pub content_hash: String,
+    pub path: RcStr,
+    pub content_hash: RcStr,
 }

 impl From<AssetPath> for NapiAssetPath {
     fn from(asset_path: AssetPath) -> Self {
         Self {
-            path: asset_path.path.into_owned(),
-            content_hash: asset_path.content_hash.into_owned(),
+            path: asset_path.path,
+            content_hash: asset_path.content_hash,
         }
     }
 }
diff --git a/crates/next-napi-bindings/src/next_api/project.rs b/crates/next-napi-bindings/src/next_api/project.rs
index 805e1a965f784..202c83c446d3d 100644
--- a/crates/next-napi-bindings/src/next_api/project.rs
+++ b/crates/next-napi-bindings/src/next_api/project.rs
@@ -786,7 +786,7 @@ pub struct AppPageNapiRoute {
 #[derive(Default)]
 pub struct NapiRoute {
     /// The router path
-    pub pathname: String,
+    pub pathname: RcStr,
     /// The relative path from project_path to the route file
     pub original_name: Option<RcStr>,

@@ -804,7 +804,7 @@ pub struct NapiRoute {

 impl NapiRoute {
     fn from_route(
-        pathname: String,
+        pathname: RcStr,
         value: RouteOperation,
         turbopack_ctx: &NextTurbopackContext,
     ) -> Self {
@@ -928,7 +928,7 @@ impl NapiEntrypoints {
         let routes = entrypoints
             .routes
             .iter()
-            .map(|(k, v)| NapiRoute::from_route(k.to_string(), v.clone(), turbopack_ctx))
+            .map(|(k, v)| NapiRoute::from_route(k.clone(), v.clone(), turbopack_ctx))
             .collect();
         let middleware = entrypoints
             .middleware
diff --git a/crates/next-napi-bindings/src/next_api/utils.rs b/crates/next-napi-bindings/src/next_api/utils.rs
index dd6f47c8b5bef..722a43362fde6 100644
--- a/crates/next-napi-bindings/src/next_api/utils.rs
+++ b/crates/next-napi-bindings/src/next_api/utils.rs
@@ -13,6 +13,7 @@ use once_cell::sync::Lazy;
 use regex::Regex;
 use rustc_hash::FxHashMap;
 use serde::Serialize;
+use turbo_rcstr::RcStr;
 use turbo_tasks::{
     Effects, OperationVc, ReadRef, TaskId, TryJoinIterExt, Vc, VcValueType, get_effects,
 };
@@ -226,13 +227,13 @@ fn render_issue_code_frame(issue: &PlainIssue) -> Result<Option<String>> {
 pub struct NapiIssue {
     pub severity: String,
     pub stage: String,
-    pub file_path: String,
+    pub file_path: RcStr,
     pub title: serde_json::Value,
     pub description: Option<serde_json::Value>,
     pub detail: Option<serde_json::Value>,
     pub source: Option<NapiIssueSource>,
     pub additional_sources: Vec<NapiAdditionalIssueSource>,
-    pub documentation_link: String,
+    pub documentation_link: RcStr,
     pub import_traces: serde_json::Value,
     /// Pre-rendered code frame for the issue's source location, if available.
     /// Rendered in Rust to avoid transferring full source file content to JS.
@@ -241,7 +242,7 @@ pub struct NapiIssue {

 #[napi(object)]
 pub struct NapiAdditionalIssueSource {
-    pub description: String,
+    pub description: RcStr,
     pub source: NapiIssueSource,
     /// Pre-rendered code frame for this additional source location, if available.
     pub code_frame: Option<String>,
@@ -255,19 +256,19 @@ impl From<&PlainIssue> for NapiIssue {
                 .as_ref()
                 .map(|styled| serde_json::to_value(StyledStringSerialize::from(styled)).unwrap()),
             stage: issue.stage.to_string(),
-            file_path: issue.file_path.to_string(),
+            file_path: issue.file_path.clone(),
             detail: issue
                 .detail
                 .as_ref()
                 .map(|styled| serde_json::to_value(StyledStringSerialize::from(styled)).unwrap()),
-            documentation_link: issue.documentation_link.to_string(),
+            documentation_link: issue.documentation_link.clone(),
             severity: issue.severity.as_str().to_string(),
             source: issue.source.as_ref().map(|source| source.into()),
             additional_sources: issue
                 .additional_sources
                 .iter()
                 .map(|s| NapiAdditionalIssueSource {
-                    description: s.description.to_string(),
+                    description: s.description.clone(),
                     code_frame: render_source_code_frame(&s.source, &s.source.asset.file_path)
                         .unwrap_or_default(),
                     source: (&s.source).into(),
@@ -353,15 +354,15 @@ impl From<&(SourcePos, SourcePos)> for NapiIssueSourceRange {

 #[napi(object)]
 pub struct NapiSource {
-    pub ident: String,
-    pub file_path: String,
+    pub ident: RcStr,
+    pub file_path: RcStr,
 }

 impl From<&PlainSource> for NapiSource {
     fn from(source: &PlainSource) -> Self {
         Self {
-            ident: source.ident.to_string(),
-            file_path: source.file_path.to_string(),
+            ident: (*source.ident).clone(),
+            file_path: (*source.file_path).clone(),
         }
     }
 }
@@ -383,21 +384,21 @@ impl From<SourcePos> for NapiSourcePos {

 #[napi(object)]
 pub struct NapiDiagnostic {
-    pub category: String,
-    pub name: String,
+    pub category: RcStr,
+    pub name: RcStr,
     #[napi(ts_type = "Record<string, string>")]
-    pub payload: FxHashMap<String, String>,
+    pub payload: FxHashMap<RcStr, RcStr>,
 }

 impl NapiDiagnostic {
     pub fn from(diagnostic: &PlainDiagnostic) -> Self {
         Self {
-            category: diagnostic.category.to_string(),
-            name: diagnostic.name.to_string(),
+            category: diagnostic.category.clone(),
+            name: diagnostic.name.clone(),
             payload: diagnostic
                 .payload
                 .iter()
-                .map(|(k, v)| (k.to_string(), v.to_string()))
+                .map(|(k, v)| (k.clone(), v.clone()))
                 .collect(),
         }
     }

PATCH

echo "Fix applied successfully."
