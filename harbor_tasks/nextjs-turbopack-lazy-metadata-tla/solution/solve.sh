#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotency: check if the lazy require pattern is already applied
if grep -q '() => require(/\*turbopackChunkingType' crates/next-core/src/app_page_loader_tree.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/next-core/src/app_page_loader_tree.rs b/crates/next-core/src/app_page_loader_tree.rs
index a10976b59291c9..46b8c5511d175f 100644
--- a/crates/next-core/src/app_page_loader_tree.rs
+++ b/crates/next-core/src/app_page_loader_tree.rs
@@ -189,7 +189,7 @@ impl AppPageLoaderTreeBuilder {
                 // when mixing ESM imports and requires).
                 self.base.imports.push(
                     format!(
-                        "const {identifier} = require(/*turbopackChunkingType: \
+                        "const {identifier} = () => require(/*turbopackChunkingType: \
                          shared*/\"{inner_module_id}\");"
                     )
                     .into(),
@@ -208,7 +208,10 @@ impl AppPageLoaderTreeBuilder {
                     .insert(inner_module_id.into(), module);

                 let s = "      ";
-                writeln!(self.loader_tree_code, "{s}{identifier}.default,")?;
+                writeln!(
+                    self.loader_tree_code,
+                    "{s}async (props) => interopDefault(await {identifier}())(props),"
+                )?;
             }
         }
         Ok(())
@@ -239,7 +242,7 @@ impl AppPageLoaderTreeBuilder {
         // requires).
         self.base.imports.push(
             format!(
-                "const {identifier} = require(/*turbopackChunkingType: \
+                "const {identifier} = () => require(/*turbopackChunkingType: \
                  shared*/\"{inner_module_id}\");"
             )
             .into(),
@@ -254,8 +257,51 @@ impl AppPageLoaderTreeBuilder {
             .inner_assets
             .insert(inner_module_id.into(), module);

+        let alt = if let Some(alt_path) = alt_path {
+            let identifier = magic_identifier::mangle(&format!("{name} alt text #{i}"));
+            let inner_module_id = format!("METADATA_ALT_{i}");
+
+            // This should use the same importing mechanism as create_module_tuple_code, so that the
+            // relative order of items is retained (which isn't the case when mixing ESM imports and
+            // requires).
+            self.base.imports.push(
+                format!(
+                    "const {identifier} = () => require(/*turbopackChunkingType: \
+                     shared*/\"{inner_module_id}\");"
+                )
+                .into(),
+            );
+
+            let module = self
+                .base
+                .process_source(Vc::upcast(TextContentFileSource::new(Vc::upcast(
+                    FileSource::new(alt_path),
+                ))))
+                .to_resolved()
+                .await?;
+
+            self.base
+                .inner_assets
+                .insert(inner_module_id.into(), module);
+
+            Some(identifier)
+        } else {
+            None
+        };
+
         let s = "      ";
-        writeln!(self.loader_tree_code, "{s}(async (props) => [{{")?;
+        writeln!(self.loader_tree_code, "{s}(async (props) => {{")?;
+        writeln!(
+            self.loader_tree_code,
+            "{s}  const mod = interopDefault(await {identifier}());"
+        )?;
+        if let Some(alt) = &alt {
+            writeln!(
+                self.loader_tree_code,
+                "{s}  const alt = interopDefault(await {alt}());"
+            )?;
+        }
+        writeln!(self.loader_tree_code, "{s}  return [{{")?;
         let pathname_prefix = if let Some(base_path) = &self.base_path {
             format!("{base_path}/{app_page}")
         } else {
@@ -264,68 +310,37 @@ impl AppPageLoaderTreeBuilder {
         let metadata_route = &*get_metadata_route_name(item.clone().into()).await?;
         writeln!(
             self.loader_tree_code,
-            "{s}  url: fillMetadataSegment({}, await props.params, {}, true) + \
-             `?${{{identifier}.default.src.split(\"/\").splice(-1)[0]}}`,",
+            "{s}    url: fillMetadataSegment({}, await props.params, {}, true) + \
+             `?${{mod.src.split(\"/\").splice(-1)[0]}}`,",
             StringifyJs(&pathname_prefix),
             StringifyJs(metadata_route),
         )?;

         let numeric_sizes = name == "twitter" || name == "openGraph";
         if numeric_sizes {
-            writeln!(
-                self.loader_tree_code,
-                "{s}  width: {identifier}.default.width,"
-            )?;
-            writeln!(
-                self.loader_tree_code,
-                "{s}  height: {identifier}.default.height,"
-            )?;
+            writeln!(self.loader_tree_code, "{s}    width: mod.width,")?;
+            writeln!(self.loader_tree_code, "{s}    height: mod.height,")?;
         } else {
             // For SVGs, skip sizes and use "any" to let it scale automatically based on viewport,
             // For the images doesn't provide the size properly, use "any" as well.
             // If the size is presented, use the actual size for the image.
             let sizes = if path.has_extension(".svg") {
-                "any".to_string()
+                "any"
             } else {
-                format!("${{{identifier}.default.width}}x${{{identifier}.default.height}}")
+                "${mod.width}x${mod.height}"
             };
-            writeln!(self.loader_tree_code, "{s}  sizes: `{sizes}`,")?;
+            writeln!(self.loader_tree_code, "{s}    sizes: `{sizes}`,")?;
         }

         let content_type = get_content_type(path).await?;
-        writeln!(self.loader_tree_code, "{s}  type: `{content_type}`,")?;
-
-        if let Some(alt_path) = alt_path {
-            let identifier = magic_identifier::mangle(&format!("{name} alt text #{i}"));
-            let inner_module_id = format!("METADATA_ALT_{i}");
-
-            // This should use the same importing mechanism as create_module_tuple_code, so that the
-            // relative order of items is retained (which isn't the case when mixing ESM imports and
-            // requires).
-            self.base.imports.push(
-                format!(
-                    "const {identifier} = require(/*turbopackChunkingType: \
-                     shared*/\"{inner_module_id}\");"
-                )
-                .into(),
-            );
-
-            let module = self
-                .base
-                .process_source(Vc::upcast(TextContentFileSource::new(Vc::upcast(
-                    FileSource::new(alt_path),
-                ))))
-                .to_resolved()
-                .await?;
-
-            self.base
-                .inner_assets
-                .insert(inner_module_id.into(), module);
+        writeln!(self.loader_tree_code, "{s}    type: `{content_type}`,")?;

-            writeln!(self.loader_tree_code, "{s}  alt: {identifier}.default,")?;
+        if alt.is_some() {
+            writeln!(self.loader_tree_code, "{s}    alt,")?;
         }

-        writeln!(self.loader_tree_code, "{s}}}]),")?;
+        writeln!(self.loader_tree_code, "{s}  }}];")?;
+        writeln!(self.loader_tree_code, "{s}}}),")?;

         Ok(())
     }
diff --git a/packages/next/src/lib/metadata/resolve-metadata.ts b/packages/next/src/lib/metadata/resolve-metadata.ts
index bac8bb9e146bea..1ae86da5d768e4 100644
--- a/packages/next/src/lib/metadata/resolve-metadata.ts
+++ b/packages/next/src/lib/metadata/resolve-metadata.ts
@@ -41,7 +41,6 @@ import {
   getComponentTypeModule,
   getLayoutOrPageModule,
 } from '../../server/lib/app-dir-module'
-import { interopDefault } from '../interop-default'
 import {
   resolveAlternates,
   resolveAppleWebApp,
@@ -572,11 +571,11 @@ async function collectStaticImagesFiles(

   const iconPromises = metadata[type as 'icon' | 'apple'].map(
     async (imageModule: (p: any) => Promise<MetadataImageModule[]>) =>
-      await interopDefault(imageModule)(props)
+      await imageModule(props)
   )

   return iconPromises?.length > 0
-    ? (await Promise.all(iconPromises))?.flat()
+    ? (await Promise.all(iconPromises)).flat()
     : undefined
 }

PATCH

echo "Patch applied successfully."
