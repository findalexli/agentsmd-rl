#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotent: skip if already applied
if grep -q "mergedData.Count > 0 || !isPopping" src/Controls/src/Core/Shell/ShellNavigationManager.cs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/src/Controls/src/Core/Shell/ShellNavigationManager.cs b/src/Controls/src/Core/Shell/ShellNavigationManager.cs
index dbe205c51e56..efac0f54f2e6 100644
--- a/src/Controls/src/Core/Shell/ShellNavigationManager.cs
+++ b/src/Controls/src/Core/Shell/ShellNavigationManager.cs
@@ -313,14 +313,27 @@ public static void ApplyQueryAttributes(Element element, ShellRouteParameters qu
 			var mergedData = MergeData(element, filteredQuery, isPopping);

 			//if we are pop or navigating back, we need to apply the query attributes to the ShellContent
-			if (isPopping)
+			if (isPopping && mergedData.Count > 0 )
 			{
 				element.SetValue(ShellContent.QueryAttributesProperty, mergedData);
 			}
-			baseShellItem.ApplyQueryAttributes(mergedData);
+
+			// Skip applying query attributes if the merged data is empty and we're popping back
+			// This respects when user calls query.Clear() - they don't want attributes applied on back navigation
+			if (mergedData.Count > 0 || !isPopping)
+			{
+				baseShellItem.ApplyQueryAttributes(mergedData);
+			}
 		}
 		else if (isLastItem)
-			element.SetValue(ShellContent.QueryAttributesProperty, MergeData(element, query, isPopping));
+		{
+			var mergedData = MergeData(element, query, isPopping);
+			// Skip setting query attributes if the merged data is empty and we're popping back
+			if (mergedData.Count > 0 || !isPopping)
+			{
+				element.SetValue(ShellContent.QueryAttributesProperty, mergedData);
+			}
+		}

 		ShellRouteParameters MergeData(Element shellElement, ShellRouteParameters data, bool isPopping)
 		{

PATCH

echo "Patch applied successfully."
