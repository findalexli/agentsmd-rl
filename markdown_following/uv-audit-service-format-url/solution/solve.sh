#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if VulnerabilityServiceFormat already exists
if grep -q 'VulnerabilityServiceFormat' crates/uv-audit/src/service/mod.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/Cargo.lock b/Cargo.lock
index 8cce0cc3e0c6f..9d2fd2166c8df 100644
--- a/Cargo.lock
+++ b/Cargo.lock
@@ -5803,6 +5803,7 @@ name = "uv-audit"
 version = "0.0.32"
 dependencies = [
  "astral-reqwest-middleware",
+ "clap",
  "futures",
  "insta",
  "jiff",
@@ -6078,6 +6079,7 @@ dependencies = [
  "insta",
  "serde",
  "url",
+ "uv-audit",
  "uv-auth",
  "uv-cache",
  "uv-configuration",
diff --git a/crates/uv-audit/Cargo.toml b/crates/uv-audit/Cargo.toml
index 8d7e48a597a7a..2beb4408f9f63 100644
--- a/crates/uv-audit/Cargo.toml
+++ b/crates/uv-audit/Cargo.toml
@@ -22,6 +22,7 @@ uv-normalize = { workspace = true }
 uv-redacted = { workspace = true }
 uv-small-str = { workspace = true }

+clap = { workspace = true, optional = true }
 futures = { workspace = true }
 jiff = { workspace = true }
 reqwest-middleware = { workspace = true, features = ["json"] }
diff --git a/crates/uv-audit/src/service/mod.rs b/crates/uv-audit/src/service/mod.rs
index 2c0024edb682a..5822d83d08664 100644
--- a/crates/uv-audit/src/service/mod.rs
+++ b/crates/uv-audit/src/service/mod.rs
@@ -1,3 +1,10 @@
 //! Vulnerability services.

 pub mod osv;
+
+/// The shape of the vulnerability service.
+#[derive(Copy, Clone, Debug)]
+#[cfg_attr(feature = "clap", derive(clap::ValueEnum))]
+pub enum VulnerabilityServiceFormat {
+    Osv,
+}
diff --git a/crates/uv-cli/Cargo.toml b/crates/uv-cli/Cargo.toml
index 1c7dcc0f409c4..814187472e989 100644
--- a/crates/uv-cli/Cargo.toml
+++ b/crates/uv-cli/Cargo.toml
@@ -16,6 +16,7 @@ doctest = false
 workspace = true

 [dependencies]
+uv-audit = { workspace = true, features = ["clap"] }
 uv-auth = { workspace = true }
 uv-cache = { workspace = true, features = ["clap"] }
 uv-configuration = { workspace = true, features = ["clap"] }
diff --git a/crates/uv-cli/src/lib.rs b/crates/uv-cli/src/lib.rs
index 2cf9438468c0c..c0bddbcbbcb99 100644
--- a/crates/uv-cli/src/lib.rs
+++ b/crates/uv-cli/src/lib.rs
@@ -11,6 +11,7 @@ use clap::error::ErrorKind;
 use clap::{Args, Parser, Subcommand};
 use clap::{ValueEnum, ValueHint};

+use uv_audit::service::VulnerabilityServiceFormat;
 use uv_auth::Service;
 use uv_cache::CacheArgs;
 use uv_configuration::{
@@ -5267,6 +5268,24 @@ pub struct AuditArgs {
     /// `aarch64-apple-darwin`.
     #[arg(long)]
     pub python_platform: Option<TargetTriple>,
+
+    /// The service format to use for vulnerability lookups.
+    ///
+    /// Each service format has a default URL, which can be
+    /// changed with `--service-url`. The defaults are:
+    ///
+    /// * OSV: <https://api.osv.dev/>
+    #[arg(long, value_enum, default_value = "osv")]
+    pub service_format: VulnerabilityServiceFormat,
+
+    /// The URL to vulnerability service API endpoint.
+    ///
+    /// If not provided, the default URL for the selected service will be used.
+    ///
+    /// The service needs to use the OSV protocol, unless a different
+    /// format was requested by `--service-format`.
+    #[arg(long, value_hint = ValueHint::Url)]
+    pub service_url: Option<String>,
 }

 #[derive(Args)]
diff --git a/crates/uv/src/commands/project/audit.rs b/crates/uv/src/commands/project/audit.rs
index bc006dfdaa2de..de1d99dca1d65 100644
--- a/crates/uv/src/commands/project/audit.rs
+++ b/crates/uv/src/commands/project/audit.rs
@@ -19,7 +19,7 @@ use crate::settings::{FrozenSource, LockCheck, ResolverSettings};

 use anyhow::Result;
 use tracing::trace;
-use uv_audit::service::osv;
+use uv_audit::service::{VulnerabilityServiceFormat, osv};
 use uv_audit::types::{Dependency, Finding};
 use uv_cache::Cache;
 use uv_client::BaseClientBuilder;
@@ -27,7 +27,6 @@ use uv_configuration::{Concurrency, DependencyGroups, ExtrasSpecification, Targe
 use uv_normalize::{DefaultExtras, DefaultGroups};
 use uv_preview::{Preview, PreviewFeature};
 use uv_python::{PythonDownloads, PythonPreference, PythonVersion};
-use uv_redacted::DisplaySafeUrl;
 use uv_scripts::Pep723Script;
 use uv_settings::PythonInstallMirrors;
 use uv_warnings::warn_user;
@@ -52,6 +51,8 @@ pub(crate) async fn audit(
     cache: Cache,
     printer: Printer,
     preview: Preview,
+    service: VulnerabilityServiceFormat,
+    service_url: Option<String>,
 ) -> Result<ExitStatus> {
     // Check if the audit feature is in preview
     if !preview.is_enabled(PreviewFeature::Audit) {
@@ -215,23 +216,27 @@ pub(crate) async fn audit(
         .collect();

     // Perform the audit.
-    let base_client = client_builder.build();
-    let osv_url =
-        DisplaySafeUrl::parse(osv::API_BASE).expect("impossible: embedded URL is invalid");
-    let service = osv::Osv::new(
-        base_client.for_host(&osv_url).raw_client().clone(),
-        None,
-        concurrency,
-    );
-    trace!("Auditing {n} dependencies against OSV", n = auditable.len());
-
     let reporter = AuditReporter::from(printer);
-
     let dependencies: Vec<Dependency> = auditable
         .iter()
         .map(|(name, version)| Dependency::new((*name).clone(), (*version).clone()))
         .collect();
-    let all_findings = service.query_batch(&dependencies).await?;
+    let base_client = client_builder.build();
+    let all_findings = {
+        match service {
+            VulnerabilityServiceFormat::Osv => {
+                let osv_url = service_url
+                    .as_deref()
+                    .unwrap_or(osv::API_BASE)
+                    .parse()
+                    .expect("invalid OSV service URL");
+                let client = base_client.for_host(&osv_url).raw_client().clone();
+                let service = osv::Osv::new(client, None, concurrency);
+                trace!("Auditing {n} dependencies against OSV", n = auditable.len());
+                service.query_batch(&dependencies).await?
+            }
+        }
+    };

     reporter.on_audit_complete();

diff --git a/crates/uv/src/lib.rs b/crates/uv/src/lib.rs
index 455c8eab1b885..d7e360158fcb5 100644
--- a/crates/uv/src/lib.rs
+++ b/crates/uv/src/lib.rs
@@ -2654,6 +2654,8 @@ async fn run_project(
                 cache,
                 printer,
                 globals.preview,
+                args.service_format,
+                args.service_url,
             ))
             .await
         }
diff --git a/crates/uv/src/settings.rs b/crates/uv/src/settings.rs
index bfe980ba81e79..c1b4a0d610b93 100644
--- a/crates/uv/src/settings.rs
+++ b/crates/uv/src/settings.rs
@@ -6,6 +6,7 @@ use std::str::FromStr;
 use std::time::Duration;

 use rustc_hash::FxHashSet;
+use uv_audit::service::VulnerabilityServiceFormat;

 use crate::commands::{PythonUpgrade, PythonUpgradeSource};
 use uv_auth::Service;
@@ -2477,6 +2478,8 @@ pub(crate) struct AuditSettings {
     pub(crate) python_platform: Option<TargetTriple>,
     pub(crate) install_mirrors: PythonInstallMirrors,
     pub(crate) settings: ResolverSettings,
+    pub(crate) service_format: VulnerabilityServiceFormat,
+    pub(crate) service_url: Option<String>,
 }

 impl AuditSettings {
@@ -2506,6 +2509,8 @@ impl AuditSettings {
             frozen,
             build,
             resolver,
+            service_format,
+            service_url,
         } = args;

         let filesystem_install_mirrors = filesystem
@@ -2551,6 +2556,8 @@ impl AuditSettings {
                 .install_mirrors
                 .combine(filesystem_install_mirrors),
             settings: ResolverSettings::combine(resolver_options(resolver, build), filesystem),
+            service_format,
+            service_url,
         }
     }
 }

PATCH

echo "Patch applied successfully."
