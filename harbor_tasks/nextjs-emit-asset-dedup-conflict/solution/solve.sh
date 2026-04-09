#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

EMIT_RS="crates/next-core/src/emit.rs"

# Idempotency check: if EmitConflictIssue is already defined, skip
if grep -q 'struct EmitConflictIssue' "$EMIT_RS" 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/next-core/src/emit.rs b/crates/next-core/src/emit.rs
index 2f789ed115b8b..bf9279d4f4a0f 100644
--- a/crates/next-core/src/emit.rs
+++ b/crates/next-core/src/emit.rs
@@ -1,9 +1,16 @@
-use anyhow::Result;
+use anyhow::{Ok, Result};
+use futures::join;
+use smallvec::{SmallVec, smallvec};
 use tracing::Instrument;
-use turbo_tasks::{TryFlatJoinIterExt, ValueToStringRef, Vc};
-use turbo_tasks_fs::{FileSystemPath, rebase};
+use turbo_rcstr::RcStr;
+use turbo_tasks::{
+    FxIndexMap, ResolvedVc, TryFlatJoinIterExt, TryJoinIterExt, ValueToStringRef, Vc,
+};
+use turbo_tasks_fs::{FileContent, FileSystemPath, rebase};
+use turbo_tasks_hash::{encode_hex, hash_xxh3_hash64};
 use turbopack_core::{
-    asset::Asset,
+    asset::{Asset, AssetContent},
+    issue::{Issue, IssueExt, IssueSeverity, IssueStage, OptionStyledString, StyledString},
     output::{ExpandedOutputAssets, OutputAsset, OutputAssets},
     reference::all_assets_from_entries,
 };
