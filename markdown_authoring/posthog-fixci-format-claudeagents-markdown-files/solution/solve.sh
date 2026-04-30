#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotency guard
if grep -qF "return Promise.resolve(inputs.filter(isValid).map((input) => ok(transform(input)" ".claude/agents/ingestion/pipeline-composition-doctor.md" && grep -qF "return function parseStep(input: T): Promise<PipelineResult<T & { parsed: boolea" ".claude/agents/ingestion/pipeline-step-doctor.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/agents/ingestion/pipeline-composition-doctor.md b/.claude/agents/ingestion/pipeline-composition-doctor.md
@@ -76,16 +76,16 @@ The framework throws if this invariant is violated.
 ```typescript
 // GOOD - one result per input
 function createBatchStep(): BatchProcessingStep<Input, Output> {
-    return function batchStep(inputs) {
-        return Promise.resolve(inputs.map(input => ok(transform(input))))
-    }
+  return function batchStep(inputs) {
+    return Promise.resolve(inputs.map((input) => ok(transform(input))))
+  }
 }
 
 // BAD - filtering inside batch step (changes cardinality)
 function createBatchStep(): BatchProcessingStep<Input, Output> {
-    return function batchStep(inputs) {
-        return Promise.resolve(inputs.filter(isValid).map(input => ok(transform(input))))
-    }
+  return function batchStep(inputs) {
+    return Promise.resolve(inputs.filter(isValid).map((input) => ok(transform(input))))
+  }
 }
 ```
 
diff --git a/.claude/agents/ingestion/pipeline-step-doctor.md b/.claude/agents/ingestion/pipeline-step-doctor.md
@@ -106,16 +106,16 @@ Don't repeat them.
 ```typescript
 // GOOD - types inferred from ProcessingStep<T, T & { parsed: boolean }>
 function createParseStep<T extends { raw: string }>(): ProcessingStep<T, T & { parsed: boolean }> {
-    return function parseStep(input) {
-        return Promise.resolve(ok({ ...input, parsed: true }))
-    }
+  return function parseStep(input) {
+    return Promise.resolve(ok({ ...input, parsed: true }))
+  }
 }
 
 // BAD - redundant annotation on inner function
 function createParseStep<T extends { raw: string }>(): ProcessingStep<T, T & { parsed: boolean }> {
-    return function parseStep(input: T): Promise<PipelineResult<T & { parsed: boolean }>> {
-        return Promise.resolve(ok({ ...input, parsed: true }))
-    }
+  return function parseStep(input: T): Promise<PipelineResult<T & { parsed: boolean }>> {
+    return Promise.resolve(ok({ ...input, parsed: true }))
+  }
 }
 ```
 
@@ -126,17 +126,17 @@ Dependencies are injected via factory function parameters, never via globals or
 ```typescript
 // GOOD - config injected via factory
 function createLookupStep(db: Database, timeout: number): ProcessingStep<Input, Output> {
-    return function lookupStep(input) {
-        // uses db and timeout from closure
-    }
+  return function lookupStep(input) {
+    // uses db and timeout from closure
+  }
 }
 
 // BAD - reads from global
 const db = getGlobalDatabase()
 function createLookupStep(): ProcessingStep<Input, Output> {
-    return function lookupStep(input) {
-        // uses module-level db
-    }
+  return function lookupStep(input) {
+    // uses module-level db
+  }
 }
 ```
 
PATCH

echo "Gold patch applied."
