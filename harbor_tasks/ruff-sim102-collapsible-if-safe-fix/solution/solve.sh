#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'is_collapsible_if_fix_safe_enabled' crates/ruff_linter/src/rules/flake8_simplify/rules/collapsible_if.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ruff_linter/src/preview.rs b/crates/ruff_linter/src/preview.rs
index 7f539ab5431be8..79f883d7a4b44f 100644
--- a/crates/ruff_linter/src/preview.rs
+++ b/crates/ruff_linter/src/preview.rs
@@ -332,8 +332,13 @@ pub const fn is_warning_severity_enabled(preview: PreviewMode) -> bool {
     preview.is_enabled()
 }

-/// <https://github.com/astral-sh/ruff/pull/24071>
-/// Make sure to stabilize the corresponding formatter preview behavior when stabilizing this preview style.
+// https://github.com/astral-sh/ruff/pull/24071
+// Make sure to stabilize the corresponding formatter preview behavior when stabilizing this preview style.
 pub(crate) const fn is_trailing_pragma_in_line_length_enabled(preview: PreviewMode) -> bool {
     preview.is_enabled()
 }
+
+// https://github.com/astral-sh/ruff/pull/24371
+pub(crate) const fn is_collapsible_if_fix_safe_enabled(settings: &LinterSettings) -> bool {
+    settings.preview.is_enabled()
+}
diff --git a/crates/ruff_linter/src/rules/flake8_simplify/rules/collapsible_if.rs b/crates/ruff_linter/src/rules/flake8_simplify/rules/collapsible_if.rs
index 89971175ebcfc2..d53f2908d0a08a 100644
--- a/crates/ruff_linter/src/rules/flake8_simplify/rules/collapsible_if.rs
+++ b/crates/ruff_linter/src/rules/flake8_simplify/rules/collapsible_if.rs
@@ -1,3 +1,4 @@
+use ruff_diagnostics::Applicability::{Safe, Unsafe};
 use std::borrow::Cow;

 use anyhow::{Result, bail};
@@ -18,6 +19,7 @@ use crate::cst::helpers::space;
 use crate::cst::matchers::{match_function_def, match_if, match_indented_block, match_statement};
 use crate::fix::codemods::CodegenStylist;
 use crate::fix::edits::fits;
+use crate::preview::is_collapsible_if_fix_safe_enabled;
 use crate::{Edit, Fix, FixAvailability, Violation};

 /// ## What it does
@@ -41,6 +43,12 @@ use crate::{Edit, Fix, FixAvailability, Violation};
 /// if foo and bar:
 ///     ...
 /// ```
+/// ## Preview and Fix Safety
+/// When [preview] is enabled, the fix for this rule is considered
+/// as safe. When [preview] is not enabled, the fix is always
+/// considered unsafe.
+///
+/// [preview]: https://docs.astral.sh/ruff/preview/
 ///
 /// ## Options
 ///
@@ -121,8 +129,8 @@ pub(crate) fn nested_if_statements(
         CollapsibleIf,
         TextRange::new(nested_if.start(), colon.end()),
     );
-    // The fixer preserves comments in the nested body, but removes comments between
-    // the outer and inner if statements.
+    // We skip the fix if there are comments between the outer and inner if
+    // statements.
     if !checker.comment_ranges().intersects(TextRange::new(
         nested_if.start(),
         nested_if.body()[0].start(),
@@ -139,7 +147,14 @@ pub(crate) fn nested_if_statements(
                             checker.settings().tab_size,
                         )
                     }) {
-                        Ok(Some(Fix::unsafe_edit(edit)))
+                        Ok(Some(Fix::applicable_edit(
+                            edit,
+                            if is_collapsible_if_fix_safe_enabled(checker.settings()) {
+                                Safe
+                            } else {
+                                Unsafe
+                            },
+                        )))
                     } else {
                         Ok(None)
                     }

PATCH

echo "Patch applied successfully."
