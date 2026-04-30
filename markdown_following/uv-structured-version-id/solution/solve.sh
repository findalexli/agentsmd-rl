#!/usr/bin/env bash
set -euo pipefail

cd /workspace/uv

# Idempotent: skip if already applied
if grep -q 'ArchiveUrl' crates/uv-distribution-types/src/id.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-distribution-types/src/cached.rs b/crates/uv-distribution-types/src/cached.rs
index 11f914ba2c586..6f3dd1f6aee4b 100644
--- a/crates/uv-distribution-types/src/cached.rs
+++ b/crates/uv-distribution-types/src/cached.rs
@@ -7,7 +7,7 @@ use uv_pypi_types::{HashDigest, HashDigests, VerbatimParsedUrl};

 use crate::{
     BuildInfo, BuiltDist, Dist, DistributionMetadata, Hashed, InstalledMetadata, InstalledVersion,
-    Name, ParsedUrl, SourceDist, VersionOrUrlRef,
+    Name, ParsedUrl, SourceDist, VersionId, VersionOrUrlRef,
 };

 /// A built distribution (wheel) that exists in the local cache.
@@ -211,6 +211,10 @@ impl DistributionMetadata for CachedDirectUrlDist {
     fn version_or_url(&self) -> VersionOrUrlRef<'_> {
         VersionOrUrlRef::Url(&self.url.verbatim)
     }
+
+    fn version_id(&self) -> VersionId {
+        VersionId::from_parsed_url(&self.url.parsed_url)
+    }
 }

 impl DistributionMetadata for CachedDist {
@@ -220,6 +224,13 @@ impl DistributionMetadata for CachedDist {
             Self::Url(dist) => dist.version_or_url(),
         }
     }
