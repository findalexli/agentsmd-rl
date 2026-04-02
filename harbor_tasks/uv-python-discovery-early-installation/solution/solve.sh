#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if from_tuple is already removed, patch is applied
if ! grep -q 'fn from_tuple' crates/uv-python/src/installation.rs 2>/dev/null; then
    echo "Patch already applied (from_tuple removed)."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-python/src/discovery.rs b/crates/uv-python/src/discovery.rs
index 01ee8ebd98fda..13840df6601b7 100644
--- a/crates/uv-python/src/discovery.rs
+++ b/crates/uv-python/src/discovery.rs
@@ -738,7 +738,7 @@ fn find_all_minor(
 /// the interpreter. The caller is responsible for ensuring it is applied otherwise.
 ///
 /// See [`python_executables`] for more information on discovery.
-fn python_interpreters<'a>(
+fn python_installations<'a>(
     version: &'a VersionRequest,
     implementation: Option<&'a ImplementationName>,
     platform: PlatformRequest,
@@ -746,8 +746,8 @@ fn python_interpreters<'a>(
     preference: PythonPreference,
     cache: &'a Cache,
     preview: Preview,
-) -> impl Iterator<Item = Result<(PythonSource, Interpreter), Error>> + 'a {
-    let interpreters = python_interpreters_from_executables(
+) -> impl Iterator<Item = Result<PythonInstallation, Error>> + 'a {
+    let installations = python_installations_from_executables(
         // Perform filtering on the discovered executables based on their source. This avoids
         // unnecessary interpreter queries, which are generally expensive. We'll filter again
         // with `interpreter_satisfies_environment_preference` after querying.
@@ -764,52 +764,59 @@ fn python_interpreters<'a>(
         }),
         cache,
     )
