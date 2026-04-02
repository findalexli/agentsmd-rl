#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if is_explicit method already exists on PythonSource
if grep -q 'fn is_explicit(self) -> bool' crates/uv-python/src/discovery.rs; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-python/src/discovery.rs b/crates/uv-python/src/discovery.rs
index e2f4bf9f07944..ed1d5bc549637 100644
--- a/crates/uv-python/src/discovery.rs
+++ b/crates/uv-python/src/discovery.rs
@@ -2282,6 +2282,24 @@ impl PythonSource {
         }
     }

+    /// Whether this source is "explicit", e.g., it was directly provided by the user or is
+    /// an active virtual environment.
+    pub(crate) fn is_explicit(self) -> bool {
+        match self {
+            Self::ProvidedPath
+            | Self::ParentInterpreter
+            | Self::ActiveEnvironment
+            | Self::CondaPrefix => true,
+            Self::Managed
+            | Self::DiscoveredEnvironment
+            | Self::SearchPath
+            | Self::SearchPathFirst
+            | Self::Registry
+            | Self::MicrosoftStore
+            | Self::BaseCondaPrefix => false,
+        }
+    }
+
     /// Whether this source **could** be a system interpreter.
     pub(crate) fn is_maybe_system(self) -> bool {
         match self {
@@ -2343,35 +2361,19 @@ impl PythonPreference {
     /// Returns `true` if the given installation is allowed by this preference.
     ///
     /// Explicit sources (e.g., provided paths, active environments) are always allowed, even if
-    /// they conflict with the preference.
+    /// they conflict with the preference. We may want to invalidate the environment in some
+    /// cases, like in projects, but we can't distinguish between explicit requests for a
+    /// different Python preference or a persistent preference in a configuration file which
+    /// would result in overly aggressive invalidation.
     pub fn allows_installation(self, installation: &PythonInstallation) -> bool {
         let source = installation.source;
         let interpreter = &installation.interpreter;

-        // If the source is "explicit", we will not apply the Python preference, e.g., if the
-        // user has activated a virtual environment, we should always allow it. We may want to
-        // invalidate the environment in some cases, like in projects, but we can't distinguish
-        // between explicit requests for a different Python preference or a persistent preference
-        // in a configuration file which would result in overly aggressive invalidation.
-        let is_explicit = match source {
-            PythonSource::ProvidedPath
-            | PythonSource::ParentInterpreter
-            | PythonSource::ActiveEnvironment
-            | PythonSource::CondaPrefix => true,
-            PythonSource::Managed
-            | PythonSource::DiscoveredEnvironment
-            | PythonSource::SearchPath
-            | PythonSource::SearchPathFirst
-            | PythonSource::Registry
-            | PythonSource::MicrosoftStore
-            | PythonSource::BaseCondaPrefix => false,
-        };
-
         match self {
             Self::OnlyManaged => {
                 if self.allows_interpreter(interpreter) {
                     true
-                } else if is_explicit {
+                } else if source.is_explicit() {
                     debug!(
                         "Allowing unmanaged Python interpreter at `{}` (in conflict with the `python-preference`) since it is from source: {source}",
                         interpreter.sys_executable().display()
@@ -2390,7 +2392,7 @@ impl PythonPreference {
             Self::OnlySystem => {
                 if self.allows_interpreter(interpreter) {
                     true
-                } else if is_explicit {
+                } else if source.is_explicit() {
                     debug!(
                         "Allowing managed Python interpreter at `{}` (in conflict with the `python-preference`) since it is from source: {source}",
                         interpreter.sys_executable().display()

PATCH

echo "Patch applied successfully."
