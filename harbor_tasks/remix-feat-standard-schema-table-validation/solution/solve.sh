#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'validatePartialRowInput' packages/data-table/src/lib/table.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply --whitespace=fix - <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
index dfa203d3d43..9aee9cd378f 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -16,6 +16,7 @@
 - **Monorepo**: pnpm workspace with packages in `packages/` directory
 - **Key packages**: headers, fetch-proxy, fetch-router, file-storage, form-data-parser, lazy-file, multipart-parser, node-fetch-server, route-pattern, tar-parser
 - **Package exports**: All `exports` in `package.json` have a dedicated file in `src` that defines the public API by re-exporting from within `src/lib`
+- **Cross-package boundaries**: Avoid re-exporting APIs/types from other packages. Consumers should import from the owning package directly. Reuse shared concepts from sibling packages internally instead of creating bespoke duplicate implementations.
 - **Philosophy**: Web standards-first, runtime-agnostic (Node.js, Bun, Deno, Cloudflare Workers). Use Web Streams API, Uint8Array, Web Crypto API, Blob/File instead of Node.js APIs
 - **Tests run from source** (no build required), using Node.js test runner

diff --git a/packages/data-table/.changes/minor.table-standard-schema.md b/packages/data-table/.changes/minor.table-standard-schema.md
new file mode 100644
index 00000000000..8778a3b348f
--- /dev/null
+++ b/packages/data-table/.changes/minor.table-standard-schema.md
@@ -0,0 +1,3 @@
+Make `createTable()` results Standard Schema-compatible so tables can be used directly with `parse()`/`parseSafe()` from `remix/data-schema`.
+
+Table parsing now mirrors write validation semantics used by `create()`/`update()`: partial objects are accepted, provided values are parsed via column schemas, and unknown columns are rejected.
diff --git a/packages/data-table/README.md b/packages/data-table/README.md
index 616e1d5d79e..3771fd309d5 100644
--- a/packages/data-table/README.md
+++ b/packages/data-table/README.md
@@ -14,10 +14,10 @@ Typed relational query toolkit for JavaScript runtimes.

 `data-table` gives you two complementary APIs:

