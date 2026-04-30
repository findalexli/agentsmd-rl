#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'Import any driver-specific types you need directly from' packages/data-table-mysql/README.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/data-table-mysql/README.md b/packages/data-table-mysql/README.md
index 45ab6d75ffe..0f43a4b00b5 100644
--- a/packages/data-table-mysql/README.md
+++ b/packages/data-table-mysql/README.md
@@ -5,7 +5,7 @@ Use this package when you want `data-table` APIs backed by `mysql2`.

 ## Features

-- **Native `mysql2` Integration**: Works with `mysql2/promise` connection pools
+- **Native `mysql2` Integration**: Works with `mysql2/promise` `Pool` and `PoolConnection` instances
 - **Full `data-table` API Support**: Queries, relations, writes, and transactions
 - **Adapter-Owned Compiler**: SQL compilation lives in this adapter, with optional shared pure helpers from `data-table`
 - **Migration DDL Support**: Compiles and executes `DataMigrationOperation` operations for `remix/data-table/migrations`
@@ -34,6 +34,7 @@ let db = createDatabase(createMysqlDatabaseAdapter(pool))
 ```

 Use `db.query(...)`, relation loading, and transactions from `remix/data-table`.
+Import any driver-specific types you need directly from `mysql2/promise`.

 ## Adapter Capabilities

diff --git a/packages/data-table-mysql/src/index.ts b/packages/data-table-mysql/src/index.ts
index ffe281fba5f..2c17fac02cf 100644
--- a/packages/data-table-mysql/src/index.ts
+++ b/packages/data-table-mysql/src/index.ts
@@ -1,9 +1,2 @@
-export type {
-  MysqlDatabaseAdapterOptions,
-  MysqlDatabaseConnection,
-  MysqlDatabasePool,
-  MysqlQueryResponse,
-  MysqlQueryResultHeader,
-  MysqlQueryRows,
-} from './lib/adapter.ts'
+export type { MysqlDatabaseAdapterOptions } from './lib/adapter.ts'
 export { createMysqlDatabaseAdapter, MysqlDatabaseAdapter } from './lib/adapter.ts'
diff --git a/packages/data-table-mysql/src/lib/adapter.ts b/packages/data-table-mysql/src/lib/adapter.ts
index bd0fff75053..10d8cacda29 100644
--- a/packages/data-table-mysql/src/lib/adapter.ts
+++ b/packages/data-table-mysql/src/lib/adapter.ts
@@ -19,46 +19,16 @@ import {
   quoteLiteral as quoteLiteralHelper,
   quoteTableRef as quoteTableRefHelper,
 } from '@remix-run/data-table/sql-helpers'
+import type {
+  Connection as MysqlConnection,
+  Pool as MysqlPool,
+  PoolConnection as MysqlPoolConnection,
+  ResultSetHeader,
+  RowDataPacket,
+} from 'mysql2/promise'

 import { compileMysqlOperation } from './sql-compiler.ts'

-/**
- * Row-array response shape for mysql query calls.
- */
-export type MysqlQueryRows = Record<string, unknown>[]
-
-/**
- * Metadata shape for mysql write results.
- */
-export type MysqlQueryResultHeader = {
-  affectedRows: number
-  insertId: unknown
-}
-
-/**
- * Supported mysql `query()` response tuple.
- */
-export type MysqlQueryResponse = [result: unknown, fields?: unknown]
-
-/**
- * Single mysql connection contract used by this adapter.
- */
-export type MysqlDatabaseConnection = {
-  query(text: string, values?: unknown[]): Promise<MysqlQueryResponse>
-  beginTransaction(): Promise<void>
-  commit(): Promise<void>
-  rollback(): Promise<void>
-  release?: () => void
-}
-
-/**
- * Mysql pool contract used by this adapter.
- */
-export type MysqlDatabasePool = {
-  query(text: string, values?: unknown[]): Promise<MysqlQueryResponse>
-  getConnection(): Promise<MysqlDatabaseConnection>
-}
-
 /**
  * Mysql adapter configuration.
  */
@@ -67,11 +37,17 @@ export type MysqlDatabaseAdapterOptions = {
 }

 type TransactionState = {
-  connection: MysqlDatabaseConnection
+  connection: MysqlTransactionConnection
   releaseOnClose: boolean
 }

-type MysqlQueryable = MysqlDatabasePool | MysqlDatabaseConnection
+type MysqlQueryRows = RowDataPacket[]
+type MysqlQueryResultHeader = {
+  affectedRows: number
+  insertId: unknown
+}
+type MysqlTransactionConnection = MysqlConnection | MysqlPoolConnection
+type MysqlQueryable = MysqlPool | MysqlTransactionConnection

 /**
  * `DatabaseAdapter` implementation for mysql-compatible clients.
@@ -227,7 +203,7 @@ export class MysqlDatabaseAdapter implements DatabaseAdapter {
    */
   async beginTransaction(options?: TransactionOptions): Promise<TransactionToken> {
     let releaseOnClose = false
-    let connection: MysqlDatabaseConnection
+    let connection: MysqlTransactionConnection

     if (isMysqlPool(this.#client)) {
       connection = await this.#client.getConnection()
@@ -276,8 +252,8 @@ export class MysqlDatabaseAdapter implements DatabaseAdapter {
     } finally {
       this.#transactions.delete(token.id)

-      if (transaction.releaseOnClose) {
-        transaction.connection.release?.()
+      if (transaction.releaseOnClose && isMysqlPoolConnection(transaction.connection)) {
+        transaction.connection.release()
       }
     }
   }
@@ -299,8 +275,8 @@ export class MysqlDatabaseAdapter implements DatabaseAdapter {
     } finally {
       this.#transactions.delete(token.id)

-      if (transaction.releaseOnClose) {
-        transaction.connection.release?.()
+      if (transaction.releaseOnClose && isMysqlPoolConnection(transaction.connection)) {
+        transaction.connection.release()
       }
     }
   }
@@ -354,7 +330,7 @@ export class MysqlDatabaseAdapter implements DatabaseAdapter {
     await this.#client.query('select release_lock(?)', ['data_table_migrations'])
   }

-  #resolveClient(token: TransactionToken | undefined): MysqlDatabaseConnection | MysqlDatabasePool {
+  #resolveClient(token: TransactionToken | undefined): MysqlQueryable {
     if (!token) {
       return this.#client
     }
@@ -362,7 +338,7 @@ export class MysqlDatabaseAdapter implements DatabaseAdapter {
     return this.#transactionConnection(token)
   }

-  #transactionConnection(token: TransactionToken): MysqlDatabaseConnection {
+  #transactionConnection(token: TransactionToken): MysqlTransactionConnection {
     let transaction = this.#transactions.get(token.id)

     if (!transaction) {
@@ -396,8 +372,14 @@ export function createMysqlDatabaseAdapter(
   return new MysqlDatabaseAdapter(client, options)
 }

-function isMysqlPool(client: MysqlQueryable): client is MysqlDatabasePool {
-  return typeof (client as MysqlDatabasePool).getConnection === 'function'
+function isMysqlPool(client: MysqlQueryable): client is MysqlPool {
+  return 'getConnection' in client && typeof client.getConnection === 'function'
+}
+
+function isMysqlPoolConnection(
+  connection: MysqlTransactionConnection,
+): connection is MysqlPoolConnection {
+  return 'release' in connection && typeof connection.release === 'function'
 }

 function isRowsResult(result: unknown): result is MysqlQueryRows {
@@ -430,7 +412,7 @@ function normalizeRows(rows: MysqlQueryRows): Record<string, unknown>[] {

 function normalizeHeader(result: unknown): MysqlQueryResultHeader {
   if (typeof result === 'object' && result !== null) {
-    let header = result as { affectedRows?: unknown; insertId?: unknown }
+    let header = result as Partial<ResultSetHeader>

     return {
       affectedRows: typeof header.affectedRows === 'number' ? header.affectedRows : 0,
diff --git a/packages/data-table-postgres/README.md b/packages/data-table-postgres/README.md
index 6e05ef2897e..911f1149d26 100644
--- a/packages/data-table-postgres/README.md
+++ b/packages/data-table-postgres/README.md
@@ -5,7 +5,7 @@ Use this package when you want `data-table` APIs backed by `pg`.

 ## Features

-- **Native `pg` Integration**: Works with `Pool` and Postgres connection strings
+- **Native `pg` Integration**: Works with `pg` `Pool` and `PoolClient` instances
 - **Full `data-table` API Support**: Queries, relations, writes, and transactions
 - **Adapter-Owned Compiler**: SQL compilation lives in this adapter, with optional shared pure helpers from `data-table`
 - **Migration DDL Support**: Compiles and executes `DataMigrationOperation` operations for `remix/data-table/migrations`
@@ -37,6 +37,7 @@ let db = createDatabase(createPostgresDatabaseAdapter(pool))
 ```

 Use `db.query(...)`, relation loading, and transactions from `remix/data-table`.
