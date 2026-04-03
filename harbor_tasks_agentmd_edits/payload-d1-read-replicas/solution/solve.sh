#!/usr/bin/env bash
set -euo pipefail

cd /workspace/payload

# Idempotent: skip if already applied
if grep -q "readReplicas" packages/db-d1-sqlite/src/types.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/docs/database/sqlite.mdx b/docs/database/sqlite.mdx
index dd93e1c59c9..ef0b171a1b9 100644
--- a/docs/database/sqlite.mdx
+++ b/docs/database/sqlite.mdx
@@ -310,3 +310,29 @@ export default buildConfig({
 It inherits the options from the SQLite adapter above with the exception of the connection options in favour of the `binding`.

 You can see our [Cloudflare D1 template](https://github.com/payloadcms/payload/tree/main/templates/with-cloudflare-d1) for a full example of how to set this up.
+
+### D1 Read Replicas
+
+You can enable read replicas support with the `first-primary` strategy. This is experimental.
+
+You must also enable it on your D1 database in the Cloudflare dashboard. Read more about it in the [Cloudflare documentation](https://developers.cloudflare.com/d1/best-practices/read-replication/).
+
+<Banner type="info">
+  All write queries are still forwarded to the primary database instance. Read
+  replication only improves the response time for read query requests.
+</Banner>
+
+```ts
+import { sqliteD1Adapter } from '@payloadcms/db-d1-sqlite'
+
+export default buildConfig({
+  collections: [],
+  db: sqliteD1Adapter({
+    binding: cloudflare.env.D1,
+    // You can also enable read replicas support with the `first-primary` strategy.
+    readReplicas: 'first-primary',
+  }),
+})
+```
+
+You can then verify that they're being used by checking the logs in your Cloudflare dashboard. You should see logs indicating whether a read or write operation was performed, and on which database instance.
diff --git a/packages/db-d1-sqlite/src/connect.ts b/packages/db-d1-sqlite/src/connect.ts
index b8f081d708a..753b075a97c 100644
--- a/packages/db-d1-sqlite/src/connect.ts
+++ b/packages/db-d1-sqlite/src/connect.ts
@@ -21,8 +21,20 @@ export const connect: Connect = async function connect(

   try {
     const logger = this.logger || false
+    const readReplicas = this.readReplicas
+
+    let binding = this.binding
+
+    if (readReplicas && readReplicas === 'first-primary') {
+      // @ts-expect-error - need to have types that support withSession binding from D1
+      binding = this.binding.withSession('first-primary')
+    }
+
+    this.drizzle = drizzle(binding, {
+      logger,
+      schema: this.schema,
+    })

-    this.drizzle = drizzle(this.binding, { logger, schema: this.schema })
     this.client = this.drizzle.$client as any

     if (!hotReload) {
diff --git a/packages/db-d1-sqlite/src/index.ts b/packages/db-d1-sqlite/src/index.ts
index fb74c0e0abc..98b601eff1c 100644
--- a/packages/db-d1-sqlite/src/index.ts
+++ b/packages/db-d1-sqlite/src/index.ts
@@ -117,6 +117,7 @@ export function sqliteD1Adapter(args: Args): DatabaseAdapterObj<SQLiteD1Adapter>
       push: args.push,
       rawRelations: {},
       rawTables: {},
+      readReplicas: args.readReplicas,
       relations: {},
       relationshipsSuffix: args.relationshipsSuffix || '_rels',
       schema: {},
diff --git a/packages/db-d1-sqlite/src/types.ts b/packages/db-d1-sqlite/src/types.ts
index f74366fd5d4..c9ab17f2ad3 100644
--- a/packages/db-d1-sqlite/src/types.ts
+++ b/packages/db-d1-sqlite/src/types.ts
@@ -27,6 +27,15 @@ export type SQLiteSchemaHook = (args: SQLiteSchemaHookArgs) => Promise<SQLiteSch

 export type Args = {
   binding: AnyD1Database
+  /**
+   * Experimental. Enables read replicas support with the `first-primary` strategy.
+   *
+   * @experimental
+   * @example
+   *
+   * ```readReplicas: 'first-primary'```
+   */
+  readReplicas?: 'first-primary'
 } & BaseSQLiteArgs

 export type GenericColumns = {
@@ -99,6 +108,14 @@ export type SQLiteD1Adapter = {
   binding: Args['binding']
   client: AnyD1Database
   drizzle: Drizzle
+  /**
+   * Experimental. Enables read replicas support with the `first-primary` strategy.
+   *
+   * @example
+   *
+   * ```readReplicas: 'first-primary'```
+   */
+  readReplicas?: 'first-primary'
 } & BaseSQLiteAdapter &
   SQLiteDrizzleAdapter

diff --git a/templates/with-cloudflare-d1/README.md b/templates/with-cloudflare-d1/README.md
index 2e77914fd6a..3bc4d878e6c 100644
--- a/templates/with-cloudflare-d1/README.md
+++ b/templates/with-cloudflare-d1/README.md
@@ -2,7 +2,7 @@

 [![Deploy to Cloudflare](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=https://github.com/payloadcms/payload/tree/main/templates/with-cloudflare-d1)

-This template comes configured with the bare minimum to get started on anything you need.
+**This can only be deployed on Paid Workers right now due to size limits.** This template comes configured with the bare minimum to get started on anything you need.

 ## Quick start

@@ -48,6 +48,8 @@ Images will be served from an R2 bucket which you can then further configure to

 The Worker will have direct access to a D1 SQLite database which Wrangler can connect locally to, just note that you won't have a connection string as you would typically with other providers.

+You can enable read replicas by adding `readReplicas: 'first-primary'` in the DB adapter and then enabling it on your D1 Cloudflare dashboard. Read more about this feature on [our docs](https://payloadcms.com/docs/database/sqlite#d1-read-replicas).
+
 ## Working with Cloudflare


PATCH

echo "Patch applied successfully."
