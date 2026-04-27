#!/usr/bin/env bash
set -euo pipefail

cd /workspace/OpenHands

# Idempotency: skip if patch already applied.
if grep -q "forceShowAdvancedView = false" \
     frontend/src/components/features/settings/sdk-settings/sdk-section-page.tsx \
     2>/dev/null; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/frontend/src/components/features/settings/sdk-settings/sdk-section-page.tsx b/frontend/src/components/features/settings/sdk-settings/sdk-section-page.tsx
index f30e42562dac..8c84cd901fb4 100644
--- a/frontend/src/components/features/settings/sdk-settings/sdk-section-page.tsx
+++ b/frontend/src/components/features/settings/sdk-settings/sdk-section-page.tsx
@@ -49,6 +49,35 @@ const getLessDetailedView = (
 ): SettingsView =>
   VIEW_ORDER[nextView] < VIEW_ORDER[currentView] ? nextView : currentView;

+const normalizeView = (
+  view: SettingsView,
+  {
+    showAdvanced,
+    showAll,
+  }: {
+    showAdvanced: boolean;
+    showAll: boolean;
+  },
+): SettingsView => {
+  if (view === "all") {
+    if (showAll) {
+      return "all";
+    }
+
+    return showAdvanced ? "advanced" : "basic";
+  }
+
+  if (view === "advanced") {
+    if (showAdvanced) {
+      return "advanced";
+    }
+
+    return showAll ? "all" : "basic";
+  }
+
+  return "basic";
+};
+
 export interface SdkSectionHeaderProps {
   values: SettingsFormValues;
   isDisabled: boolean;
@@ -75,6 +104,8 @@ export function SdkSectionPage({
   buildPayload,
   onSaveSuccess,
   getInitialView,
+  forceShowAdvancedView = false,
+  allowAllView = true,
   testId = "sdk-section-settings-screen",
 }: {
   sectionKeys: string[];
@@ -97,6 +128,8 @@ export function SdkSectionPage({
     settings: Settings,
     filteredSchema: SettingsSchema,
   ) => SettingsView;
+  forceShowAdvancedView?: boolean;
+  allowAllView?: boolean;
   testId?: string;
 }) {
   const { t } = useTranslation();
@@ -148,8 +181,9 @@ export function SdkSectionPage({
     };
   }, [schema, stableSectionKeys]);

-  const showAdvanced = hasAdvancedSettings(filteredSchema);
-  const showAll = hasMinorSettings(filteredSchema);
+  const showAdvanced =
+    forceShowAdvancedView || hasAdvancedSettings(filteredSchema);
+  const showAll = allowAllView && hasMinorSettings(filteredSchema);

   const initialValues = React.useMemo(() => {
     if (!settings || !filteredSchema) return null;
@@ -162,10 +196,20 @@ export function SdkSectionPage({

   const initialView = React.useMemo(() => {
     if (!settings || !filteredSchema) return null;
-    return getInitialView
+
+    const resolvedInitialView = getInitialView
       ? getInitialView(settings, filteredSchema)
       : inferInitialView(settings, filteredSchema, settingsSource);
-  }, [settings, filteredSchema, getInitialView, settingsSource]);
+
+    return normalizeView(resolvedInitialView, { showAdvanced, showAll });
+  }, [
+    settings,
+    filteredSchema,
+    getInitialView,
+    settingsSource,
+    showAdvanced,
+    showAll,
+  ]);

   React.useEffect(() => {
     hasHydratedViewRef.current = false;
diff --git a/frontend/src/routes/llm-settings.tsx b/frontend/src/routes/llm-settings.tsx
index 67b0cddfdf70..631eadbcb2ba 100644
--- a/frontend/src/routes/llm-settings.tsx
+++ b/frontend/src/routes/llm-settings.tsx
@@ -391,6 +391,8 @@ export function LlmSettingsScreen({
       header={buildHeader}
       buildPayload={buildPayload}
       getInitialView={getInitialView}
+      forceShowAdvancedView
+      allowAllView={!isSaasMode}
       testId="llm-settings-screen"
     />
   );
PATCH

echo "Gold patch applied successfully."
