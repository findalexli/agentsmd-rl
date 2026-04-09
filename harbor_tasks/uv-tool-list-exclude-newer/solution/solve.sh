#!/usr/bin/env bash
set -euo pipefail

cd /workspace/uv

# Idempotent: skip if already applied
if grep -q 'pub exclude_newer: Option<ExcludeNewerValue>' crates/uv-cli/src/lib.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-cli/src/lib.rs b/crates/uv-cli/src/lib.rs
index ab86c9e53bb3e..c431e3ef10f7a 100644
--- a/crates/uv-cli/src/lib.rs
+++ b/crates/uv-cli/src/lib.rs
@@ -5801,6 +5801,19 @@ pub struct ToolListArgs {
     #[arg(long, overrides_with("outdated"), hide = true)]
     pub no_outdated: bool,

+    /// Limit candidate packages to those that were uploaded prior to the given date.
+    ///
+    /// Accepts RFC 3339 timestamps (e.g., `2006-12-02T02:07:43Z`), local dates in the same format
+    /// (e.g., `2006-12-02`) resolved based on your system's configured time zone, a "friendly"
+    /// duration (e.g., `24 hours`, `1 week`, `30 days`), or an ISO 8601 duration (e.g., `PT24H`,
+    /// `P7D`, `P30D`).
+    ///
+    /// Durations do not respect semantics of the local time zone and are always resolved to a fixed
+    /// number of seconds assuming that a day is 24 hours (e.g., DST transitions are ignored).
+    /// Calendar units such as months and years are not allowed.
+    #[arg(long, env = EnvVars::UV_EXCLUDE_NEWER, help_heading = "Resolver options")]
+    pub exclude_newer: Option<ExcludeNewerValue>,
+
     // Hide unused global Python options.
     #[arg(long, hide = true)]
     pub python_preference: Option<PythonPreference>,
diff --git a/crates/uv/src/commands/tool/list.rs b/crates/uv/src/commands/tool/list.rs
index a2674f23aae69..8f8d3e26f6cb1 100644
--- a/crates/uv/src/commands/tool/list.rs
+++ b/crates/uv/src/commands/tool/list.rs
@@ -15,7 +15,7 @@ use uv_distribution_types::{IndexCapabilities, RequiresPython};
 use uv_fs::Simplified;
 use uv_normalize::PackageName;
 use uv_python::LenientImplementationName;
-use uv_settings::ResolverInstallerOptions;
+use uv_settings::{Combine, ResolverInstallerOptions};
 use uv_tool::InstalledTools;
 use uv_warnings::warn_user;

@@ -34,6 +34,8 @@ pub(crate) async fn list(
     show_extras: bool,
     show_python: bool,
     outdated: bool,
+    args: ResolverInstallerOptions,
+    filesystem: ResolverInstallerOptions,
     client_builder: BaseClientBuilder<'_>,
     concurrency: Concurrency,
     cache: &Cache,
@@ -124,10 +126,12 @@ pub(crate) async fn list(
             .map(|(name, tool, tool_env, _version)| {
                 let client_builder = client_builder.clone();
                 let download_concurrency = download_concurrency.clone();
+                let args = args.clone();
+                let filesystem = filesystem.clone();
                 async move {
                     let capabilities = IndexCapabilities::default();
-                    let settings = ResolverInstallerSettings::from(ResolverInstallerOptions::from(
-                        tool.options().clone(),
+                    let settings = ResolverInstallerSettings::from(args.combine(
+                        ResolverInstallerOptions::from(tool.options().clone()).combine(filesystem),
                     ));
                     let interpreter = tool_env.environment().interpreter();

diff --git a/crates/uv/src/lib.rs b/crates/uv/src/lib.rs
index ea3d9ba89bb3f..075ac91ac7b1c 100644
--- a/crates/uv/src/lib.rs
+++ b/crates/uv/src/lib.rs
@@ -1627,6 +1627,8 @@ async fn run(cli: Cli) -> Result<ExitStatus> {
                 args.show_extras,
                 args.show_python,
                 args.outdated,
+                args.args,
+                args.filesystem,
                 client_builder.subcommand(vec!["tool".to_owned(), "list".to_owned()]),
                 globals.concurrency,
                 &cache,
diff --git a/crates/uv/src/settings.rs b/crates/uv/src/settings.rs
index e0230020f29e3..bbd3007965dd5 100644
--- a/crates/uv/src/settings.rs
+++ b/crates/uv/src/settings.rs
@@ -1111,12 +1111,13 @@ pub(crate) struct ToolListSettings {
     pub(crate) show_extras: bool,
     pub(crate) show_python: bool,
     pub(crate) outdated: bool,
+    pub(crate) args: ResolverInstallerOptions,
+    pub(crate) filesystem: ResolverInstallerOptions,
 }

 impl ToolListSettings {
     /// Resolve the [`ToolListSettings`] from the CLI and filesystem configuration.
-    #[expect(clippy::needless_pass_by_value)]
-    pub(crate) fn resolve(args: ToolListArgs, _filesystem: Option<FilesystemOptions>) -> Self {
+    pub(crate) fn resolve(args: ToolListArgs, filesystem: Option<FilesystemOptions>) -> Self {
         let ToolListArgs {
             show_paths,
             show_version_specifiers,
@@ -1125,10 +1126,17 @@ impl ToolListSettings {
             show_python,
             outdated,
             no_outdated,
+            exclude_newer,
             python_preference: _,
             no_python_downloads: _,
         } = args;

+        let filesystem = filesystem.map(FilesystemOptions::into_options);
+        let filesystem = ResolverInstallerOptions {
+            exclude_newer: filesystem.and_then(|options| options.top_level.exclude_newer),
+            ..ResolverInstallerOptions::default()
+        };
+
         Self {
             show_paths,
             show_version_specifiers,
@@ -1136,6 +1144,11 @@ impl ToolListSettings {
             show_extras,
             show_python,
             outdated: flag(outdated, no_outdated, "outdated").unwrap_or(false),
+            args: ResolverInstallerOptions {
+                exclude_newer,
+                ..ResolverInstallerOptions::default()
+            },
+            filesystem,
         }
     }
 }

PATCH

echo "Patch applied successfully."