+
+    fn version_id(&self) -> VersionId {
+        match self {
+            Self::Registry(dist) => dist.version_id(),
+            Self::Url(dist) => dist.version_id(),
+        }
+    }
 }

 impl InstalledMetadata for CachedRegistryDist {
diff --git a/crates/uv-distribution-types/src/id.rs b/crates/uv-distribution-types/src/id.rs
index b68b4f24cb9fd..0f557210ab757 100644
--- a/crates/uv-distribution-types/src/id.rs
+++ b/crates/uv-distribution-types/src/id.rs
@@ -1,11 +1,14 @@
 use std::fmt::{Display, Formatter};
-use std::path::PathBuf;
+use std::path::{Path, PathBuf};

 use uv_cache_key::{CanonicalUrl, RepositoryUrl};
+use uv_git_types::GitUrl;

 use uv_normalize::PackageName;
 use uv_pep440::Version;
-use uv_pypi_types::HashDigest;
+use uv_pypi_types::{
+    HashDigest, ParsedArchiveUrl, ParsedDirectoryUrl, ParsedGitUrl, ParsedPathUrl, ParsedUrl,
+};
 use uv_redacted::DisplaySafeUrl;

 /// A unique identifier for a package. A package can either be identified by a name (e.g., `black`)
@@ -40,12 +43,33 @@ impl Display for PackageId {
 }

 /// A unique identifier for a package at a specific version (e.g., `black==23.10.0`).
+///
+/// URL-based variants use kind-specific identity semantics. Archive URLs ignore hash fragments
+/// while preserving semantic `subdirectory` information. Git URLs preserve semantic
+/// `subdirectory` information while ignoring unrelated fragments. Local file URLs are keyed by
+/// their resolved path and kind.
 #[derive(Debug, Clone, PartialEq, Eq, Hash, PartialOrd, Ord)]
 pub enum VersionId {
     /// The identifier consists of a package name and version.
     NameVersion(PackageName, Version),
-    /// The identifier consists of a URL.
-    Url(CanonicalUrl),
+    /// The identifier consists of an archive URL identified by its location and optional source
+    /// subdirectory.
+    ArchiveUrl {
+        location: CanonicalUrl,
+        subdirectory: Option<PathBuf>,
+    },
+    /// The identifier consists of a Git repository URL, its reference, and optional source
+    /// subdirectory.
+    Git {
+        url: GitUrl,
+        subdirectory: Option<PathBuf>,
+    },
+    /// The identifier consists of a local file path.
+    Path(PathBuf),
+    /// The identifier consists of a local directory path.
+    Directory(PathBuf),
+    /// The identifier consists of a URL whose source kind could not be determined.
+    Unknown(DisplaySafeUrl),
 }

 impl VersionId {
@@ -54,9 +78,74 @@ impl VersionId {
         Self::NameVersion(name, version)
     }

+    /// Create a new [`VersionId`] from a parsed URL.
+    pub fn from_parsed_url(url: &ParsedUrl) -> Self {
+        match url {
+            ParsedUrl::Path(path) => Self::from_path_url(path),
+            ParsedUrl::Directory(directory) => Self::from_directory_url(directory),
+            ParsedUrl::Git(git) => Self::from_git_url(git),
+            ParsedUrl::Archive(archive) => Self::from_archive_url(archive),
+        }
+    }
+
     /// Create a new [`VersionId`] from a URL.
     pub fn from_url(url: &DisplaySafeUrl) -> Self {
-        Self::Url(CanonicalUrl::new(url))
+        match ParsedUrl::try_from(url.clone()) {
+            Ok(parsed) => Self::from_parsed_url(&parsed),
+            Err(_) => Self::Unknown(url.clone()),
+        }
+    }
+
+    /// Create a new [`VersionId`] from an archive URL.
+    pub fn from_archive(location: &DisplaySafeUrl, subdirectory: Option<&Path>) -> Self {
+        Self::ArchiveUrl {
+            location: CanonicalUrl::new(location),
+            subdirectory: subdirectory.map(Path::to_path_buf),
+        }
+    }
+
+    /// Create a new [`VersionId`] from a Git URL.
+    pub fn from_git(git: &GitUrl, subdirectory: Option<&Path>) -> Self {
+        // TODO(charlie): Canonicalize repository URLs in `GitUrl` itself so `VersionId` does not
+        // need to rebuild the value here.
+        let git = GitUrl::from_fields(
+            DisplaySafeUrl::from(CanonicalUrl::new(git.repository())),
+            git.reference().clone(),
+            git.precise(),
+            git.lfs(),
+        )
+        .expect("canonical Git URLs should preserve supported schemes");
+
+        Self::Git {
+            url: git,
+            subdirectory: subdirectory.map(Path::to_path_buf),
+        }
+    }
+
+    /// Create a new [`VersionId`] from a local file path.
+    pub fn from_path(path: &Path) -> Self {
+        Self::Path(path.to_path_buf())
+    }
+
+    /// Create a new [`VersionId`] from a local directory path.
+    pub fn from_directory(path: &Path) -> Self {
+        Self::Directory(path.to_path_buf())
+    }
+
+    fn from_archive_url(archive: &ParsedArchiveUrl) -> Self {
+        Self::from_archive(&archive.url, archive.subdirectory.as_deref())
+    }
+
+    fn from_path_url(path: &ParsedPathUrl) -> Self {
+        Self::from_path(path.install_path.as_ref())
+    }
+
+    fn from_directory_url(directory: &ParsedDirectoryUrl) -> Self {
+        Self::from_directory(directory.install_path.as_ref())
+    }
+
+    fn from_git_url(git: &ParsedGitUrl) -> Self {
+        Self::from_git(&git.url, git.subdirectory.as_deref())
     }
 }

@@ -64,7 +153,49 @@ impl Display for VersionId {
     fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
         match self {
             Self::NameVersion(name, version) => write!(f, "{name}-{version}"),
-            Self::Url(url) => write!(f, "{url}"),
+            Self::ArchiveUrl {
+                location,
+                subdirectory,
+            } => {
+                let mut location = DisplaySafeUrl::from(location.clone());
+                if let Some(subdirectory) = subdirectory {
+                    location
+                        .set_fragment(Some(&format!("subdirectory={}", subdirectory.display())));
+                }
+                write!(f, "{location}")
+            }
+            Self::Git { url, subdirectory } => {
+                let mut git_url = DisplaySafeUrl::parse(&format!("git+{}", url.repository()))
+                    .expect("canonical Git URLs should be display-safe");
+                if let Some(precise) = url.precise() {
+                    let path = format!("{}@{}", git_url.path(), precise);
+                    git_url.set_path(&path);
+                } else if let Some(reference) = url.reference().as_str() {
+                    let path = format!("{}@{}", git_url.path(), reference);
+                    git_url.set_path(&path);
+                }
+
+                let mut fragments = Vec::new();
+                if let Some(subdirectory) = subdirectory {
+                    fragments.push(format!("subdirectory={}", subdirectory.display()));
+                }
+                if url.lfs().enabled() {
+                    fragments.push("lfs=true".to_string());
+                }
+                if !fragments.is_empty() {
+                    git_url.set_fragment(Some(&fragments.join("&")));
+                }
+
+                write!(f, "{git_url}")
+            }
+            Self::Path(path) | Self::Directory(path) => {
+                if let Ok(url) = DisplaySafeUrl::from_file_path(path) {
+                    write!(f, "{url}")
+                } else {
+                    write!(f, "{}", path.display())
+                }
+            }
+            Self::Unknown(url) => write!(f, "{url}"),
         }
     }
 }
