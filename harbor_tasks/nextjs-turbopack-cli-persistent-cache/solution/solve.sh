#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotency check: if persistent_caching field already exists, patch is applied
if grep -q 'persistent_caching' turbopack/crates/turbopack-cli/src/arguments.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/Cargo.lock b/Cargo.lock
index db1b13b67a0dd..1be561b71816e 100644
--- a/Cargo.lock
+++ b/Cargo.lock
@@ -9896,6 +9896,7 @@ dependencies = [
  "codspeed-criterion-compat",
  "console-subscriber",
  "dunce",
+ "either",
  "futures",
  "owo-colors",
  "regex",
@@ -9927,6 +9928,7 @@ dependencies = [
  "turbopack-nodejs",
  "turbopack-resolve",
  "turbopack-trace-utils",
+ "vergen-gitcl",
  "webbrowser",
 ]

diff --git a/turbopack/crates/turbopack-cli/Cargo.toml b/turbopack/crates/turbopack-cli/Cargo.toml
index ed9c1eb2b0f8e..1aa40c7d2444b 100644
--- a/turbopack/crates/turbopack-cli/Cargo.toml
+++ b/turbopack/crates/turbopack-cli/Cargo.toml
@@ -42,6 +42,7 @@ bincode = { workspace = true }
 clap = { workspace = true, features = ["derive", "env"] }
 console-subscriber = { workspace = true, optional = true }
 dunce = { workspace = true }
+either = { workspace = true }
 futures = { workspace = true }
 owo-colors = { workspace = true }
 rustc-hash = { workspace = true }
@@ -75,6 +76,10 @@ turbopack-resolve = { workspace = true }
 turbopack-trace-utils = { workspace = true }
 webbrowser = { workspace = true }

+[build-dependencies]
+anyhow = { workspace = true }
+vergen-gitcl = { workspace = true }
+
 [dev-dependencies]
 criterion = { workspace = true, features = ["async_tokio"] }
 regex = { workspace = true }
diff --git a/turbopack/crates/turbopack-cli/benches/small_apps.rs b/turbopack/crates/turbopack-cli/benches/small_apps.rs
index 0d072be73ea43..c8a2b747b2d26 100644
--- a/turbopack/crates/turbopack-cli/benches/small_apps.rs
+++ b/turbopack/crates/turbopack-cli/benches/small_apps.rs
@@ -72,6 +72,8 @@ fn bench_small_apps(c: &mut Criterion) {
                                 full_stats: false,
                                 target: None,
                                 worker_threads: None,
+                                persistent_caching: false,
+                                cache_dir: None,
                             },
                             no_sourcemap: false,
                             no_minify: false,
diff --git a/turbopack/crates/turbopack-cli/build.rs b/turbopack/crates/turbopack-cli/build.rs
new file mode 100644
index 0000000000000..3840ad52c040d
--- /dev/null
+++ b/turbopack/crates/turbopack-cli/build.rs
@@ -0,0 +1,36 @@
+use std::env;
+
+fn main() -> anyhow::Result<()> {
+    println!("cargo:rerun-if-env-changed=CI");
+    let is_ci = env::var("CI").is_ok_and(|value| !value.is_empty());
+
+    // We use the git dirty state to disable filesystem cache (filesystem cache relies on a
+    // commit hash to be safe). One tradeoff of this is that we must invalidate the rust build more
+    // often.
+    //
+    // This invalidates the build if any untracked files change. That's sufficient for the case
+    // where we transition from dirty to clean.
+    //
+    // There's an edge-case here where the repository could be newly dirty, but we can't know
+    // because our build hasn't been invalidated, since the untracked files weren't untracked last
+    // time we ran. That will cause us to incorrectly report ourselves as clean.
+    //
+    // However, in practice that shouldn't be much of an issue: If no other dependency of this
+    // top-level crate has changed (which would've triggered our rebuild), then the resulting binary
+    // must be equivalent to a clean build anyways. Therefore, filesystem cache using the HEAD
+    // commit hash as a version is okay.
+    let git = vergen_gitcl::GitclBuilder::default()
+        .dirty(/* include_untracked */ true)
+        .describe(
+            /* tags */ true,
+            /* dirty */ !is_ci, // suppress the dirty suffix in CI
+            /* matches */ Some("v[0-9]*"), // find the last version tag
+        )
+        .build()?;
+    vergen_gitcl::Emitter::default()
+        .add_instructions(&git)?
+        .fail_on_error()
+        .emit()?;
+
+    Ok(())
+}
diff --git a/turbopack/crates/turbopack-cli/src/arguments.rs b/turbopack/crates/turbopack-cli/src/arguments.rs
index 4f9d98c886471..c8a094853f36f 100644
--- a/turbopack/crates/turbopack-cli/src/arguments.rs
+++ b/turbopack/crates/turbopack-cli/src/arguments.rs
@@ -95,6 +95,16 @@ pub struct CommonArguments {
     /// Number of worker threads to use for parallel processing
     #[clap(long)]
     pub worker_threads: Option<usize>,
+
+    /// Enable filesystem-backed persistent caching.
+    /// Cache is stored at `<cache-dir>/<git-version>`.
+    #[clap(long)]
+    pub persistent_caching: bool,
+
+    /// Directory to store the persistent cache.
+    /// Defaults to `.turbopack/cache` relative to the project directory.
+    #[clap(long)]
+    pub cache_dir: Option<PathBuf>,
     // Enable experimental garbage collection with the provided memory limit in
     // MB.
     // #[clap(long)]
diff --git a/turbopack/crates/turbopack-cli/src/build/mod.rs b/turbopack/crates/turbopack-cli/src/build/mod.rs
index f892e6c15cc45..9ea9996c70383 100644
--- a/turbopack/crates/turbopack-cli/src/build/mod.rs
+++ b/turbopack/crates/turbopack-cli/src/build/mod.rs
@@ -6,12 +6,14 @@ use std::{
 };

 use anyhow::{Context, Result, bail};
+use either::Either;
 use rustc_hash::FxHashSet;
 use tracing::Instrument;
 use turbo_rcstr::RcStr;
 use turbo_tasks::{ResolvedVc, TransientInstance, TryJoinIterExt, TurboTasks, Vc, apply_effects};
 use turbo_tasks_backend::{
-    BackendOptions, NoopBackingStorage, TurboTasksBackend, noop_backing_storage,
+    BackendOptions, GitVersionInfo, NoopBackingStorage, StartupCacheState, StorageMode,
+    TurboBackingStorage, TurboTasksBackend, noop_backing_storage, turbo_backing_storage,
 };
 use turbo_tasks_fs::FileSystem;
 use turbo_unix_path::join_path;
@@ -55,7 +57,7 @@ use crate::{
     },
 };

-type Backend = TurboTasksBackend<NoopBackingStorage>;
+type Backend = TurboTasksBackend<Either<TurboBackingStorage, NoopBackingStorage>>;

 pub struct TurbopackBuildBuilder {
     turbo_tasks: Arc<TurboTasks<Backend>>,
@@ -523,14 +525,57 @@ pub async fn build(args: &BuildArguments) -> Result<()> {
         root_dir,
     } = normalize_dirs(&args.common.dir, &args.common.root)?;

-    let tt = TurboTasks::new(TurboTasksBackend::new(
-        BackendOptions {
-            dependency_tracking: false,
-            storage_mode: None,
-            ..Default::default()
-        },
-        noop_backing_storage(),
-    ));
+    let is_ci = std::env::var("CI").is_ok_and(|v| !v.is_empty());
+    let is_short_session = true; // build sessions are always short
+
+    let tt = if args.common.persistent_caching {
+        let version_info = GitVersionInfo {
+            describe: env!("VERGEN_GIT_DESCRIBE"),
+            dirty: option_env!("CI").is_none_or(|v| v.is_empty())
+                && env!("VERGEN_GIT_DIRTY") == "true",
+        };
+        let cache_dir = args
+            .common
+            .cache_dir
+            .clone()
+            .unwrap_or_else(|| PathBuf::from(&*project_dir).join(".turbopack/cache"));
+        let (backing_storage, cache_state) =
+            turbo_backing_storage(&cache_dir, &version_info, is_ci, is_short_session)?;
+        let storage_mode = if std::env::var("TURBO_ENGINE_READ_ONLY").is_ok() {
+            StorageMode::ReadOnly
+        } else if is_ci || is_short_session {
+            StorageMode::ReadWriteOnShutdown
+        } else {
+            StorageMode::ReadWrite
+        };
+        let tt = TurboTasks::new(TurboTasksBackend::new(
+            BackendOptions {
+                dependency_tracking: false,
+                storage_mode: Some(storage_mode),
+                ..Default::default()
+            },
+            Either::Left(backing_storage),
+        ));
+        if let StartupCacheState::Invalidated { reason_code } = cache_state {
+            eprintln!(
+                "warn  - Turbopack cache was invalidated{}",
+                reason_code
+                    .as_deref()
+                    .map(|r| format!(": {r}"))
+                    .unwrap_or_default()
+            );
+        }
+        tt
+    } else {
+        TurboTasks::new(TurboTasksBackend::new(
+            BackendOptions {
+                dependency_tracking: false,
+                storage_mode: None,
+                ..Default::default()
+            },
+            Either::Right(noop_backing_storage()),
+        ))
+    };

     let mut builder = TurbopackBuildBuilder::new(tt.clone(), project_dir, root_dir)
         .log_detail(args.common.log_detail)
diff --git a/turbopack/crates/turbopack-cli/src/dev/mod.rs b/turbopack/crates/turbopack-cli/src/dev/mod.rs
index ff0dff606762c..4a74ffcc8a21f 100644
--- a/turbopack/crates/turbopack-cli/src/dev/mod.rs
+++ b/turbopack/crates/turbopack-cli/src/dev/mod.rs
@@ -9,6 +9,7 @@ use std::{
 };

 use anyhow::{Context, Result};
+use either::Either;
 use owo_colors::OwoColorize;
 use rustc_hash::FxHashSet;
 use turbo_rcstr::{RcStr, rcstr};
@@ -18,7 +19,8 @@ use turbo_tasks::{
     util::{FormatBytes, FormatDuration},
 };
 use turbo_tasks_backend::{
-    BackendOptions, NoopBackingStorage, TurboTasksBackend, noop_backing_storage,
+    BackendOptions, GitVersionInfo, NoopBackingStorage, StartupCacheState, StorageMode,
+    TurboBackingStorage, TurboTasksBackend, noop_backing_storage, turbo_backing_storage,
 };
 use turbo_tasks_fs::FileSystem;
 use turbo_tasks_malloc::TurboMalloc;
@@ -54,7 +56,7 @@ use crate::{

 pub(crate) mod web_entry_source;

-type Backend = TurboTasksBackend<NoopBackingStorage>;
+type Backend = TurboTasksBackend<Either<TurboBackingStorage, NoopBackingStorage>>;

 pub struct TurbopackDevServerBuilder {
     turbo_tasks: Arc<TurboTasks<Backend>>,
@@ -374,13 +376,56 @@ pub async fn start_server(args: &DevArguments) -> Result<()> {
         root_dir,
     } = normalize_dirs(&args.common.dir, &args.common.root)?;

-    let tt = TurboTasks::new(TurboTasksBackend::new(
-        BackendOptions {
-            storage_mode: None,
-            ..Default::default()
-        },
-        noop_backing_storage(),
-    ));
+    let is_ci = std::env::var("CI").is_ok_and(|v| !v.is_empty());
+    let is_short_session = is_ci;
+
+    let tt = if args.common.persistent_caching {
+        let version_info = GitVersionInfo {
+            describe: env!("VERGEN_GIT_DESCRIBE"),
+            dirty: option_env!("CI").is_none_or(|v| v.is_empty())
+                && env!("VERGEN_GIT_DIRTY") == "true",
+        };
+        let cache_dir = args
+            .common
+            .cache_dir
+            .clone()
+            .unwrap_or_else(|| PathBuf::from(&*project_dir).join(".turbopack/cache"));
+        let (backing_storage, cache_state) =
+            turbo_backing_storage(&cache_dir, &version_info, is_ci, is_short_session)?;
+        let storage_mode = if std::env::var("TURBO_ENGINE_READ_ONLY").is_ok() {
+            StorageMode::ReadOnly
+        } else if is_ci || is_short_session {
+            StorageMode::ReadWriteOnShutdown
+        } else {
+            StorageMode::ReadWrite
+        };
+        let tt = TurboTasks::new(TurboTasksBackend::new(
+            BackendOptions {
+                storage_mode: Some(storage_mode),
+                ..Default::default()
+            },
+            Either::Left(backing_storage),
+        ));
+        if let StartupCacheState::Invalidated { reason_code } = cache_state {
+            eprintln!(
+                "{} - Turbopack cache was invalidated{}",
+                "warn ".yellow(),
+                reason_code
+                    .as_deref()
+                    .map(|r| format!(": {r}"))
+                    .unwrap_or_default()
+            );
+        }
+        tt
+    } else {
+        TurboTasks::new(TurboTasksBackend::new(
+            BackendOptions {
+                storage_mode: None,
+                ..Default::default()
+            },
+            Either::Right(noop_backing_storage()),
+        ))
+    };

     let tt_clone = tt.clone();

PATCH

echo "Patch applied successfully."
