#!/bin/bash
set -e

cd /workspace/antd

# Idempotency check - skip if patch already applied
if grep -q "mergedSelectedKeyList" components/table/hooks/useSelection.tsx 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Create the patch file
cat > /tmp/fix.patch << 'PATCH'
--- a/components/table/hooks/useSelection.tsx
+++ b/components/table/hooks/useSelection.tsx
@@ -123,6 +123,9 @@ const useSelection = <RecordType extends AnyObject = AnyObject>(
     },
   );

+  // Ensure mergedSelectedKeys is always an array for subsequent operations
+  const mergedSelectedKeyList = mergedSelectedKeys ?? EMPTY_LIST;
+
   // ======================== Caches ========================
   const preserveRecordsRef = React.useRef(new Map<Key, RecordType>());

@@ -149,8 +152,8 @@ const useSelection = <RecordType extends AnyObject = AnyObject>(

   // Update cache with selectedKeys
   React.useEffect(() => {
-    updatePreserveRecordsCache(mergedSelectedKeys);
-  }, [mergedSelectedKeys]);
+    updatePreserveRecordsCache(mergedSelectedKeyList);
+  }, [mergedSelectedKeyList, updatePreserveRecordsCache]);

   // Get flatten data
   const flattedData = useMemo(
@@ -213,14 +216,14 @@ const useSelection = <RecordType extends AnyObject = AnyObject>(

   const [derivedSelectedKeys, derivedHalfSelectedKeys] = useMemo(() => {
     if (checkStrictly) {
-      return [mergedSelectedKeys || [], []];
+      return [mergedSelectedKeyList, []];
     }
     const { checkedKeys, halfCheckedKeys } = conductCheck(
-      mergedSelectedKeys,
+      mergedSelectedKeyList,
       true,
       keyEntities as any,
       isCheckboxDisabled as any,
     );
     return [checkedKeys || [], halfCheckedKeys];
-  }, [mergedSelectedKeys, checkStrictly, keyEntities, isCheckboxDisabled]);
+  }, [mergedSelectedKeyList, checkStrictly, keyEntities, isCheckboxDisabled]);

   const derivedSelectedKeySet = useMemo<Set<Key>>(() => {
PATCH

# Apply the patch
git apply /tmp/fix.patch

echo "Patch applied successfully"
