#!/usr/bin/env bash
set -euo pipefail
cd /repo

# Check if already applied
if grep -q 'fn allows_installation' crates/uv-python/src/discovery.rs 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-python/src/discovery.rs b/crates/uv-python/src/discovery.rs
index 13840df6601b7..e2f4bf9f07944 100644
--- a/crates/uv-python/src/discovery.rs
+++ b/crates/uv-python/src/discovery.rs
@@ -784,9 +784,7 @@ fn python_installations<'a>(
             false
         }
     })
-    .filter_ok(move |installation| {
-        satisfies_python_preference(installation.source, &installation.interpreter, preference)
-    });
+    .filter_ok(move |installation| preference.allows_installation(installation));

     if std::env::var(uv_static::EnvVars::UV_INTERNAL__TEST_PYTHON_MANAGED).is_ok() {
         Either::Left(installations.map_ok(|mut installation| {
@@ -930,95 +928,6 @@ fn source_satisfies_environment_preference(
     }
 }

-/// Returns true if a Python interpreter matches the [`PythonPreference`].
-pub fn satisfies_python_preference(
-    source: PythonSource,
-    interpreter: &Interpreter,
-    preference: PythonPreference,
-) -> bool {
-    // If the source is "explicit", we will not apply the Python preference, e.g., if the user has
-    // activated a virtual environment, we should always allow it. We may want to invalidate the
-    // environment in some cases, like in projects, but we can't distinguish between explicit
-    // requests for a different Python preference or a persistent preference in a configuration file
-    // which would result in overly aggressive invalidation.
-    let is_explicit = match source {
-        PythonSource::ProvidedPath
-        | PythonSource::ParentInterpreter
-        | PythonSource::ActiveEnvironment
-        | PythonSource::CondaPrefix => true,
-        PythonSource::Managed
-        | PythonSource::DiscoveredEnvironment
-        | PythonSource::SearchPath
-        | PythonSource::SearchPathFirst
-        | PythonSource::Registry
-        | PythonSource::MicrosoftStore
-        | PythonSource::BaseCondaPrefix => false,
-    };
-
-    match preference {
-        PythonPreference::OnlyManaged => {
-            // Perform a fast check using the source before querying the interpreter
-            if matches!(source, PythonSource::Managed) || interpreter.is_managed() {
-                true
-            } else {
-                if is_explicit {
-                    debug!(
-                        "Allowing unmanaged Python interpreter at `{}` (in conflict with the `python-preference`) since it is from source: {source}",
-                        interpreter.sys_executable().display()
-                    );
-                    true
-                } else {
-                    debug!(
-                        "Ignoring Python interpreter at `{}`: only managed interpreters allowed",
-                        interpreter.sys_executable().display()
-                    );
-                    false
-                }
-            }
-        }
-        // If not "only" a kind, any interpreter is okay
-        PythonPreference::Managed | PythonPreference::System => true,
-        PythonPreference::OnlySystem => {
-            if is_system_interpreter(source, interpreter) {
-                true
-            } else {
-                if is_explicit {
-                    debug!(
-                        "Allowing managed Python interpreter at `{}` (in conflict with the `python-preference`) since it is from source: {source}",
-                        interpreter.sys_executable().display()
-                    );
-                    true
-                } else {
-                    debug!(
-                        "Ignoring Python interpreter at `{}`: only system interpreters allowed",
-                        interpreter.sys_executable().display()
-                    );
-                    false
-                }
-            }
-        }
-    }
-}
-
-pub(crate) fn is_system_interpreter(source: PythonSource, interpreter: &Interpreter) -> bool {
-    match source {
-        // A managed interpreter is never a system interpreter
-        PythonSource::Managed => false,
-        // We can't be sure if this is a system interpreter without checking
-        PythonSource::ProvidedPath
-        | PythonSource::ParentInterpreter
-        | PythonSource::ActiveEnvironment
-        | PythonSource::CondaPrefix
-        | PythonSource::DiscoveredEnvironment
-        | PythonSource::SearchPath
-        | PythonSource::SearchPathFirst
-        | PythonSource::Registry
-        | PythonSource::BaseCondaPrefix => !interpreter.is_managed(),
-        // Managed interpreters should never be found in the store
-        PythonSource::MicrosoftStore => true,
-    }
-}
-
 /// Check if an encountered error is critical and should stop discovery.
 ///
 /// Returns false when an error could be due to a faulty Python installation and we should continue searching for a working one.
@@ -1133,7 +1042,7 @@ pub fn find_python_installations<'a>(

     match request {
         PythonRequest::File(path) => Box::new(iter::once({
-            if preference.allows(PythonSource::ProvidedPath) {
+            if preference.allows_source(PythonSource::ProvidedPath) {
                 debug!("Checking for Python interpreter at {request}");
                 match python_installation_from_executable(path, cache) {
                     Ok(installation) => Ok(Ok(installation)),
@@ -1159,7 +1068,7 @@ pub fn find_python_installations<'a>(
             }
         })),
         PythonRequest::Directory(path) => Box::new(iter::once({
-            if preference.allows(PythonSource::ProvidedPath) {
+            if preference.allows_source(PythonSource::ProvidedPath) {
                 debug!("Checking for Python interpreter in {request}");
                 match python_installation_from_directory(path, cache) {
                     Ok(installation) => Ok(Ok(installation)),
@@ -1185,7 +1094,7 @@ pub fn find_python_installations<'a>(
             }
         })),
         PythonRequest::ExecutableName(name) => {
-            if preference.allows(PythonSource::SearchPath) {
+            if preference.allows_source(PythonSource::SearchPath) {
                 debug!("Searching for Python interpreter with {request}");
                 Box::new(
                     python_installations_with_executable_name(name, cache)
@@ -1400,9 +1309,7 @@ pub(crate) fn find_python_installation(

         // If it's a managed Python installation, and system interpreters are preferred, skip it
         // for now.
-        if matches!(preference, PythonPreference::System)
-            && !is_system_interpreter(installation.source, installation.interpreter())
-        {
+        if matches!(preference, PythonPreference::System) && installation.is_managed() {
             debug!(
                 "Skipping managed installation {}: system installation preferred",
                 installation.key()
@@ -2393,7 +2300,7 @@ impl PythonSource {
 }

 impl PythonPreference {
-    fn allows(self, source: PythonSource) -> bool {
+    fn allows_source(self, source: PythonSource) -> bool {
         // If not dealing with a system interpreter source, we don't care about the preference
         if !matches!(
             source,
@@ -2421,6 +2328,85 @@ impl PythonPreference {
         }
     }

+    /// Returns `true` if the given interpreter is allowed by this preference.
+    ///
+    /// Unlike [`PythonPreference::allows_source`], which checks the [`PythonSource`], this checks
+    /// whether the interpreter's base prefix is in a managed location.
+    pub fn allows_interpreter(self, interpreter: &Interpreter) -> bool {
+        match self {
+            Self::OnlyManaged => interpreter.is_managed(),
+            Self::OnlySystem => !interpreter.is_managed(),
+            Self::Managed | Self::System => true,
+        }
+    }
+
+    /// Returns `true` if the given installation is allowed by this preference.
+    ///
+    /// Explicit sources (e.g., provided paths, active environments) are always allowed, even if
+    /// they conflict with the preference.
+    pub fn allows_installation(self, installation: &PythonInstallation) -> bool {
+        let source = installation.source;
+        let interpreter = &installation.interpreter;
+
+        // If the source is "explicit", we will not apply the Python preference, e.g., if the
+        // user has activated a virtual environment, we should always allow it. We may want to
+        // invalidate the environment in some cases, like in projects, but we can't distinguish
+        // between explicit requests for a different Python preference or a persistent preference
+        // in a configuration file which would result in overly aggressive invalidation.
+        let is_explicit = match source {
+            PythonSource::ProvidedPath
+            | PythonSource::ParentInterpreter
+            | PythonSource::ActiveEnvironment
+            | PythonSource::CondaPrefix => true,
+            PythonSource::Managed
+            | PythonSource::DiscoveredEnvironment
+            | PythonSource::SearchPath
+            | PythonSource::SearchPathFirst
+            | PythonSource::Registry
+            | PythonSource::MicrosoftStore
+            | PythonSource::BaseCondaPrefix => false,
+        };
+
+        match self {
+            Self::OnlyManaged => {
+                if self.allows_interpreter(interpreter) {
+                    true
+                } else if is_explicit {
+                    debug!(
+                        "Allowing unmanaged Python interpreter at `{}` (in conflict with the `python-preference`) since it is from source: {source}",
+                        interpreter.sys_executable().display()
+                    );
+                    true
+                } else {
+                    debug!(
+                        "Ignoring Python interpreter at `{}`: only managed interpreters allowed",
+                        interpreter.sys_executable().display()
+                    );
+                    false
+                }
+            }
+            // If not "only" a kind, any interpreter is okay
+            Self::Managed | Self::System => true,
+            Self::OnlySystem => {
+                if self.allows_interpreter(interpreter) {
+                    true
+                } else if is_explicit {
+                    debug!(
+                        "Allowing managed Python interpreter at `{}` (in conflict with the `python-preference`) since it is from source: {source}",
+                        interpreter.sys_executable().display()
+                    );
+                    true
+                } else {
+                    debug!(
+                        "Ignoring Python interpreter at `{}`: only system interpreters allowed",
+                        interpreter.sys_executable().display()
+                    );
+                    false
+                }
+            }
+        }
+    }
+
     /// Returns a new preference when the `--system` flag is used.
     ///
     /// This will convert [`PythonPreference::Managed`] to [`PythonPreference::System`] when system
diff --git a/crates/uv-python/src/installation.rs b/crates/uv-python/src/installation.rs
index 04c8c36512f7e..df37c10709fea 100644
--- a/crates/uv-python/src/installation.rs
+++ b/crates/uv-python/src/installation.rs
@@ -38,6 +38,14 @@ pub struct PythonInstallation {
 }

 impl PythonInstallation {
+    /// Create a new [`PythonInstallation`] from a source and interpreter.
+    pub fn new(source: PythonSource, interpreter: Interpreter) -> Self {
+        Self {
+            source,
+            interpreter,
+        }
+    }
+
     /// Find an installed [`PythonInstallation`].
     ///
     /// This is the standard interface for discovering a Python installation for creating
@@ -350,6 +358,13 @@ impl PythonInstallation {
         LenientImplementationName::from(self.interpreter.implementation_name())
     }

+    /// Returns `true` if this is a managed (uv-installed) Python installation.
+    ///
+    /// Uses the source as a fast path, then falls back to checking the interpreter's base prefix.
+    pub fn is_managed(&self) -> bool {
+        self.source.is_managed() || self.interpreter.is_managed()
+    }
+
     /// Whether this is a CPython installation.
     ///
     /// Returns false if it is an alternative implementation, e.g., PyPy.
diff --git a/crates/uv-python/src/lib.rs b/crates/uv-python/src/lib.rs
index 54f6fd79f9419..cc03792ea7808 100644
--- a/crates/uv-python/src/lib.rs
+++ b/crates/uv-python/src/lib.rs
@@ -8,7 +8,7 @@ use uv_static::EnvVars;
 pub use crate::discovery::{
     EnvironmentPreference, Error as DiscoveryError, PythonDownloads, PythonNotFound,
     PythonPreference, PythonRequest, PythonSource, PythonVariant, VersionRequest,
-    find_python_installations, satisfies_python_preference,
+    find_python_installations,
 };
 pub use crate::downloads::PlatformRequest;
 pub use crate::environment::{InvalidEnvironmentKind, PythonEnvironment};
diff --git a/crates/uv/src/commands/project/mod.rs b/crates/uv/src/commands/project/mod.rs
index 07540ea009e94..e1c389d768079 100644
--- a/crates/uv/src/commands/project/mod.rs
+++ b/crates/uv/src/commands/project/mod.rs
@@ -33,7 +33,6 @@ use uv_python::{
     BrokenLink, EnvironmentPreference, Interpreter, InvalidEnvironmentKind, PythonDownloads,
     PythonEnvironment, PythonInstallation, PythonPreference, PythonRequest, PythonSource,
     PythonVariant, PythonVersionFile, VersionFileDiscoveryOptions, VersionRequest,
-    satisfies_python_preference,
 };
 use uv_requirements::upgrade::{LockedRequirements, read_lock_requirements};
 use uv_requirements::{NamedRequirementsResolver, RequirementsSpecification};
@@ -919,11 +918,10 @@ fn environment_is_usable(
         }
     }

-    if satisfies_python_preference(
+    if python_preference.allows_installation(&PythonInstallation::new(
         PythonSource::DiscoveredEnvironment,
-        environment.interpreter(),
-        python_preference,
-    ) {
+        environment.interpreter().clone(),
+    )) {
         trace!(
             "The virtual environment's Python interpreter meets the Python preference: `{}`",
             python_preference
diff --git a/crates/uv/src/commands/python/list.rs b/crates/uv/src/commands/python/list.rs
index 135e272a9fad1..0df0d50090f92 100644
--- a/crates/uv/src/commands/python/list.rs
+++ b/crates/uv/src/commands/python/list.rs
@@ -170,11 +170,7 @@ pub(crate) async fn list(
             .filter_map(Result::ok)
             // Apply the `PythonPreference` to discovered interpreters, since we may have
             // expanded it above
-            .filter(|installation| match python_preference {
-                PythonPreference::OnlyManaged => installation.interpreter().is_managed(),
-                PythonPreference::OnlySystem => !installation.interpreter().is_managed(),
-                PythonPreference::Managed | PythonPreference::System => true,
-            }))
+            .filter(|installation| python_preference.allows_installation(installation)))
             }
             PythonListKinds::Downloads => None,
         };

PATCH
