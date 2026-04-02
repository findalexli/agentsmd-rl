#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if fix is already applied
if grep -q 'ResolverInstallerSettings::from' crates/uv/src/commands/tool/list.rs; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv/src/commands/tool/list.rs b/crates/uv/src/commands/tool/list.rs
index cd19728946d9d..a2674f23aae69 100644
--- a/crates/uv/src/commands/tool/list.rs
+++ b/crates/uv/src/commands/tool/list.rs
@@ -11,11 +11,11 @@ use uv_cache_info::Timestamp;
 use uv_client::{BaseClientBuilder, RegistryClientBuilder};
 use uv_configuration::Concurrency;
 use uv_distribution_filename::DistFilename;
-use uv_distribution_types::IndexCapabilities;
+use uv_distribution_types::{IndexCapabilities, RequiresPython};
 use uv_fs::Simplified;
 use uv_normalize::PackageName;
 use uv_python::LenientImplementationName;
-use uv_resolver::{ExcludeNewer, PrereleaseMode};
+use uv_settings::ResolverInstallerOptions;
 use uv_tool::InstalledTools;
 use uv_warnings::warn_user;

@@ -23,6 +23,7 @@ use crate::commands::ExitStatus;
 use crate::commands::pip::latest::LatestClient;
 use crate::commands::reporters::LatestVersionReporter;
 use crate::printer::Printer;
+use crate::settings::ResolverInstallerSettings;

 /// List installed tools.
 #[expect(clippy::fn_params_excessive_bools)]
@@ -114,35 +115,51 @@ pub(crate) async fn list(
     let latest: FxHashMap<PackageName, Option<DistFilename>> = if outdated
         && !valid_tools.is_empty()
     {
-        let capabilities = IndexCapabilities::default();
-
-        // Initialize the registry client.
-        let client = RegistryClientBuilder::new(
-            client_builder,
-            cache.clone().with_refresh(Refresh::All(Timestamp::now())),
-        )
-        .build();
         let download_concurrency = concurrency.downloads_semaphore.clone();

-        // Initialize the client to fetch the latest version of each package.
-        let latest_client = LatestClient {
-            client: &client,
-            capabilities: &capabilities,
-            prerelease: PrereleaseMode::default(),
-            exclude_newer: &ExcludeNewer::default(),
-            tags: None,
-            requires_python: None,
-        };
-
         let reporter = LatestVersionReporter::from(printer).with_length(valid_tools.len() as u64);

         // Fetch the latest version for each tool.
         let mut fetches = futures::stream::iter(&valid_tools)
-            .map(async |(name, _tool, _tool_env, _version)| {
-                let latest = latest_client
-                    .find_latest(name, None, &download_concurrency)
-                    .await?;
-                Ok::<(&PackageName, Option<DistFilename>), uv_client::Error>((name, latest))
+            .map(|(name, tool, tool_env, _version)| {
+                let client_builder = client_builder.clone();
+                let download_concurrency = download_concurrency.clone();
+                async move {
+                    let capabilities = IndexCapabilities::default();
+                    let settings = ResolverInstallerSettings::from(ResolverInstallerOptions::from(
+                        tool.options().clone(),
+                    ));
+                    let interpreter = tool_env.environment().interpreter();
+
+                    let client = RegistryClientBuilder::new(
+                        client_builder
+                            .clone()
+                            .keyring(settings.resolver.keyring_provider),
+                        cache.clone().with_refresh(Refresh::All(Timestamp::now())),
+                    )
+                    .index_locations(settings.resolver.index_locations.clone())
+                    .index_strategy(settings.resolver.index_strategy)
+                    .markers(interpreter.markers())
+                    .platform(interpreter.platform())
+                    .build();
+
+                    let requires_python = RequiresPython::greater_than_equal_version(
+                        interpreter.python_full_version(),
+                    );
+                    let latest_client = LatestClient {
+                        client: &client,
+                        capabilities: &capabilities,
+                        prerelease: settings.resolver.prerelease,
+                        exclude_newer: &settings.resolver.exclude_newer,
+                        tags: None,
+                        requires_python: Some(&requires_python),
+                    };
+
+                    let latest = latest_client
+                        .find_latest(name, None, &download_concurrency)
+                        .await?;
+                    Ok::<(&PackageName, Option<DistFilename>), anyhow::Error>((name, latest))
+                }
             })
             .buffer_unordered(concurrency.downloads);

PATCH

echo "Patch applied successfully."
