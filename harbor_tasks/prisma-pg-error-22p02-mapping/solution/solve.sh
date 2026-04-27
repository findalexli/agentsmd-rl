#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prisma

# Idempotency: bail out if patch already applied
if grep -q "kind: 'InvalidInputValue'" packages/adapter-pg/src/errors.ts 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/adapter-neon/src/errors.ts b/packages/adapter-neon/src/errors.ts
index 2fe00e83b59e..cb3009865b31 100644
--- a/packages/adapter-neon/src/errors.ts
+++ b/packages/adapter-neon/src/errors.ts
@@ -25,6 +25,11 @@ function mapDriverError(error: DatabaseError): MappedError {
         kind: 'ValueOutOfRange',
         cause: error.message,
       }
+    case '22P02':
+      return {
+        kind: 'InvalidInputValue',
+        message: error.message,
+      }
     case '23505': {
       const fields = error.detail
         ?.match(/Key \(([^)]+)\)/)
diff --git a/packages/adapter-pg/src/__tests__/errors.test.ts b/packages/adapter-pg/src/__tests__/errors.test.ts
index a56e7a5f7101..7577cadb75a4 100644
--- a/packages/adapter-pg/src/__tests__/errors.test.ts
+++ b/packages/adapter-pg/src/__tests__/errors.test.ts
@@ -23,6 +23,16 @@ describe('convertDriverError', () => {
     })
   })

+  it('should handle InvalidInputValue (22P02)', () => {
+    const error = { code: '22P02', message: 'invalid input value for enum "Status": "INVALID"', severity: 'ERROR' }
+    expect(convertDriverError(error)).toEqual({
+      kind: 'InvalidInputValue',
+      message: 'invalid input value for enum "Status": "INVALID"',
+      originalCode: error.code,
+      originalMessage: error.message,
+    })
+  })
+
   it('should handle UniqueConstraintViolation (23505)', () => {
     const error = { code: '23505', message: 'msg', severity: 'ERROR', detail: 'Key (id)' }
     expect(convertDriverError(error)).toEqual({
diff --git a/packages/adapter-pg/src/errors.ts b/packages/adapter-pg/src/errors.ts
index 18c586fee06f..e7188172231c 100644
--- a/packages/adapter-pg/src/errors.ts
+++ b/packages/adapter-pg/src/errors.ts
@@ -69,6 +69,11 @@ function mapDriverError(error: DatabaseError): MappedError {
         kind: 'ValueOutOfRange',
         cause: error.message,
       }
+    case '22P02':
+      return {
+        kind: 'InvalidInputValue',
+        message: error.message,
+      }
     case '23505': {
       const fields = error.detail
         ?.match(/Key \(([^)]+)\)/)
diff --git a/packages/adapter-ppg/src/errors.ts b/packages/adapter-ppg/src/errors.ts
index 84fa4c798163..c1a5622d39b4 100644
--- a/packages/adapter-ppg/src/errors.ts
+++ b/packages/adapter-ppg/src/errors.ts
@@ -25,6 +25,11 @@ function mapDriverError(error: DatabaseError): MappedError {
         kind: 'ValueOutOfRange',
         cause: error.message,
       }
+    case '22P02':
+      return {
+        kind: 'InvalidInputValue',
+        message: error.message,
+      }
     case '23505': {
       const fields = error.details.detail
         ?.match(/Key \(([^)]+)\)/)
diff --git a/packages/client-engine-runtime/src/user-facing-error.ts b/packages/client-engine-runtime/src/user-facing-error.ts
index 61b42e362348..682443e73fcd 100644
--- a/packages/client-engine-runtime/src/user-facing-error.ts
+++ b/packages/client-engine-runtime/src/user-facing-error.ts
@@ -79,6 +79,8 @@ function getErrorCode(err: DriverAdapterError): string | undefined {
       return 'P2002'
     case 'ForeignKeyConstraintViolation':
       return 'P2003'
+    case 'InvalidInputValue':
+      return 'P2007'
     case 'UnsupportedNativeDataType':
       return 'P2010'
     case 'NullConstraintViolation':
@@ -176,6 +178,8 @@ function renderErrorMessage(err: DriverAdapterError): string | undefined {
       return `Error in external connector (id ${err.cause.id})`
     case 'TooManyConnections':
       return `Too many database connections opened: ${err.cause.cause}`
+    case 'InvalidInputValue':
+      return `Invalid input value: ${err.cause.message}`
     case 'sqlite':
     case 'postgres':
     case 'mysql':
diff --git a/packages/driver-adapter-utils/src/types.ts b/packages/driver-adapter-utils/src/types.ts
index cd9354592f33..6523e04933aa 100644
--- a/packages/driver-adapter-utils/src/types.ts
+++ b/packages/driver-adapter-utils/src/types.ts
@@ -141,6 +141,10 @@ export type MappedError =
       kind: 'ValueOutOfRange'
       cause: string
     }
+  | {
+      kind: 'InvalidInputValue'
+      message: string
+    }
   | {
       kind: 'MissingFullTextSearchIndex'
     }
PATCH

echo "Gold patch applied successfully"
