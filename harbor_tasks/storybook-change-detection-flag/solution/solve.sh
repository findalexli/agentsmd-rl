#!/usr/bin/env bash
set -euo pipefail

cd /workspace/storybook

# Idempotent: skip if already applied
if grep -q 'changeDetection' code/core/src/core-server/presets/common-preset.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/code/core/src/core-server/presets/common-preset.ts b/code/core/src/core-server/presets/common-preset.ts
index c3479f2e42b1..60a2787a8176 100644
--- a/code/core/src/core-server/presets/common-preset.ts
+++ b/code/core/src/core-server/presets/common-preset.ts
@@ -204,19 +204,20 @@ export const core = async (existing: CoreConfig, options: Options): Promise<Core

 export const features: PresetProperty<'features'> = async (existing) => ({
   ...existing,
+  actions: true,
   argTypeTargetsV7: true,
-  legacyDecoratorFileOrder: false,
+  backgrounds: true,
+  changeDetection: false,
+  componentsManifest: true,
+  controls: true,
   disallowImplicitActionsInRenderV8: true,
-  viewport: true,
   highlight: true,
-  controls: true,
   interactions: true,
-  actions: true,
-  backgrounds: true,
-  outline: true,
+  legacyDecoratorFileOrder: false,
   measure: true,
+  outline: true,
   sidebarOnboardingChecklist: true,
-  componentsManifest: true,
+  viewport: true,
 });

 export const csfIndexer: Indexer = {
diff --git a/code/core/src/types/modules/core-common.ts b/code/core/src/types/modules/core-common.ts
index 5f6339dd09e8..4b5e046df196 100644
--- a/code/core/src/types/modules/core-common.ts
+++ b/code/core/src/types/modules/core-common.ts
@@ -535,6 +535,13 @@ export interface StorybookConfigRaw {
      * @experimental This feature is in early development and may change significantly in future releases.
      */
     experimentalCodeExamples?: boolean;
+
+    /**
+     * Enable change detection
+     * TODO: Turn to true before 10.4 release
+     * @default false
+     */
+    changeDetection?: boolean;
   };

   build?: TestBuildConfig;
diff --git a/docs/api/main-config/main-config-features.mdx b/docs/api/main-config/main-config-features.mdx
index 6f7d63370219..f119c8d2239b 100644
--- a/docs/api/main-config/main-config-features.mdx
+++ b/docs/api/main-config/main-config-features.mdx
@@ -16,6 +16,7 @@ Type:
   actions?: boolean;
   argTypeTargetsV7?: boolean;
   backgrounds?: boolean;
+  changeDetection?: boolean;
   componentsManifest?: boolean;
   controls?: boolean;
   developmentModeForBuild?: boolean;
@@ -41,6 +42,7 @@ Type:
   angularFilterNonInputControls?: boolean;
   argTypeTargetsV7?: boolean;
   backgrounds?: boolean;
+  changeDetection?: boolean;
   controls?: boolean;
   developmentModeForBuild?: boolean;
   highlight?: boolean;
@@ -62,6 +64,7 @@ Type:
   actions?: boolean;
   argTypeTargetsV7?: boolean;
   backgrounds?: boolean;
+  changeDetection?: boolean;
   controls?: boolean;
   developmentModeForBuild?: boolean;
   highlight?: boolean;
@@ -135,6 +138,14 @@ Generate [manifests](../../ai/manifests.mdx), used by the [MCP server](../../ai/

 </If>

+## `changeDetection`
+
+Type: `boolean`
+
+Default: `true`
+
+Enable change detection.
+
 ## `controls`

 Type: `boolean`

PATCH

echo "Patch applied successfully."
