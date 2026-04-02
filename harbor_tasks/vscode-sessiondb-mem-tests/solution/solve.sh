: true
#!/bin/bash
set -euo pipefail

# Idempotent fix: Make SessionDatabase testable for :memory: databases
# This exports runMigrations and makes protected members accessible for subclassing

# Check if already applied - check for 'export' on runMigrations
if grep -q "export async function runMigrations" src/vs/platform/agentHost/node/sessionDatabase.ts 2>/dev/null; then
    echo "Fix already applied, skipping..."
    exit 0
fi

# Apply the patch
git apply - <<'PATCH'
diff --git a/src/vs/platform/agentHost/node/sessionDatabase.ts b/src/vs/platform/agentHost/node/sessionDatabase.ts
index 7f960f89d2a67..8c9e51c106d09 100644
--- a/src/vs/platform/agentHost/node/sessionDatabase.ts
+++ b/src/vs/platform/agentHost/node/sessionDatabase.ts
@@ -112,7 +112,7 @@ function dbOpen(path: string): Promise<Database> {
  * `PRAGMA user_version` are run inside a serialized transaction. After all
  * migrations complete the pragma is updated to the highest applied version.
  */
-async function runMigrations(db: Database, migrations: readonly ISessionDatabaseMigration[]): Promise<void> {
+export async function runMigrations(db: Database, migrations: readonly ISessionDatabaseMigration[]): Promise<void> {
 	// Enable foreign key enforcement — must be set outside a transaction
 	// and every time a connection is opened.
 	await dbExec(db, 'PRAGMA foreign_keys = ON');
@@ -154,8 +154,8 @@ async function runMigrations(db: Database, migrations: readonly ISessionDatabaseM
  */
 export class SessionDatabase implements ISessionDatabase {

-	private _dbPromise: Promise<Database> | undefined;
-	private _closed: Promise<void> | true | undefined;
+	protected _dbPromise: Promise<Database> | undefined;
+	protected _closed: Promise<void> | true | undefined;
 	private readonly _fileEditSequencer = new SequencerByKey<string>();

 	constructor(
@@ -174,7 +174,7 @@ export class SessionDatabase implements ISessionDatabase {
 		return inst;
 	}

-	private _ensureDb(): Promise<Database> {
+	protected _ensureDb(): Promise<Database> {
 		if (this._closed) {
 			return Promise.reject(new Error('SessionDatabase has been disposed'));
 		}
PATCH

echo "Fix applied successfully"
