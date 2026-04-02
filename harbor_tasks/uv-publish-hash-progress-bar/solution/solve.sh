#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Check if already applied (look for on_hash_start in the Reporter trait)
if grep -q 'fn on_hash_start' crates/uv-publish/src/lib.rs; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-publish/src/lib.rs b/crates/uv-publish/src/lib.rs
index 4123186f665c4..be6a77fd0fed4 100644
--- a/crates/uv-publish/src/lib.rs
+++ b/crates/uv-publish/src/lib.rs
@@ -160,6 +160,9 @@ pub trait Reporter: Send + Sync + 'static {
     fn on_upload_start(&self, name: &str, size: Option<u64>) -> usize;
     fn on_upload_progress(&self, id: usize, inc: u64);
     fn on_upload_complete(&self, id: usize);
+    fn on_hash_start(&self, name: &DistFilename, size: Option<u64>) -> usize;
+    fn on_hash_progress(&self, id: usize, inc: u64);
+    fn on_hash_complete(&self, id: usize);
 }

 /// Context for using a fresh registry client for check URL requests.
@@ -622,6 +625,7 @@ pub async fn upload(
                             &group.file,
                             &group.filename,
                             download_concurrency,
+                            reporter.clone(),
                         )
                         .await?
                         {
@@ -941,6 +945,7 @@ pub async fn check_url(
     file: &Path,
     filename: &DistFilename,
     download_concurrency: &Semaphore,
+    reporter: Arc<impl Reporter>,
 ) -> Result<bool, PublishError> {
     let CheckUrlClient {
         index_url,
@@ -1016,14 +1021,16 @@ pub async fn check_url(
     if let Some(remote_hash) = archived_file.hashes.first() {
         // We accept the risk for TOCTOU errors here, since we already read the file once before the
         // streaming upload to compute the hash for the form metadata.
-        let local_hash = &hash_file(file, vec![Hasher::from(remote_hash.algorithm)])
-            .await
-            .map_err(|err| {
-                PublishError::PublishPrepare(
-                    file.to_path_buf(),
-                    Box::new(PublishPrepareError::Io(err)),
-                )
-            })?[0];
+        let local_hash = &hash_file(
+            file,
+            filename,
+            vec![Hasher::from(remote_hash.algorithm)],
+            reporter,
+        )
+        .await
+        .map_err(|err| {
+            PublishError::PublishPrepare(file.to_path_buf(), Box::new(PublishPrepareError::Io(err)))
+        })?[0];
         if local_hash.digest == remote_hash.digest {
             debug!(
                 "Found {filename} in the registry with matching hash {}",
@@ -1046,12 +1053,30 @@ pub async fn check_url(
 /// Calculate the requested hashes of a file.
 async fn hash_file(
     path: impl AsRef<Path>,
+    filename: &DistFilename,
     hashers: Vec<Hasher>,
+    reporter: Arc<impl Reporter>,
 ) -> Result<Vec<HashDigest>, io::Error> {
-    debug!("Hashing {}", path.as_ref().display());
-    let file = BufReader::new(File::open(path.as_ref()).await?);
+    let path = path.as_ref();
+    debug!("Hashing {}", path.user_display());
+
+    let file = File::open(path).await?;
+    let file_size = file.metadata().await?.len();
+    let idx = reporter.on_hash_start(filename, Some(file_size));
+
+    let reader = BufReader::new(file);
     let mut hashers = hashers;
-    HashReader::new(file, &mut hashers).finish().await?;
+    let reporter_clone = reporter.clone();
+    let mut reader = HashReader::new(
+        ProgressReader::new(reader, move |read| {
+            reporter_clone.on_hash_progress(idx, read as u64);
+        }),
+        &mut hashers,
+    );
+
+    let result = reader.finish().await;
+    reporter.on_hash_complete(idx);
+    result?;

     Ok(hashers
         .into_iter()
@@ -1131,13 +1156,16 @@ impl FormMetadata {
     pub async fn read_from_file(
         file: &Path,
         filename: &DistFilename,
+        reporter: Arc<impl Reporter>,
     ) -> Result<Self, PublishPrepareError> {
         let hashes = hash_file(
             file,
+            filename,
             vec![
                 Hasher::from(HashAlgorithm::Sha256),
                 Hasher::from(HashAlgorithm::Blake2b),
             ],
+            reporter,
         )
         .await?;

@@ -1505,6 +1533,11 @@ mod tests {
         }
         fn on_upload_progress(&self, _id: usize, _inc: u64) {}
         fn on_upload_complete(&self, _id: usize) {}
+        fn on_hash_start(&self, _name: &DistFilename, _size: Option<u64>) -> usize {
+            0
+        }
+        fn on_hash_progress(&self, _id: usize, _inc: u64) {}
+        fn on_hash_complete(&self, _id: usize) {}
     }

     async fn mock_server_upload(mock_server: &MockServer) -> Result<bool, PublishError> {
@@ -1519,9 +1552,10 @@ mod tests {
             attestations: vec![],
         };

-        let form_metadata = FormMetadata::read_from_file(&group.file, &group.filename)
-            .await
-            .unwrap();
+        let form_metadata =
+            FormMetadata::read_from_file(&group.file, &group.filename, Arc::new(DummyReporter))
+                .await
+                .unwrap();

         let client = BaseClientBuilder::default()
             .redirect(RedirectPolicy::NoRedirect)
@@ -1840,9 +1874,10 @@ mod tests {
             }
         };

-        let form_metadata = FormMetadata::read_from_file(&group.file, &group.filename)
-            .await
-            .unwrap();
+        let form_metadata =
+            FormMetadata::read_from_file(&group.file, &group.filename, Arc::new(DummyReporter))
+                .await
+                .unwrap();

         let formatted_metadata = form_metadata
             .iter()
@@ -1962,9 +1997,10 @@ mod tests {
             }
         };

-        let form_metadata = FormMetadata::read_from_file(&group.file, &group.filename)
-            .await
-            .unwrap();
+        let form_metadata =
+            FormMetadata::read_from_file(&group.file, &group.filename, Arc::new(DummyReporter))
+                .await
+                .unwrap();

         let formatted_metadata = form_metadata
             .iter()
diff --git a/crates/uv/src/commands/publish.rs b/crates/uv/src/commands/publish.rs
index 95e20fa4d1081..55544c0b4606d 100644
--- a/crates/uv/src/commands/publish.rs
+++ b/crates/uv/src/commands/publish.rs
@@ -217,12 +217,15 @@ pub(crate) async fn publish(
             );
         }

+        let reporter = Arc::new(PublishReporter::single(printer));
+
         if let Some(check_url_client) = &check_url_client {
             match uv_publish::check_url(
                 check_url_client,
                 &group.file,
                 &group.filename,
                 &download_concurrency,
+                reporter.clone(),
             )
             .await
             {
@@ -260,27 +263,36 @@ pub(crate) async fn publish(
             writeln!(
                 printer.stderr(),
                 "{} {} {}",
-                "Uploading".bold().green(),
+                "Hashing".bold().green(),
                 group.filename,
                 format!("({bytes:.1}{unit})").dimmed()
             )?;
         }

         // Collect the metadata for the file.
-        let form_metadata = match FormMetadata::read_from_file(&group.file, &group.filename)
-            .await
-            .map_err(|err| PublishError::PublishPrepare(group.file.clone(), Box::new(err)))
-        {
-            Ok(metadata) => metadata,
-            Err(err) => {
-                if dry_run {
-                    write_error_chain(&err, printer.stderr(), "error", AnsiColors::Red)?;
-                    error_count += 1;
-                    continue;
+        let form_metadata =
+            match FormMetadata::read_from_file(&group.file, &group.filename, reporter.clone())
+                .await
+                .map_err(|err| PublishError::PublishPrepare(group.file.clone(), Box::new(err)))
+            {
+                Ok(metadata) => metadata,
+                Err(err) => {
+                    if dry_run {
+                        write_error_chain(&err, printer.stderr(), "error", AnsiColors::Red)?;
+                        error_count += 1;
+                        continue;
+                    }
+                    return Err(err.into());
                 }
-                return Err(err.into());
-            }
-        };
+            };
+
+        writeln!(
+            printer.stderr(),
+            "{} {} {}",
+            "Uploading".bold().green(),
+            group.filename,
+            format!("({bytes:.1}{unit})").dimmed()
+        )?;

         let uploaded = if direct {
             if dry_run {
@@ -320,7 +332,6 @@ pub(crate) async fn publish(
             }

             debug!("Using two-phase upload (direct mode)");
-            let reporter = PublishReporter::single(printer);
             upload_two_phase(
                 &group,
                 &form_metadata,
@@ -329,8 +340,7 @@ pub(crate) async fn publish(
                 &s3_client,
                 retry_policy,
                 &credentials,
-                // Needs to be an `Arc` because the reqwest `Body` static lifetime requirement
-                Arc::new(reporter),
+                reporter.clone(),
             )
             .await?
         } else {
@@ -355,7 +365,6 @@ pub(crate) async fn publish(
                     if !should_upload {
                         false
                     } else {
-                        let reporter = PublishReporter::single(printer);
                         upload(
                             &group,
                             &form_metadata,
@@ -365,8 +374,7 @@ pub(crate) async fn publish(
                             &credentials,
                             check_url_client.as_ref(),
                             &download_concurrency,
-                            // Needs to be an `Arc` because the reqwest `Body` static lifetime requirement
-                            Arc::new(reporter),
+                            reporter.clone(),
                         )
                         .await? // Filename and/or URL are already attached, if applicable.
                     }
diff --git a/crates/uv/src/commands/reporters.rs b/crates/uv/src/commands/reporters.rs
index e16ec15a85884..b7d78e9b7dec0 100644
--- a/crates/uv/src/commands/reporters.rs
+++ b/crates/uv/src/commands/reporters.rs
@@ -12,6 +12,7 @@ use rustc_hash::FxHashMap;
 use crate::commands::human_readable_bytes;
 use crate::printer::Printer;
 use uv_cache::Removal;
+use uv_distribution_filename::DistFilename;
 use uv_distribution_types::{
     BuildableSource, CachedDist, DistributionMetadata, Name, SourceDist, VersionOrUrlRef,
 };
@@ -108,6 +109,7 @@ enum Direction {
     Upload,
     Download,
     Extract,
+    Hash,
 }

 impl Direction {
@@ -116,6 +118,7 @@ impl Direction {
             Self::Download => "Downloading",
             Self::Upload => "Uploading",
             Self::Extract => "Extracting",
+            Self::Hash => "Hashing",
         }
     }
 }
@@ -328,6 +331,7 @@ impl ProgressReporter {
                         Direction::Download => "Downloaded",
                         Direction::Upload => "Uploaded",
                         Direction::Extract => "Extracted",
+                        Direction::Hash => "Hashed",
                     }
                     .bold()
                     .cyan(),
@@ -364,6 +368,18 @@ impl ProgressReporter {
         self.on_request_start(Direction::Upload, name, size)
     }

+    fn on_hash_progress(&self, id: usize, bytes: u64) {
+        self.on_request_progress(id, bytes);
+    }
+
+    fn on_hash_complete(&self, id: usize) {
+        self.on_request_complete(Direction::Hash, id);
+    }
+
+    fn on_hash_start(&self, name: String, size: Option<u64>) -> usize {
+        self.on_request_start(Direction::Hash, name, size)
+    }
+
     fn on_checkout_start(&self, url: &DisplaySafeUrl, rev: &str) -> usize {
         let ProgressMode::Multi {
             multi_progress,
@@ -711,6 +727,18 @@ impl uv_publish::Reporter for PublishReporter {
     fn on_upload_complete(&self, id: usize) {
         self.reporter.on_upload_complete(id);
     }
+
+    fn on_hash_start(&self, name: &DistFilename, size: Option<u64>) -> usize {
+        self.reporter.on_hash_start(name.to_string(), size)
+    }
+
+    fn on_hash_progress(&self, id: usize, inc: u64) {
+        self.reporter.on_hash_progress(id, inc);
+    }
+
+    fn on_hash_complete(&self, id: usize) {
+        self.reporter.on_hash_complete(id);
+    }
 }

 #[derive(Debug)]
diff --git a/crates/uv/tests/it/publish.rs b/crates/uv/tests/it/publish.rs
index 9b1219a396f1a..4afba8af04025 100644
--- a/crates/uv/tests/it/publish.rs
+++ b/crates/uv/tests/it/publish.rs
@@ -39,6 +39,7 @@ fn username_password_no_longer_supported() {

     ----- stderr -----
     Publishing 1 file to https://test.pypi.org/legacy/
+    Hashing ok-1.0.0-py3-none-any.whl ([SIZE])
     Uploading ok-1.0.0-py3-none-any.whl ([SIZE])
     error: Failed to publish `[WORKSPACE]/test/links/ok-1.0.0-py3-none-any.whl` to https://test.pypi.org/legacy/
       Caused by: Server returned status code 403 Forbidden. Server says: 403 Username/Password authentication is no longer supported. Migrate to API Tokens or Trusted Publishers instead. See https://test.pypi.org/help/#apitoken and https://test.pypi.org/help/#trusted-publishers
@@ -64,6 +65,7 @@ fn invalid_token() {

     ----- stderr -----
     Publishing 1 file to https://test.pypi.org/legacy/
+    Hashing ok-1.0.0-py3-none-any.whl ([SIZE])
     Uploading ok-1.0.0-py3-none-any.whl ([SIZE])
     error: Failed to publish `[WORKSPACE]/test/links/ok-1.0.0-py3-none-any.whl` to https://test.pypi.org/legacy/
       Caused by: Server returned status code 403 Forbidden. Server says: 403 Invalid or non-existent authentication information. See https://test.pypi.org/help/#invalid-auth for more information.
@@ -149,6 +151,7 @@ fn no_credentials() {
       Caused by: Failed to obtain OIDC token: is the `id-token: write` permission missing?
       Caused by: GitHub Actions detection error
       Caused by: insufficient permissions: missing ACTIONS_ID_TOKEN_REQUEST_URL
+    Hashing ok-1.0.0-py3-none-any.whl ([SIZE])
     Uploading ok-1.0.0-py3-none-any.whl ([SIZE])
     error: Failed to publish `[WORKSPACE]/test/links/ok-1.0.0-py3-none-any.whl` to https://test.pypi.org/legacy/
       Caused by: Failed to send POST request
@@ -248,6 +251,7 @@ fn check_keyring_behaviours() {

     ----- stderr -----
     Publishing 1 file to https://test.pypi.org/legacy/?ok
+    Hashing ok-1.0.0-py3-none-any.whl ([SIZE])
     Uploading ok-1.0.0-py3-none-any.whl ([SIZE])
     error: Failed to publish `[WORKSPACE]/test/links/ok-1.0.0-py3-none-any.whl` to https://test.pypi.org/legacy/?ok
       Caused by: Server returned status code 403 Forbidden. Server says: 403 Username/Password authentication is no longer supported. Migrate to API Tokens or Trusted Publishers instead. See https://test.pypi.org/help/#apitoken and https://test.pypi.org/help/#trusted-publishers
@@ -273,6 +277,7 @@ fn check_keyring_behaviours() {
     ----- stderr -----
     Publishing 1 file to https://test.pypi.org/legacy/?ok
     warning: Using `--keyring-provider` with a password or token and no check URL has no effect
+    Hashing ok-1.0.0-py3-none-any.whl ([SIZE])
     Uploading ok-1.0.0-py3-none-any.whl ([SIZE])
     error: Failed to publish `[WORKSPACE]/test/links/ok-1.0.0-py3-none-any.whl` to https://test.pypi.org/legacy/?ok
       Caused by: Server returned status code 403 Forbidden. Server says: 403 Username/Password authentication is no longer supported. Migrate to API Tokens or Trusted Publishers instead. See https://test.pypi.org/help/#apitoken and https://test.pypi.org/help/#trusted-publishers
@@ -301,6 +306,7 @@ fn check_keyring_behaviours() {
     Keyring request for dummy@https://test.pypi.org/legacy/?ok
     Keyring request for dummy@test.pypi.org
     warning: Keyring has no password for URL `https://test.pypi.org/legacy/?ok` and username `dummy`
+    Hashing ok-1.0.0-py3-none-any.whl ([SIZE])
     Uploading ok-1.0.0-py3-none-any.whl ([SIZE])
     Keyring request for dummy@https://test.pypi.org/legacy/?ok
     Keyring request for dummy@test.pypi.org
@@ -328,6 +334,7 @@ fn check_keyring_behaviours() {
     ----- stderr -----
     Publishing 1 file to https://test.pypi.org/legacy/?ok
     Keyring request for dummy@https://test.pypi.org/legacy/?ok
+    Hashing ok-1.0.0-py3-none-any.whl ([SIZE])
     Uploading ok-1.0.0-py3-none-any.whl ([SIZE])
     error: Failed to publish `[WORKSPACE]/test/links/ok-1.0.0-py3-none-any.whl` to https://test.pypi.org/legacy/?ok
       Caused by: Server returned status code 403 Forbidden. Server says: 403 Username/Password authentication is no longer supported. Migrate to API Tokens or Trusted Publishers instead. See https://test.pypi.org/help/#apitoken and https://test.pypi.org/help/#trusted-publishers
@@ -480,6 +487,7 @@ async fn read_index_credential_env_vars_for_check_url() {

     ----- stderr -----
     Publishing 1 file to http://[LOCALHOST]/upload
+    Hashing astral_test_private-0.1.0-py3-none-any.whl ([SIZE])
     Uploading astral_test_private-0.1.0-py3-none-any.whl ([SIZE])
     error: Failed to publish `dist/astral_test_private-0.1.0-py3-none-any.whl` to http://[LOCALHOST]/upload
       Caused by: Failed to send POST request
@@ -554,6 +562,7 @@ async fn gitlab_trusted_publishing_pypi_id_token() {

     ----- stderr -----
     Publishing 1 file to http://[LOCALHOST]/upload
+    Hashing ok-1.0.0-py3-none-any.whl ([SIZE])
     Uploading ok-1.0.0-py3-none-any.whl ([SIZE])
     "
     );
@@ -608,6 +617,7 @@ async fn gitlab_trusted_publishing_testpypi_id_token() {

     ----- stderr -----
     Publishing 1 file to http://[LOCALHOST]/upload
+    Hashing ok-1.0.0-py3-none-any.whl ([SIZE])
     Uploading ok-1.0.0-py3-none-any.whl ([SIZE])
     "
     );
@@ -642,6 +652,7 @@ async fn upload_error_pypi_json() {

     ----- stderr -----
     Publishing 1 file to http://[LOCALHOST]/upload
+    Hashing ok-1.0.0-py3-none-any.whl ([SIZE])
     Uploading ok-1.0.0-py3-none-any.whl ([SIZE])
     error: Failed to publish `[WORKSPACE]/test/links/ok-1.0.0-py3-none-any.whl` to http://[LOCALHOST]/upload
       Caused by: Server returned status code 400 Bad Request. Server says: 400 Use 'source' as Python version for an sdist.
@@ -678,6 +689,7 @@ async fn upload_error_problem_details() {

     ----- stderr -----
     Publishing 1 file to http://[LOCALHOST]/upload
+    Hashing ok-1.0.0-py3-none-any.whl ([SIZE])
     Uploading ok-1.0.0-py3-none-any.whl ([SIZE])
     error: Failed to publish `[WORKSPACE]/test/links/ok-1.0.0-py3-none-any.whl` to http://[LOCALHOST]/upload
       Caused by: Server returned status code 400 Bad Request. Server message: Bad Request, Missing required field `name`
@@ -750,7 +762,7 @@ fn non_normalized_filename_warning() {
     ----- stderr -----
     Publishing 1 file to https://test.pypi.org/legacy/
     warning: `ok-1.01.0-py3-none-any.whl` has a non-normalized filename (expected `ok-1.1.0-py3-none-any.whl`). Pass `--preview-features publish-require-normalized` to skip such files.
-    Uploading ok-1.1.0-py3-none-any.whl ([SIZE])
+    Hashing ok-1.1.0-py3-none-any.whl ([SIZE])
     error: Failed to publish: `ok-1.01.0-py3-none-any.whl`
       Caused by: Failed to read metadata
       Caused by: Failed to read from zip file

PATCH

echo "Patch applied successfully"
