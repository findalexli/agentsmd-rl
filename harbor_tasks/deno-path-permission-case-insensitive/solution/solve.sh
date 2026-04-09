#!/usr/bin/env bash
set -euo pipefail

cd /workspace/deno

# Idempotent: skip if already applied
if grep -q 'fn comparison_path(path: &Path) -> PathBuf' runtime/permissions/lib.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/runtime/permissions/lib.rs b/runtime/permissions/lib.rs
index b842bd9cefd882..00838419572074 100644
--- a/runtime/permissions/lib.rs
+++ b/runtime/permissions/lib.rs
@@ -1292,6 +1292,9 @@ impl<
 #[derive(Clone, Debug)]
 pub struct PathQueryDescriptor<'a> {
   path: Cow<'a, Path>,
+  /// Lowercased on Windows for case-insensitive comparison; same as `path` on
+  /// other platforms. Used by PartialEq, starts_with, etc.
+  cmp_path: PathBuf,
   /// Custom requested display name when differs from resolved.
   requested: Option<String>,
   is_windows_device_path: bool,
@@ -1299,7 +1302,7 @@ pub struct PathQueryDescriptor<'a> {

 impl PartialEq for PathQueryDescriptor<'_> {
   fn eq(&self, other: &Self) -> bool {
-    self.path == other.path
+    self.cmp_path == other.cmp_path
   }
 }

@@ -1307,7 +1310,18 @@ impl Eq for PathQueryDescriptor<'_> {}

 impl PartialEq<PathDescriptor> for PathQueryDescriptor<'_> {
   fn eq(&self, other: &PathDescriptor) -> bool {
-    self.path == other.path
+    self.cmp_path == other.cmp_path
+  }
+}
+
+/// On Windows, returns a lowercased copy of the path for case-insensitive
+/// comparison, matching NTFS behavior. On other platforms, returns a clone.
+#[inline]
+fn comparison_path(path: &Path) -> PathBuf {
+  if cfg!(windows) {
+    PathBuf::from(path.to_string_lossy().to_ascii_lowercase())
+  } else {
+    path.to_path_buf()
   }
 }

@@ -1338,8 +1352,10 @@ impl<'a> PathQueryDescriptor<'a> {
         Some(path.to_string_lossy().into_owned()),
       )
     };
+    let cmp_path = comparison_path(&path);
     Ok(Self {
       path,
+      cmp_path,
       requested,
       is_windows_device_path,
     })
@@ -1357,8 +1373,10 @@ impl<'a> PathQueryDescriptor<'a> {
     } else {
       normalize_path(path)
     };
+    let cmp_path = comparison_path(&path);
     Self {
       path,
+      cmp_path,
       requested: None,
       is_windows_device_path,
     }
@@ -1372,7 +1390,7 @@ impl<'a> PathQueryDescriptor<'a> {
   }

   pub fn starts_with(&self, base: &PathDescriptor) -> bool {
-    self.path.starts_with(&base.path)
+    self.cmp_path.starts_with(&base.cmp_path)
   }

   pub fn display_name(&self) -> Cow<'_, str> {
