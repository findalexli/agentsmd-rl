#!/bin/bash
set -e

cd /workspace/ant-design

# Check if already patched (idempotency check)
if grep -q "maskClosable?: boolean" "components/image/hooks/useMergedPreviewConfig.ts" 2>/dev/null; then
    echo "Already patched, skipping..."
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/components/image/PreviewGroup.tsx b/components/image/PreviewGroup.tsx
index e990f1172baf..22e9ff34b8d4 100644
--- a/components/image/PreviewGroup.tsx
+++ b/components/image/PreviewGroup.tsx
@@ -34,7 +34,10 @@ export const icons = {

 type RcPreviewGroupProps = GetProps<typeof RcImage.PreviewGroup>;

-type OriginPreviewConfig = NonNullable<Exclude<RcPreviewGroupProps['preview'], boolean>>;
+type OriginPreviewConfig = Omit<
+  NonNullable<Exclude<RcPreviewGroupProps['preview'], boolean>>,
+  'maskClosable'
+>;

 export type GroupPreviewConfig = OriginPreviewConfig &
   DeprecatedPreviewConfig & {
diff --git a/components/image/hooks/useMergedPreviewConfig.ts b/components/image/hooks/useMergedPreviewConfig.ts
index 7b247448d1f5..b4702debc56a 100644
--- a/components/image/hooks/useMergedPreviewConfig.ts
+++ b/components/image/hooks/useMergedPreviewConfig.ts
@@ -15,9 +15,9 @@ const useMergedPreviewConfig = <T extends PreviewConfig | GroupPreviewConfig>(
   getContextPopupContainer: PreviewConfig['getContainer'],
   icons: PreviewConfig['icons'],
   defaultCover?: React.ReactNode,
-): T & { blurClassName?: string } => {
+): T & { blurClassName?: string; maskClosable?: boolean } => {
   const [zIndex] = useZIndex('ImagePreview', previewConfig?.zIndex);
-  const [mergedPreviewMask, blurClassName] = useMergedMask(
+  const [mergedPreviewMask, blurClassName, mergedMaskClosable] = useMergedMask(
     previewConfig?.mask as MaskType,
     contextPreviewConfig?.mask as MaskType,
     `${prefixCls}-preview`,
@@ -45,6 +45,7 @@ const useMergedPreviewConfig = <T extends PreviewConfig | GroupPreviewConfig>(
       closeIcon: closeIcon ?? contextCloseIcon,
       rootClassName: clsx(mergedRootClassName, previewRootClassName),
       mask: mergedPreviewMask,
+      maskClosable: mergedMaskClosable,
       blurClassName: blurClassName.mask,
     };
   }, [
@@ -57,6 +58,7 @@ const useMergedPreviewConfig = <T extends PreviewConfig | GroupPreviewConfig>(
     icons,
     zIndex,
     mergedPreviewMask,
+    mergedMaskClosable,
     blurClassName,
   ]);
 };
diff --git a/components/image/index.tsx b/components/image/index.tsx
index 4d1212559ac2..2a534bede96b 100644
--- a/components/image/index.tsx
+++ b/components/image/index.tsx
@@ -17,7 +17,10 @@ import Progress from './Progress';
 import type { ProgressClassNames, ProgressStyles } from './Progress';
 import useStyle from './style';

-type OriginPreviewConfig = NonNullable<Exclude<RcImageProps['preview'], boolean>>;
+type OriginPreviewConfig = Omit<
+  NonNullable<Exclude<RcImageProps['preview'], boolean>>,
+  'maskClosable'
+>;

 export type DeprecatedPreviewConfig = {
   /** @deprecated Use `open` instead */
PATCH

echo "Patch applied successfully"
