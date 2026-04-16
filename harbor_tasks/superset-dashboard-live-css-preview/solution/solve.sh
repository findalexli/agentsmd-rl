#!/bin/bash
set -e

cd /workspace/superset

# Check if already applied
if grep -q "handleCustomCssChange" superset-frontend/src/dashboard/components/PropertiesModal/index.tsx; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/superset-frontend/src/dashboard/components/PropertiesModal/index.tsx b/superset-frontend/src/dashboard/components/PropertiesModal/index.tsx
index 1234567..abcdefg 100644
--- a/superset-frontend/src/dashboard/components/PropertiesModal/index.tsx
+++ b/superset-frontend/src/dashboard/components/PropertiesModal/index.tsx
@@ -53,6 +53,7 @@ import {
   setColorScheme,
   setDashboardMetadata,
 } from 'src/dashboard/actions/dashboardState';
+import { dashboardInfoChanged } from 'src/dashboard/actions/dashboardInfo';
 import { areObjectsEqual } from 'src/reduxUtils';
 import { StandardModal, useModalValidation } from 'src/components/Modal';
 import { validateRefreshFrequency } from '../RefreshFrequency';
@@ -143,6 +144,8 @@ const PropertiesModal = ({
   >([]);
   const categoricalSchemeRegistry = getCategoricalSchemeRegistry();
   const originalDashboardMetadata = useRef<Record<string, any>>({});
+  const originalCss = useRef<string | null>(null);
+  const cssDebounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

   const handleErrorResponse = async (response: Response) => {
     const { error, statusText, message } = await getClientErrorObject(response);
@@ -195,6 +198,9 @@ const PropertiesModal = ({
       setOwners(owners);
       setRoles(roles);
       setCustomCss(css || '');
+      if (originalCss.current === null) {
+        originalCss.current = css || '';
+      }
       setCurrentColorScheme(metadata?.color_scheme);
       setSelectedThemeId(theme?.id || null);

@@ -269,7 +275,19 @@ const PropertiesModal = ({
     setRoles(parsedRoles);
   };

-  const handleOnCancel = () => onHide();
+  const handleOnCancel = () => {
+    if (cssDebounceTimer.current) {
+      clearTimeout(cssDebounceTimer.current);
+      cssDebounceTimer.current = null;
+    }
+    if (originalCss.current !== null) {
+      dispatch(dashboardInfoChanged({ css: originalCss.current }));
+      dispatch(
+        setColorScheme(originalDashboardMetadata.current.color_scheme ?? ''),
+      );
+    }
+    onHide();
+  };

   const onColorSchemeChange = (
     colorScheme = '',
@@ -429,6 +447,14 @@ const PropertiesModal = ({
     }
   };

+  // Must be defined before the data-loading effect so it runs first when show
+  // becomes true, ensuring handleDashboardData sees null and captures original CSS
+  useEffect(() => {
+    if (show) {
+      originalCss.current = null;
+    }
+  }, [show]);
+
   useEffect(() => {
     if (show) {
       // Reset loading state when modal opens
@@ -596,6 +622,32 @@ const PropertiesModal = ({

   const isDataReady = !isLoading && dashboardInfo;

+  // Debounced live CSS preview so changes are reflected on the dashboard
+  // without clicking Apply. Called only on user edits, not on data load.
+  const handleCustomCssChange = useCallback(
+    (css: string) => {
+      setCustomCss(css);
+      if (cssDebounceTimer.current) {
+        clearTimeout(cssDebounceTimer.current);
+        cssDebounceTimer.current = null;
+      }
+      cssDebounceTimer.current = setTimeout(() => {
+        dispatch(dashboardInfoChanged({ css }));
+      }, 500);
+    },
+    [dispatch],
+  );
+
+  useEffect(
+    () => () => {
+      if (cssDebounceTimer.current) {
+        clearTimeout(cssDebounceTimer.current);
+        cssDebounceTimer.current = null;
+      }
+    },
+    [],
+  );
+
   // Validate basic section when title changes or data loads
   useEffect(() => {
     if (isDataReady) {
@@ -722,7 +774,7 @@ const PropertiesModal = ({
                   showChartTimestamps={showChartTimestamps}
                   onThemeChange={handleThemeChange}
                   onColorSchemeChange={onColorSchemeChange}
-                  onCustomCssChange={setCustomCss}
+                  onCustomCssChange={handleCustomCssChange}
                   onShowChartTimestampsChange={setShowChartTimestamps}
                   addDangerToast={addDangerToast}
                 />
PATCH

echo "Patch applied successfully"
