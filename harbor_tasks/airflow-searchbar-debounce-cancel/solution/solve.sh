#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Gold solution: applies the fix from apache/airflow#64893

set -euo pipefail

cd /workspace/airflow

# Idempotency check: skip if already applied
if grep -q "handleSearchChange.cancel();" airflow-core/src/airflow/ui/src/components/SearchBar.tsx 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/airflow-core/src/airflow/ui/src/components/SearchBar.tsx b/airflow-core/src/airflow/ui/src/components/SearchBar.tsx
index 21bfca4bf50ae..91825004d45ed 100644
--- a/airflow-core/src/airflow/ui/src/components/SearchBar.tsx
+++ b/airflow-core/src/airflow/ui/src/components/SearchBar.tsx
@@ -50,6 +50,11 @@ export const SearchBar = ({
     setValue(event.target.value);
     handleSearchChange(event.target.value);
   };
+  const clearSearch = () => {
+    handleSearchChange.cancel();
+    setValue("");
+    onChange("");
+  };

   useHotkeys(
     "mod+k",
@@ -70,10 +75,7 @@ export const SearchBar = ({
               aria-label={translate("search.clear")}
               colorPalette="brand"
               data-testid="clear-search"
-              onClick={() => {
-                setValue("");
-                onChange("");
-              }}
+              onClick={clearSearch}
               size="xs"
             />
           ) : undefined}
PATCH

echo "Patch applied successfully."
