#!/bin/bash
set -euo pipefail

cd /workspace/react

# Check if already applied
current_line=$(grep -n "errors: Array<{category: string; reason: string" compiler/packages/snap/src/minimize.ts 2>/dev/null | head -1 || true)
if [[ -z "$current_line" ]]; then
    echo "Patch already applied or file structure different"
    exit 0
fi

# Apply the patch
git apply - <<'PATCH'
diff --git a/compiler/packages/snap/src/minimize.ts b/compiler/packages/snap/src/minimize.ts
index 0cce5ce1bdee..c734c9306d98 100644
--- a/compiler/packages/snap/src/minimize.ts
+++ b/compiler/packages/snap/src/minimize.ts
@@ -18,7 +18,7 @@ type CompileSuccess = {kind: 'success'};
 type CompileParseError = {kind: 'parse_error'; message: string};
 type CompileErrors = {
   kind: 'errors';
-  errors: Array<{category: string; reason: string}>;
+  errors: Array<{category: string; reason: string; description: string | null}>;
 };
 type CompileResult = CompileSuccess | CompileParseError | CompileErrors;

@@ -70,7 +70,11 @@ function compileAndGetError(
     return {kind: 'success'};
   } catch (e: unknown) {
     const error = e as Error & {
-      details?: Array<{category: string; reason: string}>;
+      details?: Array<{
+        category: string;
+        reason: string;
+        description: string | null;
+      }>;
     };
     // Check if this is a CompilerError with details
     if (error.details && error.details.length > 0) {
@@ -79,6 +83,7 @@ function compileAndGetError(
         errors: error.details.map(detail => ({
           category: detail.category,
           reason: detail.reason,
+          description: detail.description,
         })),
       };
     }
@@ -89,6 +94,7 @@ function compileAndGetError(
         {
           category: error.name ?? 'Error',
           reason: error.message,
+          description: null,
         },
       ],
     };
@@ -108,7 +114,8 @@ function errorsMatch(a: CompileErrors, b: CompileResult): boolean {
   for (let i = 0; i < a.errors.length; i++) {
     if (
       a.errors[i].category !== b.errors[i].category ||
-      a.errors[i].reason !== b.errors[i].reason
+      a.errors[i].reason !== b.errors[i].reason ||
+      a.errors[i].description !== b.errors[i].description
     ) {
       return false;
     }
@@ -217,6 +224,45 @@ function* removeCallArguments(ast: t.File): Generator<t.File> {
   }
 }

+/**
+ * Generator that yields ASTs with function parameters removed one at a time
+ */
+function* removeFunctionParameters(ast: t.File): Generator<t.File> {
+  // Collect all functions with parameters
+  const funcSites: Array<{funcIndex: number; paramCount: number}> = [];
+  let funcIndex = 0;
+  t.traverseFast(ast, node => {
+    if (t.isFunction(node) && node.params.length > 0) {
+      funcSites.push({funcIndex, paramCount: node.params.length});
+      funcIndex++;
+    }
+  });
+
+  // For each function, try removing each parameter (from end to start)
+  for (const {funcIndex: targetFuncIdx, paramCount} of funcSites) {
+    for (let paramIdx = paramCount - 1; paramIdx >= 0; paramIdx--) {
+      const cloned = cloneAst(ast);
+      let idx = 0;
+      let modified = false;
+
+      t.traverseFast(cloned, node => {
+        if (modified) return;
+        if (t.isFunction(node) && node.params.length > 0) {
+          if (idx === targetFuncIdx && paramIdx < node.params.length) {
+            node.params.splice(paramIdx, 1);
+            modified = true;
+          }
+          idx++;
+        }
+      });
+
+      if (modified) {
+        yield cloned;
+      }
+    }
+  }
+}
+
 /**
  * Generator that simplifies call expressions by replacing them with their arguments.
  * For single argument: foo(x) -> x
@@ -1566,6 +1612,84 @@ function* removeObjectProperties(ast: t.File): Generator<t.File> {
   }
 }

+/**
+ * Generator that removes elements from array destructuring patterns one at a time
+ */
+function* removeArrayPatternElements(ast: t.File): Generator<t.File> {
+  // Collect all array patterns with elements
+  const patternSites: Array<{patternIndex: number; elementCount: number}> = [];
+  let patternIndex = 0;
+  t.traverseFast(ast, node => {
+    if (t.isArrayPattern(node) && node.elements.length > 0) {
+      patternSites.push({patternIndex, elementCount: node.elements.length});
+      patternIndex++;
+    }
+  });
+
+  // For each pattern, try removing each element (from end to start)
+  for (const {patternIndex: targetPatternIdx, elementCount} of patternSites) {
+    for (let elemIdx = elementCount - 1; elemIdx >= 0; elemIdx--) {
+      const cloned = cloneAst(ast);
+      let idx = 0;
+      let modified = false;
+
+      t.traverseFast(cloned, node => {
+        if (modified) return;
+        if (t.isArrayPattern(node) && node.elements.length > 0) {
+          if (idx === targetPatternIdx && elemIdx < node.elements.length) {
+            node.elements.splice(elemIdx, 1);
+            modified = true;
+          }
+          idx++;
+        }
+      });
+
+      if (modified) {
+        yield cloned;
+      }
+    }
+  }
+}
+
+/**
+ * Generator that removes properties from object destructuring patterns one at a time
+ */
+function* removeObjectPatternProperties(ast: t.File): Generator<t.File> {
+  // Collect all object patterns with properties
+  const patternSites: Array<{patternIndex: number; propCount: number}> = [];
+  let patternIndex = 0;
+  t.traverseFast(ast, node => {
+    if (t.isObjectPattern(node) && node.properties.length > 0) {
+      patternSites.push({patternIndex, propCount: node.properties.length});
+      patternIndex++;
+    }
+  });
+
+  // For each pattern, try removing each property (from end to start)
+  for (const {patternIndex: targetPatternIdx, propCount} of patternSites) {
+    for (let propIdx = propCount - 1; propIdx >= 0; propIdx--) {
+      const cloned = cloneAst(ast);
+      let idx = 0;
+      let modified = false;
+
+      t.traverseFast(cloned, node => {
+        if (modified) return;
+        if (t.isObjectPattern(node) && node.properties.length > 0) {
+          if (idx === targetPatternIdx && propIdx < node.properties.length) {
+            node.properties.splice(propIdx, 1);
+            modified = true;
+          }
+          idx++;
+        }
+      });
+
+      if (modified) {
+        yield cloned;
+      }
+    }
+  }
+}
+
 /**
  * Generator that simplifies assignment expressions (a = b) -> a or b
  */
@@ -1852,8 +1976,14 @@ function* simplifyIdentifiersRenameRef(ast: t.File): Generator<t.File> {
 const simplificationStrategies = [
   {name: 'removeStatements', generator: removeStatements},
   {name: 'removeCallArguments', generator: removeCallArguments},
+  {name: 'removeFunctionParameters', generator: removeFunctionParameters},
   {name: 'removeArrayElements', generator: removeArrayElements},
   {name: 'removeObjectProperties', generator: removeObjectProperties},
+  {name: 'removeArrayPatternElements', generator: removeArrayPatternElements},
+  {
+    name: 'removeObjectPatternProperties',
+    generator: removeObjectPatternProperties,
+  },
   {name: 'removeJSXAttributes', generator: removeJSXAttributes},
   {name: 'removeJSXChildren', generator: removeJSXChildren},
   {name: 'removeJSXFragmentChildren', generator: removeJSXFragmentChildren},
PATCH

echo "Patch applied successfully"
