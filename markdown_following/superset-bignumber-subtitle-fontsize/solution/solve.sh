#!/usr/bin/env bash
# Gold patch for apache/superset#39493 — fix Big Number subtitle/subheader
# default font size and add subtitleFontSize fallback.
set -euo pipefail

cd /workspace/superset

# Idempotency guard: detect a distinctive string from the patched file.
if grep -q "subheaderFontSize ?? subtitleFontSize ?? PROPORTION.SUBHEADER" \
    superset-frontend/plugins/plugin-chart-echarts/src/BigNumber/BigNumberTotal/transformProps.ts \
    2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/superset-frontend/plugins/plugin-chart-echarts/src/BigNumber/BigNumberTotal/transformProps.ts b/superset-frontend/plugins/plugin-chart-echarts/src/BigNumber/BigNumberTotal/transformProps.ts
index c79e85784ba4..7c250595962f 100644
--- a/superset-frontend/plugins/plugin-chart-echarts/src/BigNumber/BigNumberTotal/transformProps.ts
+++ b/superset-frontend/plugins/plugin-chart-echarts/src/BigNumber/BigNumberTotal/transformProps.ts
@@ -29,6 +29,7 @@ import {
 } from '@superset-ui/core';
 import { GenericDataType } from '@apache-superset/core/common';
 import { BigNumberTotalChartProps, BigNumberVizProps } from '../types';
+import { PROPORTION } from '../constants';
 import { getDateFormatter, getOriginalLabel, parseMetricValue } from '../utils';
 import { Refs } from '../../types';

@@ -76,8 +77,8 @@ export default function transformProps(
   const showMetricName = chartProps.rawFormData?.show_metric_name ?? false;
   const formattedSubtitle = subtitle?.trim() ? subtitle : subheader || '';
   const formattedSubtitleFontSize = subtitle?.trim()
-    ? (subtitleFontSize ?? 1)
-    : (subheaderFontSize ?? 1);
+    ? (subtitleFontSize ?? PROPORTION.SUBHEADER)
+    : (subheaderFontSize ?? subtitleFontSize ?? PROPORTION.SUBHEADER);
   const bigNumber =
     data.length === 0 ? null : parseMetricValue(data[0][metricName]);

diff --git a/superset-frontend/plugins/plugin-chart-echarts/src/BigNumber/BigNumberViz.tsx b/superset-frontend/plugins/plugin-chart-echarts/src/BigNumber/BigNumberViz.tsx
index 3215eb3dd6cb..38a08b65f5e3 100644
--- a/superset-frontend/plugins/plugin-chart-echarts/src/BigNumber/BigNumberViz.tsx
+++ b/superset-frontend/plugins/plugin-chart-echarts/src/BigNumber/BigNumberViz.tsx
@@ -30,20 +30,11 @@ import {
 import { styled, useTheme } from '@apache-superset/core/theme';
 import Echart from '../components/Echart';
 import { BigNumberVizProps } from './types';
+import { PROPORTION } from './constants';
 import { EventHandlers } from '../types';

 const defaultNumberFormatter = getNumberFormatter();

-const PROPORTION = {
-  // text size: proportion of the chart container sans trendline
-  METRIC_NAME: 0.125,
-  KICKER: 0.1,
-  HEADER: 0.3,
-  SUBHEADER: 0.125,
-  // trendline size: proportion of the whole chart container
-  TRENDLINE: 0.3,
-};
-
 function BigNumberVis({
   className = '',
   headerFormatter = defaultNumberFormatter,
diff --git a/superset-frontend/plugins/plugin-chart-echarts/src/BigNumber/constants.tsx b/superset-frontend/plugins/plugin-chart-echarts/src/BigNumber/constants.tsx
new file mode 100644
index 000000000000..97d35562f14a
--- /dev/null
+++ b/superset-frontend/plugins/plugin-chart-echarts/src/BigNumber/constants.tsx
@@ -0,0 +1,26 @@
+/**
+ * Licensed to the Apache Software Foundation (ASF) under one
+ * or more contributor license agreements.  See the NOTICE file
+ * distributed with this work for additional information
+ * regarding copyright ownership.  The ASF licenses this file
+ * to you under the Apache License, Version 2.0 (the
+ * "License"); you may not use this file except in compliance
+ * with the License.  You may obtain a copy of the License at
+ *
+ *   http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing,
+ * software distributed under the License is distributed on an
+ * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
+ * KIND, either express or implied.  See the License for the
+ * specific language governing permissions and limitations
+ * under the License.
+ */
+
+export const PROPORTION = {
+  METRIC_NAME: 0.125,
+  KICKER: 0.1,
+  HEADER: 0.3,
+  SUBHEADER: 0.125,
+  TRENDLINE: 0.3,
+};
PATCH

echo "Patch applied successfully."
