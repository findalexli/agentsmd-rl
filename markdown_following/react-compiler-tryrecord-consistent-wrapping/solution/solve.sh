#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'fn.env.recordErrors(errors)' compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoDerivedComputationsInEffects.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/compiler/fault-tolerance-overview.md b/compiler/fault-tolerance-overview.md
index aaeee21676dd..63e7b01d99cc 100644
--- a/compiler/fault-tolerance-overview.md
+++ b/compiler/fault-tolerance-overview.md
@@ -328,4 +328,6 @@ Walk through `runWithEnvironment` and wrap each pass call site. This is the inte
 * **Partial HIR can trigger downstream invariants.** When lowering skips or partially handles constructs (e.g., unreachable hoisted functions, `var` declarations before the fix), downstream passes like `InferMutationAliasingEffects` may encounter uninitialized identifiers and throw invariants. This is acceptable since the function still correctly bails out of compilation, but error messages may be less specific. The fix for `var` (treating as `let`) demonstrates how to avoid this: continue lowering with a best-effort representation rather than skipping entirely.
 * **Errors accumulated on `env` are lost when an invariant propagates out of the pipeline.** Since invariant CompilerErrors always re-throw through `tryRecord()`, they exit the pipeline as exceptions. The caller only sees the invariant error, not any errors previously recorded on `env`. This is a design limitation that could be addressed by aggregating env errors with caught exceptions in `tryCompileFunction()`.
 * **Dedicated fault tolerance test fixtures** were added in `__tests__/fixtures/compiler/fault-tolerance/`. Each fixture combines two or more errors from different passes to verify the compiler reports all of them rather than short-circuiting on the first. Coverage includes: `var`+props mutation (BuildHIR→InferMutationAliasingEffects), `var`+ref access (BuildHIR→ValidateNoRefAccessInRender), `try/finally`+props mutation (BuildHIR→InferMutationAliasingEffects), `try/finally`+ref access (BuildHIR→ValidateNoRefAccessInRender), and a 3-error test combining try/finally+ref access+props mutation.
+* **Cleanup: consistent `tryRecord()` wrapping in Pipeline.ts.** All validation passes and inference passes are now wrapped in `env.tryRecord()` for defense-in-depth, consistent with the approach used for transform passes. Previously only transform passes were wrapped. Merged duplicate `env.enableValidations` guard blocks. Pattern B lint-only passes (`env.logErrors()`) were intentionally not wrapped since they use a different error recording strategy.
+* **Cleanup: normalized validation error recording pattern.** Four validation passes (`ValidateNoDerivedComputationsInEffects`, `ValidateMemoizedEffectDependencies`, `ValidatePreservedManualMemoization`, `ValidateSourceLocations`) were using `for (const detail of errors.details) { env.recordError(detail); }` instead of the simpler `env.recordErrors(errors)`. Normalized to use the batch method.

