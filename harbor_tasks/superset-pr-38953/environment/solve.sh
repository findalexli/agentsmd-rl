#!/bin/bash
set -e

cd /workspace/superset

# Apply the fix
patch -p1 <<'PATCH'
diff --git a/superset-frontend/plugins/plugin-chart-pivot-table/src/react-pivottable/TableRenderers.tsx b/superset-frontend/plugins/plugin-chart-pivot-table/src/react-pivottable/TableRenderers.tsx
index cbf7e1619df0..be4fca29d004 100644
--- a/superset-frontend/plugins/plugin-chart-pivot-table/src/react-pivottable/TableRenderers.tsx
+++ b/superset-frontend/plugins/plugin-chart-pivot-table/src/react-pivottable/TableRenderers.tsx
@@ -269,6 +269,11 @@ function sortHierarchicalObject(
   return result;
 }

+function convertToNumberIfNumeric(value: string): string | number {
+  const n = Number(value);
+  return value.trim() !== '' && !Number.isNaN(n) ? n : value;
+}
+
 function convertToArray(
   obj: Map<string, unknown>,
   rowEnabled: boolean | undefined,
@@ -868,7 +873,7 @@ export class TableRenderer extends Component<
           );
         };
         const headerCellFormattedValue =
-          dateFormatters?.[attrName]?.(colKey[attrIdx]) ?? colKey[attrIdx];
+          dateFormatters?.[attrName]?.(convertToNumberIfNumeric(colKey[attrIdx])) ?? colKey[attrIdx];
         const { backgroundColor, color } = getCellColor(
           [attrName],
           headerCellFormattedValue,
@@ -1111,7 +1116,7 @@ export class TableRenderer extends Component<
           : null;

         const headerCellFormattedValue =
-          dateFormatters?.[rowAttrs[i]]?.(r) ?? r;
+          dateFormatters?.[rowAttrs[i]]?.(convertToNumberIfNumeric(r)) ?? r;

         const { backgroundColor, color } = getCellColor(
           [rowAttrs[i]],
PATCH

echo "Patch applied successfully"
