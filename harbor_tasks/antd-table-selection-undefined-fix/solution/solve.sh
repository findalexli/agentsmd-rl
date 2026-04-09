#!/bin/bash
set -e

cd /workspace/ant-design

# Apply the gold patch for the Table rowSelection fix using git apply
cat <<'PATCH' > /tmp/fix.patch
diff --git a/components/table/hooks/useSelection.tsx b/components/table/hooks/useSelection.tsx
index afcc9aca80ba..50feedba794e 100644
--- a/components/table/hooks/useSelection.tsx
+++ b/components/table/hooks/useSelection.tsx
@@ -123,6 +123,7 @@ const useSelection = <RecordType extends AnyObject = AnyObject>(
       value: selectedRowKeys,
     },
   );
+  const mergedSelectedKeyList = mergedSelectedKeys ?? EMPTY_LIST;

   // ======================== Caches ========================
   const preserveRecordsRef = React.useRef(new Map<Key, RecordType>());
@@ -150,8 +151,8 @@ const useSelection = <RecordType extends AnyObject = AnyObject>(

   // Update cache with selectedKeys
   React.useEffect(() => {
-    updatePreserveRecordsCache(mergedSelectedKeys);
-  }, [mergedSelectedKeys]);
+    updatePreserveRecordsCache(mergedSelectedKeyList);
+  }, [mergedSelectedKeyList, updatePreserveRecordsCache]);

   // Get flatten data
   const flattedData = useMemo(
@@ -213,16 +214,16 @@ const useSelection = <RecordType extends AnyObject = AnyObject>(

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
     const keys = selectionType === 'radio' ? derivedSelectedKeys.slice(0, 1) : derivedSelectedKeys;
PATCH

git apply /tmp/fix.patch

# Idempotency check - verify the distinctive line was added
grep -q "const mergedSelectedKeyList = mergedSelectedKeys ?? EMPTY_LIST;" components/table/hooks/useSelection.tsx && echo "Patch applied successfully"
