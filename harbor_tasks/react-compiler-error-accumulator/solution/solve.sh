#!/bin/bash
set -euo pipefail

# Apply the error accumulation infrastructure fix to Environment.ts

cd /workspace/react/compiler/packages/babel-plugin-react-compiler/src/HIR

# Check if already applied (idempotency check)
if grep -q "tryRecord" Environment.ts; then
    echo "Fix already applied, skipping"
    exit 0
fi

# Apply the patch
git apply - <<'PATCH'
diff --git a/src/HIR/Environment.ts b/src/HIR/Environment.ts
index ba224d352..a44ae542b 100644
--- a/src/HIR/Environment.ts
+++ b/src/HIR/Environment.ts
@@ -8,7 +8,12 @@
 import * as t from '@babel/types';
 import {ZodError, z} from 'zod/v4';
 import {fromZodError} from 'zod-validation-error/v4';
-import {CompilerError} from '../CompilerError';
+import {
+  CompilerDiagnostic,
+  CompilerError,
+  CompilerErrorDetail,
+  ErrorCategory,
+} from '../CompilerError';
 import {CompilerOutputMode, Logger, ProgramContext} from '../Entrypoint';
 import {Err, Ok, Result} from '../Utils/Result';
 import {
@@ -545,6 +550,12 @@ export class Environment {

   #flowTypeEnvironment: FlowTypeEnv | null;

+  /**
+   * Accumulated compilation errors. Passes record errors here instead of
+   * throwing, so the pipeline can continue and report all errors at once.
+   */
+  #errors: CompilerError = new CompilerError();
+
   constructor(
     scope: BabelScope,
     fnType: ReactFunctionType,
@@ -702,6 +713,75 @@ export class Environment {
     }
   }

+  /**
+   * Record a single diagnostic or error detail on this environment.
+   * If the error is an Invariant, it is immediately thrown since invariants
+   * represent internal bugs that cannot be recovered from.
+   * Otherwise, the error is accumulated and optionally logged.
+   */
+  recordError(error: CompilerDiagnostic | CompilerErrorDetail): void {
+    if (error.category === ErrorCategory.Invariant) {
+      const compilerError = new CompilerError();
+      if (error instanceof CompilerDiagnostic) {
+        compilerError.pushDiagnostic(error);
+      } else {
+        compilerError.pushErrorDetail(error);
+      }
+      throw compilerError;
+    }
+    if (error instanceof CompilerDiagnostic) {
+      this.#errors.pushDiagnostic(error);
+    } else {
+      this.#errors.pushErrorDetail(error);
+    }
+  }
+
+  /**
+   * Record all diagnostics from a CompilerError onto this environment.
+   */
+  recordErrors(error: CompilerError): void {
+    for (const detail of error.details) {
+      this.recordError(detail);
+    }
+  }
+
+  /**
+   * Returns true if any errors have been recorded during compilation.
+   */
+  hasErrors(): boolean {
+    return this.#errors.hasAnyErrors();
+  }
+
+  /**
+   * Returns the accumulated CompilerError containing all recorded diagnostics.
+   */
+  aggregateErrors(): CompilerError {
+    return this.#errors;
+  }
+
+  /**
+   * Wraps a callback in try/catch: if the callback throws a CompilerError
+   * that is NOT an invariant, the error is recorded and execution continues.
+   * Non-CompilerError exceptions and invariants are re-thrown.
+   */
+  tryRecord(fn: () => void): void {
+    try {
+      fn();
+    } catch (err) {
+      if (err instanceof CompilerError) {
+        // Check if any detail is an invariant — if so, re-throw
+        for (const detail of err.details) {
+          if (detail.category === ErrorCategory.Invariant) {
+            throw err;
+          }
+        }
+        this.recordErrors(err);
+      } else {
+        throw err;
+      }
+    }
+  }
+
   isContextIdentifier(node: t.Identifier): boolean {
     return this.#contextIdentifiers.has(node);
   }
PATCH

echo "Fix applied successfully"
