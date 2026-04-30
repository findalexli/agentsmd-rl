#!/bin/bash
# Gold solution for ant-design/ant-design#57440
# Applies the patch that adds Typography actions placement feature

set -e

cd /workspace/antd

# Check if patch already applied (idempotency)
if grep -q "ant-typography-actions-start" components/typography/style/index.ts 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
git apply --whitespace=fix <<'PATCH'
diff --git a/components/typography/Base/Ellipsis.tsx b/components/typography/Base/Ellipsis.tsx
index b42b928bbf4a..170cfa5fc41f 100644
--- a/components/typography/Base/Ellipsis.tsx
+++ b/components/typography/Base/Ellipsis.tsx
@@ -91,6 +91,11 @@ export interface EllipsisProps {
   ) => React.ReactNode;
   onEllipsis: (isEllipsis: boolean) => void;
   expanded: boolean;
+  /**
+   * Mark for measurement update that may affect ellipsis content layout.
+   * e.g. operation placement change.
+   */
+  measureDeps: any[];
   /**
    * Mark for misc update. Which will not affect ellipsis content length.
    * e.g. tooltip content update.
@@ -112,14 +117,24 @@ const lineClipStyle: React.CSSProperties = {
 };

 export default function EllipsisMeasure(props: EllipsisProps) {
-  const { enableMeasure, width, text, children, rows, expanded, miscDeps, onEllipsis } = props;
+  const {
+    enableMeasure,
+    width,
+    text,
+    children,
+    rows,
+    expanded,
+    measureDeps,
+    miscDeps,
+    onEllipsis,
+  } = props;

   const nodeList = React.useMemo(() => toArray(text), [text]);
   const nodeLen = React.useMemo(() => getNodesLen(nodeList), [text]);

   // ========================= Full Content =========================
   // Used for measure only, which means it's always render as no need ellipsis
-  const fullContent = React.useMemo(() => children(nodeList, false), [text]);
+  const fullContent = React.useMemo(() => children(nodeList, false), [text, ...measureDeps]);

   // ========================= Cut Content ==========================
   const [ellipsisCutIndex, setEllipsisCutIndex] = React.useState<[number, number] | null>(null);
@@ -146,7 +161,7 @@ export default function EllipsisMeasure(props: EllipsisProps) {
     } else {
       setNeedEllipsis(STATUS_MEASURE_NONE);
     }
-  }, [width, text, rows, enableMeasure, nodeList]);
+  }, [width, text, rows, enableMeasure, nodeList, ...measureDeps]);

   // Measure process
   useLayoutEffect(() => {
diff --git a/components/typography/Base/index.tsx b/components/typography/Base/index.tsx
index 4e531c87034f..88cf02347ce8 100644
--- a/components/typography/Base/index.tsx
+++ b/components/typography/Base/index.tsx
@@ -74,6 +74,10 @@ export interface CopyConfig {
   tabIndex?: number;
 }

+export interface ActionsConfig {
+  placement?: 'start' | 'end';
+}
+
 interface EditConfig {
   text?: string;
   editing?: boolean;
@@ -104,6 +108,10 @@ export interface EllipsisConfig {

 export interface BlockProps<C extends keyof JSX.IntrinsicElements = keyof JSX.IntrinsicElements>
   extends TypographyProps<C> {
+  /**
+   * @since 6.4.0
+   */
+  actions?: ActionsConfig;
   title?: string;
   editable?: boolean | EditConfig;
   copyable?: boolean | CopyConfig;
@@ -171,6 +179,7 @@ const Base = React.forwardRef<HTMLElement, BlockProps>((props, ref) => {
     ellipsis,
     editable,
     copyable,
+    actions,
     component,
     title,
     onMouseEnter,
@@ -231,6 +240,8 @@ const Base = React.forwardRef<HTMLElement, BlockProps>((props, ref) => {
   // ========================== Copyable ==========================
   const [enableCopy, copyConfig] = useMergedConfig<CopyConfig>(copyable);

+  const { placement = 'end' } = actions ?? {};
+
   const { copied, copyLoading, onClick: onCopyClick } = useCopyClick({ copyConfig, children });

   // ========================== Ellipsis ==========================
@@ -476,7 +487,9 @@ const Base = React.forwardRef<HTMLElement, BlockProps>((props, ref) => {
     return (
       <span
         key="operations"
-        className={clsx(`${prefixCls}-actions`, mergedClassNames.actions)}
+        className={clsx(`${prefixCls}-actions`, mergedClassNames.actions, {
+          [`${prefixCls}-actions-start`]: placement === 'start',
+        })}
         style={mergedStyles.actions}
         onMouseEnter={() => setIsHoveringOperations(true)}
         onMouseLeave={() => setIsHoveringOperations(false)}
@@ -495,7 +508,6 @@ const Base = React.forwardRef<HTMLElement, BlockProps>((props, ref) => {
       </span>
     ),
     ellipsisConfig.suffix,
-    renderOperations(canEllipsis),
   ];

   return (
@@ -549,12 +561,14 @@ const Base = React.forwardRef<HTMLElement, BlockProps>((props, ref) => {
               width={ellipsisWidth}
               onEllipsis={onJsEllipsis}
               expanded={expanded}
+              measureDeps={[placement]}
               miscDeps={[
                 copied,
                 expanded,
                 copyLoading,
                 enableEdit,
                 enableCopy,
+                placement,
                 textLocale,
                 ...DECORATION_PROPS.map((key) => props[key as keyof BlockProps]),
               ]}
@@ -563,6 +577,7 @@ const Base = React.forwardRef<HTMLElement, BlockProps>((props, ref) => {
                 wrapperDecorations(
                   props,
                   <>
+                    {placement === 'start' ? renderOperations(canEllipsis) : null}
                     {node.length > 0 && canEllipsis && !expanded && topAriaLabel ? (
                       <span key="show-content" aria-hidden>
                         {node}
@@ -571,6 +586,7 @@ const Base = React.forwardRef<HTMLElement, BlockProps>((props, ref) => {
                       node
                     )}
                     {renderEllipsis(canEllipsis)}
+                    {placement === 'start' ? null : renderOperations(canEllipsis)}
                   </>,
                 )
               }
diff --git a/components/typography/style/index.ts b/components/typography/style/index.ts
index 3521eb1d4618..725a9a0394d1 100644
--- a/components/typography/style/index.ts
+++ b/components/typography/style/index.ts
@@ -123,6 +123,18 @@ const genTypographyStyle: GenerateStyle<TypographyToken, CSSObject> = (token) =>
         marginInlineStart: token.marginXXS,
       },

+      [`${componentCls}-actions-start`]: {
+        [`
+          ${componentCls}-expand,
+          ${componentCls}-collapse,
+          ${componentCls}-edit,
+          ${componentCls}-copy:not(${componentCls}-copy-icon-only)
+        `]: {
+          marginInlineStart: 0,
+          marginInlineEnd: token.marginXXS,
+        },
+      },
+
       ...getEditableStyles(token),

       ...getCopyableStyles(token),
PATCH

echo "Patch applied successfully"
