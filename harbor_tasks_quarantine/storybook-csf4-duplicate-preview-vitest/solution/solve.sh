#!/usr/bin/env bash
set -euo pipefail

cd /workspace/storybook

# Idempotent: skip if already applied
if ! grep -q 'isCSF4' code/addons/vitest/src/vitest-plugin/utils.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/code/addons/vitest/src/vitest-plugin/index.ts b/code/addons/vitest/src/vitest-plugin/index.ts
index 8d3f7c2666a4..98af7d649d54 100644
--- a/code/addons/vitest/src/vitest-plugin/index.ts
+++ b/code/addons/vitest/src/vitest-plugin/index.ts
@@ -303,14 +303,9 @@ export const storybookTest = async (options?: UserOptions): Promise<Plugin[]> =>
       finalOptions.includeStories = includeStories;
       const projectId = oneWayHash(finalOptions.configDir);

-      const previewOrConfigFile = loadPreviewOrConfigFile({ configDir: finalOptions.configDir });
-      const previewConfig = previewOrConfigFile ? await readConfig(previewOrConfigFile) : undefined;
-      const isCSF4 = previewConfig ? isCsfFactoryPreview(previewConfig) : false;
-
       const areProjectAnnotationRequired = await requiresProjectAnnotations(
         nonMutableInputConfig.test,
-        finalOptions,
-        isCSF4
+        finalOptions
       );

       const internalSetupFiles = (
@@ -318,7 +313,6 @@ export const storybookTest = async (options?: UserOptions): Promise<Plugin[]> =>
           '@storybook/addon-vitest/internal/setup-file',
           areProjectAnnotationRequired &&
             '@storybook/addon-vitest/internal/setup-file-with-project-annotations',
-          isCSF4 && previewOrConfigFile,
         ].filter(Boolean) as string[]
       ).map((filePath) => fileURLToPath(import.meta.resolve(filePath)));

diff --git a/code/addons/vitest/src/vitest-plugin/utils.ts b/code/addons/vitest/src/vitest-plugin/utils.ts
index dfa3c74cc0e6..ce3946aa9498 100644
--- a/code/addons/vitest/src/vitest-plugin/utils.ts
+++ b/code/addons/vitest/src/vitest-plugin/utils.ts
@@ -20,8 +20,7 @@ const logBoxOnce = (message: string) => {

 export async function requiresProjectAnnotations(
   testConfig: ViteUserConfig['test'] | undefined,
-  finalOptions: InternalOptions,
-  isCSF4: boolean
+  finalOptions: InternalOptions
 ) {
   const setupFiles = Array.isArray(testConfig?.setupFiles)
     ? testConfig.setupFiles
@@ -58,8 +57,6 @@ export async function requiresProjectAnnotations(
       You can safely remove the "setProjectAnnotations" call from your setup file, or remove the file entirely if you don't have custom code there.
     `);

-    return false;
-  } else if (isCSF4) {
     return false;
   }


PATCH

echo "Patch applied successfully."