-    .filter_ok(move |(source, interpreter)| {
-        interpreter_satisfies_environment_preference(*source, interpreter, environments)
+    .filter_ok(move |installation| {
+        interpreter_satisfies_environment_preference(
+            installation.source,
+            &installation.interpreter,
+            environments,
+        )
     })
-    .filter_ok(move |(source, interpreter)| {
-        let request = version.clone().into_request_for_source(*source);
-        if request.matches_interpreter(interpreter) {
+    .filter_ok(move |installation| {
+        let request = version.clone().into_request_for_source(installation.source);
+        if request.matches_interpreter(&installation.interpreter) {
             true
         } else {
             debug!(
-                "Skipping interpreter at `{}` from {source}: does not satisfy request `{request}`",
-                interpreter.sys_executable().user_display()
+                "Skipping interpreter at `{}` from {}: does not satisfy request `{request}`",
+                installation.interpreter.sys_executable().user_display(),
+                installation.source,
             );
             false
         }
     })
-    .filter_ok(move |(source, interpreter)| {
-        satisfies_python_preference(*source, interpreter, preference)
+    .filter_ok(move |installation| {
+        satisfies_python_preference(installation.source, &installation.interpreter, preference)
     });

     if std::env::var(uv_static::EnvVars::UV_INTERNAL__TEST_PYTHON_MANAGED).is_ok() {
-        Either::Left(interpreters.map_ok(|(source, interpreter)| {
+        Either::Left(installations.map_ok(|mut installation| {
             // In test mode, change the source to `Managed` if a version was marked as such via
             // `TestContext::with_versions_as_managed`.
-            if interpreter.is_managed() {
-                (PythonSource::Managed, interpreter)
-            } else {
-                (source, interpreter)
+            if installation.interpreter.is_managed() {
+                installation.source = PythonSource::Managed;
             }
+            installation
         }))
     } else {
-        Either::Right(interpreters)
+        Either::Right(installations)
     }
 }

-/// Lazily convert Python executables into interpreters.
-fn python_interpreters_from_executables<'a>(
+/// Lazily convert Python executables into installations.
+fn python_installations_from_executables<'a>(
     executables: impl Iterator<Item = Result<(PythonSource, PathBuf), Error>> + 'a,
     cache: &'a Cache,
-) -> impl Iterator<Item = Result<(PythonSource, Interpreter), Error>> + 'a {
+) -> impl Iterator<Item = Result<PythonInstallation, Error>> + 'a {
     executables.map(|result| match result {
         Ok((source, path)) => Interpreter::query(&path, cache)
-            .map(|interpreter| (source, interpreter))
-            .inspect(|(source, interpreter)| {
+            .map(|interpreter| PythonInstallation {
+                source,
+                interpreter,
+            })
+            .inspect(|installation| {
                 debug!(
                     "Found `{}` at `{}` ({source})",
-                    interpreter.key(),
+                    installation.key(),
                     path.display()
                 );
             })
@@ -1097,12 +1104,12 @@ fn python_installation_from_directory(
     python_installation_from_executable(&executable, cache)
 }

-/// Lazily iterate over all Python interpreters on the path with the given executable name.
-fn python_interpreters_with_executable_name<'a>(
+/// Lazily iterate over all Python installations on the path with the given executable name.
+fn python_installations_with_executable_name<'a>(
     name: &'a str,
     cache: &'a Cache,
-) -> impl Iterator<Item = Result<(PythonSource, Interpreter), Error>> + 'a {
-    python_interpreters_from_executables(
+) -> impl Iterator<Item = Result<PythonInstallation, Error>> + 'a {
+    python_installations_from_executables(
         which_all(name)
             .into_iter()
             .flat_map(|inner| inner.map(|path| Ok((PythonSource::SearchPath, path)))),
@@ -1181,15 +1188,15 @@ pub fn find_python_installations<'a>(
             if preference.allows(PythonSource::SearchPath) {
                 debug!("Searching for Python interpreter with {request}");
                 Box::new(
-                    python_interpreters_with_executable_name(name, cache)
-                        .filter_ok(move |(source, interpreter)| {
+                    python_installations_with_executable_name(name, cache)
+                        .filter_ok(move |installation| {
                             interpreter_satisfies_environment_preference(
-                                *source,
-                                interpreter,
+                                installation.source,
+                                &installation.interpreter,
                                 environments,
                             )
                         })
-                        .map_ok(|tuple| Ok(PythonInstallation::from_tuple(tuple))),
+                        .map_ok(Ok),
                 )
             } else {
                 Box::new(iter::once(Err(Error::SourceNotAllowed(
@@ -1201,7 +1208,7 @@ pub fn find_python_installations<'a>(
         }
         PythonRequest::Any => Box::new({
             debug!("Searching for any Python interpreter in {sources}");
-            python_interpreters(
+            python_installations(
                 &VersionRequest::Any,
                 None,
                 PlatformRequest::default(),
@@ -1210,11 +1217,11 @@ pub fn find_python_installations<'a>(
                 cache,
                 preview,
             )
-            .map_ok(|tuple| Ok(PythonInstallation::from_tuple(tuple)))
+            .map_ok(Ok)
         }),
         PythonRequest::Default => Box::new({
             debug!("Searching for default Python interpreter in {sources}");
-            python_interpreters(
+            python_installations(
                 &VersionRequest::Default,
                 None,
                 PlatformRequest::default(),
@@ -1223,7 +1230,7 @@ pub fn find_python_installations<'a>(
                 cache,
                 preview,
             )
-            .map_ok(|tuple| Ok(PythonInstallation::from_tuple(tuple)))
+            .map_ok(Ok)
         }),
         PythonRequest::Version(version) => {
             if let Err(err) = version.check_supported() {
@@ -1231,7 +1238,7 @@ pub fn find_python_installations<'a>(
             }
             Box::new({
                 debug!("Searching for {request} in {sources}");
-                python_interpreters(
+                python_installations(
                     version,
                     None,
                     PlatformRequest::default(),
@@ -1240,12 +1247,12 @@ pub fn find_python_installations<'a>(
                     cache,
                     preview,
                 )
-                .map_ok(|tuple| Ok(PythonInstallation::from_tuple(tuple)))
+                .map_ok(Ok)
             })
         }
         PythonRequest::Implementation(implementation) => Box::new({
             debug!("Searching for a {request} interpreter in {sources}");
-            python_interpreters(
+            python_installations(
                 &VersionRequest::Default,
                 Some(implementation),
                 PlatformRequest::default(),
@@ -1254,8 +1261,8 @@ pub fn find_python_installations<'a>(
                 cache,
                 preview,
             )
-            .filter_ok(|(_source, interpreter)| implementation.matches_interpreter(interpreter))
-            .map_ok(|tuple| Ok(PythonInstallation::from_tuple(tuple)))
+            .filter_ok(|installation| implementation.matches_interpreter(&installation.interpreter))
+            .map_ok(Ok)
         }),
         PythonRequest::ImplementationVersion(implementation, version) => {
             if let Err(err) = version.check_supported() {
@@ -1263,7 +1270,7 @@ pub fn find_python_installations<'a>(
             }
             Box::new({
                 debug!("Searching for {request} in {sources}");
-                python_interpreters(
+                python_installations(
                     version,
                     Some(implementation),
                     PlatformRequest::default(),
@@ -1272,8 +1279,10 @@ pub fn find_python_installations<'a>(
                     cache,
                     preview,
                 )
-                .filter_ok(|(_source, interpreter)| implementation.matches_interpreter(interpreter))
-                .map_ok(|tuple| Ok(PythonInstallation::from_tuple(tuple)))
+                .filter_ok(|installation| {
+                    implementation.matches_interpreter(&installation.interpreter)
+                })
+                .map_ok(Ok)
             })
         }
         PythonRequest::Key(request) => {
@@ -1285,7 +1294,7 @@ pub fn find_python_installations<'a>(

             Box::new({
                 debug!("Searching for {request} in {sources}");
-                python_interpreters(
+                python_installations(
                     request.version().unwrap_or(&VersionRequest::Default),
                     request.implementation(),
                     request.platform(),
@@ -1294,10 +1303,10 @@ pub fn find_python_installations<'a>(
                     cache,
                     preview,
                 )
-                .filter_ok(move |(_source, interpreter)| {
-                    request.satisfied_by_interpreter(interpreter)
+                .filter_ok(move |installation| {
+                    request.satisfied_by_interpreter(&installation.interpreter)
                 })
-                .map_ok(|tuple| Ok(PythonInstallation::from_tuple(tuple)))
+                .map_ok(Ok)
             })
         }
     }
diff --git a/crates/uv-python/src/installation.rs b/crates/uv-python/src/installation.rs
index adbcbd3264cb9..04c8c36512f7e 100644
--- a/crates/uv-python/src/installation.rs
+++ b/crates/uv-python/src/installation.rs
@@ -38,15 +38,6 @@ pub struct PythonInstallation {
 }

 impl PythonInstallation {
-    /// Create a new [`PythonInstallation`] from a source, interpreter tuple.
-    pub(crate) fn from_tuple(tuple: (PythonSource, Interpreter)) -> Self {
-        let (source, interpreter) = tuple;
-        Self {
-            source,
-            interpreter,
-        }
-    }
-
     /// Find an installed [`PythonInstallation`].
     ///
     /// This is the standard interface for discovering a Python installation for creating

PATCH

echo "Patch applied successfully."
