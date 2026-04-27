#!/usr/bin/env bash
set -euo pipefail

cd /workspace/superset

if grep -q 'compactChartHeight: 100' superset-frontend/plugins/plugin-chart-echarts/src/constants.ts 2>/dev/null; then
    echo "Gold patch already applied."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/superset-frontend/plugins/plugin-chart-echarts/src/Timeseries/transformProps.ts b/superset-frontend/plugins/plugin-chart-echarts/src/Timeseries/transformProps.ts
index f7d6fe86c81c..6966be78a3ef 100644
--- a/superset-frontend/plugins/plugin-chart-echarts/src/Timeseries/transformProps.ts
+++ b/superset-frontend/plugins/plugin-chart-echarts/src/Timeseries/transformProps.ts
@@ -711,6 +711,10 @@ export default function transformProps(
     onLegendScroll,
   } = hooks;

+  const addYAxisLabelOffset =
+    !!yAxisTitle && convertInteger(yAxisTitleMargin) !== 0;
+  const addXAxisLabelOffset =
+    !!xAxisTitle && convertInteger(xAxisTitleMargin) !== 0;
   const legendData =
     colorByPrimaryAxis && groupBy.length === 0 && series.length > 0
       ? (() => {
@@ -745,10 +749,6 @@ export default function transformProps(
           )
           .map(entry => entry.name || '')
           .concat(extractAnnotationLabels(annotationLayers));
-  const addYAxisLabelOffset =
-    !!yAxisTitle && convertInteger(yAxisTitleMargin) !== 0;
-  const addXAxisLabelOffset =
-    !!xAxisTitle && convertInteger(xAxisTitleMargin) !== 0;

   const sortedLegendData = [...legendData].sort((a: string, b: string) => {
     if (!legendSort) return 0;
@@ -824,12 +824,21 @@ export default function transformProps(
     isHorizontal,
   );

+  // Reduce grid padding for small charts to maximize the drawing area.
+  // Keep enough top padding so the max label doesn't clip against the cell border.
+  // Preserve bottom padding when zoomable, since getPadding() reserves space for the dataZoom slider.
+  if (height < TIMESERIES_CONSTANTS.compactChartHeight) {
+    padding.top = Math.min(padding.top, 12);
+    if (!zoomable) {
+      padding.bottom = Math.min(padding.bottom, 5);
+    }
+  }
+
   // When showMaxLabel is true, ECharts may render a label at the axis
   // boundary that formats identically to the last data-point tick (e.g.
   // "2005" appears twice with Year grain). Wrap the formatter to suppress
   // consecutive duplicate labels.
-  const showMaxLabel =
-    xAxisType === AxisType.Time && xAxisLabelRotation === 0;
+  const showMaxLabel = xAxisType === AxisType.Time && xAxisLabelRotation === 0;
   const deduplicatedFormatter = showMaxLabel
     ? (() => {
         let lastLabel: string | undefined;
@@ -897,14 +906,35 @@ export default function transformProps(
     ),
   };

+  // Adapt y-axis to chart height: three tiers based on available space.
+  // >= 100px: full axis with proportional tick count
+  // 60-99px: show only min/max boundary labels (splitNumber=1), hide lines/ticks
+  // < 60px: hide all axis decorations, show line only
+  const isSmallChart = height < TIMESERIES_CONSTANTS.compactChartHeight;
+  const isMicroChart = height < TIMESERIES_CONSTANTS.microChartHeight;
+  const yAxisSplitNumber = isMicroChart
+    ? undefined
+    : isSmallChart
+      ? 1
+      : Math.max(
+          3,
+          Math.floor(height / TIMESERIES_CONSTANTS.yAxisPixelsPerTick),
+        );
+
   let yAxis: any = {
     ...defaultYAxis,
     type: logAxis ? AxisType.Log : AxisType.Value,
+    ...(yAxisSplitNumber !== undefined && { splitNumber: yAxisSplitNumber }),
     min: yAxisMin,
     max: yAxisMax,
-    minorTick: { show: minorTicks },
-    minorSplitLine: { show: minorSplitLine },
+    minorTick: { show: isSmallChart ? false : minorTicks },
+    minorSplitLine: { show: isSmallChart ? false : minorSplitLine },
+    splitLine: { show: !isSmallChart },
     axisLabel: {
+      show: !isMicroChart,
+      showMinLabel: !isMicroChart,
+      showMaxLabel: !isMicroChart,
+      hideOverlap: true,
       formatter: getYAxisFormatter(
         metrics,
         forcePercentFormatter,
@@ -913,8 +943,9 @@ export default function transformProps(
         yAxisFormat,
       ),
     },
+    axisTick: { show: !isSmallChart },
     scale: truncateYAxis,
-    name: yAxisTitle,
+    name: isSmallChart ? undefined : yAxisTitle,
     nameGap: convertInteger(yAxisTitleMargin),
     nameLocation: yAxisTitlePosition === 'Left' ? 'middle' : 'end',
   };
@@ -1066,7 +1097,8 @@ export default function transformProps(
       ...getLegendProps(
         effectiveLegendType,
         legendOrientation,
-        showLegend,
+        // Hide legend on compact charts — not enough vertical space
+        isSmallChart ? false : showLegend,
         theme,
         zoomable,
         legendState,
diff --git a/superset-frontend/plugins/plugin-chart-echarts/src/constants.ts b/superset-frontend/plugins/plugin-chart-echarts/src/constants.ts
index 76de92178684..d1169f8a27db 100644
--- a/superset-frontend/plugins/plugin-chart-echarts/src/constants.ts
+++ b/superset-frontend/plugins/plugin-chart-echarts/src/constants.ts
@@ -47,6 +47,11 @@ export const TIMESERIES_CONSTANTS = {
   extraControlsOffset: 22,
   // Min right padding (px) for horizontal bar charts to ensure value labels are fully visible
   horizontalBarLabelRightPadding: 70,
+  // Height thresholds (px) for responsive y-axis behavior
+  compactChartHeight: 100,
+  microChartHeight: 60,
+  // One y-axis tick per this many pixels of chart height
+  yAxisPixelsPerTick: 80,
 };

 export enum OpacityEnum {
PATCH

echo "Gold patch applied."