+Import any driver-specific types you need directly from `pg`.

 ## Adapter Capabilities

diff --git a/packages/data-table-postgres/src/index.ts b/packages/data-table-postgres/src/index.ts
index 7992f2d15c9..78fb1214cc3 100644
--- a/packages/data-table-postgres/src/index.ts
+++ b/packages/data-table-postgres/src/index.ts
@@ -1,8 +1,2 @@
-export type {
-  PostgresDatabaseAdapterOptions,
-  PostgresDatabaseClient,
-  PostgresDatabasePool,
-  PostgresQueryResult,
-  PostgresTransactionClient,
-} from './lib/adapter.ts'
+export type { PostgresDatabaseAdapterOptions } from './lib/adapter.ts'
 export { createPostgresDatabaseAdapter, PostgresDatabaseAdapter } from './lib/adapter.ts'
diff --git a/packages/data-table-postgres/src/lib/adapter.ts b/packages/data-table-postgres/src/lib/adapter.ts
index d1656385608..4336731f3c5 100644
--- a/packages/data-table-postgres/src/lib/adapter.ts
+++ b/packages/data-table-postgres/src/lib/adapter.ts
@@ -19,46 +19,10 @@ import {
   quoteLiteral as quoteLiteralHelper,
   quoteTableRef as quoteTableRefHelper,
 } from '@remix-run/data-table/sql-helpers'
