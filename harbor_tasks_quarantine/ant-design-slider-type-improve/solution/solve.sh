#!/bin/bash
set -e

cd /workspace/ant-design

# Check if already patched (idempotency check - distinctive line from the patch)
if grep -q "onChangeComplete as RcSliderProps\['onChangeComplete'\]" components/slider/index.tsx; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/components/slider/index.tsx b/components/slider/index.tsx
index cce1e907324c..7502bb52ed9f 100644
--- a/components/slider/index.tsx
+++ b/components/slider/index.tsx
@@ -225,7 +225,7 @@ const Slider = React.forwardRef<SliderRef, SliderSingleProps | SliderRangeProps>
   const [dragging, setDragging] = useRafLock();

   const onInternalChangeComplete: RcSliderProps['onChangeComplete'] = (nextValues) => {
-    onChangeComplete?.(nextValues as any);
+    (onChangeComplete as RcSliderProps['onChangeComplete'])?.(nextValues);
     setDragging(false);
   };

@@ -406,9 +406,8 @@ const Slider = React.forwardRef<SliderRef, SliderSingleProps | SliderRangeProps>
   };

   return (
-    // @ts-ignore
     <RcSlider
-      {...restProps}
+      {...(restProps as Omit<SliderProps, 'onAfterChange' | 'onChange'>)}
       classNames={mergedClassNames}
       styles={mergedStyles}
       step={restProps.step}
PATCH

echo "Patch applied successfully!"
