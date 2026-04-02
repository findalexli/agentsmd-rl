#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if fix is already applied
if grep -q 'Self::Uv =>' crates/uv-bin-install/src/lib.rs 2>/dev/null \
   && grep -q 'fn is_official_public_uv_install' crates/uv/src/commands/self_update.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-bin-install/src/lib.rs b/crates/uv-bin-install/src/lib.rs
index 32da0153e064d..aaa5d0f42b34e 100644
--- a/crates/uv-bin-install/src/lib.rs
+++ b/crates/uv-bin-install/src/lib.rs
@@ -34,6 +34,7 @@ use uv_redacted::DisplaySafeUrl;
 #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
 pub enum Binary {
     Ruff,
+    Uv,
 }

 impl Binary {
@@ -50,6 +51,7 @@ impl Binary {
             ]
             .into_iter()
             .collect(),
+            Self::Uv => VersionSpecifiers::empty(),
         }
     }

@@ -59,13 +61,11 @@ impl Binary {
     pub fn name(&self) -> &'static str {
         match self {
             Self::Ruff => "ruff",
+            Self::Uv => "uv",
         }
     }

     /// Get the ordered list of download URLs for a specific version and platform.
-    ///
-    /// The default Astral mirror is returned first, followed by the canonical GitHub URL as a
-    /// fallback.
     pub fn download_urls(
         &self,
         version: &Version,
@@ -88,22 +88,42 @@ impl Binary {
                     })?,
                 ])
             }
+            Self::Uv => {
+                let canonical = format!(
+                    "{UV_GITHUB_URL_PREFIX}{version}/uv-{platform}.{}",
+                    format.extension()
+                );
+                Ok(vec![DisplaySafeUrl::parse(&canonical).map_err(|err| {
+                    Error::UrlParse {
+                        url: canonical,
+                        source: err,
+                    }
+                })?])
+            }
         }
     }

-    /// Return the ordered list of manifest URLs to try: the default Astral mirror first, then the
-    /// canonical URL as a fallback.
+    /// Return the ordered list of manifest URLs to try for this binary.
     fn manifest_urls(self) -> Vec<DisplaySafeUrl> {
         let name = self.name();
-        // These are static strings so parsing cannot fail.
-        vec![
-            DisplaySafeUrl::parse(&format!("{VERSIONS_MANIFEST_MIRROR}/{name}.ndjson")).unwrap(),
-            DisplaySafeUrl::parse(&format!("{VERSIONS_MANIFEST_URL}/{name}.ndjson")).unwrap(),
-        ]
+        match self {
+            // These are static strings so parsing cannot fail.
+            Self::Ruff => vec![
+                DisplaySafeUrl::parse(&format!("{VERSIONS_MANIFEST_MIRROR}/{name}.ndjson"))
+                    .unwrap(),
+                DisplaySafeUrl::parse(&format!("{VERSIONS_MANIFEST_URL}/{name}.ndjson")).unwrap(),
+            ],
+            Self::Uv => {
+                vec![
+                    DisplaySafeUrl::parse(&format!("{VERSIONS_MANIFEST_URL}/{name}.ndjson"))
+                        .unwrap(),
+                ]
+            }
+        }
     }

-    /// Given a canonical artifact URL (e.g., from the versions manifest), return an ordered list
-    /// of URLs to try: the default Astral mirror first, then the canonical URL as a fallback.
+    /// Given a canonical artifact URL (e.g., from the versions manifest), return the ordered list
+    /// of URLs to try for this binary.
     fn mirror_urls(self, canonical_url: DisplaySafeUrl) -> Vec<DisplaySafeUrl> {
         match self {
             Self::Ruff => {
@@ -115,6 +135,7 @@ impl Binary {
                 }
                 vec![canonical_url]
             }
+            Self::Uv => vec![canonical_url],
         }
     }

