#!/bin/bash
set -e

cd /workspace/kotlin

# Apply the fix for typo in package name: relfection -> reflection
# This patch:
# 1. Renames the directory from relfection to reflection
# 2. Updates the package declaration in toStringDataClassLike.kt
# 3. Updates the import in KaSymbolPointer.kt

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/analysis/analysis-api/src/org/jetbrains/kotlin/analysis/api/symbols/pointers/KaSymbolPointer.kt b/analysis/analysis-api/src/org/jetbrains/kotlin/analysis/api/symbols/pointers/KaSymbolPointer.kt
index cb308f50a4249..5db890688f322 100644
--- a/analysis/analysis-api/src/org/jetbrains/kotlin/analysis/api/symbols/pointers/KaSymbolPointer.kt
+++ b/analysis/analysis-api/src/org/jetbrains/kotlin/analysis/api/symbols/pointers/KaSymbolPointer.kt
@@ -8,7 +8,7 @@ package org.jetbrains.kotlin.analysis.api.symbols.pointers
 import org.jetbrains.kotlin.analysis.api.KaImplementationDetail
 import org.jetbrains.kotlin.analysis.api.KaSession
 import org.jetbrains.kotlin.analysis.api.symbols.KaSymbol
-import org.jetbrains.kotlin.analysis.utils.relfection.renderAsDataClassToString
+import org.jetbrains.kotlin.analysis.utils.reflection.renderAsDataClassToString

 /**
  * [KaSymbolPointer] allows to point to a [KaSymbol] and later retrieve it in another [KaSession]. A pointer is necessary because
diff --git a/analysis/analysis-internal-utils/src/org/jetbrains/kotlin/analysis/utils/relfection/toStringDataClassLike.kt b/analysis/analysis-internal-utils/src/org/jetbrains/kotlin/analysis/utils/reflection/toStringDataClassLike.kt
similarity index 89%
rename from analysis/analysis-internal-utils/src/org/jetbrains/kotlin/analysis/utils/relfection/toStringDataClassLike.kt
rename to analysis/analysis-internal-utils/src/org/jetbrains/kotlin/analysis/utils/reflection/toStringDataClassLike.kt
index 4f4ec9dd4a860..47d1582eac1ae 100644
--- a/analysis/analysis-internal-utils/src/org/jetbrains/kotlin/analysis/utils/relfection/toStringDataClassLike.kt
+++ b/analysis/analysis-internal-utils/src/org/jetbrains/kotlin/analysis/utils/reflection/toStringDataClassLike.kt
@@ -1,9 +1,9 @@
 /*
- * Copyright 2010-2023 JetBrains s.r.o. and Kotlin Programming Language contributors.
+ * Copyright 2010-2026 JetBrains s.r.o. and Kotlin Programming Language contributors.
  * Use of this source code is governed by the Apache 2.0 license that can be found in the license/LICENSE.txt file.
  */

-package org.jetbrains.kotlin.analysis.utils.relfection
+package org.jetbrains.kotlin.analysis.utils.reflection

 import java.lang.reflect.InvocationTargetException
 import kotlin.reflect.full.declaredMemberProperties
PATCH

# Idempotency check: Verify the fix was applied by checking for the distinctive line
if ! grep -q "org.jetbrains.kotlin.analysis.utils.reflection" analysis/analysis-api/src/org/jetbrains/kotlin/analysis/api/symbols/pointers/KaSymbolPointer.kt; then
    echo "ERROR: Fix not applied correctly"
    exit 1
fi

echo "Fix applied successfully: typo 'relfection' -> 'reflection' corrected"
