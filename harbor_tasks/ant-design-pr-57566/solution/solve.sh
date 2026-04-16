#!/bin/bash
# Gold solution: Apply the fix for typography native ellipsis measurement
set -e

cd /workspace/antd

# Check for idempotency - if the fix is already applied, exit
if grep -q "needNativeEllipsisMeasure = cssEllipsis && !!tooltipProps.title" components/typography/Base/index.tsx 2>/dev/null; then
    echo "Fix already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/components/typography/Base/index.tsx b/components/typography/Base/index.tsx
index 5aa79c377fd6..b48d536fc880 100644
--- a/components/typography/Base/index.tsx
+++ b/components/typography/Base/index.tsx
@@ -252,7 +252,12 @@ const Base = React.forwardRef<HTMLElement, BlockProps>((props, ref) => {
     setCssEllipsis(canUseCssEllipsis && mergedEnableEllipsis);
   }, [canUseCssEllipsis, mergedEnableEllipsis]);

-  const isMergedEllipsis = mergedEnableEllipsis && (cssEllipsis ? isNativeEllipsis : isJsEllipsis);
+  const tooltipProps = useTooltipProps(ellipsisConfig.tooltip, editConfig.text, children);
+  const needNativeEllipsisMeasure = cssEllipsis && !!tooltipProps.title;
+
+  const isMergedEllipsis =
+    mergedEnableEllipsis &&
+    (cssEllipsis ? needNativeEllipsisMeasure && isNativeEllipsis : isJsEllipsis);

   const cssTextOverflow = mergedEnableEllipsis && rows === 1 && cssEllipsis;
   const cssLineClamp = mergedEnableEllipsis && rows > 1 && cssEllipsis;
@@ -284,14 +289,21 @@ const Base = React.forwardRef<HTMLElement, BlockProps>((props, ref) => {
   React.useEffect(() => {
     const textEle = typographyRef.current;

-    if (enableEllipsis && cssEllipsis && textEle) {
+    if (enableEllipsis && needNativeEllipsisMeasure && textEle) {
       const currentEllipsis = isEleEllipsis(textEle);

       if (isNativeEllipsis !== currentEllipsis) {
         setIsNativeEllipsis(currentEllipsis);
       }
     }
-  }, [enableEllipsis, cssEllipsis, children, cssLineClamp, isNativeVisible, ellipsisWidth]);
+  }, [
+    enableEllipsis,
+    needNativeEllipsisMeasure,
+    children,
+    cssLineClamp,
+    isNativeVisible,
+    ellipsisWidth,
+  ]);

   // https://github.com/ant-design/ant-design/issues/36786
   // Use IntersectionObserver to check if element is invisible
@@ -300,7 +312,7 @@ const Base = React.forwardRef<HTMLElement, BlockProps>((props, ref) => {
     if (
       typeof IntersectionObserver === 'undefined' ||
       !textEle ||
-      !cssEllipsis ||
+      !needNativeEllipsisMeasure ||
       !mergedEnableEllipsis
     ) {
       return;
@@ -314,11 +326,9 @@ const Base = React.forwardRef<HTMLElement, BlockProps>((props, ref) => {
     return () => {
       observer.disconnect();
     };
-  }, [cssEllipsis, mergedEnableEllipsis]);
+  }, [needNativeEllipsisMeasure, mergedEnableEllipsis]);

   // ========================== Tooltip ===========================
-  const tooltipProps = useTooltipProps(ellipsisConfig.tooltip, editConfig.text, children);
-
   const topAriaLabel = React.useMemo(() => {
     if (!enableEllipsis || cssEllipsis) {
       return undefined;
diff --git a/components/typography/__tests__/ellipsis.test.tsx b/components/typography/__tests__/ellipsis.test.tsx
index 0d6091667e16..7c9585e3e56e 100644
--- a/components/typography/__tests__/ellipsis.test.tsx
+++ b/components/typography/__tests__/ellipsis.test.tsx
@@ -14,6 +14,7 @@ import type { ConfigProviderProps } from '../../config-provider';
 import zhCN from '../../locale/zh_CN';
 import type { EllipsisConfig } from '../Base';
 import Base from '../Base';
+import * as baseUtil from '../Base/util';

 type Locale = ConfigProviderProps['locale'];
 jest.mock('copy-to-clipboard');
@@ -141,6 +142,23 @@ describe('Typography.Ellipsis', () => {
     ).toEqual('2');
   });

+  it('should skip native ellipsis measure when tooltip is not configured', async () => {
+    const ellipsisSpy = jest.spyOn(baseUtil, 'isEleEllipsis').mockReturnValue(true);
+    const ref = React.createRef<HTMLElement>();
+
+    render(
+      <Base ellipsis component="p" ref={ref}>
+        {fullStr}
+      </Base>,
+    );
+
+    triggerResize(ref.current!);
+    await waitFakeTimer();
+
+    expect(ellipsisSpy).not.toHaveBeenCalled();
+    ellipsisSpy.mockRestore();
+  });
+
   it('string with parentheses', async () => {
     const parenthesesStr = `Ant Design, a design language (for background applications, is refined by
         Ant UED Team. Ant Design, a design language for background applications,
@@ -328,7 +346,11 @@ describe('Typography.Ellipsis', () => {
         disconnect = disconnectFn;
       };

-      const { container, unmount } = render(<Base ellipsis component="p" />);
+      const { container, unmount } = render(
+        <Base ellipsis={{ tooltip: true }} component="p">
+          {fullStr}
+        </Base>,
+      );

       expect(observeFn).toHaveBeenCalled();
PATCH

echo "Gold patch applied successfully"
