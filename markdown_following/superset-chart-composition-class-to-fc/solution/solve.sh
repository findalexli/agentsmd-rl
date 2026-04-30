#!/usr/bin/env bash
set -euo pipefail

cd /workspace/superset

# Idempotency: skip if already applied
if grep -q "export default memo(ChartFrame);" \
    superset-frontend/packages/superset-ui-core/src/chart-composition/ChartFrame.tsx 2>/dev/null; then
  echo "Patch already applied; skipping."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/superset-frontend/packages/superset-ui-core/src/chart-composition/ChartFrame.tsx b/superset-frontend/packages/superset-ui-core/src/chart-composition/ChartFrame.tsx
index 88cf52ec72fd..91836814e9fd 100644
--- a/superset-frontend/packages/superset-ui-core/src/chart-composition/ChartFrame.tsx
+++ b/superset-frontend/packages/superset-ui-core/src/chart-composition/ChartFrame.tsx
@@ -17,7 +17,7 @@
  * under the License.
  */

-import { PureComponent, ReactNode } from 'react';
+import { memo, ReactNode } from 'react';

 import { isDefined } from '../utils';

@@ -29,7 +29,7 @@ type Props = {
   contentWidth?: number;
   contentHeight?: number;
   height: number;
-  renderContent: ({
+  renderContent?: ({
     height,
     width,
   }: {
@@ -39,36 +39,35 @@ type Props = {
   width: number;
 };

-export default class ChartFrame extends PureComponent<Props, {}> {
-  static defaultProps = {
-    renderContent() {},
-  };
+function ChartFrame({
+  contentWidth,
+  contentHeight,
+  width,
+  height,
+  renderContent = () => null,
+}: Props) {
+  const overflowX = checkNumber(contentWidth) && contentWidth > width;
+  const overflowY = checkNumber(contentHeight) && contentHeight > height;

-  render() {
-    const { contentWidth, contentHeight, width, height, renderContent } =
-      this.props;
-
-    const overflowX = checkNumber(contentWidth) && contentWidth > width;
-    const overflowY = checkNumber(contentHeight) && contentHeight > height;
-
-    if (overflowX || overflowY) {
-      return (
-        <div
-          style={{
-            height,
-            overflowX: overflowX ? 'auto' : 'hidden',
-            overflowY: overflowY ? 'auto' : 'hidden',
-            width,
-          }}
-        >
-          {renderContent({
-            height: Math.max(contentHeight ?? 0, height),
-            width: Math.max(contentWidth ?? 0, width),
-          })}
-        </div>
-      );
-    }
-
-    return renderContent({ height, width });
+  if (overflowX || overflowY) {
+    return (
+      <div
+        style={{
+          height,
+          overflowX: overflowX ? 'auto' : 'hidden',
+          overflowY: overflowY ? 'auto' : 'hidden',
+          width,
+        }}
+      >
+        {renderContent({
+          height: Math.max(contentHeight ?? 0, height),
+          width: Math.max(contentWidth ?? 0, width),
+        })}
+      </div>
+    );
   }
+
+  return <>{renderContent({ height, width })}</>;
 }
+
+export default memo(ChartFrame);
diff --git a/superset-frontend/packages/superset-ui-core/src/chart-composition/legend/WithLegend.tsx b/superset-frontend/packages/superset-ui-core/src/chart-composition/legend/WithLegend.tsx
index a2cac92ee338..48e7309cdabf 100644
--- a/superset-frontend/packages/superset-ui-core/src/chart-composition/legend/WithLegend.tsx
+++ b/superset-frontend/packages/superset-ui-core/src/chart-composition/legend/WithLegend.tsx
@@ -17,26 +17,19 @@
  * under the License.
  */

-import { CSSProperties, ReactNode, PureComponent } from 'react';
+import { CSSProperties, ReactNode, memo, useMemo } from 'react';
 import { ParentSize } from '@visx/responsive';

-const defaultProps = {
-  className: '',
-  height: 'auto' as number | string,
-  position: 'top',
-  width: 'auto' as number | string,
-};
-
 type Props = {
-  className: string;
+  className?: string;
   debounceTime?: number;
-  width: number | string;
-  height: number | string;
+  width?: number | string;
+  height?: number | string;
   legendJustifyContent?: 'center' | 'flex-start' | 'flex-end';
-  position: 'top' | 'left' | 'bottom' | 'right';
+  position?: 'top' | 'left' | 'bottom' | 'right';
   renderChart: (dim: { width: number; height: number }) => ReactNode;
   renderLegend?: (params: { direction: string }) => ReactNode;
-} & Readonly<typeof defaultProps>;
+};

 const LEGEND_STYLE_BASE: CSSProperties = {
   display: 'flex',
@@ -52,95 +45,101 @@ const CHART_STYLE_BASE: CSSProperties = {
   position: 'relative',
 };

-class WithLegend extends PureComponent<Props, {}> {
-  static defaultProps = defaultProps;
-
-  getContainerDirection(): CSSProperties['flexDirection'] {
-    const { position } = this.props;
-
-    if (position === 'left') {
-      return 'row';
-    }
-    if (position === 'right') {
-      return 'row-reverse';
-    }
-    if (position === 'bottom') {
-      return 'column-reverse';
-    }
-
-    return 'column';
+function getContainerDirection(
+  position: Props['position'],
+): CSSProperties['flexDirection'] {
+  if (position === 'left') {
+    return 'row';
+  }
+  if (position === 'right') {
+    return 'row-reverse';
+  }
+  if (position === 'bottom') {
+    return 'column-reverse';
   }

-  getLegendJustifyContent() {
-    const { legendJustifyContent, position } = this.props;
-    if (legendJustifyContent) {
-      return legendJustifyContent;
-    }
-
-    if (position === 'left' || position === 'right') {
-      return 'flex-start';
-    }
+  return 'column';
+}

-    return 'flex-end';
+function getLegendJustifyContent(
+  legendJustifyContent: Props['legendJustifyContent'],
+  position: Props['position'],
+) {
+  if (legendJustifyContent) {
+    return legendJustifyContent;
   }

-  render() {
-    const {
-      className,
-      debounceTime,
-      width,
-      height,
-      position,
-      renderChart,
-      renderLegend,
-    } = this.props;
+  if (position === 'left' || position === 'right') {
+    return 'flex-start';
+  }

-    const isHorizontal = position === 'left' || position === 'right';
+  return 'flex-end';
+}

-    const style: CSSProperties = {
+function WithLegend({
+  className = '',
+  debounceTime,
+  width = 'auto',
+  height = 'auto',
+  legendJustifyContent,
+  position = 'top',
+  renderChart,
+  renderLegend,
+}: Props) {
+  const isHorizontal = position === 'left' || position === 'right';
+
+  const style: CSSProperties = useMemo(
+    () => ({
       display: 'flex',
-      flexDirection: this.getContainerDirection(),
+      flexDirection: getContainerDirection(position),
       height,
       width,
-    };
+    }),
+    [position, height, width],
+  );

-    const chartStyle: CSSProperties = { ...CHART_STYLE_BASE };
+  const chartStyle: CSSProperties = useMemo(() => {
+    const baseStyle = { ...CHART_STYLE_BASE };
     if (isHorizontal) {
-      chartStyle.width = 0;
+      baseStyle.width = 0;
     } else {
-      chartStyle.height = 0;
+      baseStyle.height = 0;
     }
+    return baseStyle;
+  }, [isHorizontal]);

-    const legendDirection = isHorizontal ? 'column' : 'row';
-    const legendStyle: CSSProperties = {
+  const legendDirection = isHorizontal ? 'column' : 'row';
+  const legendStyle: CSSProperties = useMemo(
+    () => ({
       ...LEGEND_STYLE_BASE,
       flexDirection: legendDirection,
-      justifyContent: this.getLegendJustifyContent(),
-    };
-
-    return (
-      <div className={`with-legend ${className}`} style={style}>
-        {renderLegend && (
-          <div className="legend-container" style={legendStyle}>
-            {renderLegend({
-              // Pass flexDirection for @vx/legend to arrange legend items
-              direction: legendDirection,
-            })}
-          </div>
-        )}
-        <div className="main-container" style={chartStyle}>
-          <ParentSize debounceTime={debounceTime}>
-            {(parent: { width: number; height: number }) =>
-              parent.width > 0 && parent.height > 0
-                ? // Only render when necessary
-                  renderChart(parent)
-                : null
-            }
-          </ParentSize>
+      justifyContent: getLegendJustifyContent(legendJustifyContent, position),
+    }),
+    [legendDirection, legendJustifyContent, position],
+  );
+
+  return (
+    <div className={`with-legend ${className}`} style={style}>
+      {renderLegend && (
+        <div className="legend-container" style={legendStyle}>
+          {renderLegend({
+            // Pass flexDirection for @vx/legend to arrange legend items
+            direction: legendDirection,
+          })}
         </div>
+      )}
+      <div className="main-container" style={chartStyle}>
+        <ParentSize debounceTime={debounceTime}>
+          {(parent: { width: number; height: number }) =>
+            parent.width > 0 && parent.height > 0
+              ? // Only render when necessary
+                renderChart(parent)
+              : null
+          }
+        </ParentSize>
       </div>
-    );
-  }
+    </div>
+  );
 }

-export default WithLegend;
+export default memo(WithLegend);
diff --git a/superset-frontend/packages/superset-ui-core/src/chart-composition/tooltip/TooltipFrame.tsx b/superset-frontend/packages/superset-ui-core/src/chart-composition/tooltip/TooltipFrame.tsx
index d470a229403f..190086543164 100644
--- a/superset-frontend/packages/superset-ui-core/src/chart-composition/tooltip/TooltipFrame.tsx
+++ b/superset-frontend/packages/superset-ui-core/src/chart-composition/tooltip/TooltipFrame.tsx
@@ -17,31 +17,21 @@
  * under the License.
  */

-import { PureComponent, ReactNode } from 'react';
-
-const defaultProps = {
-  className: '',
-};
+import { memo, ReactNode } from 'react';

 type Props = {
   className?: string;
   children: ReactNode;
-} & Readonly<typeof defaultProps>;
+};

 const CONTAINER_STYLE = { padding: 8 };

-class TooltipFrame extends PureComponent<Props, {}> {
-  static defaultProps = defaultProps;
-
-  render() {
-    const { className, children } = this.props;
-
-    return (
-      <div className={className} style={CONTAINER_STYLE}>
-        {children}
-      </div>
-    );
-  }
+function TooltipFrame({ className = '', children }: Props) {
+  return (
+    <div className={className} style={CONTAINER_STYLE}>
+      {children}
+    </div>
+  );
 }

-export default TooltipFrame;
+export default memo(TooltipFrame);
PATCH

echo "Patch applied successfully."
