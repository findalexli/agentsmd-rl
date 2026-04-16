#!/bin/bash
set -e

cd /workspace/bun
# Idempotency check - if fix is already applied, exit
if grep -q "buildDefinedColumnsAndQuery" src/js/internal/sql/shared.ts 2>/dev/null; then
    echo "Fix already applied, skipping"
    exit 0
fi

# Apply the gold patch - code changes + config file update

cat > /tmp/fix.patch << 'PATCH_EOF'
diff --git a/src/js/internal/sql/mysql.ts b/src/js/internal/sql/mysql.ts
index 9dce2eb17c4..ef6f33bf788 100644
--- a/src/js/internal/sql/mysql.ts
+++ b/src/js/internal/sql/mysql.ts
@@ -1,7 +1,7 @@
 import type { MySQLErrorOptions } from "internal/sql/errors";
 import type { Query } from "./query";
 import type { ArrayType, DatabaseAdapter, SQLArrayParameter, SQLHelper, SQLResultArray, SSLMode } from "./shared";
-const { SQLHelper, SSLMode, SQLResultArray } = require("internal/sql/shared");
+const { SQLHelper, SSLMode, SQLResultArray, buildDefinedColumnsAndQuery } = require("internal/sql/shared");
 const {
   Query,
   SQLQueryFlags,
@@ -455,11 +455,10 @@ class PooledMySQLConnection {
   }
 }

