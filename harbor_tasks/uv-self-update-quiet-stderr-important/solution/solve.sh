#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if stderr_important already exists, patch is applied
if grep -q 'fn stderr_important' crates/uv/src/printer.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv/src/printer.rs b/crates/uv/src/printer.rs
index 234a569c7872c..4848a59375833 100644
--- a/crates/uv/src/printer.rs
+++ b/crates/uv/src/printer.rs
@@ -52,6 +52,17 @@ impl Printer {
         }
     }

+    /// Return the [`Stderr`] for this printer.
+    pub(crate) fn stderr_important(self) -> Stderr {
+        match self {
+            Self::Silent => Stderr::Disabled,
+            Self::Quiet => Stderr::Enabled,
+            Self::Default => Stderr::Enabled,
+            Self::Verbose => Stderr::Enabled,
+            Self::NoProgress => Stderr::Enabled,
+        }
+    }
+
     /// Return the [`Stderr`] for this printer.
     pub(crate) fn stderr(self) -> Stderr {
         match self {
diff --git a/crates/uv/src/commands/self_update.rs b/crates/uv/src/commands/self_update.rs
index 6d4fa9a571bb2..2a1256727c674 100644
--- a/crates/uv/src/commands/self_update.rs
+++ b/crates/uv/src/commands/self_update.rs
@@ -24,7 +24,7 @@ pub(crate) async fn self_update(
 ) -> Result<ExitStatus> {
     if client_builder.is_offline() {
         writeln!(
-            printer.stderr(),
+            printer.stderr_important(),
             "{}",
             format_args!(
                 "{}{} Self-update is not possible because network connectivity is disabled (i.e., with `--offline`)",
@@ -47,7 +47,7 @@ pub(crate) async fn self_update(
     let Ok(updater) = updater.load_receipt() else {
         debug!("No receipt found; assuming uv was installed via a package manager");
         writeln!(
-            printer.stderr(),
+            printer.stderr_important(),
             "{}",
             format_args!(
                 concat!(
@@ -79,7 +79,7 @@ pub(crate) async fn self_update(
         let receipt_prefix = updater.install_prefix_root()?;

         writeln!(
-            printer.stderr(),
+            printer.stderr_important(),
             "{}",
             format_args!(
                 concat!(
@@ -152,7 +152,7 @@ pub(crate) async fn self_update(

         if dry_run {
             writeln!(
-                printer.stderr(),
+                printer.stderr_important(),
                 "Would update uv from {} to {}",
                 format!("v{}", env!("CARGO_PKG_VERSION")).bold().white(),
                 format!("v{}", resolved.version).bold().white(),
@@ -188,7 +188,7 @@ pub(crate) async fn self_update(
                 }
             };
             writeln!(
-                printer.stderr(),
+                printer.stderr_important(),
                 "Would update uv from {} to {}",
                 format!("v{}", env!("CARGO_PKG_VERSION")).bold().white(),
                 version.bold().white(),
@@ -309,7 +309,7 @@ async fn run_updater(
             };

             writeln!(
-                printer.stderr(),
+                printer.stderr_important(),
                 "{}",
                 format_args!(
                     "{}{} {direction} uv {}! {}",
@@ -340,7 +340,7 @@ async fn run_updater(
             return if let AxoupdateError::Reqwest(err) = err {
                 if err.status() == Some(http::StatusCode::FORBIDDEN) && !has_token {
                     writeln!(
-                        printer.stderr(),
+                        printer.stderr_important(),
                         "{}",
                         format_args!(
                             "{}{} GitHub API rate limit exceeded. Please provide a GitHub token via the {} option.",

PATCH

echo "Patch applied successfully."
