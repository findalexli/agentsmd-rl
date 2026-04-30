#!/usr/bin/env bash
set -euo pipefail

cd /workspace/superset

if grep -q 'selectContainerRef' superset-frontend/packages/superset-ui-core/src/components/Select/Select.tsx; then
  echo "[solve.sh] patch already applied; skipping"
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/superset-frontend/packages/superset-ui-core/src/components/Select/Select.tsx b/superset-frontend/packages/superset-ui-core/src/components/Select/Select.tsx
index 3f5d9cf4bf8c..fc0df73f9d6a 100644
--- a/superset-frontend/packages/superset-ui-core/src/components/Select/Select.tsx
+++ b/superset-frontend/packages/superset-ui-core/src/components/Select/Select.tsx
@@ -149,6 +149,8 @@ const Select = forwardRef(
     // Prevent maxTagCount change during click events to avoid click target disappearing
     const [stableMaxTagCount, setStableMaxTagCount] = useState(maxTagCount);
     const isOpeningRef = useRef(false);
+    const selectContainerRef = useRef<HTMLDivElement>(null);
+    const [dropdownWidth, setDropdownWidth] = useState<number | true>(true);

     useEffect(() => {
       if (oneLine) {
@@ -159,12 +161,23 @@ const Select = forwardRef(
           requestAnimationFrame(() => {
             setStableMaxTagCount(0);
             isOpeningRef.current = false;
+
+            // Measure collapsed width and update dropdown width
+            const selectElement =
+              selectContainerRef.current?.querySelector('.ant-select');
+            if (selectElement) {
+              const { width } = selectElement.getBoundingClientRect();
+              if (width > 0) {
+                setDropdownWidth(width);
+              }
+            }
           });
           return;
         }
         if (!isDropdownVisible) {
           // When closing, immediately show the first tag
           setStableMaxTagCount(1);
+          setDropdownWidth(true); // Reset to default when closing
           isOpeningRef.current = false;
         }
         return;
@@ -717,7 +730,11 @@ const Select = forwardRef(
     };

     return (
-      <StyledContainer className={className} headerPosition={headerPosition}>
+      <StyledContainer
+        ref={selectContainerRef}
+        className={className}
+        headerPosition={headerPosition}
+      >
         {header && (
           <StyledHeader headerPosition={headerPosition}>{header}</StyledHeader>
         )}
@@ -777,7 +794,7 @@ const Select = forwardRef(
           options={visibleOptions}
           optionRender={option => <Space>{option.label || option.value}</Space>}
           oneLine={oneLine}
-          popupMatchSelectWidth
+          popupMatchSelectWidth={oneLine ? dropdownWidth : true}
           css={props.css}
           dropdownAlign={DROPDOWN_ALIGN_BOTTOM}
           {...props}
PATCH

echo "[solve.sh] patch applied"
