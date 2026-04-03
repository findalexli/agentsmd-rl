#!/usr/bin/env bash
set -euo pipefail

cd /workspace/Ghost

# Idempotent: skip if already applied
if grep -q 'migrate:create' ghost/core/package.json 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.claude/skills/create-database-migration/SKILL.md b/.claude/skills/create-database-migration/SKILL.md
index ddc2e3a2e87..dd0a404e023 100644
--- a/.claude/skills/create-database-migration/SKILL.md
+++ b/.claude/skills/create-database-migration/SKILL.md
@@ -7,15 +7,14 @@ description: Create a database migration to add a table, add columns to an exist

 ## Instructions

-1. Change directories into `ghost/core`: `cd ghost/core`
-2. Create a new, empty migration file using slimer: `slimer migration <name-of-database-migration>`. IMPORTANT: do not create the migration file manually; always use slimer to create the initial empty migration file.
-3. The above command will create a new directory in `ghost/core/core/server/data/migrations/versions` if needed, and create the empty migration file with the appropriate name.
-4. Update the migration file with the changes you want to make in the database, following the existing patterns in the codebase. Where appropriate, prefer to use the utility functions in `ghost/core/core/server/data/migrations/utils/*`.
-5. Update the schema definition file in `ghost/core/core/server/data/schema/schema.js`, and make sure it aligns with the latest changes from the migration.
-6. Test the migration manually: `yarn knex-migrator migrate --v {version directory} --force`
-7. If adding or dropping a table, update `ghost/core/core/server/data/exporter/table-lists.js` as appropriate.
-8. Run the schema integrity test, and update the hash: `yarn test:single test/unit/server/data/schema/integrity.test.js`
-9. Run unit tests in Ghost core, and iterate until they pass: `cd ghost/core && yarn test:unit`
+1. Create a new, empty migration file: `cd ghost/core && yarn migrate:create <kebab-case-slug>`. IMPORTANT: do not create the migration file manually; always use this script to create the initial empty migration file. The slug must be kebab-case (e.g. `add-column-to-posts`).
+2. The above command will create a new directory in `ghost/core/core/server/data/migrations/versions` if needed, create the empty migration file with the appropriate name, and bump the core and admin package versions to RC if this is the first migration after a release.
+3. Update the migration file with the changes you want to make in the database, following the existing patterns in the codebase. Where appropriate, prefer to use the utility functions in `ghost/core/core/server/data/migrations/utils/*`.
+4. Update the schema definition file in `ghost/core/core/server/data/schema/schema.js`, and make sure it aligns with the latest changes from the migration.
+5. Test the migration manually: `yarn knex-migrator migrate --v {version directory} --force`
+6. If adding or dropping a table, update `ghost/core/core/server/data/exporter/table-lists.js` as appropriate.
+7. Run the schema integrity test, and update the hash: `yarn test:single test/unit/server/data/schema/integrity.test.js`
+8. Run unit tests in Ghost core, and iterate until they pass: `cd ghost/core && yarn test:unit`

 ## Examples
 See [examples.md](examples.md) for example migrations.
