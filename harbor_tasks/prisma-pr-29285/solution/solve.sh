#!/bin/bash
set -e

cd /workspace/prisma

# Apply the gold patch
git apply <<'PATCH'
diff --git a/packages/adapter-mariadb/src/mariadb.ts b/packages/adapter-mariadb/src/mariadb.ts
index 92ef04b232a7..7c1f1ac7f194 100644
--- a/packages/adapter-mariadb/src/mariadb.ts
+++ b/packages/adapter-mariadb/src/mariadb.ts
@@ -63,7 +63,8 @@ class MariaDbQueryable<Connection extends mariadb.Pool | mariadb.Connection> imp
         typeCast,
       }
       const values = args.map((arg, i) => mapArg(arg, query.argTypes[i]))
-      return await this.client.query(req, values)
+      // We intentionally use `execute` here, because it uses the binary protocol, unlike `query`.
+      return await this.client.execute(req, values)
     } catch (e) {
       const error = e as Error
       this.onError(error)
@@ -76,9 +77,11 @@ class MariaDbQueryable<Connection extends mariadb.Pool | mariadb.Connection> imp
   }
 }

+// All transaction operations use `client.query` instead of `client.execute` to avoid using the
+// binary protocol, which does not support transactions in the MariaDB driver.
 class MariaDbTransaction extends MariaDbQueryable<mariadb.Connection> implements Transaction {
   constructor(
-    conn: mariadb.Connection,
+    readonly conn: mariadb.Connection,
     readonly options: TransactionOptions,
     readonly cleanup?: () => void,
   ) {
@@ -88,27 +91,39 @@ class MariaDbTransaction extends MariaDbQueryable<mariadb.Connection> implements
   async commit(): Promise<void> {
     debug(`[js::commit]`)

-    this.cleanup?.()
-    await this.client.end()
+    try {
+      await this.client.query({ sql: 'COMMIT' })
+    } catch (err) {
+      this.onError(err)
+    } finally {
+      this.cleanup?.()
+      await this.client.end()
+    }
   }

   async rollback(): Promise<void> {
     debug(`[js::rollback]`)

-    this.cleanup?.()
-    await this.client.end()
+    try {
+      await this.client.query({ sql: 'ROLLBACK' })
+    } catch (err) {
+      this.onError(err)
+    } finally {
+      this.cleanup?.()
+      await this.client.end()
+    }
   }

   async createSavepoint(name: string): Promise<void> {
-    await this.executeRaw({ sql: `SAVEPOINT ${name}`, args: [], argTypes: [] })
+    await this.client.query({ sql: `SAVEPOINT ${name}` }).catch(this.onError.bind(this))
   }

   async rollbackToSavepoint(name: string): Promise<void> {
-    await this.executeRaw({ sql: `ROLLBACK TO ${name}`, args: [], argTypes: [] })
+    await this.client.query({ sql: `ROLLBACK TO ${name}` }).catch(this.onError.bind(this))
   }

   async releaseSavepoint(name: string): Promise<void> {
-    await this.executeRaw({ sql: `RELEASE SAVEPOINT ${name}`, args: [], argTypes: [] })
+    await this.client.query({ sql: `RELEASE SAVEPOINT ${name}` }).catch(this.onError.bind(this))
   }
 }

@@ -143,7 +158,7 @@ export class PrismaMariaDbAdapter extends MariaDbQueryable<mariadb.Pool> impleme

   async startTransaction(isolationLevel?: IsolationLevel): Promise<Transaction> {
     const options: TransactionOptions = {
-      usePhantomQuery: false,
+      usePhantomQuery: true,
     }

     const tag = '[js::startTransaction]'
@@ -169,7 +184,8 @@ export class PrismaMariaDbAdapter extends MariaDbQueryable<mariadb.Pool> impleme
           argTypes: [],
         })
       }
-      await tx.executeRaw({ sql: 'BEGIN', args: [], argTypes: [] })
+      // Uses `query` instead of `execute` to avoid the binary protocol.
+      await tx.conn.query({ sql: 'BEGIN' }).catch(this.onError.bind(this))
       return tx
     } catch (error) {
       await conn.end()
PATCH

# Note: Build is skipped because tests check source code directly, not compiled output