@@ -1385,6 +1403,7 @@ impl<'a> PathQueryDescriptor<'a> {
   pub fn as_descriptor(&self) -> PathDescriptor {
     PathDescriptor {
       path: self.path.to_path_buf(),
+      cmp_path: self.cmp_path.clone(),
       requested: self.requested.clone(),
       is_windows_device_path: self.is_windows_device_path,
     }
@@ -1393,6 +1412,7 @@ impl<'a> PathQueryDescriptor<'a> {
   pub fn into_descriptor(self) -> PathDescriptor {
     PathDescriptor {
       path: self.path.into_owned(),
+      cmp_path: self.cmp_path,
       requested: self.requested,
       is_windows_device_path: self.is_windows_device_path,
     }
@@ -1475,6 +1495,9 @@ impl QueryDescriptor for ReadQueryDescriptor<'_> {
 #[derive(Clone, Debug)]
 pub struct PathDescriptor {
   path: PathBuf,
+  /// Lowercased on Windows for case-insensitive comparison; same as `path` on
+  /// other platforms. Used by PartialEq, Hash, starts_with, cmp_*.
+  cmp_path: PathBuf,
   /// Custom requested display name when differs from resolved.
   requested: Option<String>,
   is_windows_device_path: bool,
@@ -1482,7 +1505,7 @@ pub struct PathDescriptor {

 impl PartialEq for PathDescriptor {
   fn eq(&self, other: &Self) -> bool {
-    self.path == other.path
+    self.cmp_path == other.cmp_path
   }
 }

@@ -1490,7 +1513,7 @@ impl Eq for PathDescriptor {}

 impl Hash for PathDescriptor {
   fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
-    self.path.hash(state);
+    self.cmp_path.hash(state);
   }
 }

@@ -1519,8 +1542,10 @@ impl PathDescriptor {
         Some(path.to_string_lossy().into_owned()),
       )
     };
+    let cmp_path = comparison_path(&path);
     Self {
       path: path.into_owned(),
+      cmp_path,
       requested: display,
       is_windows_device_path,
     }
@@ -1531,7 +1556,7 @@ impl PathDescriptor {
   }

   pub fn starts_with(&self, base: &PathQueryDescriptor) -> bool {
-    self.path.starts_with(&base.path)
+    self.cmp_path.starts_with(&base.cmp_path)
   }

   pub fn display_name(&self) -> Cow<'_, str> {
@@ -1544,6 +1569,7 @@ impl PathDescriptor {
   pub fn as_query_descriptor(&self) -> PathQueryDescriptor<'static> {
     PathQueryDescriptor {
       path: Cow::Owned(self.path.clone()),
+      cmp_path: self.cmp_path.clone(),
       requested: self.requested.clone(),
       is_windows_device_path: self.is_windows_device_path,
     }
@@ -1566,21 +1592,21 @@ impl PathDescriptor {
   }

   fn cmp_allow_allow(&self, other: &PathDescriptor) -> Ordering {
-    if self.path == other.path {
+    if self.cmp_path == other.cmp_path {
       Ordering::Equal
-    } else if other.path.starts_with(&self.path) {
+    } else if other.cmp_path.starts_with(&self.cmp_path) {
       Ordering::Greater
-    } else if self.path.starts_with(&other.path) {
+    } else if self.cmp_path.starts_with(&other.cmp_path) {
       Ordering::Less
     } else {
-      self.path.cmp(&other.path)
+      self.cmp_path.cmp(&other.cmp_path)
     }
   }

   fn cmp_allow_deny(&self, other: &PathDescriptor) -> Ordering {
-    if other.path.starts_with(&self.path) {
+    if other.cmp_path.starts_with(&self.cmp_path) {
       Ordering::Greater
-    } else if self.path.starts_with(&other.path) {
+    } else if self.cmp_path.starts_with(&other.cmp_path) {
       Ordering::Less
     } else {
       Ordering::Greater
@@ -2489,11 +2515,15 @@ impl<'a> RunQueryDescriptor<'a> {
         .map_err(PathResolveError::CwdResolve)?;
       match which::which_in(sys.clone(), requested, sys.env_var_os("PATH"), cwd)
       {
-        Ok(resolved) => Ok(RunQueryDescriptor::Path(PathQueryDescriptor {
-          path: Cow::Owned(resolved),
-          requested: Some(requested.to_string()),
-          is_windows_device_path: false,
-        })),
+        Ok(resolved) => {
+          let cmp_path = comparison_path(&resolved);
+          Ok(RunQueryDescriptor::Path(PathQueryDescriptor {
+            path: Cow::Owned(resolved),
+            cmp_path,
+            requested: Some(requested.to_string()),
+            is_windows_device_path: false,
+          }))
+        }
         Err(_) => Ok(RunQueryDescriptor::Name(requested.to_string())),
       }
     }
@@ -2769,6 +2799,7 @@ impl<'a> SpecialFilePathQueryDescriptor<'a> {
     let PathQueryDescriptor {
       is_windows_device_path,
       path,
+      cmp_path: _,
       requested,
     } = path;
     // On Linux, /proc may contain magic links that we don't want to resolve
@@ -5314,8 +5345,10 @@ mod tests {
       } else {
         PathBuf::from("/").join(path)
       };
+      let cmp_path = comparison_path(&path);
       PathDescriptor {
         path,
+        cmp_path,
         requested: None,
         is_windows_device_path: false,
       }
@@ -5396,8 +5429,10 @@ mod tests {
       &self,
       path: Cow<'a, Path>,
     ) -> Result<PathQueryDescriptor<'a>, PathResolveError> {
+      let cmp_path = comparison_path(&path);
       Ok(PathQueryDescriptor {
         path,
+        cmp_path,
         requested: None,
         is_windows_device_path: false,
       })
@@ -9191,4 +9226,65 @@ mod tests {
       "failed second to first"
     );
   }
+
+  #[test]
+  #[cfg(windows)]
+  fn check_path_case_insensitive() {
+    set_prompter(Box::new(TestPrompter));
+    let parser = TestPermissionDescriptorParser;
+    let perms = Permissions::from_options(
+      &parser,
+      &PermissionsOptions {
+        allow_read: Some(svec!["C:\\Users\\Admin"]),
+        deny_read: Some(svec!["C:\\Users\\Admin\\Secret"]),
+        ..Default::default()
+      },
+    )
+    .unwrap();
+    let perms = PermissionsContainer::new(Arc::new(parser), perms);
+
+    // Matching case should be allowed
+    assert!(
+      perms
+        .check_open(
+          Cow::Borrowed(Path::new("C:\\Users\\Admin\\file.txt")),
+          OpenAccessKind::Read,
+          Some("api"),
+        )
+        .is_ok()
+    );
+
+    // Different case should also be allowed
+    assert!(
+      perms
+        .check_open(
+          Cow::Borrowed(Path::new("c:\\users\\admin\\file.txt")),
+          OpenAccessKind::Read,
+          Some("api"),
+        )
+        .is_ok()
+    );
+
+    // Deny with matching case should block
+    assert!(
+      perms
+        .check_open(
+          Cow::Borrowed(Path::new("C:\\Users\\Admin\\Secret\\data.txt")),
+          OpenAccessKind::Read,
+          Some("api"),
+        )
+        .is_err()
+    );
+
+    // Deny with different case should also block
+    assert!(
+      perms
+        .check_open(
+          Cow::Borrowed(Path::new("c:\\users\\admin\\secret\\data.txt")),
+          OpenAccessKind::Read,
+          Some("api"),
+        )
+        .is_err()
+    );
+  }
 }
diff --git a/tests/specs/permission/path_case_insensitive/__test__.jsonc b/tests/specs/permission/path_case_insensitive/__test__.jsonc
new file mode 100644
index 00000000000000..a771d0c433f6da
--- /dev/null
+++ b/tests/specs/permission/path_case_insensitive/__test__.jsonc
@@ -0,0 +1,5 @@
+{
+  "if": "windows",
+  "args": "run -A main.ts",
+  "output": "[WILDCARD]BLOCKED:NotCapable\n"
+}
diff --git a/tests/specs/permission/path_case_insensitive/main.ts b/tests/specs/permission/path_case_insensitive/main.ts
new file mode 100644
index 00000000000000..6a246e4a9a9afd
--- /dev/null
+++ b/tests/specs/permission/path_case_insensitive/main.ts
@@ -0,0 +1,44 @@
+// Test that path permissions are case-insensitive on Windows.
+// A deny-read rule should block access regardless of the path casing.
+const dir = Deno.makeTempDirSync();
+const file = dir + "\\secret.txt";
+Deno.writeTextFileSync(file, "secret");
+
+const lowerDir = dir.toLowerCase();
+const lowerFile = lowerDir + "\\secret.txt";
+
+// Write the test script to a separate temp dir (not under the denied path).
+const scriptDir = Deno.makeTempDirSync();
+const scriptFile = scriptDir + "\\test_read.ts";
+Deno.writeTextFileSync(
+  scriptFile,
+  `try {
+  Deno.readTextFileSync(${JSON.stringify(lowerFile)});
+  console.log("BYPASSED");
+} catch (e) {
+  console.log("BLOCKED:" + e.constructor.name);
+}
+`,
+);
+
+// Spawn a subprocess with --deny-read on the original-case path,
+// then run the script which reads via the lowered-case path.
+const result = new Deno.Command(Deno.execPath(), {
+  args: [
+    "run",
+    "--allow-read",
+    `--deny-read=${dir}`,
+    scriptFile,
+  ],
+}).outputSync();
+
+const stdout = new TextDecoder().decode(result.stdout).trim();
+const stderr = new TextDecoder().decode(result.stderr).trim();
+if (stdout) {
+  console.log(stdout);
+} else {
+  console.log(stderr || "NO OUTPUT");
+}
+
+Deno.removeSync(dir, { recursive: true });
+Deno.removeSync(scriptDir, { recursive: true });

PATCH

echo "Patch applied successfully."
