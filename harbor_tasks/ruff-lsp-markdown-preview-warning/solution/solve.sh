#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Check if already applied (look for FormatResult enum in format.rs)
if grep -q 'pub(crate) enum FormatResult' crates/ruff_server/src/format.rs; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ruff_server/src/format.rs b/crates/ruff_server/src/format.rs
index e8e8efbf5ca57..d5ddb2ecb0139 100644
--- a/crates/ruff_server/src/format.rs
+++ b/crates/ruff_server/src/format.rs
@@ -29,13 +29,29 @@ pub(crate) enum FormatBackend {
     Uv,
 }

+#[derive(Debug, PartialEq, Eq)]
+pub(crate) enum FormatResult {
+    Formatted(String),
+    Unchanged,
+    PreviewOnly { file_format: &'static str },
+}
+
+impl FormatResult {
+    fn into_formatted(self) -> Option<String> {
+        match self {
+            Self::Formatted(formatted) => Some(formatted),
+            Self::Unchanged | Self::PreviewOnly { .. } => None,
+        }
+    }
+}
+
 pub(crate) fn format(
     document: &TextDocument,
     source_type: SourceType,
     formatter_settings: &FormatterSettings,
     path: &Path,
     backend: FormatBackend,
-) -> crate::Result<Option<String>> {
+) -> crate::Result<FormatResult> {
     match backend {
         FormatBackend::Uv => format_external(document, source_type, formatter_settings, path),
         FormatBackend::Internal => format_internal(document, source_type, formatter_settings, path),
@@ -48,7 +64,7 @@ fn format_internal(
     source_type: SourceType,
     formatter_settings: &FormatterSettings,
     path: &Path,
-) -> crate::Result<Option<String>> {
+) -> crate::Result<FormatResult> {
     match source_type {
         SourceType::Python(py_source_type) => {
             let format_options = formatter_settings.to_format_options(
@@ -60,16 +76,16 @@ fn format_internal(
                 Ok(formatted) => {
                     let formatted = formatted.into_code();
                     if formatted == document.contents() {
-                        Ok(None)
+                        Ok(FormatResult::Unchanged)
                     } else {
-                        Ok(Some(formatted))
+                        Ok(FormatResult::Formatted(formatted))
                     }
                 }
                 // Special case - syntax/parse errors are handled here instead of
                 // being propagated as visible server errors.
                 Err(FormatModuleError::ParseError(error)) => {
                     tracing::warn!("Unable to format document: {error}");
-                    Ok(None)
+                    Ok(FormatResult::Unchanged)
                 }
                 Err(err) => Err(err.into()),
             }
@@ -77,17 +93,19 @@ fn format_internal(
         SourceType::Markdown => {
             if !formatter_settings.preview.is_enabled() {
                 tracing::warn!("Markdown formatting is experimental, enable preview mode.");
-                return Ok(None);
+                return Ok(FormatResult::PreviewOnly {
+                    file_format: "Markdown",
+                });
             }

             match format_code_blocks(document.contents(), Some(path), formatter_settings) {
-                MarkdownResult::Formatted(formatted) => Ok(Some(formatted)),
-                MarkdownResult::Unchanged => Ok(None),
+                MarkdownResult::Formatted(formatted) => Ok(FormatResult::Formatted(formatted)),
+                MarkdownResult::Unchanged => Ok(FormatResult::Unchanged),
             }
         }
         SourceType::Toml(_) => {
-            tracing::warn!("Formatting TOML files not supported");
-            Ok(None)
+            tracing::warn!("Formatting TOML files is not supported");
+            Ok(FormatResult::Unchanged)
         }
     }
 }
@@ -98,7 +116,7 @@ fn format_external(
     source_type: SourceType,
     formatter_settings: &FormatterSettings,
     path: &Path,
-) -> crate::Result<Option<String>> {
+) -> crate::Result<FormatResult> {
     let format_options = match source_type {
         SourceType::Python(py_source_type) => {
             formatter_settings.to_format_options(py_source_type, document.contents(), Some(path))
@@ -110,7 +128,7 @@ fn format_external(
         ),
         SourceType::Toml(_) => {
             tracing::warn!("Formatting TOML files not supported");
-            return Ok(None);
+            return Ok(FormatResult::Unchanged);
         }
     };
     let uv_command = UvFormatCommand::from(format_options);
@@ -188,10 +206,10 @@ fn format_range_external(
     let uv_command = UvFormatCommand::from(format_options);

     // Format the range using uv and convert the result to `PrintedRange`
-    match uv_command.format_range(document.contents(), range, path, document.index())? {
-        Some(formatted) => Ok(Some(PrintedRange::new(formatted, range))),
-        None => Ok(None),
-    }
+    Ok(uv_command
+        .format_range(document.contents(), range, path, document.index())?
+        .into_formatted()
+        .map(|formatted| PrintedRange::new(formatted, range)))
 }

 /// Builder for uv format commands
@@ -296,7 +314,7 @@ impl UvFormatCommand {
         source: &str,
         path: &Path,
         range_with_index: Option<(TextRange, &LineIndex)>,
-    ) -> crate::Result<Option<String>> {
+    ) -> crate::Result<FormatResult> {
         let mut command =
             self.build_command(path, range_with_index.map(|(r, idx)| (r, idx, source)));
         let mut child = match command.spawn() {
@@ -325,7 +343,7 @@ impl UvFormatCommand {
             // We don't propagate format errors due to invalid syntax
             if stderr.contains("Failed to parse") {
                 tracing::warn!("Unable to format document: {}", stderr);
-                return Ok(None);
+                return Ok(FormatResult::Unchanged);
             }
             // Special-case for when `uv format` is not available
             if stderr.contains("unrecognized subcommand 'format'") {
@@ -340,18 +358,14 @@ impl UvFormatCommand {
             .context("Failed to parse stdout from format subprocess as utf-8")?;

         if formatted == source {
-            Ok(None)
+            Ok(FormatResult::Unchanged)
         } else {
-            Ok(Some(formatted))
+            Ok(FormatResult::Formatted(formatted))
         }
     }

     /// Format the entire document.
-    pub(crate) fn format_document(
-        &self,
-        source: &str,
-        path: &Path,
-    ) -> crate::Result<Option<String>> {
+    pub(crate) fn format_document(&self, source: &str, path: &Path) -> crate::Result<FormatResult> {
         self.format(source, path, None)
     }

@@ -362,7 +376,7 @@ impl UvFormatCommand {
         range: TextRange,
         path: &Path,
         line_index: &LineIndex,
-    ) -> crate::Result<Option<String>> {
+    ) -> crate::Result<FormatResult> {
         self.format(source, path, Some((range, line_index)))
     }
 }
@@ -378,7 +392,13 @@ mod tests {
     use ruff_workspace::FormatterSettings;

     use crate::TextDocument;
-    use crate::format::{FormatBackend, format, format_range};
+    use crate::format::{FormatBackend, FormatResult, format, format_range};
+
+    fn expect_formatted(result: FormatResult) -> String {
+        result
+            .into_formatted()
+            .expect("Expected formatting changes")
+    }

     #[test]
     fn format_per_file_version() {
@@ -404,8 +424,9 @@ with open("a_really_long_foo") as foo, open("a_really_long_bar") as bar, open("a
             Path::new("test.py"),
             FormatBackend::Internal,
         )
-        .expect("Expected no errors when formatting")
-        .expect("Expected formatting changes");
+        .expect("Expected no errors when formatting");
+
+        let result = expect_formatted(result);

         assert_snapshot!(result, @r#"
         with (
@@ -427,8 +448,9 @@ with open("a_really_long_foo") as foo, open("a_really_long_bar") as bar, open("a
             Path::new("test.py"),
             FormatBackend::Internal,
         )
-        .expect("Expected no errors when formatting")
-        .expect("Expected formatting changes");
+        .expect("Expected no errors when formatting");
+
+        let result = expect_formatted(result);

         assert_snapshot!(result, @r#"
         with open("a_really_long_foo") as foo, open("a_really_long_bar") as bar, open(
@@ -539,8 +561,9 @@ def world(  ):
                 Path::new("test.py"),
                 FormatBackend::Uv,
             )
-            .expect("Expected no errors when formatting with uv")
-            .expect("Expected formatting changes");
+            .expect("Expected no errors when formatting with uv");
+
+            let result = expect_formatted(result);

             // uv should format this to a consistent style
             assert_snapshot!(result, @r#"
@@ -622,8 +645,9 @@ def hello(very_long_parameter_name_1, very_long_parameter_name_2, very_long_para
                 Path::new("test.py"),
                 FormatBackend::Uv,
             )
-            .expect("Expected no errors when formatting with uv")
-            .expect("Expected formatting changes");
+            .expect("Expected no errors when formatting with uv");
+
+            let result = expect_formatted(result);

             // With line length 60, the function should be wrapped
             assert_snapshot!(result, @r#"
@@ -669,8 +693,9 @@ def hello():
                 Path::new("test.py"),
                 FormatBackend::Uv,
             )
-            .expect("Expected no errors when formatting with uv")
-            .expect("Expected formatting changes");
+            .expect("Expected no errors when formatting with uv");
+
+            let result = expect_formatted(result);

             // Should have formatting changes (spaces to tabs)
             assert_snapshot!(result, @r#"
@@ -693,7 +718,6 @@ def broken(:
                 0,
             );

-            // uv should return None for syntax errors (as indicated by the TODO comment)
             let result = format(
                 &document,
                 SourceType::Python(PySourceType::Python),
@@ -703,8 +727,11 @@ def broken(:
             )
             .expect("Expected no errors from format function");

-            // Should return None since the syntax is invalid
-            assert_eq!(result, None, "Expected None for syntax error");
+            assert_eq!(
+                result,
+                FormatResult::Unchanged,
+                "Expected unchanged for syntax error"
+            );
         }

         #[test]
@@ -735,8 +762,9 @@ line'''
                 Path::new("test.py"),
                 FormatBackend::Uv,
             )
-            .expect("Expected no errors when formatting with uv")
-            .expect("Expected formatting changes");
+            .expect("Expected no errors when formatting with uv");
+
+            let result = expect_formatted(result);

             assert_snapshot!(result, @r#"
             x = 'hello'
@@ -777,8 +805,9 @@ bar = [1, 2, 3,]
                 Path::new("test.py"),
                 FormatBackend::Uv,
             )
-            .expect("Expected no errors when formatting with uv")
-            .expect("Expected formatting changes");
+            .expect("Expected no errors when formatting with uv");
+
+            let result = expect_formatted(result);

             assert_snapshot!(result, @r#"
             foo = [1, 2, 3]
diff --git a/crates/ruff_server/src/server/api/requests/execute_command.rs b/crates/ruff_server/src/server/api/requests/execute_command.rs
index 1303e0ee1451b..632a196ab91c8 100644
--- a/crates/ruff_server/src/server/api/requests/execute_command.rs
+++ b/crates/ruff_server/src/server/api/requests/execute_command.rs
@@ -89,7 +89,7 @@ impl super::SyncRequestHandler for ExecuteCommand {
                         .with_failure_code(ErrorCode::InternalError)?;
                 }
                 SupportedCommand::Format => {
-                    let fixes = super::format::format_full_document(&snapshot)?;
+                    let fixes = super::format::format_full_document(&snapshot, client)?;
                     edit_tracker
                         .set_fixes_for_document(fixes, version)
                         .with_failure_code(ErrorCode::InternalError)?;
diff --git a/crates/ruff_server/src/server/api/requests/format.rs b/crates/ruff_server/src/server/api/requests/format.rs
index 407c5eb2297cb..c1a31099cd4f4 100644
--- a/crates/ruff_server/src/server/api/requests/format.rs
+++ b/crates/ruff_server/src/server/api/requests/format.rs
@@ -6,6 +6,7 @@ use ruff_source_file::LineIndex;

 use crate::edit::{Replacement, ToRangeExt};
 use crate::fix::Fixes;
+use crate::format::FormatResult;
 use crate::resolve::is_document_excluded_for_formatting;
 use crate::server::Result;
 use crate::server::api::LSPResult;
@@ -22,15 +23,15 @@ impl super::BackgroundDocumentRequestHandler for Format {
     super::define_document_url!(params: &types::DocumentFormattingParams);
     fn run_with_snapshot(
         snapshot: DocumentSnapshot,
-        _client: &Client,
+        client: &Client,
         _params: types::DocumentFormattingParams,
     ) -> Result<super::FormatResponse> {
-        format_document(&snapshot)
+        format_document(&snapshot, client)
     }
 }

 /// Formats either a full text document or each individual cell in a single notebook document.
-pub(super) fn format_full_document(snapshot: &DocumentSnapshot) -> Result<Fixes> {
+pub(super) fn format_full_document(snapshot: &DocumentSnapshot, client: &Client) -> Result<Fixes> {
     let mut fixes = Fixes::default();
     let query = snapshot.query();
     let backend = snapshot
@@ -44,16 +45,21 @@ pub(super) fn format_full_document(snapshot: &DocumentSnapshot) -> Result<Fixes>
                 .urls()
                 .map(|url| (url.clone(), notebook.cell_document_by_uri(url).unwrap()))
             {
-                if let Some(changes) =
-                    format_text_document(text_document, query, snapshot.encoding(), true, backend)?
-                {
+                if let Some(changes) = format_text_document(
+                    text_document,
+                    query,
+                    snapshot.encoding(),
+                    true,
+                    backend,
+                    client,
+                )? {
                     fixes.insert(url, changes);
                 }
             }
         }
         DocumentQuery::Text { document, .. } => {
             if let Some(changes) =
-                format_text_document(document, query, snapshot.encoding(), false, backend)?
+                format_text_document(document, query, snapshot.encoding(), false, backend, client)?
             {
                 fixes.insert(snapshot.query().make_key().into_url(), changes);
             }
@@ -65,7 +71,10 @@ pub(super) fn format_full_document(snapshot: &DocumentSnapshot) -> Result<Fixes>

 /// Formats either a full text document or an specific notebook cell. If the query within the snapshot is a notebook document
 /// with no selected cell, this will throw an error.
-pub(super) fn format_document(snapshot: &DocumentSnapshot) -> Result<super::FormatResponse> {
+pub(super) fn format_document(
+    snapshot: &DocumentSnapshot,
+    client: &Client,
+) -> Result<super::FormatResponse> {
     let text_document = snapshot
         .query()
         .as_single_document()
@@ -82,6 +91,7 @@ pub(super) fn format_document(snapshot: &DocumentSnapshot) -> Result<super::Form
         snapshot.encoding(),
         query.as_notebook().is_some(),
         backend,
+        client,
     )
 }

@@ -91,6 +101,7 @@ fn format_text_document(
     encoding: PositionEncoding,
     is_notebook: bool,
     backend: crate::format::FormatBackend,
+    client: &Client,
 ) -> Result<super::FormatResponse> {
     let settings = query.settings();
     let file_path = query.virtual_file_path();
@@ -114,8 +125,17 @@ fn format_text_document(
         backend,
     )
     .with_failure_code(lsp_server::ErrorCode::InternalError)?;
-    let Some(mut formatted) = formatted else {
-        return Ok(None);
+    let mut formatted = match formatted {
+        FormatResult::Formatted(formatted) => formatted,
+        FormatResult::Unchanged => return Ok(None),
+        FormatResult::PreviewOnly { file_format } => {
+            client.show_warning_message(
+                format_args!(
+                    "{file_format} formatting is available only in preview mode. Enable `format.preview = true` in your Ruff configuration."
+                ),
+            );
+            return Ok(None);
+        }
     };

     // special case - avoid adding a newline to a notebook cell if it didn't already exist

PATCH

echo "Gold patch applied successfully."
