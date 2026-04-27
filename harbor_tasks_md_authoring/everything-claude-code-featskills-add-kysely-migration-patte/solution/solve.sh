#!/usr/bin/env bash
set -euo pipefail

cd /workspace/everything-claude-code

# Idempotency guard
if grep -qF "description: Database migration best practices for schema changes, data migratio" "skills/database-migrations/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/database-migrations/SKILL.md b/skills/database-migrations/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: database-migrations
-description: Database migration best practices for schema changes, data migrations, rollbacks, and zero-downtime deployments across PostgreSQL, MySQL, and common ORMs (Prisma, Drizzle, Django, TypeORM, golang-migrate).
+description: Database migration best practices for schema changes, data migrations, rollbacks, and zero-downtime deployments across PostgreSQL, MySQL, and common ORMs (Prisma, Drizzle, Kysely, Django, TypeORM, golang-migrate).
 origin: ECC
 ---
 
@@ -204,6 +204,100 @@ export const users = pgTable("users", {
 });
 ```
 
+## Kysely (TypeScript/Node.js)
+
+### Workflow (kysely-ctl)
+
+```bash
+# Initialize config file (kysely.config.ts)
+kysely init
+
+# Create a new migration file
+kysely migrate make add_user_avatar
+
+# Apply all pending migrations
+kysely migrate latest
+
+# Rollback last migration
+kysely migrate down
+
+# Show migration status
+kysely migrate list
+```
+
+### Migration File
+
+```typescript
+// migrations/2024_01_15_001_create_user_profile.ts
+import { type Kysely, sql } from 'kysely'
+
+// IMPORTANT: Always use Kysely<any>, not your typed DB interface.
+// Migrations are frozen in time and must not depend on current schema types.
+export async function up(db: Kysely<any>): Promise<void> {
+  await db.schema
+    .createTable('user_profile')
+    .addColumn('id', 'serial', (col) => col.primaryKey())
+    .addColumn('email', 'varchar(255)', (col) => col.notNull().unique())
+    .addColumn('avatar_url', 'text')
+    .addColumn('created_at', 'timestamp', (col) =>
+      col.defaultTo(sql`now()`).notNull()
+    )
+    .execute()
+
+  await db.schema
+    .createIndex('idx_user_profile_avatar')
+    .on('user_profile')
+    .column('avatar_url')
+    .execute()
+}
+
+export async function down(db: Kysely<any>): Promise<void> {
+  await db.schema.dropTable('user_profile').execute()
+}
+```
+
+### Programmatic Migrator
+
+```typescript
+import { Migrator, FileMigrationProvider } from 'kysely'
+import { promises as fs } from 'fs'
+import * as path from 'path'
+// ESM only — CJS can use __dirname directly
+import { fileURLToPath } from 'url'
+const migrationFolder = path.join(
+  path.dirname(fileURLToPath(import.meta.url)),
+  './migrations',
+)
+
+// `db` is your Kysely<any> database instance
+const migrator = new Migrator({
+  db,
+  provider: new FileMigrationProvider({
+    fs,
+    path,
+    migrationFolder,
+  }),
+  // WARNING: Only enable in development. Disables timestamp-ordering
+  // validation, which can cause schema drift between environments.
+  // allowUnorderedMigrations: true,
+})
+
+const { error, results } = await migrator.migrateToLatest()
+
+results?.forEach((it) => {
+  if (it.status === 'Success') {
+    console.log(`migration "${it.migrationName}" executed successfully`)
+  } else if (it.status === 'Error') {
+    console.error(`failed to execute migration "${it.migrationName}"`)
+  }
+})
+
+if (error) {
+  console.error('migration failed', error)
+  process.exit(1)
+}
+```
+
 ## Django (Python)
 
 ### Workflow
PATCH

echo "Gold patch applied."