+import type { Pool as PostgresPool, PoolClient as PostgresPoolClient } from 'pg'

 import { compilePostgresOperation } from './sql-compiler.ts'

-type Pretty<value> = {
-  [key in keyof value]: value[key]
-} & {}
-
-/**
- * Result shape returned by postgres client `query()` calls.
- */
-export type PostgresQueryResult = {
-  rows: unknown[]
-  rowCount: number | null
-}
-
-/**
- * Minimal postgres client contract used by this adapter.
- */
-export type PostgresDatabaseClient = {
-  query(text: string, values?: unknown[]): Promise<PostgresQueryResult>
-}
-
-/**
- * Postgres transaction client with optional connection release support.
- */
-export type PostgresTransactionClient = Pretty<
-  PostgresDatabaseClient & {
-    release?: () => void
-  }
->
-
-/**
- * Postgres pool-like client contract used by this adapter.
- */
-export type PostgresDatabasePool = Pretty<
-  PostgresDatabaseClient & {
-    connect?: () => Promise<PostgresTransactionClient>
-  }
->
-
 /**
  * Postgres adapter configuration.
  */
@@ -67,10 +31,12 @@ export type PostgresDatabaseAdapterOptions = {
 }

 type TransactionState = {
-  client: PostgresTransactionClient
+  client: PostgresPoolClient
   releaseOnClose: boolean
 }

+type PostgresQueryable = PostgresPool | PostgresPoolClient
+
 /**
  * `DatabaseAdapter` implementation for postgres-compatible clients.
  */
