#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Check if already applied
if grep -q 'ImportRequest::import(&full_module_name' crates/ruff_linter/src/rules/flake8_async/rules/async_zero_sleep.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ruff_linter/resources/test/fixtures/flake8_async/ASYNC115.py b/crates/ruff_linter/resources/test/fixtures/flake8_async/ASYNC115.py
index 6ec5d0133eee6..2711daf74f538 100644
--- a/crates/ruff_linter/resources/test/fixtures/flake8_async/ASYNC115.py
+++ b/crates/ruff_linter/resources/test/fixtures/flake8_async/ASYNC115.py
@@ -177,3 +177,12 @@ async def func():
     0 # comment
     )
     )
+
+
+async def func():
+    # https://github.com/astral-sh/ruff/issues/21693
+    # The autofix for anyio should use `import anyio.lowlevel` instead of
+    # `from anyio import lowlevel`, since `anyio.lowlevel` is a submodule.
+    from anyio import sleep as anyio_sleep
+
+    await anyio_sleep(0)  # ASYNC115
\ No newline at end of file
diff --git a/crates/ruff_linter/src/rules/flake8_async/rules/async_zero_sleep.rs b/crates/ruff_linter/src/rules/flake8_async/rules/async_zero_sleep.rs
index aee5788ae4079..572b270871c66 100644
--- a/crates/ruff_linter/src/rules/flake8_async/rules/async_zero_sleep.rs
+++ b/crates/ruff_linter/src/rules/flake8_async/rules/async_zero_sleep.rs
@@ -27,7 +27,7 @@ use crate::{AlwaysFixableViolation, Edit, Fix};
 ///
 /// Use instead:
 /// ```python
-/// import trio
+/// import trio.lowlevel
 ///
 ///
 /// async def func():
@@ -128,13 +128,18 @@ pub(crate) fn async_zero_sleep(checker: &Checker, call: &ExprCall) {

         let mut diagnostic = checker.report_diagnostic(AsyncZeroSleep { module }, call.range());
         diagnostic.try_set_fix(|| {
+            // `anyio.lowlevel` is a submodule, so we need `import anyio.lowlevel`
+            // rather than `from anyio import lowlevel`.
+            let full_module_name = format!("{module}.lowlevel");
+
             let (import_edit, binding) = checker.importer().get_or_import_symbol(
-                &ImportRequest::import_from(&module.to_string(), "lowlevel"),
+                &ImportRequest::import(&full_module_name, "checkpoint"),
                 call.func.start(),
                 checker.semantic(),
             )?;
-            let reference_edit =
-                Edit::range_replacement(format!("{binding}.checkpoint"), call.func.range());
+
+            let reference_edit = Edit::range_replacement(binding, call.func.range());
+
             let arg_edit = Edit::range_replacement("()".to_string(), call.arguments.range());
             Ok(Fix::applicable_edits(
                 import_edit,

PATCH

echo "Patch applied successfully."