@@ -121,3 +252,106 @@ impl From<&Self> for ResourceId {
         value.clone()
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use std::time::{SystemTime, UNIX_EPOCH};
+
+    use fs_err as fs;
+
+    use super::VersionId;
+    use uv_redacted::DisplaySafeUrl;
+
+    #[test]
+    fn version_id_ignores_hash_fragments() {
+        let first = DisplaySafeUrl::parse(
+            "https://example.com/pkg-0.1.0.whl#sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
+        )
+        .unwrap();
+        let second = DisplaySafeUrl::parse(
+            "https://example.com/pkg-0.1.0.whl#sha512=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
+        )
+        .unwrap();
+
+        assert_eq!(VersionId::from_url(&first), VersionId::from_url(&second));
+    }
+
+    #[test]
+    fn version_id_preserves_non_hash_fragments() {
+        let first =
+            DisplaySafeUrl::parse("https://example.com/pkg-0.1.0.tar.gz#subdirectory=foo").unwrap();
+        let second =
+            DisplaySafeUrl::parse("https://example.com/pkg-0.1.0.tar.gz#subdirectory=bar").unwrap();
+
+        assert_ne!(VersionId::from_url(&first), VersionId::from_url(&second));
+    }
+
+    #[test]
+    fn version_id_ignores_hash_fragments_with_subdirectory() {
+        let first = DisplaySafeUrl::parse(
+            "https://example.com/pkg-0.1.0.tar.gz#subdirectory=foo&sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
+        )
+        .unwrap();
+        let second = DisplaySafeUrl::parse(
+            "https://example.com/pkg-0.1.0.tar.gz#sha512=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb&subdirectory=foo",
+        )
+        .unwrap();
+
+        assert_eq!(VersionId::from_url(&first), VersionId::from_url(&second));
+    }
+
+    #[test]
+    fn version_id_preserves_non_archive_fragments() {
+        let first =
+            DisplaySafeUrl::parse("git+https://example.com/pkg.git#subdirectory=foo").unwrap();
+        let second =
+            DisplaySafeUrl::parse("git+https://example.com/pkg.git#subdirectory=bar").unwrap();
+
+        assert_ne!(VersionId::from_url(&first), VersionId::from_url(&second));
+    }
+
+    #[test]
+    fn version_id_ignores_irrelevant_git_fragments() {
+        let first =
+            DisplaySafeUrl::parse("git+https://example.com/pkg.git@main#egg=pkg&subdirectory=foo")
+                .unwrap();
+        let second =
+            DisplaySafeUrl::parse("git+https://example.com/pkg.git@main#subdirectory=foo").unwrap();
+
+        assert_eq!(VersionId::from_url(&first), VersionId::from_url(&second));
+    }
+
+    #[test]
+    fn version_id_uses_file_kinds() {
+        let nonce = SystemTime::now()
+            .duration_since(UNIX_EPOCH)
+            .unwrap()
+            .as_nanos();
+        let root = std::env::temp_dir().join(format!("uv-version-id-{nonce}"));
+        let file = root.join("pkg-0.1.0.whl");
+        let directory = root.join("pkg");
+
+        fs::create_dir_all(&directory).unwrap();
+        fs::write(&file, b"wheel").unwrap();
+
+        let file_url = DisplaySafeUrl::from_file_path(&file).unwrap();
+        let directory_url = DisplaySafeUrl::from_file_path(&directory).unwrap();
+
+        assert!(matches!(VersionId::from_url(&file_url), VersionId::Path(_)));
+        assert!(matches!(
+            VersionId::from_url(&directory_url),
+            VersionId::Directory(_)
+        ));
+
+        fs::remove_file(file).unwrap();
+        fs::remove_dir_all(root).unwrap();
+    }
+
+    #[test]
+    fn version_id_uses_unknown_for_invalid_git_like_urls() {
+        let url =
+            DisplaySafeUrl::parse("git+ftp://example.com/pkg.git@main#subdirectory=foo").unwrap();
+
+        assert!(matches!(VersionId::from_url(&url), VersionId::Unknown(_)));
+    }
+}
diff --git a/crates/uv-distribution-types/src/lib.rs b/crates/uv-distribution-types/src/lib.rs
index 568946cfd92a6..126be39c0a2dc 100644
--- a/crates/uv-distribution-types/src/lib.rs
+++ b/crates/uv-distribution-types/src/lib.rs
@@ -901,12 +901,20 @@ impl DistributionMetadata for DirectUrlBuiltDist {
     fn version_or_url(&self) -> VersionOrUrlRef<'_> {
         VersionOrUrlRef::Url(&self.url)
     }