@@ -200,6 +221,9 @@ impl fmt::Display for BinVersion {
 /// The canonical GitHub URL prefix for Ruff releases.
 const RUFF_GITHUB_URL_PREFIX: &str = "https://github.com/astral-sh/ruff/releases/download/";

+/// The canonical GitHub URL prefix for uv releases.
+const UV_GITHUB_URL_PREFIX: &str = "https://github.com/astral-sh/uv/releases/download/";
+
 /// The default Astral mirror for Ruff releases.
 ///
 /// This mirror is tried first for Ruff downloads. If it fails, uv falls back to the canonical
@@ -243,8 +267,6 @@ pub struct ResolvedVersion {
     /// The version number.
     pub version: Version,
     /// The ordered list of download URLs to try for this version and current platform.
-    ///
-    /// The default Astral mirror is listed first, with the canonical GitHub URL as a fallback.
     pub artifact_urls: Vec<DisplaySafeUrl>,
     /// The archive format.
     pub archive_format: ArchiveFormat,
@@ -841,6 +863,29 @@ mod tests {

     use super::*;

+    #[test]
+    fn test_uv_download_urls() {
+        let urls = Binary::Uv
+            .download_urls(
+                &Version::new([0, 6, 0]),
+                "x86_64-unknown-linux-gnu",
+                ArchiveFormat::TarGz,
+            )
+            .expect("uv download URLs should be valid");
+
+        let urls = urls
+            .into_iter()
+            .map(|url| url.to_string())
+            .collect::<Vec<_>>();
+        assert_eq!(
+            urls,
+            vec![
+                "https://github.com/astral-sh/uv/releases/download/0.6.0/uv-x86_64-unknown-linux-gnu.tar.gz"
+                    .to_string(),
+            ]
+        );
+    }
+
     /// Verify that `should_try_next_url` returns `true` even for streaming errors
     /// that `retryable_on_request_failure` does not recognise as transient.
     ///
diff --git a/crates/uv/src/commands/self_update.rs b/crates/uv/src/commands/self_update.rs
index 80db0acf83167..6d4fa9a571bb2 100644
--- a/crates/uv/src/commands/self_update.rs
+++ b/crates/uv/src/commands/self_update.rs
@@ -1,12 +1,15 @@
 use std::fmt::Write;
+use std::str::FromStr;

-use anyhow::Result;
-use axoupdater::{AxoUpdater, AxoupdateError, UpdateRequest};
+use anyhow::{Context, Result};
+use axoupdater::{AxoUpdater, AxoupdateError, ReleaseSource, ReleaseSourceType, UpdateRequest};
 use owo_colors::OwoColorize;
-use tracing::debug;
-
+use tracing::{debug, warn};
+use uv_bin_install::{Binary, find_matching_version};
 use uv_client::BaseClientBuilder;
 use uv_fs::Simplified;
+use uv_pep440::{Version as Pep440Version, VersionSpecifier, VersionSpecifiers};
+use uv_static::EnvVars;

 use crate::commands::ExitStatus;
 use crate::printer::Printer;
@@ -104,6 +107,66 @@ pub(crate) async fn self_update(
         )
     )?;

+    if is_official_public_uv_install(updater.source.as_ref()) {
+        debug!("Using official public self-update path");
+
+        let retry_policy = client_builder.retry_policy();
+        let client = client_builder.retries(0).build();
+        let constraints = official_target_version_specifiers(version.as_deref())?;
+
+        let resolved = find_matching_version(
+            Binary::Uv,
+            constraints.as_ref(),
+            None,
+            &client,
+            &retry_policy,
+        )
+        .await
+        .with_context(|| match version.as_deref() {
+            Some(version) => format!("Failed to resolve uv version `{version}`"),
+            None => "Failed to resolve the latest uv version".to_string(),
+        })?;
+
+        debug!("Resolved self-update target to `uv=={}`", resolved.version);
+
+        let current_version = Pep440Version::from_str(env!("CARGO_PKG_VERSION"))
+            .context("Failed to parse the current uv version")?;
+        if !is_update_needed(&current_version, &resolved.version, version.is_some()) {
+            writeln!(
+                printer.stderr(),
+                "{}",
+                format_args!(
+                    "{}{} You're already on version {} of uv{}.",
+                    "success".green().bold(),
+                    ":".bold(),
+                    format!("v{}", env!("CARGO_PKG_VERSION")).bold().cyan(),
+                    if version.is_none() {
+                        " (the latest version)".to_string()
+                    } else {
+                        String::new()
+                    }
+                )
+            )?;
+            return Ok(ExitStatus::Success);
+        }
+
+        if dry_run {
+            writeln!(
+                printer.stderr(),
+                "Would update uv from {} to {}",
+                format!("v{}", env!("CARGO_PKG_VERSION")).bold().white(),
+                format!("v{}", resolved.version).bold().white(),
+            )?;
+            return Ok(ExitStatus::Success);
+        }
+
+        updater
+            .configure_version_specifier(UpdateRequest::SpecificTag(resolved.version.to_string()));
+        return run_updater(updater, printer, token.is_some()).await;
+    }
+
+    debug!("Using legacy self-update path");
+
     let update_request = if let Some(version) = version {
         UpdateRequest::SpecificTag(version)
     } else {
@@ -143,8 +206,86 @@ pub(crate) async fn self_update(
         return Ok(ExitStatus::Success);
     }

-    // Run the updater. This involves a network request, since we need to determine the latest
-    // available version of uv.
+    run_updater(updater, printer, token.is_some()).await
+}
+
+/// Returns `true` if the `source` is the official GitHub repository for uv, or
+/// if an installer base url override environment variable is set.
+fn is_official_public_uv_install(source: Option<&ReleaseSource>) -> bool {
+    is_official_public_uv_install_with_overrides(
+        source,
+        std::env::var_os(EnvVars::UV_INSTALLER_GITHUB_BASE_URL).is_some(),
+        std::env::var_os(EnvVars::UV_INSTALLER_GHE_BASE_URL).is_some(),
+    )
+}
+
+/// Helper function for [`is_official_public_uv_install`] that allows for easier
+/// testing.
+fn is_official_public_uv_install_with_overrides(
+    source: Option<&ReleaseSource>,
+    has_github_base_url_override: bool,
+    has_ghe_base_url_override: bool,
+) -> bool {
+    if has_github_base_url_override || has_ghe_base_url_override {
+        return false;
+    }
+
+    matches!(
+        source,
+        Some(ReleaseSource {
+            release_type: ReleaseSourceType::GitHub,
+            owner,
+            name,
+            app_name,
+        }) if owner == "astral-sh" && name == "uv" && app_name == "uv"
+    )
+}
+
+/// Parse an explicit `uv self update` target version for the official public case.
+///
+/// To preserve legacy tag-based behavior, only exact `major.minor.patch` release versions are
+/// accepted. Inputs that normalize to a different version string, such as `0.10` or `v0.10.0`,
+/// are rejected instead of being silently rewritten.
+fn official_target_version_specifiers(
+    target_version: Option<&str>,
+) -> Result<Option<VersionSpecifiers>> {
+    let Some(target_version) = target_version else {
+        return Ok(None);
+    };
+
+    let pep440_version = Pep440Version::from_str(target_version)
+        .with_context(|| format!("Failed to parse version specifier `{target_version}`"))?;
+    if pep440_version.to_string() != target_version || pep440_version.release().len() < 3 {
+        warn!(
+            "Rejecting explicit self-update version specifier `{target_version}` after parsing it as `{pep440_version}`"
+        );
+        anyhow::bail!(
+            "Failed to parse version specifier `{target_version}`: explicit versions must include an exact major.minor.patch release"
+        );
+    }
+
+    Ok(Some(VersionSpecifiers::from(
+        VersionSpecifier::equals_version(pep440_version),
+    )))
+}
+
+fn is_update_needed(
+    current_version: &Pep440Version,
+    target_version: &Pep440Version,
+    has_target_version: bool,
+) -> bool {
+    if has_target_version {
+        current_version != target_version
+    } else {
+        current_version < target_version
+    }
+}
+
+async fn run_updater(
+    updater: &mut AxoUpdater,
+    printer: Printer,
+    has_token: bool,
+) -> Result<ExitStatus> {
     match updater.run().await {
         Ok(Some(result)) => {
             let direction = if result
@@ -197,7 +338,7 @@ pub(crate) async fn self_update(
         }
         Err(err) => {
             return if let AxoupdateError::Reqwest(err) = err {
-                if err.status() == Some(http::StatusCode::FORBIDDEN) && token.is_none() {
+                if err.status() == Some(http::StatusCode::FORBIDDEN) && !has_token {
                     writeln!(
                         printer.stderr(),
                         "{}",
@@ -220,3 +361,91 @@ pub(crate) async fn self_update(

     Ok(ExitStatus::Success)
 }
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+
+    #[test]
+    fn test_is_official_public_uv_install() {
+        let source = ReleaseSource {
+            release_type: ReleaseSourceType::GitHub,
+            owner: "astral-sh".to_string(),
+            name: "uv".to_string(),
+            app_name: "uv".to_string(),
+        };
+
+        assert!(!is_official_public_uv_install_with_overrides(
+            None, false, false,
+        ));
+        assert!(is_official_public_uv_install_with_overrides(
+            Some(&source),
+            false,
+            false,
+        ));
+        assert!(!is_official_public_uv_install_with_overrides(
+            Some(&source),
+            true,
+            false,
+        ));
+        assert!(!is_official_public_uv_install_with_overrides(
+            Some(&source),
+            false,
+            true,
+        ));
+
+        let source = ReleaseSource {
+            owner: "astral-sh".to_string(),
+            name: "ruff".to_string(),
+            app_name: "uv".to_string(),
+            ..source
+        };
+        assert!(!is_official_public_uv_install_with_overrides(
+            Some(&source),
+            false,
+            false,
+        ));
+    }
+
+    #[test]
+    fn test_official_target_version_specifiers() {
+        assert_eq!(official_target_version_specifiers(None).unwrap(), None);
+        assert_eq!(
+            official_target_version_specifiers(Some("1.2.3")).unwrap(),
+            Some(VersionSpecifiers::from(VersionSpecifier::equals_version(
+                Pep440Version::new([1, 2, 3]),
+            )))
+        );
+        assert!(official_target_version_specifiers(Some("0.10")).is_err());
+        assert!(official_target_version_specifiers(Some("v1.2.3")).is_err());
+    }
+
+    #[test]
+    fn test_official_update_needed() {
+        assert!(!is_update_needed(
+            &Pep440Version::new([1, 2, 3]),
+            &Pep440Version::new([1, 2, 3]),
+            false,
+        ));
+        assert!(is_update_needed(
+            &Pep440Version::new([1, 2, 3]),
+            &Pep440Version::new([1, 2, 4]),
+            false,
+        ));
+        assert!(!is_update_needed(
+            &Pep440Version::new([1, 2, 4]),
+            &Pep440Version::new([1, 2, 3]),
+            false,
+        ));
+        assert!(!is_update_needed(
+            &Pep440Version::new([1, 2, 3]),
+            &Pep440Version::new([1, 2, 3]),
+            true,
+        ));
+        assert!(is_update_needed(
+            &Pep440Version::new([1, 2, 4]),
+            &Pep440Version::new([1, 2, 3]),
+            true,
+        ));
+    }
+}

PATCH

echo "Gold patch applied successfully."
