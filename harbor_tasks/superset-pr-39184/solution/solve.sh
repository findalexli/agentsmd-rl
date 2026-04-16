#!/bin/bash
set -e

cd /workspace/superset

# Idempotency check - skip if patch already applied
if grep -q "ColumnHeightOutlined" superset-frontend/plugins/plugin-chart-table/src/TableChart.tsx 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
git apply --whitespace=fix <<'PATCH'
diff --git a/superset-frontend/plugins/plugin-chart-pivot-table/package.json b/superset-frontend/plugins/plugin-chart-pivot-table/package.json
index 9eeaf62234c4..7d0d0b56e1d0 100644
--- a/superset-frontend/plugins/plugin-chart-pivot-table/package.json
+++ b/superset-frontend/plugins/plugin-chart-pivot-table/package.json
@@ -34,8 +34,7 @@
     "lodash": "^4.18.1",
     "prop-types": "*",
     "react": "^17.0.2",
-    "react-dom": "^17.0.2",
-    "react-icons": "5.4.0"
+    "react-dom": "^17.0.2"
   },
   "devDependencies": {
     "@babel/types": "^7.29.0",
diff --git a/superset-frontend/plugins/plugin-chart-pivot-table/src/react-pivottable/TableRenderers.tsx b/superset-frontend/plugins/plugin-chart-pivot-table/src/react-pivottable/TableRenderers.tsx
index be4fca29d004..af142249cca9 100644
--- a/superset-frontend/plugins/plugin-chart-pivot-table/src/react-pivottable/TableRenderers.tsx
+++ b/superset-frontend/plugins/plugin-chart-pivot-table/src/react-pivottable/TableRenderers.tsx
@@ -22,9 +22,11 @@ import { safeHtmlSpan } from '@superset-ui/core';
 import { t } from '@apache-superset/core/translation';
 import { supersetTheme } from '@apache-superset/core/theme';
 import PropTypes from 'prop-types';
-import { FaSort } from 'react-icons/fa';
-import { FaSortDown as FaSortDesc } from 'react-icons/fa';
-import { FaSortUp as FaSortAsc } from 'react-icons/fa';
+import {
+  CaretUpOutlined,
+  CaretDownOutlined,
+  ColumnHeightOutlined,
+} from '@ant-design/icons';
 import {
   ColorFormatters,
   getTextColorForBackground,
@@ -855,7 +857,7 @@ export class TableRenderer extends Component<

           if (activeSortColumn !== key) {
             return (
-              <FaSort
+              <ColumnHeightOutlined
                 onClick={() =>
                   this.sortData(key, visibleColKeys, pivotData, maxRowIndex)
                 }
@@ -863,7 +865,8 @@ export class TableRenderer extends Component<
             );
           }

-          const SortIcon = sortingOrder[key] === 'asc' ? FaSortAsc : FaSortDesc;
+          const SortIcon =
+            sortingOrder[key] === 'asc' ? CaretUpOutlined : CaretDownOutlined;
           return (
             <SortIcon
               onClick={() =>
@@ -873,7 +876,9 @@ export class TableRenderer extends Component<
           );
         };
         const headerCellFormattedValue =
-          dateFormatters?.[attrName]?.(convertToNumberIfNumeric(colKey[attrIdx])) ?? colKey[attrIdx];
+          dateFormatters?.[attrName]?.(
+            convertToNumberIfNumeric(colKey[attrIdx]),
+          ) ?? colKey[attrIdx];
         const { backgroundColor, color } = getCellColor(
           [attrName],
           headerCellFormattedValue,
diff --git a/superset-frontend/plugins/plugin-chart-table/package.json b/superset-frontend/plugins/plugin-chart-table/package.json
index 38ce880c570a..d4b9f099a695 100644
--- a/superset-frontend/plugins/plugin-chart-table/package.json
+++ b/superset-frontend/plugins/plugin-chart-table/package.json
@@ -30,7 +30,6 @@
     "d3-array": "^3.2.4",
     "lodash": "^4.18.1",
     "memoize-one": "^5.2.1",
-    "react-icons": "5.4.0",
     "react-table": "^7.8.0",
     "regenerator-runtime": "^0.14.1",
     "xss": "^1.0.15"
diff --git a/superset-frontend/plugins/plugin-chart-table/src/TableChart.tsx b/superset-frontend/plugins/plugin-chart-table/src/TableChart.tsx
index 02b0a8520a64..f8105c5198f9 100644
--- a/superset-frontend/plugins/plugin-chart-table/src/TableChart.tsx
+++ b/superset-frontend/plugins/plugin-chart-table/src/TableChart.tsx
@@ -35,9 +35,11 @@ import {
   Row,
 } from 'react-table';
 import { extent as d3Extent, max as d3Max } from 'd3-array';
-import { FaSort } from 'react-icons/fa';
-import { FaSortDown as FaSortDesc } from 'react-icons/fa';
-import { FaSortUp as FaSortAsc } from 'react-icons/fa';
+import {
+  CaretUpOutlined,
+  CaretDownOutlined,
+  ColumnHeightOutlined,
+} from '@ant-design/icons';
 import cx from 'classnames';
 import {
   DataRecord,
@@ -221,9 +223,9 @@ function cellBackground({

 function SortIcon<D extends object>({ column }: { column: ColumnInstance<D> }) {
   const { isSorted, isSortedDesc } = column;
-  let sortIcon = <FaSort />;
+  let sortIcon = <ColumnHeightOutlined />;
   if (isSorted) {
-    sortIcon = isSortedDesc ? <FaSortDesc /> : <FaSortAsc />;
+    sortIcon = isSortedDesc ? <CaretDownOutlined /> : <CaretUpOutlined />;
   }
   return sortIcon;
 }
PATCH

echo "Patch applied successfully"
