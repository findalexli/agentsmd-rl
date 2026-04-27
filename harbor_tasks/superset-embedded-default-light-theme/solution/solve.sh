#!/usr/bin/env bash
set -euo pipefail

cd /workspace/superset

# Idempotency: if patch already applied, skip
if grep -q "this.initialMode = initialMode;" superset-frontend/src/theme/ThemeController.ts 2>/dev/null; then
  echo "Gold patch already applied"
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/superset-frontend/packages/superset-core/src/theme/types.ts b/superset-frontend/packages/superset-core/src/theme/types.ts
index a0b30ca59562..87bd226f874f 100644
--- a/superset-frontend/packages/superset-core/src/theme/types.ts
+++ b/superset-frontend/packages/superset-core/src/theme/types.ts
@@ -426,6 +426,7 @@ export interface ThemeControllerOptions {
   canUpdateTheme?: () => boolean;
   canUpdateMode?: () => boolean;
   isGlobalContext?: boolean;
+  initialMode?: ThemeMode;
 }

 export interface ThemeContextType {
diff --git a/superset-frontend/src/embedded/EmbeddedContextProviders.tsx b/superset-frontend/src/embedded/EmbeddedContextProviders.tsx
index 9ea9c0744ab7..0a832ed294af 100644
--- a/superset-frontend/src/embedded/EmbeddedContextProviders.tsx
+++ b/superset-frontend/src/embedded/EmbeddedContextProviders.tsx
@@ -26,7 +26,7 @@ import { DynamicPluginProvider } from 'src/components';
 import { EmbeddedUiConfigProvider } from 'src/components/UiConfigContext';
 import { SupersetThemeProvider } from 'src/theme/ThemeProvider';
 import { ThemeController } from 'src/theme/ThemeController';
-import { type ThemeStorage } from '@apache-superset/core/theme';
+import { type ThemeStorage, ThemeMode } from '@apache-superset/core/theme';
 import { store } from 'src/views/store';
 import querystring from 'query-string';

@@ -52,6 +52,7 @@ class ThemeMemoryStorageAdapter implements ThemeStorage {

 const themeController = new ThemeController({
   storage: new ThemeMemoryStorageAdapter(),
+  initialMode: ThemeMode.DEFAULT,
 });

 export const getThemeController = (): ThemeController => themeController;
diff --git a/superset-frontend/src/theme/ThemeController.ts b/superset-frontend/src/theme/ThemeController.ts
index fafbe784914a..5234ff19aa57 100644
--- a/superset-frontend/src/theme/ThemeController.ts
+++ b/superset-frontend/src/theme/ThemeController.ts
@@ -102,15 +102,19 @@ export class ThemeController {
   // Track loaded font URLs to avoid duplicate injections
   private loadedFontUrls: Set<string> = new Set();

+  private initialMode: ThemeMode | undefined;
+
   constructor({
     storage = new LocalStorageAdapter(),
     modeStorageKey = STORAGE_KEYS.THEME_MODE,
     themeObject = supersetThemeObject,
     defaultTheme = (supersetThemeObject.theme as AnyThemeConfig) ?? {},
     onChange = undefined,
+    initialMode = undefined,
   }: ThemeControllerOptions = {}) {
     this.storage = storage;
     this.modeStorageKey = modeStorageKey;
+    this.initialMode = initialMode;

     // Controller creates and owns the global theme
     this.globalTheme = themeObject;
@@ -743,6 +747,13 @@ export class ThemeController {
       return ThemeMode.DEFAULT;
     }

+    // Use explicit initial mode if provided (e.g. embedded dashboards default to light)
+    if (
+      this.initialMode !== undefined &&
+      this.isValidThemeMode(this.initialMode)
+    )
+      return this.initialMode;
+
     // Default to system preference when both themes are available
     return ThemeMode.SYSTEM;
   }
PATCH

echo "Gold patch applied"