@@ -85,11 +51,11 @@ export class PostgresDatabaseAdapter implements DatabaseAdapter {
    */
   capabilities

-  #client: PostgresDatabasePool
+  #client: PostgresQueryable
   #transactions = new Map<string, TransactionState>()
   #transactionCounter = 0

-  constructor(client: PostgresDatabasePool, options?: PostgresDatabaseAdapterOptions) {
+  constructor(client: PostgresQueryable, options?: PostgresDatabaseAdapterOptions) {
     this.#client = client
     this.capabilities = {
       returning: options?.capabilities?.returning ?? true,
@@ -205,9 +171,9 @@ export class PostgresDatabaseAdapter implements DatabaseAdapter {
    */
   async beginTransaction(options?: TransactionOptions): Promise<TransactionToken> {
     let releaseOnClose = false
-    let transactionClient: PostgresTransactionClient
+    let transactionClient: PostgresPoolClient

-    if (this.#client.connect) {
+    if (isPostgresPool(this.#client)) {
       transactionClient = await this.#client.connect()
       releaseOnClose = true
     } else {
@@ -249,7 +215,7 @@ export class PostgresDatabaseAdapter implements DatabaseAdapter {
       this.#transactions.delete(token.id)

       if (transaction.releaseOnClose) {
-        transaction.client.release?.()
+        releasePostgresClient(transaction.client)
       }
     }
   }
@@ -272,7 +238,7 @@ export class PostgresDatabaseAdapter implements DatabaseAdapter {
       this.#transactions.delete(token.id)

       if (transaction.releaseOnClose) {
-        transaction.client.release?.()
+        releasePostgresClient(transaction.client)
       }
     }
   }
@@ -326,7 +292,7 @@ export class PostgresDatabaseAdapter implements DatabaseAdapter {
     await this.#client.query('select pg_advisory_unlock(hashtext($1))', ['data_table_migrations'])
   }

-  #resolveClient(token: TransactionToken | undefined): PostgresDatabaseClient {
+  #resolveClient(token: TransactionToken | undefined): PostgresQueryable {
     if (!token) {
       return this.#client
     }
@@ -334,7 +300,7 @@ export class PostgresDatabaseAdapter implements DatabaseAdapter {
     return this.#transactionClient(token)
   }

-  #transactionClient(token: TransactionToken): PostgresTransactionClient {
+  #transactionClient(token: TransactionToken): PostgresPoolClient {
     let transaction = this.#transactions.get(token.id)

     if (!transaction) {
@@ -347,7 +313,7 @@ export class PostgresDatabaseAdapter implements DatabaseAdapter {

 /**
  * Creates a postgres `DatabaseAdapter`.
- * @param client Postgres pool or client.
+ * @param client `pg` pool or pool client.
  * @param options Optional adapter capability overrides.
  * @returns A configured postgres adapter.
  * @example
@@ -362,12 +328,21 @@ export class PostgresDatabaseAdapter implements DatabaseAdapter {
  * ```
  */
 export function createPostgresDatabaseAdapter(
-  client: PostgresDatabasePool,
+  client: PostgresQueryable,
   options?: PostgresDatabaseAdapterOptions,
 ): PostgresDatabaseAdapter {
   return new PostgresDatabaseAdapter(client, options)
 }

+function isPostgresPool(client: PostgresQueryable): client is PostgresPool {
+  return 'connect' in client && typeof client.connect === 'function'
+}
+
+function releasePostgresClient(client: PostgresPoolClient): void {
+  let release = (client as { release?: () => void }).release
+  release?.()
+}
+
 function buildSetTransactionStatement(options: TransactionOptions): string {
   let parts = ['set transaction']

diff --git a/packages/data-table-sqlite/README.md b/packages/data-table-sqlite/README.md
index 0e5e6fa4bd5..dfbce75f458 100644
--- a/packages/data-table-sqlite/README.md
+++ b/packages/data-table-sqlite/README.md
@@ -34,6 +34,7 @@ let db = createDatabase(createSqliteDatabaseAdapter(sqlite))
 ```

 This is a good fit for local development, embedded deployments, and single-node services.
+Import any driver-specific types you need directly from `better-sqlite3`.

 ## Adapter Capabilities

diff --git a/packages/data-table-sqlite/src/index.ts b/packages/data-table-sqlite/src/index.ts
index 0c20ad8525b..e1ffa13d6c5 100644
--- a/packages/data-table-sqlite/src/index.ts
+++ b/packages/data-table-sqlite/src/index.ts
@@ -1,2 +1,2 @@
-export type { SqliteDatabaseAdapterOptions, SqliteDatabaseConnection } from './lib/adapter.ts'
+export type { SqliteDatabaseAdapterOptions } from './lib/adapter.ts'
 export { createSqliteDatabaseAdapter, SqliteDatabaseAdapter } from './lib/adapter.ts'
diff --git a/packages/data-table-sqlite/src/lib/adapter.ts b/packages/data-table-sqlite/src/lib/adapter.ts
index 695b23c5b98..1c4a7dd82b3 100644
--- a/packages/data-table-sqlite/src/lib/adapter.ts
+++ b/packages/data-table-sqlite/src/lib/adapter.ts
@@ -23,11 +23,6 @@ import type { Database as BetterSqliteDatabase, RunResult } from 'better-sqlite3

 import { compileSqliteOperation } from './sql-compiler.ts'

-/**
- * Better SQLite3 database handle accepted by the sqlite adapter.
- */
-export type SqliteDatabaseConnection = BetterSqliteDatabase
-
 /**
  * Sqlite adapter configuration.
  */
@@ -49,11 +44,11 @@ export class SqliteDatabaseAdapter implements DatabaseAdapter {
    */
   capabilities

-  #database: SqliteDatabaseConnection
+  #database: BetterSqliteDatabase
   #transactions = new Set<string>()
   #transactionCounter = 0

-  constructor(database: SqliteDatabaseConnection, options?: SqliteDatabaseAdapterOptions) {
+  constructor(database: BetterSqliteDatabase, options?: SqliteDatabaseAdapterOptions) {
     this.#database = database
     this.capabilities = {
       returning: options?.capabilities?.returning ?? true,
@@ -279,7 +274,7 @@ export class SqliteDatabaseAdapter implements DatabaseAdapter {
  * ```
  */
 export function createSqliteDatabaseAdapter(
-  database: SqliteDatabaseConnection,
+  database: BetterSqliteDatabase,
   options?: SqliteDatabaseAdapterOptions,
 ): SqliteDatabaseAdapter {
   return new SqliteDatabaseAdapter(database, options)

PATCH

echo "Patch applied successfully."