+
+    fn version_id(&self) -> VersionId {
+        VersionId::from_archive(self.location.as_ref(), None)
+    }
 }

 impl DistributionMetadata for PathBuiltDist {
     fn version_or_url(&self) -> VersionOrUrlRef<'_> {
         VersionOrUrlRef::Url(&self.url)
     }
+
+    fn version_id(&self) -> VersionId {
+        VersionId::from_path(self.install_path.as_ref())
+    }
 }

 impl DistributionMetadata for RegistrySourceDist {
@@ -919,24 +927,40 @@ impl DistributionMetadata for DirectUrlSourceDist {
     fn version_or_url(&self) -> VersionOrUrlRef<'_> {
         VersionOrUrlRef::Url(&self.url)
     }
+
+    fn version_id(&self) -> VersionId {
+        VersionId::from_archive(self.location.as_ref(), self.subdirectory.as_deref())
+    }
 }

 impl DistributionMetadata for GitSourceDist {
     fn version_or_url(&self) -> VersionOrUrlRef<'_> {
         VersionOrUrlRef::Url(&self.url)
     }
+
+    fn version_id(&self) -> VersionId {
+        VersionId::from_git(self.git.as_ref(), self.subdirectory.as_deref())
+    }
 }

 impl DistributionMetadata for PathSourceDist {
     fn version_or_url(&self) -> VersionOrUrlRef<'_> {
         VersionOrUrlRef::Url(&self.url)
     }
+
+    fn version_id(&self) -> VersionId {
+        VersionId::from_path(self.install_path.as_ref())
+    }
 }

 impl DistributionMetadata for DirectorySourceDist {
     fn version_or_url(&self) -> VersionOrUrlRef<'_> {
         VersionOrUrlRef::Url(&self.url)
     }