-class MySQLAdapter implements DatabaseAdapter<
-  PooledMySQLConnection,
-  $ZigGeneratedClasses.MySQLConnection,
-  $ZigGeneratedClasses.MySQLQuery
-> {
+class MySQLAdapter
+  implements
+    DatabaseAdapter<PooledMySQLConnection, $ZigGeneratedClasses.MySQLConnection, $ZigGeneratedClasses.MySQLQuery>
+{
   public readonly connectionInfo: Bun.SQL.__internal.DefinedPostgresOrMySQLOptions;

   public readonly connections: PooledMySQLConnection[];
@@ -1020,29 +1019,32 @@ class MySQLAdapter implements DatabaseAdapter<
               // insert into users ${sql(users)} or insert into users ${sql(user)}
               //

-              query += "(";
-              for (let j = 0; j < columnCount; j++) {
-                query += this.escapeIdentifier(columns[j]);
-                if (j < lastColumnIndex) {
-                  query += ", ";
-                }
+              // Build column list while determining which columns have at least one defined value
+              const { definedColumns, columnsSql } = buildDefinedColumnsAndQuery(
+                columns,
+                items,
+                this.escapeIdentifier.bind(this),
+              );
+
+              const definedColumnCount = definedColumns.length;
+              if (definedColumnCount === 0) {
+                throw new SyntaxError("Insert needs to have at least one column with a defined value");
               }
-              query += ") VALUES";
+              const lastDefinedColumnIndex = definedColumnCount - 1;
+
+              query += columnsSql;
               if ($isArray(items)) {
                 const itemsCount = items.length;
                 const lastItemIndex = itemsCount - 1;
                 for (let j = 0; j < itemsCount; j++) {
                   query += "(";
                   const item = items[j];
-                  for (let k = 0; k < columnCount; k++) {
-                    const column = columns[k];
+                  for (let k = 0; k < definedColumnCount; k++) {
+                    const column = definedColumns[k];
                     const columnValue = item[column];
-                    query += `?${k < lastColumnIndex ? ", " : ""}`;
-                    if (typeof columnValue === "undefined") {
-                      binding_values.push(null);
-                    } else {
-                      binding_values.push(columnValue);
-                    }
+                    query += `?${k < lastDefinedColumnIndex ? ", " : ""}`;
+                    // If this item has undefined for a column that other items defined, use null
+                    binding_values.push(typeof columnValue === "undefined" ? null : columnValue);
                   }
                   if (j < lastItemIndex) {
                     query += "),";
@@ -1053,15 +1055,11 @@ class MySQLAdapter implements DatabaseAdapter<
               } else {
                 query += "(";
                 const item = items;
-                for (let j = 0; j < columnCount; j++) {
-                  const column = columns[j];
+                for (let j = 0; j < definedColumnCount; j++) {
+                  const column = definedColumns[j];
                   const columnValue = item[column];
-                  query += `?${j < lastColumnIndex ? ", " : ""}`;
-                  if (typeof columnValue === "undefined") {
-                    binding_values.push(null);
-                  } else {
-                    binding_values.push(columnValue);
-                  }
+                  query += `?${j < lastDefinedColumnIndex ? ", " : ""}`;
+                  binding_values.push(columnValue);
                 }
                 query += ") "; // the user can add RETURNING * or RETURNING id
               }
diff --git a/src/js/internal/sql/postgres.ts b/src/js/internal/sql/postgres.ts
index 99123d93a31..af4502cd9ad 100644
--- a/src/js/internal/sql/postgres.ts
+++ b/src/js/internal/sql/postgres.ts
@@ -1,7 +1,13 @@
 import type { PostgresErrorOptions } from "internal/sql/errors";
 import type { Query } from "./query";
 import type { ArrayType, DatabaseAdapter, SQLArrayParameter, SQLHelper, SQLResultArray, SSLMode } from "./shared";
-const { SQLHelper, SSLMode, SQLResultArray, SQLArrayParameter } = require("internal/sql/shared");
+const {
+  SQLHelper,
+  SSLMode,
+  SQLResultArray,
+  SQLArrayParameter,
+  buildDefinedColumnsAndQuery,
+} = require("internal/sql/shared");
 const {
   Query,
   SQLQueryFlags,
@@ -672,11 +678,14 @@ class PooledPostgresConnection {
   }
 }

-class PostgresAdapter implements DatabaseAdapter<
-  PooledPostgresConnection,
-  $ZigGeneratedClasses.PostgresSQLConnection,
-  $ZigGeneratedClasses.PostgresSQLQuery
-> {
+class PostgresAdapter
+  implements
+    DatabaseAdapter<
+      PooledPostgresConnection,
+      $ZigGeneratedClasses.PostgresSQLConnection,
+      $ZigGeneratedClasses.PostgresSQLQuery
+    >
+{
   public readonly connectionInfo: Bun.SQL.__internal.DefinedPostgresOrMySQLOptions;

   public readonly connections: PooledPostgresConnection[];
@@ -1249,29 +1258,32 @@ class PostgresAdapter implements DatabaseAdapter<
               // insert into users ${sql(users)} or insert into users ${sql(user)}
               //

-              query += "(";
-              for (let j = 0; j < columnCount; j++) {
-                query += this.escapeIdentifier(columns[j]);
-                if (j < lastColumnIndex) {
-                  query += ", ";
-                }
+              // Build column list while determining which columns have at least one defined value
+              const { definedColumns, columnsSql } = buildDefinedColumnsAndQuery(
+                columns,
+                items,
+                this.escapeIdentifier.bind(this),
+              );
+
+              const definedColumnCount = definedColumns.length;
+              if (definedColumnCount === 0) {
+                throw new SyntaxError("Insert needs to have at least one column with a defined value");
               }
-              query += ") VALUES";
+              const lastDefinedColumnIndex = definedColumnCount - 1;
+
+              query += columnsSql;
               if ($isArray(items)) {
                 const itemsCount = items.length;
                 const lastItemIndex = itemsCount - 1;
                 for (let j = 0; j < itemsCount; j++) {
                   query += "(";
                   const item = items[j];
-                  for (let k = 0; k < columnCount; k++) {
-                    const column = columns[k];
+                  for (let k = 0; k < definedColumnCount; k++) {
+                    const column = definedColumns[k];
                     const columnValue = item[column];
-                    query += `$${binding_idx++}${k < lastColumnIndex ? ", " : ""}`;
-                    if (typeof columnValue === "undefined") {
-                      binding_values.push(null);
-                    } else {
-                      binding_values.push(columnValue);
-                    }
+                    query += `$${binding_idx++}${k < lastDefinedColumnIndex ? ", " : ""}`;
+                    // If this item has undefined for a column that other items defined, use null
+                    binding_values.push(typeof columnValue === "undefined" ? null : columnValue);
                   }
                   if (j < lastItemIndex) {
                     query += "),";
@@ -1282,15 +1294,11 @@ class PostgresAdapter implements DatabaseAdapter<
               } else {
                 query += "(";
                 const item = items;
-                for (let j = 0; j < columnCount; j++) {
-                  const column = columns[j];
+                for (let j = 0; j < definedColumnCount; j++) {
+                  const column = definedColumns[j];
                   const columnValue = item[column];
-                  query += `$${binding_idx++}${j < lastColumnIndex ? ", " : ""}`;
-                  if (typeof columnValue === "undefined") {
-                    binding_values.push(null);
-                  } else {
-                    binding_values.push(columnValue);
-                  }
+                  query += `$${binding_idx++}${j < lastDefinedColumnIndex ? ", " : ""}`;
+                  binding_values.push(columnValue);
                 }
                 query += ") "; // the user can add RETURNING * or RETURNING id
               }
diff --git a/src/js/internal/sql/shared.ts b/src/js/internal/sql/shared.ts
index 85748fcb553..fc484b00c77 100644
--- a/src/js/internal/sql/shared.ts
+++ b/src/js/internal/sql/shared.ts
@@ -177,6 +177,47 @@ class SQLHelper<T> {
   }
 }

+/**
+ * Build the column list for INSERT statements while determining which columns have defined values.
+ * This combines column name generation with defined column detection in a single pass.
+ * Returns the defined columns array and the SQL fragment for the column names.
+ */
+function buildDefinedColumnsAndQuery<T>(
+  columns: (keyof T)[],
+  items: T | T[],
+  escapeIdentifier: (name: string) => string,
+): { definedColumns: (keyof T)[]; columnsSql: string } {
+  const definedColumns: (keyof T)[] = [];
+  let columnsSql = "(";
+  const columnCount = columns.length;
+
+  for (let k = 0; k < columnCount; k++) {
+    const column = columns[k];
+
+    // Check if any item has this column defined
+    let hasDefinedValue = false;
+    if ($isArray(items)) {
+      for (let j = 0; j < items.length; j++) {
+        if (typeof items[j][column] !== "undefined") {
+          hasDefinedValue = true;
+          break;
+        }
+      }
+    } else {
+      hasDefinedValue = typeof items[column] !== "undefined";
+    }
+
+    if (hasDefinedValue) {
+      if (definedColumns.length > 0) columnsSql += ", ";
+      columnsSql += escapeIdentifier(column as string);
+      definedColumns.push(column);
+    }
+  }
+
+  columnsSql += ") VALUES";
+  return { definedColumns, columnsSql };
+}
+
 const SQLITE_MEMORY = ":memory:";
 const SQLITE_MEMORY_VARIANTS: string[] = [":memory:", "sqlite://:memory:", "sqlite:memory"];

@@ -911,6 +952,7 @@ export default {
   assertIsOptionsOfAdapter,
   parseOptions,
   SQLHelper,
+  buildDefinedColumnsAndQuery,
   normalizeSSLMode,
   SQLResultArray,
   SQLArrayParameter,
diff --git a/src/js/internal/sql/sqlite.ts b/src/js/internal/sql/sqlite.ts
index 98999489083..235f78a1214 100644
--- a/src/js/internal/sql/sqlite.ts
+++ b/src/js/internal/sql/sqlite.ts
@@ -2,7 +2,7 @@
 import type * as BunSQLiteModule from "bun:sqlite";
 import type { BaseQueryHandle, Query, SQLQueryResultMode } from "./query";
 import type { ArrayType, DatabaseAdapter, OnConnected, SQLArrayParameter, SQLHelper, SQLResultArray } from "./shared";

-const { SQLHelper, SQLResultArray } = require("internal/sql/shared");
+const { SQLHelper, SQLResultArray, buildDefinedColumnsAndQuery } = require("internal/sql/shared");
 const {
   Query,
   SQLQueryResultMode,
@@ -433,30 +433,33 @@ class SQLiteAdapter implements DatabaseAdapter<BunSQLiteModule.Database, BunSQLi
               // insert into users ${sql(users)} or insert into users ${sql(user)}
               //

-              query += "(";
-              for (let j = 0; j < columnCount; j++) {
-                query += this.escapeIdentifier(columns[j]);
-                if (j < lastColumnIndex) {
-                  query += ", ";
-                }
+              // Build column list while determining which columns have at least one defined value
+              const { definedColumns, columnsSql } = buildDefinedColumnsAndQuery(
+                columns,
+                items,
+                this.escapeIdentifier.bind(this),
+              );
+
+              const definedColumnCount = definedColumns.length;
+              if (definedColumnCount === 0) {
+                throw new SyntaxError("Insert needs to have at least one column with a defined value");
               }
-              query += ") VALUES";
+              const lastDefinedColumnIndex = definedColumnCount - 1;
+
+              query += columnsSql;
               if ($isArray(items)) {
                 const itemsCount = items.length;
                 const lastItemIndex = itemsCount - 1;
                 for (let j = 0; j < itemsCount; j++) {
                   query += "(";
                   const item = items[j];
-                  for (let k = 0; k < columnCount; k++) {
-                    const column = columns[k];
+                  for (let k = 0; k < definedColumnCount; k++) {
+                    const column = definedColumns[k];
                     const columnValue = item[column];
                     // SQLite uses ? for placeholders, not $1, $2, etc.
-                    query += `?${k < lastColumnIndex ? ", " : ""}`;
-                    if (typeof columnValue === "undefined") {
-                      binding_values.push(null);
-                    } else {
-                      binding_values.push(columnValue);
-                    }
+                    query += `?${k < lastDefinedColumnIndex ? ", " : ""}`;
+                    // If this item has undefined for a column that other items defined, use null
+                    binding_values.push(typeof columnValue === "undefined" ? null : columnValue);
                   }
                   if (j < lastItemIndex) {
                     query += "),";
@@ -467,16 +470,12 @@ class SQLiteAdapter implements DatabaseAdapter<BunSQLiteModule.Database, BunSQLi
               } else {
                 query += "(";
                 const item = items;
-                for (let j = 0; j < columnCount; j++) {
-                  const column = columns[j];
+                for (let j = 0; j < definedColumnCount; j++) {
+                  const column = definedColumns[j];
                   const columnValue = item[column];
                   // SQLite uses ? for placeholders
-                  query += `?${j < lastColumnIndex ? ", " : ""}`;
-                  if (typeof columnValue === "undefined") {
-                    binding_values.push(null);
-                  } else {
-                    binding_values.push(columnValue);
-                  }
+                  query += `?${j < lastDefinedColumnIndex ? ", " : ""}`;
+                  binding_values.push(columnValue);
                 }
                 query += ") "; // the user can add RETURNING * or RETURNING id
               }
diff --git a/test/CLAUDE.md b/test/CLAUDE.md
index d92db49229f..763b9d4fb28 100644
--- a/test/CLAUDE.md
+++ b/test/CLAUDE.md
@@ -107,7 +107,7 @@ When callbacks must be used and it's just a single callback, use `Promise.withR

 ```ts
 const ws = new WebSocket("ws://localhost:8080");
-const { promise, resolve, reject } = Promise.withResolvers();
+const { promise, resolve, reject } = Promise.withResolvers<void>(); // Can specify any type here for resolution value
 ws.onopen = resolve;
 ws.onclose = reject;
 await promise;
@@ -153,6 +153,33 @@ To create a repetitive string, use `Buffer.alloc(count, fill).toString()` inste
 - Unit tests for specific features are organized by module (e.g., `/test/js/bun/`, `/test/js/node/`)
 - Integration tests are in `/test/integration/`

+### Nested/complex object equality
+
+Prefer usage of `.toEqual` rather than many `.toBe` assertions for nested or complex objects.
+
+<example>
+
+BAD (try to avoid doing this):
+
+```ts
+expect(result).toHaveLength(3);
+expect(result[0].optional).toBe(null);
+expect(result[1].optional).toBe("middle-value"); // CRITICAL: middle item's value must be preserved
+expect(result[2].optional).toBe(null);
+```
+
+**GOOD (always prefer this):**
+
+```ts
+expect(result).toEqual([
+  { optional: null },
+  { optional: "middle-value" }, // CRITICAL: middle item's value must be preserved
+  { optional: null },
+]);
+```
+
+</example>
+
 ### Common Imports from `harness`

 ```ts
PATCH_EOF

# Apply the patch
git apply /tmp/fix.patch || true

# Now append the test file (it's a new file, not in the patch)
mkdir -p test/js/sql
cat > test/js/sql/undefined-filter-regression.test.ts << 'TESTFILE_EOF'
import { test, expect } from "bun:test";
import { sql } from "bun";

test("insert helper filters out undefined values", async () => {
  const db = sql({
    url: ":memory:",
    adapter: "sqlite",
  });

  await db`CREATE TABLE insert_undefined_test (id INTEGER PRIMARY KEY, name TEXT NOT NULL, optional TEXT)`;

  // Insert with undefined value - should only include defined columns
  await db`INSERT INTO insert_undefined_test ${db({ id: 1, name: "test", optional: undefined })}`;

  const result = await db`SELECT * FROM insert_undefined_test WHERE id = 1`;
  expect(result).toHaveLength(1);
  expect(result[0].id).toBe(1);
  expect(result[0].name).toBe("test");
  expect(result[0].optional).toBe(null); // SQLite default

  // Insert with all defined values - should work normally
  await db`INSERT INTO insert_undefined_test ${db({ id: 2, name: "test2", optional: "value" })}`;
  const result2 = await db`SELECT * FROM insert_undefined_test WHERE id = 2`;
  expect(result2[0].optional).toBe("value");

  // Bulk insert with undefined values
  await db`INSERT INTO insert_undefined_test ${db([
    { id: 3, name: "bulk1", optional: undefined },
    { id: 4, name: "bulk2", optional: undefined },
  ])}`;
  const result3 = await db`SELECT * FROM insert_undefined_test WHERE id IN (3, 4) ORDER BY id`;
  expect(result3).toHaveLength(2);
  expect(result3[0].name).toBe("bulk1");
  expect(result3[1].name).toBe("bulk2");

  // DATA LOSS TEST: Bulk insert where first item has undefined but later item has value
  // Previously this would silently lose "has-value" because columns were determined from first item only
  await db`INSERT INTO insert_undefined_test ${db([
    { id: 5, name: "mixed1", optional: undefined },
    { id: 6, name: "mixed2", optional: "has-value" },
  ])}`;
  const result4 = await db`SELECT * FROM insert_undefined_test WHERE id IN (5, 6) ORDER BY id`;
  expect(result4).toHaveLength(2);
  expect(result4[0].name).toBe("mixed1");
  expect(result4[0].optional).toBe(null); // first item's undefined becomes null
  expect(result4[1].name).toBe("mixed2");
  expect(result4[1].optional).toBe("has-value"); // CRITICAL: this value must be preserved, not lost!

  // Bulk insert with mixed undefined patterns - reverse order (first has value, second undefined)
  await db`INSERT INTO insert_undefined_test ${db([
    { id: 7, name: "mixed3", optional: "first-has-value" },
    { id: 8, name: "mixed4", optional: undefined },
  ])}`;
  const result5 = await db`SELECT * FROM insert_undefined_test WHERE id IN (7, 8) ORDER BY id`;
  expect(result5).toHaveLength(2);
  expect(result5[0].optional).toBe("first-has-value");
  expect(result5[1].optional).toBe(null); // second item's undefined becomes null

  // DATA LOSS TEST: Bulk insert with 3+ items where only middle item has value
  // Ensures we check ALL items, not just first or last
  await db`INSERT INTO insert_undefined_test ${db([
    { id: 9, name: "three1", optional: undefined },
    { id: 10, name: "three2", optional: "middle-value" },
    { id: 11, name: "three3", optional: undefined },
  ])}`;
  const result6 = await db`SELECT * FROM insert_undefined_test WHERE id IN (9, 10, 11) ORDER BY id`;
  expect(result6).toHaveLength(3);
  expect(result6[0].optional).toBe(null);
  expect(result6[1].optional).toBe("middle-value"); // CRITICAL: middle item's value must be preserved
  expect(result6[2].optional).toBe(null);

  await db.close();
});

// Exact regression test for https://github.com/oven-sh/bun/issues/25829
// undefined values should be filtered out, allowing NOT NULL columns with DEFAULT to use their default
test("insert with undefined on NOT NULL column with DEFAULT uses default value", async () => {
  const db = sql({
    url: ":memory:",
    adapter: "sqlite",
  });

  await db`CREATE TABLE issue_25829 (id TEXT PRIMARY KEY, foo TEXT NOT NULL DEFAULT 'default-foo')`;

  // This should work - foo:undefined should be filtered out, and DEFAULT should be used
  await db`INSERT INTO issue_25829 ${db({
    foo: undefined,
    id: "test-id",
  })}`;

  const result = await db`SELECT * FROM issue_25829 WHERE id = 'test-id'`;
  expect(result).toEqual([{ id: "test-id", foo: "default-foo" }]);

  await db.close();
});
TESTFILE_EOF

echo "Fix applied successfully"