diff --git a/ghost/core/bin/create-migration.js b/ghost/core/bin/create-migration.js
new file mode 100644
index 00000000000..a43f17fd660
--- /dev/null
+++ b/ghost/core/bin/create-migration.js
@@ -0,0 +1,128 @@
+#!/usr/bin/env node
+/* eslint-disable no-console, ghost/ghost-custom/no-native-error */
+
+const path = require('path');
+const fs = require('fs');
+const semver = require('semver');
+
+const MIGRATION_TEMPLATE = `const logging = require('@tryghost/logging');
+
+// For DDL - schema changes
+// const {createNonTransactionalMigration} = require('../../utils');
+
+// For DML - data changes
+// const {createTransactionalMigration} = require('../../utils');
+
+// Or use a specific helper
+// const {addTable, createAddColumnMigration} = require('../../utils');
+
+module.exports = /**/;
+`;
+
+const SLUG_PATTERN = /^[a-z0-9]+(-[a-z0-9]+)*$/;
+
+/**
+ * Validates that a slug is kebab-case (lowercase alphanumeric with single hyphens).
+ */
+function isValidSlug(slug) {
+    return typeof slug === 'string' && SLUG_PATTERN.test(slug);
+}
+
+/**
+ * Returns the migration version folder name for the given package version.
+ *
+ * semver.inc(v, 'minor') handles both cases:
+ *   - Stable 6.18.0 → 6.19.0 (increments minor)
+ *   - Prerelease 6.19.0-rc.0 → 6.19.0 (strips prerelease, keeps minor)
+ *
+ * Key invariant: 6.18.0 and 6.19.0-rc.0 both produce folder "6.19".
+ */
+function getNextMigrationVersion(version) {
+    const next = semver.inc(version, 'minor');
+    if (!next) {
+        throw new Error(`Invalid version: ${version}`);
+    }
+    return `${semver.major(next)}.${semver.minor(next)}`;
+}
+
+/**
+ * Creates a migration file and optionally bumps package versions to RC.
+ *
+ * @param {object} options
+ * @param {string} options.slug - The migration name in kebab-case
+ * @param {string} options.coreDir - Path to ghost/core directory
+ * @param {Date}   [options.date] - Override the timestamp (for testing)
+ * @returns {{migrationPath: string, rcVersion: string|null}}
+ */
+function createMigration({slug, coreDir, date}) {
+    if (!isValidSlug(slug)) {
+        throw new Error(`Invalid slug: "${slug}". Use kebab-case (e.g. add-column-to-posts)`);
+    }
+
+    const migrationsDir = path.join(coreDir, 'core', 'server', 'data', 'migrations', 'versions');
+    const corePackagePath = path.join(coreDir, 'package.json');
+
+    const corePackage = JSON.parse(fs.readFileSync(corePackagePath, 'utf8'));
+    const currentVersion = corePackage.version;
+
+    const nextVersion = getNextMigrationVersion(currentVersion);
+    const versionDir = path.join(migrationsDir, nextVersion);
+
+    const timestamp = (date || new Date()).toISOString().slice(0, 19).replace('T', '-').replaceAll(':', '-');
+    const filename = `${timestamp}-${slug}.js`;
+    const migrationPath = path.join(versionDir, filename);
+
+    fs.mkdirSync(versionDir, {recursive: true});
+    try {
+        fs.writeFileSync(migrationPath, MIGRATION_TEMPLATE, {flag: 'wx'});
+    } catch (err) {
+        if (err.code === 'EEXIST') {
+            throw new Error(`Migration already exists: ${migrationPath}`);
+        }
+        throw err;
+    }
+
+    // Auto-bump to RC if this is a stable version
+    let rcVersion = null;
+    if (!semver.prerelease(currentVersion)) {
+        rcVersion = semver.inc(currentVersion, 'preminor', 'rc');
+
+        corePackage.version = rcVersion;
+        fs.writeFileSync(corePackagePath, JSON.stringify(corePackage, null, 2) + '\n');
+
+        const adminPackagePath = path.resolve(coreDir, '..', 'admin', 'package.json');
+        if (fs.existsSync(adminPackagePath)) {
+            const adminPackage = JSON.parse(fs.readFileSync(adminPackagePath, 'utf8'));
+            adminPackage.version = rcVersion;
+            fs.writeFileSync(adminPackagePath, JSON.stringify(adminPackage, null, 2) + '\n');
+        }
+    }
+
+    return {migrationPath, rcVersion};
+}
+
+// CLI entry point
+if (require.main === module) {
+    const slug = process.argv[2];
+
+    if (!slug) {
+        console.error('Usage: yarn migrate:create <slug>');
+        console.error('  slug: kebab-case migration name (e.g. add-column-to-posts)');
+        process.exit(1);
+    }
+
+    try {
+        const coreDir = path.resolve(__dirname, '..');
+        const {migrationPath, rcVersion} = createMigration({slug, coreDir});
+
+        console.log(`Created migration: ${migrationPath}`);
+        if (rcVersion) {
+            console.log(`Bumped version to ${rcVersion}`);
+        }
+    } catch (err) {
+        console.error(err.message);
+        process.exit(1);
+    }
+}
+
+module.exports = {isValidSlug, getNextMigrationVersion, createMigration};
diff --git a/ghost/core/package.json b/ghost/core/package.json
index 4b51b625271..bec5c258e74 100644
--- a/ghost/core/package.json
+++ b/ghost/core/package.json
@@ -25,6 +25,7 @@
     "dev": "node --watch --import=tsx index.js",
     "build:assets": "yarn build:assets:css && yarn build:assets:js",
     "build:assets:js": "node bin/minify-assets.js",
+    "migrate:create": "node bin/create-migration.js",
     "build:assets:css": "postcss core/frontend/public/ghost.css --no-map --use cssnano -o core/frontend/public/ghost.min.css",
     "build:tsc": "tsc",
     "pretest": "yarn build:assets",

PATCH

echo "Patch applied successfully."