diff --git a/compiler/packages/babel-plugin-react-compiler/src/Entrypoint/Pipeline.ts b/compiler/packages/babel-plugin-react-compiler/src/Entrypoint/Pipeline.ts
index fd20af65b98a..43700ec9be57 100644
--- a/compiler/packages/babel-plugin-react-compiler/src/Entrypoint/Pipeline.ts
+++ b/compiler/packages/babel-plugin-react-compiler/src/Entrypoint/Pipeline.ts
@@ -161,8 +161,12 @@ function runWithEnvironment(
   pruneMaybeThrows(hir);
   log({kind: 'hir', name: 'PruneMaybeThrows', value: hir});

-  validateContextVariableLValues(hir);
-  validateUseMemo(hir);
+  env.tryRecord(() => {
+    validateContextVariableLValues(hir);
+  });
+  env.tryRecord(() => {
+    validateUseMemo(hir);
+  });

   if (env.enableDropManualMemoization) {
     dropManualMemoization(hir);
@@ -198,10 +202,14 @@ function runWithEnvironment(

   if (env.enableValidations) {
     if (env.config.validateHooksUsage) {
-      validateHooksUsage(hir);
+      env.tryRecord(() => {
+        validateHooksUsage(hir);
+      });
     }
     if (env.config.validateNoCapitalizedCalls) {
-      validateNoCapitalizedCalls(hir);
+      env.tryRecord(() => {
+        validateNoCapitalizedCalls(hir);
+      });
     }
   }

@@ -211,7 +219,9 @@ function runWithEnvironment(
   analyseFunctions(hir);
   log({kind: 'hir', name: 'AnalyseFunctions', value: hir});

-  inferMutationAliasingEffects(hir);
+  env.tryRecord(() => {
+    inferMutationAliasingEffects(hir);
+  });
   log({kind: 'hir', name: 'InferMutationAliasingEffects', value: hir});

   if (env.outputMode === 'ssr') {
@@ -225,25 +235,31 @@ function runWithEnvironment(
   pruneMaybeThrows(hir);
   log({kind: 'hir', name: 'PruneMaybeThrows', value: hir});

-  inferMutationAliasingRanges(hir, {
-    isFunctionExpression: false,
+  env.tryRecord(() => {
+    inferMutationAliasingRanges(hir, {
+      isFunctionExpression: false,
+    });
   });
   log({kind: 'hir', name: 'InferMutationAliasingRanges', value: hir});
   if (env.enableValidations) {
-    validateLocalsNotReassignedAfterRender(hir);
-  }
+    env.tryRecord(() => {
+      validateLocalsNotReassignedAfterRender(hir);
+    });

-  if (env.enableValidations) {
     if (env.config.assertValidMutableRanges) {
       assertValidMutableRanges(hir);
     }

     if (env.config.validateRefAccessDuringRender) {
-      validateNoRefAccessInRender(hir);
+      env.tryRecord(() => {
+        validateNoRefAccessInRender(hir);
+      });
     }

     if (env.config.validateNoSetStateInRender) {
-      validateNoSetStateInRender(hir);
+      env.tryRecord(() => {
+        validateNoSetStateInRender(hir);
+      });
     }

     if (
@@ -252,7 +268,9 @@ function runWithEnvironment(
     ) {
       env.logErrors(validateNoDerivedComputationsInEffects_exp(hir));
     } else if (env.config.validateNoDerivedComputationsInEffects) {
-      validateNoDerivedComputationsInEffects(hir);
+      env.tryRecord(() => {
+        validateNoDerivedComputationsInEffects(hir);
+      });
     }

     if (env.config.validateNoSetStateInEffects && env.outputMode === 'lint') {
@@ -277,7 +295,9 @@ function runWithEnvironment(
       env.config.validateExhaustiveEffectDependencies
     ) {
       // NOTE: this relies on reactivity inference running first
-      validateExhaustiveDependencies(hir);
+      env.tryRecord(() => {
+        validateExhaustiveDependencies(hir);
+      });
     }
   }

@@ -506,7 +526,9 @@ function runWithEnvironment(
     env.config.enablePreserveExistingMemoizationGuarantees ||
     env.config.validatePreserveExistingMemoizationGuarantees
   ) {
-    validatePreservedManualMemoization(reactiveFunction);
+    env.tryRecord(() => {
+      validatePreservedManualMemoization(reactiveFunction);
+    });
   }

   const ast = codegenFunction(reactiveFunction, {
@@ -519,7 +541,9 @@ function runWithEnvironment(
   }

   if (env.config.validateSourceLocations) {
-    validateSourceLocations(func, ast, env);
+    env.tryRecord(() => {
+      validateSourceLocations(func, ast, env);
+    });
   }

   /**
diff --git a/compiler/packages/babel-plugin-react-compiler/src/HIR/BuildHIR.ts b/compiler/packages/babel-plugin-react-compiler/src/HIR/BuildHIR.ts
index a5a66c8b8426..0ed1f1b9e4d1 100644
--- a/compiler/packages/babel-plugin-react-compiler/src/HIR/BuildHIR.ts
+++ b/compiler/packages/babel-plugin-react-compiler/src/HIR/BuildHIR.ts
@@ -217,11 +217,7 @@ export function lower(
     if (err instanceof CompilerError) {
       // Re-throw invariant errors immediately
       for (const detail of err.details) {
-        if (
-          (detail instanceof CompilerDiagnostic
-            ? detail.category
-            : detail.category) === ErrorCategory.Invariant
-        ) {
+        if (detail.category === ErrorCategory.Invariant) {
           throw err;
         }
       }
diff --git a/compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoDerivedComputationsInEffects.ts b/compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoDerivedComputationsInEffects.ts
index 6c73d4946c1c..09c30a692ab5 100644
--- a/compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoDerivedComputationsInEffects.ts
+++ b/compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoDerivedComputationsInEffects.ts
@@ -97,9 +97,7 @@ export function validateNoDerivedComputationsInEffects(fn: HIRFunction): void {
       }
     }
   }
-  for (const detail of errors.details) {
-    fn.env.recordError(detail);
-  }
+  fn.env.recordErrors(errors);
 }

 function validateEffect(
diff --git a/compiler/packages/babel-plugin-react-compiler/src/Validation/ValidatePreservedManualMemoization.ts b/compiler/packages/babel-plugin-react-compiler/src/Validation/ValidatePreservedManualMemoization.ts
index 5da731a9e923..2434e25f019e 100644
--- a/compiler/packages/babel-plugin-react-compiler/src/Validation/ValidatePreservedManualMemoization.ts
+++ b/compiler/packages/babel-plugin-react-compiler/src/Validation/ValidatePreservedManualMemoization.ts
@@ -52,9 +52,7 @@ export function validatePreservedManualMemoization(fn: ReactiveFunction): void {
     manualMemoState: null,
   };
   visitReactiveFunction(fn, new Visitor(), state);
-  for (const detail of state.errors.details) {
-    fn.env.recordError(detail);
-  }
+  fn.env.recordErrors(state.errors);
 }

 const DEBUG = false;
diff --git a/compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateSourceLocations.ts b/compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateSourceLocations.ts
index 75090397bbba..a1ae4c55bdf3 100644
--- a/compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateSourceLocations.ts
+++ b/compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateSourceLocations.ts
@@ -310,7 +310,5 @@ export function validateSourceLocations(
     }
   }

-  for (const detail of errors.details) {
-    env.recordError(detail);
-  }
+  env.recordErrors(errors);
 }

PATCH

echo "Patch applied successfully."