+
+    fn version_id(&self) -> VersionId {
+        VersionId::from_directory(self.install_path.as_ref())
+    }
 }

 impl DistributionMetadata for SourceDist {
@@ -949,6 +973,16 @@ impl DistributionMetadata for SourceDist {
             Self::Directory(dist) => dist.version_or_url(),
         }
     }
+
+    fn version_id(&self) -> VersionId {
+        match self {
+            Self::Registry(dist) => dist.version_id(),
+            Self::DirectUrl(dist) => dist.version_id(),
+            Self::Git(dist) => dist.version_id(),
+            Self::Path(dist) => dist.version_id(),
+            Self::Directory(dist) => dist.version_id(),
+        }
+    }
 }

 impl DistributionMetadata for BuiltDist {
@@ -959,6 +993,14 @@ impl DistributionMetadata for BuiltDist {
             Self::Path(dist) => dist.version_or_url(),
         }
     }
+
+    fn version_id(&self) -> VersionId {
+        match self {
+            Self::Registry(dist) => dist.version_id(),
+            Self::DirectUrl(dist) => dist.version_id(),
+            Self::Path(dist) => dist.version_id(),
+        }
+    }
 }

 impl DistributionMetadata for Dist {
@@ -968,6 +1010,13 @@ impl DistributionMetadata for Dist {
             Self::Source(dist) => dist.version_or_url(),
         }
     }
+
+    fn version_id(&self) -> VersionId {
+        match self {
+            Self::Built(dist) => dist.version_id(),
+            Self::Source(dist) => dist.version_id(),
+        }
+    }
 }

 impl RemoteSource for File {
diff --git a/crates/uv-distribution-types/src/requested.rs b/crates/uv-distribution-types/src/requested.rs
index 7ab8c23484666..dfe55729b4c8e 100644
--- a/crates/uv-distribution-types/src/requested.rs
+++ b/crates/uv-distribution-types/src/requested.rs
@@ -2,7 +2,7 @@ use std::fmt::{Display, Formatter};

 use crate::{
     Dist, DistributionId, DistributionMetadata, Identifier, InstalledDist, Name, ResourceId,
-    VersionOrUrlRef,
+    VersionId, VersionOrUrlRef,
 };
 use uv_normalize::PackageName;
 use uv_pep440::Version;
@@ -43,6 +43,13 @@ impl DistributionMetadata for RequestedDist {
             Self::Installable(dist) => dist.version_or_url(),
         }
     }
+
+    fn version_id(&self) -> VersionId {
+        match self {
+            Self::Installed(dist) => dist.version_id(),
+            Self::Installable(dist) => dist.version_id(),
+        }
+    }
 }

 impl Identifier for RequestedDist {
diff --git a/crates/uv-distribution-types/src/resolved.rs b/crates/uv-distribution-types/src/resolved.rs
index cf2f3515070c4..56d18d39afd1e 100644
--- a/crates/uv-distribution-types/src/resolved.rs
+++ b/crates/uv-distribution-types/src/resolved.rs
@@ -9,7 +9,7 @@ use uv_pypi_types::Yanked;
 use crate::{
     BuiltDist, Dist, DistributionId, DistributionMetadata, Identifier, IndexUrl, InstalledDist,
     Name, PrioritizedDist, RegistryBuiltWheel, RegistrySourceDist, ResourceId, SourceDist,
-    VersionOrUrlRef,
+    VersionId, VersionOrUrlRef,
 };

 /// A distribution that can be used for resolution and installation.
@@ -215,6 +215,13 @@ impl DistributionMetadata for ResolvedDist {
             Self::Installable { dist, .. } => dist.version_or_url(),
         }
     }
+
+    fn version_id(&self) -> VersionId {
+        match self {
+            Self::Installed { dist } => dist.version_id(),
+            Self::Installable { dist, .. } => dist.version_id(),
+        }
+    }
 }

 impl Identifier for ResolvedDist {

PATCH

echo "Patch applied successfully."