@@ -43,40 +50,124 @@ pub async fn emit_assets(
     client_relative_path: FileSystemPath,
     client_output_path: FileSystemPath,
 ) -> Result<()> {
-    let _: Vec<()> = assets
+    enum Location {
+        Node,
+        Client,
+    }
+    let assets = assets
         .await?
         .iter()
         .copied()
-        .map(|asset| {
-            let node_root = node_root.clone();
-            let client_relative_path = client_relative_path.clone();
-            let client_output_path = client_output_path.clone();
-
-            async move {
-                let path = asset.path().owned().await?;
-                let span = tracing::info_span!("emit asset", name = %path.to_string_ref().await?);
-                async move {
-                    Ok(if path.is_inside_ref(&node_root) {
-                        Some(emit(*asset).as_side_effect().await?)
-                    } else if path.is_inside_ref(&client_relative_path) {
-                        // Client assets are emitted to the client output path, which is prefixed
-                        // with _next. We need to rebase them to remove that
-                        // prefix.
-                        Some(
-                            emit_rebase(*asset, client_relative_path, client_output_path)
-                                .as_side_effect()
-                                .await?,
-                        )
-                    } else {
-                        None
-                    })
-                }
-                .instrument(span)
-                .await
-            }
+        .map(async |asset| {
+            let path = asset.path().owned().await?;
+            let location = if path.is_inside_ref(&node_root) {
+                Location::Node
+            } else if path.is_inside_ref(&client_relative_path) {
+                Location::Client
+            } else {
+                return Ok(None);
+            };
+            Ok(Some((location, path, asset)))
         })
         .try_flat_join()
         .await?;
+
+    type AssetVec = SmallVec<[ResolvedVc<Box<dyn OutputAsset>>; 1]>;
+    let mut node_assets_by_path: FxIndexMap<FileSystemPath, AssetVec> = FxIndexMap::default();
+    let mut client_assets_by_path: FxIndexMap<FileSystemPath, AssetVec> = FxIndexMap::default();
+    for (location, path, asset) in assets {
+        match location {
+            Location::Node => {
+                node_assets_by_path
+                    .entry(path)
+                    .or_insert_with(|| smallvec![])
+                    .push(asset);
+            }
+            Location::Client => {
+                client_assets_by_path
+                    .entry(path)
+                    .or_insert_with(|| smallvec![])
+                    .push(asset);
+            }
+        }
+    }
+
+    /// Checks for duplicate assets at the same path. If duplicates with
+    /// different content are found, emits an `EmitConflictIssue` for each
+    /// conflict but still returns the first asset so emission can continue.
+    async fn check_duplicates(
+        path: &FileSystemPath,
+        assets: AssetVec,
+        node_root: &FileSystemPath,
+    ) -> Result<ResolvedVc<Box<dyn OutputAsset>>> {
+        let mut iter = assets.into_iter();
+        let first = iter.next().unwrap();
+        for next in iter {
+            let ext: RcStr = path.extension().unwrap_or_default().into();
+            if let Some(detail) = assets_diff(*next, *first, ext, node_root.clone())
+                .owned()
+                .await?
+            {
+                EmitConflictIssue {
+                    asset_path: path.clone(),
+                    detail,
+                }
+                .resolved_cell()
+                .emit();
+            }
+        }
+        Ok(first)
+    }
+
+    // Use join! instead of try_join! to collect all errors deterministically
+    // rather than returning whichever branch fails first non-deterministically.
+    let (node_result, client_result) = join!(
+        node_assets_by_path
+            .into_iter()
+            .map(|(path, assets)| {
+                let node_root = node_root.clone();
+
+                async move {
+                    let asset = check_duplicates(&path, assets, &node_root).await?;
+                    let span = tracing::info_span!(
+                        "emit asset",
+                        name = %path.to_string_ref().await?
+                    );
+                    async move { emit(*asset).as_side_effect().await }
+                        .instrument(span)
+                        .await
+                }
+            })
+            .try_join(),
+        client_assets_by_path
+            .into_iter()
+            .map(|(path, assets)| {
+                let node_root = node_root.clone();
+                let client_relative_path = client_relative_path.clone();
+                let client_output_path = client_output_path.clone();
+
+                async move {
+                    let asset = check_duplicates(&path, assets, &node_root).await?;
+                    let span = tracing::info_span!(
+                        "emit asset",
+                        name = %path.to_string_ref().await?
+                    );
+                    async move {
+                        // Client assets are emitted to the client output path, which is
+                        // prefixed with _next. We need to rebase them to
+                        // remove that prefix.
+                        emit_rebase(*asset, client_relative_path, client_output_path)
+                            .as_side_effect()
+                            .await
+                    }
+                    .instrument(span)
+                    .await
+                }
+            })
+            .try_join(),
+    );
+    node_result?;
+    client_result?;
     Ok(())
 }

@@ -110,3 +201,133 @@ async fn emit_rebase(
         .await?;
     Ok(())
 }
+
+/// Compares two assets that target the same output path. If their content
+/// differs, writes both versions under `node_root` as `<hash>.<ext>` and
+/// returns a description of the difference.
+#[turbo_tasks::function]
+async fn assets_diff(
+    asset1: Vc<Box<dyn OutputAsset>>,
+    asset2: Vc<Box<dyn OutputAsset>>,
+    extension: RcStr,
+    node_root: FileSystemPath,
+) -> Result<Vc<Option<RcStr>>> {
+    let content1 = asset1.content().await?;
+    let content2 = asset2.content().await?;
+
+    let detail = match (&*content1, &*content2) {
+        (AssetContent::File(content1), AssetContent::File(content2)) => {
+            let content1 = content1.await?;
+            let content2 = content2.await?;
+
+            match (&*content1, &*content2) {
+                (FileContent::NotFound, FileContent::NotFound) => None,
+                (FileContent::Content(file1), FileContent::Content(file2)) => {
+                    if file1 == file2 {
+                        None
+                    } else {
+                        // Write both versions under node_root as <hash>.<ext> so the
+                        // user can diff them.
+                        let ext = &*extension;
+                        let hash1 = encode_hex(hash_xxh3_hash64(file1.content().content_hash()));
+                        let hash2 = encode_hex(hash_xxh3_hash64(file2.content().content_hash()));
+                        let name1 = if ext.is_empty() {
+                            hash1
+                        } else {
+                            format!("{hash1}.{ext}")
+                        };
+                        let name2 = if ext.is_empty() {
+                            hash2
+                        } else {
+                            format!("{hash2}.{ext}")
+                        };
+                        let path1 = node_root.join(&name1)?;
+                        let path2 = node_root.join(&name2)?;
+                        path1
+                            .write(FileContent::Content(file1.clone()).cell())
+                            .as_side_effect()
+                            .await?;
+                        path2
+                            .write(FileContent::Content(file2.clone()).cell())
+                            .as_side_effect()
+                            .await?;
+                        Some(format!(
+                            "file content differs, written to:\n  {}\n  {}",
+                            path1.to_string_ref().await?,
+                            path2.to_string_ref().await?,
+                        ))
+                    }
+                }
+                _ => Some(
+                    "assets at the same path have mismatched file content types (one task wants \
+                     to write the file, another wants to delete it)"
+                        .into(),
+                ),
+            }
+        }
+        (
+            AssetContent::Redirect {
+                target: target1,
+                link_type: link_type1,
+            },
+            AssetContent::Redirect {
+                target: target2,
+                link_type: link_type2,
+            },
+        ) => {
+            if target1 == target2 && link_type1 == link_type2 {
+                None
+            } else {
+                Some(format!(
+                    "assets at the same path are both redirects but point to different targets: \
+                     {target1} vs {target2}"
+                ))
+            }
+        }
+        _ => Some(
+            "assets at the same path have different content types (one is a file, the other is a \
+             redirect)"
+                .into(),
+        ),
+    };
+
+    Ok(Vc::cell(detail.map(|d| d.into())))
+}
+
+#[turbo_tasks::value]
+struct EmitConflictIssue {
+    asset_path: FileSystemPath,
+    detail: RcStr,
+}
+
+#[turbo_tasks::value_impl]
+impl Issue for EmitConflictIssue {
+    #[turbo_tasks::function]
+    fn file_path(&self) -> Vc<FileSystemPath> {
+        self.asset_path.clone().cell()
+    }
+
+    #[turbo_tasks::function]
+    fn stage(&self) -> Vc<IssueStage> {
+        IssueStage::Emit.cell()
+    }
+
+    fn severity(&self) -> IssueSeverity {
+        IssueSeverity::Error
+    }
+
+    #[turbo_tasks::function]
+    fn title(&self) -> Vc<StyledString> {
+        StyledString::Text(
+            "Two or more assets with different content were emitted to the same output path".into(),
+        )
+        .cell()
+    }
+
+    #[turbo_tasks::function]
+    fn description(&self) -> Vc<OptionStyledString> {
+        Vc::cell(Some(
+            StyledString::Text(self.detail.clone()).resolved_cell(),
+        ))
+    }
+}
diff --git a/turbopack/crates/turbopack-core/src/issue/mod.rs b/turbopack/crates/turbopack-core/src/issue/mod.rs
index feee0709e2300..80850124d7250 100644
--- a/turbopack/crates/turbopack-core/src/issue/mod.rs
+++ b/turbopack/crates/turbopack-core/src/issue/mod.rs
@@ -875,6 +875,7 @@ pub enum IssueStage {
     Resolve,
     Bindings,
     CodeGen,
+    Emit,
     Unsupported,
     Misc,
     Other(RcStr),
@@ -893,6 +894,7 @@ impl Display for IssueStage {
             IssueStage::Analysis => write!(f, "analysis"),
             IssueStage::Bindings => write!(f, "bindings"),
             IssueStage::CodeGen => write!(f, "code gen"),
+            IssueStage::Emit => write!(f, "emit"),
             IssueStage::Unsupported => write!(f, "unsupported"),
             IssueStage::AppStructure => write!(f, "app structure"),
             IssueStage::Misc => write!(f, "misc"),

PATCH

echo "Patch applied successfully."