-- **Query Builder API** for expressive joins, aggregates, eager loading, and scoped writes
-- **Database Helper API** for common CRUD flows (`find`, `create`, `update`, `delete`)
+- [**Query Builder**](#query-builder) for expressive joins, aggregates, eager loading, and scoped writes
+- [**CRUD Helpers**](#crud-helpers) for common create/read/update/delete flows (`find`, `create`, `update`, `delete`)

-Both APIs are type-safe and validate values using your `remix/data-schema` definitions.
+Both APIs are type-safe and validate values using your [remix/data-schema](https://github.com/remix-run/remix/tree/main/packages/data-schema) definitions.

 ## Installation

@@ -67,9 +67,9 @@ let pool = new Pool({ connectionString: process.env.DATABASE_URL })
 let db = createDatabase(createPostgresDatabaseAdapter(pool))
 ```

-## Query Builder API
+## Query Builder

-Use `db.query(Table)` when you need joins, custom shape selection, eager loading, or aggregate logic.
+Use `db.query(table)` when you need joins, custom shape selection, eager loading, or aggregate logic.

 ```ts
 import { eq, ilike } from 'remix/data-table'
@@ -115,11 +115,11 @@ await db
   .update({ status: 'processing' })
 ```

-## Database Helper API (High-Level CRUD)
+## CRUD Helpers

-Use these helpers for common operations without building a full query chain.
+`data-table` provides helpers for common create/read/update/delete operations. Use these helpers for common operations without building a full query chain.

-### Read helpers
+### Read operations

 ```ts
 import { or } from 'remix/data-table'
@@ -216,11 +216,44 @@ Return behavior:
 - `find`/`findOne` -> row or `null`
 - `findMany` -> rows
 - `create` -> `WriteResult` by default, row when `returnRow: true`
-- `createMany` -> `WriteResult` by default, rows when `returnRows: true` (RETURNING adapters only)
+- `createMany` -> `WriteResult` by default, rows when `returnRows: true` (not supported in MySQL because it doesn't support `RETURNING`)
 - `update` -> updated row or `null`
 - `updateMany`/`deleteMany` -> `WriteResult`
 - `delete` -> `boolean`

+### Data Validation
+
+For write operations, data validation happens before SQL is executed so invalid data does not get written to the database.
+
+`data-table` treats each column schema as both:
+
+- a runtime validator (is this input valid?)
+- a parser (what normalized value should be written?)
+
+If you're familiar with Zod, this is the same idea: schema-first validation where values are checked and parsed before use. In `data-table`, that parsing runs automatically on writes (`create`, `createMany`, `update`, `upsert`) so only schema-valid values are sent to the database. Invalid values and unknown columns fail fast before a write is attempted.
+
+Tables are also [Standard Schema](https://standardschema.dev/)-compatible, so you can run the same validation explicitly with `remix/data-schema` before writing:
+
+```ts
+import { parseSafe } from 'remix/data-schema'
+
+let result = parseSafe(users, {
+  id: 'u_004',
+  email: 'new@example.com',
+  role: 'customer',
+})
+
+if (!result.success) {
+  // Handle validation issues
+}
+```
+
+Validation semantics match `create()`/`update()` input behavior:
+
+- Partial objects are allowed
+- Unknown columns fail validation
+- Provided column values are parsed through each column schema
+
 ## Transactions

 ```ts
diff --git a/packages/data-table/src/index.ts b/packages/data-table/src/index.ts
index 085c8a7d84..2a85c4916ef 100644
--- a/packages/data-table/src/index.ts
+++ b/packages/data-table/src/index.ts
@@ -25,7 +25,6 @@ export type {
   ColumnReference,
   ColumnReferenceForQualifiedName,
   ColumnSchemas,
-  DataSchema,
   HasManyOptions,
   HasManyThroughOptions,
   HasOneOptions,
diff --git a/packages/data-table/src/lib/database.ts b/packages/data-table/src/lib/database.ts
index 127f67ceef1..80e5ea98c5f 100644
--- a/packages/data-table/src/lib/database.ts
+++ b/packages/data-table/src/lib/database.ts
@@ -1,4 +1,5 @@
 import { parseSafe } from '@remix-run/data-schema'
+import type { Schema } from '@remix-run/data-schema'

 import type {
   AdapterResult,
@@ -22,17 +23,16 @@ import { DataTableAdapterError, DataTableQueryError, DataTableValidationError }
 import type {
   AnyRelation,
   AnyTable,
-  DataSchema,
   LoadedRelationMap,
   OrderByClause,
   OrderDirection,
   PrimaryKeyInput,
   Relation,
-  Table,
   TableName,
   TablePrimaryKey,
   TableRow,
   TableRowWith,
+  TimestampConfig,
   tableMetadataKey,
 } from './table.ts'
 import {
@@ -42,6 +42,7 @@ import {
   getTableName,
   getTablePrimaryKey,
   getTableTimestamps,
+  validatePartialRow,
 } from './table.ts'
 import type { Predicate, WhereInput } from './operators.ts'
 import { and, eq, inList, normalizeWhereInput, or } from './operators.ts'
@@ -50,7 +51,7 @@ import { rawSql, isSqlStatement } from './sql.ts'
 import type { AdapterStatement } from './adapter.ts'
 import type { Pretty } from './types.ts'
 import { normalizeColumnInput } from './references.ts'
-import type { ColumnInput, NormalizeColumnInput } from './references.ts'
+import type { ColumnInput, NormalizeColumnInput, TableMetadataLike } from './references.ts'

 type QueryState = {
   select: '*' | SelectColumn[]
@@ -152,13 +153,16 @@ export type QueryTableInput<
   tableName extends string,
   row extends Record<string, unknown>,
   primaryKey extends readonly (keyof row & string)[],
-> = Table<
+> = TableMetadataLike<
   tableName,
   {
-    [column in keyof row & string]: DataSchema<any, row[column]>
+    [column in keyof row & string]: Schema<any, row[column]>
   },
-  primaryKey
->
+  primaryKey,
+  TimestampConfig | null
+> & {
+  '~standard': Schema<unknown, Partial<row>>['~standard']
+} & Record<string, unknown>

 export type QueryBuilderFor<
   tableName extends string,
@@ -1993,7 +1997,7 @@ function prepareInsertValues<table extends AnyTable>(
   now: unknown,
   touch: boolean,
 ): Record<string, unknown> {
-  let output = validatePartialRow(table, values)
+  let output = validateWriteValues(table, values)
   let timestamps = getTableTimestamps(table)
   let columns = getTableColumns(table)

@@ -2025,7 +2029,7 @@ function prepareUpdateValues<table extends AnyTable>(
   now: unknown,
   touch: boolean,
 ): Record<string, unknown> {
-  let output = validatePartialRow(table, values)
+  let output = validateWriteValues(table, values)
   let timestamps = getTableTimestamps(table)
   let columns = getTableColumns(table)

@@ -2043,49 +2047,52 @@ function prepareUpdateValues<table extends AnyTable>(
   return output
 }

-function validatePartialRow<table extends AnyTable>(
+function validateWriteValues<table extends AnyTable>(
   table: table,
   values: Partial<TableRow<table>>,
 ): Record<string, unknown> {
-  let output: Record<string, unknown> = {}
   let columns = getTableColumns(table)
   let tableName = getTableName(table)
+  let result = validatePartialRow(table, values)

-  for (let key in values as Record<string, unknown>) {
-    if (!Object.prototype.hasOwnProperty.call(values, key)) {
+  if ('issues' in result) {
+    let firstIssue = result.issues[0]
+    let issuePath = firstIssue?.path
+    let firstPathSegment = issuePath && issuePath.length > 0 ? issuePath[0] : undefined
+    let column = typeof firstPathSegment === 'string' ? firstPathSegment : undefined
+
+    if (column && !Object.prototype.hasOwnProperty.call(columns, column)) {
       continue
     }

-    if (!Object.prototype.hasOwnProperty.call(columns, key)) {
+    if (column) {
       throw new DataTableValidationError(
-        'Unknown column "' + key + '" for table "' + tableName + '"',
+        'Unknown column "' + column + '" for table "' + tableName + '"',
         [],
       )
     }

-    let schema = columns[key]
-    let inputValue = (values as Record<string, unknown>)[key]
-    let result = parseSafe(schema as any, inputValue) as
-      | { success: true; value: unknown }
-      | { success: false; issues: ReadonlyArray<unknown> }
-
-    if (!result.success) {
+    if (column) {
       throw new DataTableValidationError(
-        'Invalid value for column "' + key + '" in table "' + tableName + '"',
+        'Invalid value for column "' + column + '" in table "' + tableName + '"',
         result.issues,
         {
           metadata: {
             table: tableName,
-            column: key,
+            column,
           },
         },
       )
     }

-    output[key] = result.value
+    throw new DataTableValidationError(
+      'Invalid value for table "' + tableName + '"',
+      result.issues,
+      {
+        metadata: {
+          table: tableName,
+        },
+      },
+    )
   }
-
-  return output
+  return result.value as Record<string, unknown>
 }

 type ResolvedPredicateColumn = {
diff --git a/packages/data-table/src/lib/table.test.ts b/packages/data-table/src/lib/table.test.ts
index 22c6017d201..9ec5ccc6926 100644
--- a/packages/data-table/src/lib/table.test.ts
+++ b/packages/data-table/src/lib/table.test.ts
@@ -1,6 +1,6 @@
 import * as assert from 'node:assert/strict'
 import { describe, it } from 'node:test'
-import { number, string } from '@remix-run/data-schema'
+import { number, parseSafe, string } from '@remix-run/data-schema'

 import {
   columnMetadataKey,
@@ -34,6 +34,38 @@ describe('table metadata', () => {
     assert.equal(users[tableMetadataKey].name, 'users')
   })

+  it('is standard-schema compatible with create-style validation semantics', () => {
+    let users = createTable({
+      name: 'users',
+      columns: {
+        id: number(),
+        email: string(),
+      },
+    })
+
+    let partialResult = parseSafe(users, { id: 1 })
+    assert.equal(partialResult.success, true)
+
+    if (partialResult.success) {
+      assert.deepEqual(partialResult.value, { id: 1 })
+    }
+
+    let unknownKeyResult = parseSafe(users, { id: 1, extra: 'x' })
+    assert.equal(unknownKeyResult.success, false)
+
+    if (!unknownKeyResult.success) {
+      assert.deepEqual(unknownKeyResult.issues[0].path, ['extra'])
+      assert.match(unknownKeyResult.issues[0].message, /Unknown column "extra"/)
+    }
+
+    let invalidValueResult = parseSafe(users, { id: 'not-a-number' })
+    assert.equal(invalidValueResult.success, false)
+
+    if (!invalidValueResult.success) {
+      assert.deepEqual(invalidValueResult.issues[0].path, ['id'])
+    }
+  })
+
   it('builds relations with functional helpers', () => {
     let users = createTable({
       name: 'users',
diff --git a/packages/data-table/src/lib/table.ts b/packages/data-table/src/lib/table.ts
index 59835fbc391..594251aaa9a 100644
--- a/packages/data-table/src/lib/table.ts
+++ b/packages/data-table/src/lib/table.ts
@@ -1,3 +1,5 @@
+import { createSchema, parseSafe } from '@remix-run/data-schema'
+import type { InferOutput, Issue, ParseOptions, Schema } from '@remix-run/data-schema'
 import type { Predicate, WhereInput } from './operators.ts'
 import { inferForeignKey } from './inflection.ts'
 import { normalizeWhereInput } from './operators.ts'
@@ -10,24 +12,10 @@ import type { Pretty } from './types.ts'
  */
 export { columnMetadataKey, tableMetadataKey } from './references.ts'

-/**
- * Minimal Standard Schema-compatible contract used by `data-table`.
- */
-export type DataSchema<input = unknown, output = input> = {
-  '~standard': {
-    version: number
-    vendor: string
-    validate(
-      value: unknown,
-      options?: unknown,
-    ): { value: output } | { issues: ReadonlyArray<unknown> }
-  }
-}
-
 /**
  * Mapping of column names to schemas.
  */
-export type ColumnSchemas = Record<string, DataSchema<any, any>>
+export type ColumnSchemas = Record<string, Schema<any, any>>

 type ColumnNameFromColumns<columns extends ColumnSchemas> = keyof columns & string

@@ -69,7 +57,7 @@ type TableMetadata<
 export type ColumnReference<
   tableName extends string,
   columnName extends string,
-  schema extends DataSchema<any, any>,
+  schema extends Schema<any, any>,
 > = ColumnReferenceLike<`${tableName}.${columnName}`> & {
   [columnMetadataKey]: {
     tableName: tableName
@@ -79,7 +67,7 @@ export type ColumnReference<
   }
 }

-export type AnyColumn = ColumnReference<string, string, DataSchema<any, any>>
+export type AnyColumn = ColumnReference<string, string, Schema<any, any>>

 export type ColumnReferenceForQualifiedName<qualifiedName extends string> = AnyColumn & {
   [columnMetadataKey]: {
@@ -91,15 +79,33 @@ type TableColumnReferences<name extends string, columns extends ColumnSchemas> =
   [column in keyof columns & string]: ColumnReference<name, column, columns[column]>
 }

+type TableParseOutput<columns extends ColumnSchemas> = Partial<{
+  [column in keyof columns & string]: InferOutput<columns[column]>
+}>
+
 export type Table<
   name extends string,
   columns extends ColumnSchemas,
   primaryKey extends readonly ColumnNameFromColumns<columns>[],
 > = TableMetadataLike<name, columns, primaryKey, TimestampConfig | null> & {
   [tableMetadataKey]: TableMetadata<name, columns, primaryKey>
+  '~standard': Schema<unknown, TableParseOutput<columns>>['~standard']
 } & TableColumnReferences<name, columns>

-export type AnyTable = Table<string, ColumnSchemas, readonly string[]>
+export type AnyTable = TableMetadataLike<
+  string,
+  ColumnSchemas,
+  readonly string[],
+  TimestampConfig | null
+> & {
+  [tableMetadataKey]: {
+    name: string
+    columns: ColumnSchemas
+    primaryKey: readonly string[]
+    timestamps: TimestampConfig | null
+  }
+  '~standard': Schema<unknown, Partial<Record<string, unknown>>>['~standard']
+} & Record<string, unknown>

 export type TableName<table extends AnyTable> = table[typeof tableMetadataKey]['name']

@@ -109,11 +115,8 @@ export type TablePrimaryKey<table extends AnyTable> = table[typeof tableMetadata

 export type TableTimestamps<table extends AnyTable> = table[typeof tableMetadataKey]['timestamps']

-export type InferSchemaOutput<schema> =
-  schema extends DataSchema<any, infer output> ? output : never
-
 export type TableRow<table extends AnyTable> = Pretty<{
-  [column in keyof TableColumns<table> & string]: InferSchemaOutput<TableColumns<table>[column]>
+  [column in keyof TableColumns<table> & string]: InferOutput<TableColumns<table>[column]>
 }>

 export type TableRowWith<
@@ -307,6 +310,81 @@ let defaultTimestampConfig: TimestampConfig = {
   updatedAt: 'updated_at',
 }

+function prefixIssuePath(issue: Issue, key: string): Issue {
+  let issuePath = issue.path ?? []
+  return {
+    ...issue,
+    path: [key, ...issuePath],
+  }
+}
+
+function validatePartialRowInput<columns extends ColumnSchemas>(
+  tableName: string,
+  columns: columns,
+  value: unknown,
+  options?: ParseOptions,
+): { value: TableParseOutput<columns> } | { issues: ReadonlyArray<Issue> } {
+  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
+    return {
+      issues: [{ message: 'Expected object' }],
+    }
+  }
+
+  let input = value as Record<string, unknown>
+  let output: Record<string, unknown> = {}
+  let issues: Issue[] = []
+
+  for (let key in input) {
+    if (!Object.prototype.hasOwnProperty.call(input, key)) {
+      continue
+    }
+
+    if (!Object.prototype.hasOwnProperty.call(columns, key)) {
+      issues.push({
+        message: 'Unknown column "' + key + '" for table "' + tableName + '"',
+        path: [key],
+      })
+      continue
+    }
+
+    let result = parseSafe(columns[key], input[key], options)
+
+    if (!result.success) {
+      issues.push(...result.issues.map((issue) => prefixIssuePath(issue, key)))
+      continue
+    }
+
+    output[key] = result.value
+  }
+
+  if (issues.length > 0) {
+    return { issues }
+  }
+
+  return { value: output as TableParseOutput<columns> }
+}
+
+export function validatePartialRow<table extends AnyTable>(
+  table: table,
+  value: unknown,
+  options?: ParseOptions,
+): { value: Partial<TableRow<table>> } | { issues: ReadonlyArray<Issue> } {
+  let result = validatePartialRowInput(
+    getTableName(table),
+    getTableColumns(table),
+    value,
+    options,
+  )
+
+  if ('issues' in result) {
+    return result
+  }
+
+  return {
+    value: result.value as Partial<TableRow<table>>,
+  }
+}
+
 /**
  * Creates a table object with symbol-backed metadata and direct column references.
  * @param options Table declaration options.
@@ -322,14 +400,23 @@ export function createTable<
 >(
   options: CreateTableOptions<name, columns, primaryKey>,
 ): Table<name, columns, NormalizePrimaryKey<columns, primaryKey>> {
-  let resolvedPrimaryKey = normalizePrimaryKey(options.name, options.columns, options.primaryKey)
+  let tableName = options.name
+  let columns = options.columns
+
+  if (Object.prototype.hasOwnProperty.call(columns, '~standard')) {
+    throw new Error(
+      'Column name "~standard" is reserved for table validation on "' + tableName + '"',
+    )
+  }
+
+  let resolvedPrimaryKey = normalizePrimaryKey(tableName, columns, options.primaryKey)
   let timestampConfig = normalizeTimestampConfig(options.timestamps)
   let table = Object.create(null) as Table<name, columns, NormalizePrimaryKey<columns, primaryKey>>

   Object.defineProperty(table, tableMetadataKey, {
     value: Object.freeze({
-      name: options.name,
-      columns: options.columns,
+      name: tableName,
+      columns,
       primaryKey: resolvedPrimaryKey,
       timestamps: timestampConfig,
     }),
@@ -338,13 +425,26 @@ export function createTable<
     configurable: false,
   })

-  for (let columnName in options.columns) {
-    if (!Object.prototype.hasOwnProperty.call(options.columns, columnName)) {
+  Object.defineProperty(table, '~standard', {
+    value: Object.freeze({
+      version: 1,
+      vendor: 'data-table',
+      validate(value: unknown, parseOptions?: ParseOptions) {
+        return validatePartialRowInput(tableName, columns, value, parseOptions)
+      },
+    }),
+    enumerable: false,
+    writable: false,
+    configurable: false,
+  })
+
+  for (let columnName in columns) {
+    if (!Object.prototype.hasOwnProperty.call(columns, columnName)) {
       continue
     }

-    let schema = options.columns[columnName]
-    let column = createColumnReference(options.name, columnName, schema)
+    let schema = columns[columnName]
+    let column = createColumnReference(tableName, columnName, schema)

     Object.defineProperty(table, columnName, {
       value: column,
@@ -360,7 +460,7 @@ function createColumnReference<
   tableName: tableName,
   columnName: columnName,
-  schema extends DataSchema<any, any>,
+  schema extends Schema<any, any>,
 >(
   tableName: tableName,
   columnName: columnName,
@@ -539,30 +639,20 @@ export function hasManyThrough<source extends AnyTable, target extends AnyTable>
  * Creates a schema that accepts `Date`, string, and numeric timestamp inputs.
  * @returns Timestamp schema for generated timestamp helpers.
  */
-export function timestampSchema(): DataSchema<unknown, Date | string | number> {
-  return {
-    '~standard': {
-      version: 1,
-      vendor: 'data-table',
-      validate(value: unknown) {
-        if (value instanceof Date) {
-          return { value }
-        }
-
-        if (typeof value === 'string' || typeof value === 'number') {
-          return { value }
-        }
-
-        return {
-          issues: [
-            {
-              message: 'Expected Date, string, or number',
-            },
-          ],
-        }
-      },
-    },
-  }
+export function timestampSchema(): Schema<unknown, Date | string | number> {
+  return createSchema<unknown, Date | string | number>((value) => {
+    if (value instanceof Date) {
+      return { value }
+    }
+
+    if (typeof value === 'string' || typeof value === 'number') {
+      return { value }
+    }
+
+    return {
+      issues: [{ message: 'Expected Date, string, or number' }],
+    }
+  })
 }

 let defaultTimestampSchema = timestampSchema()
@@ -573,8 +663,8 @@ let defaultTimestampSchema = timestampSchema()
  * @returns Column schema map for `created_at`/`updated_at`.
  */
 export function timestamps(
-  schema: DataSchema<any, any> = defaultTimestampSchema,
-): Record<'created_at' | 'updated_at', DataSchema<any, any>> {
+  schema: Schema<any, any> = defaultTimestampSchema,
+): Record<'created_at' | 'updated_at', Schema<any, any>> {
   return {
     created_at: schema,
     updated_at: schema,

PATCH

echo "Patch applied successfully."
