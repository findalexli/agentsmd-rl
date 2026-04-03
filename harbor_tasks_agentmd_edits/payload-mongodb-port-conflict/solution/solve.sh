#!/usr/bin/env bash
set -euo pipefail

cd /workspace/payload

# Idempotent: skip if already applied
if grep -q 'localhost:27018/payload?authSource=admin' test/generateDatabaseAdapter.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.env.example b/.env.example
index 57137813bbd..fe0835ee7ce 100644
--- a/.env.example
+++ b/.env.example
@@ -3,3 +3,16 @@ PAYLOAD_DATABASE=mongodb

 # Optional - used for the `translateNewKeys` script
 OPENAI_KEY=
+
+
+
+
+
+
+
+
+
+# If you're NOT using our docker scripts and want to manually install your database, uncomment these and point them to your local database.
+# Do not uncomment these if you're using our Docker scripts to run your database.
+# MONGODB_URL=mongodb://127.0.0.1/payloadtests
+# POSTGRES_URL=postgres://127.0.0.1:5432/payloadtests
diff --git a/.github/actions/start-database/action.yml b/.github/actions/start-database/action.yml
index 1698aab39b7..57143730c92 100644
--- a/.github/actions/start-database/action.yml
+++ b/.github/actions/start-database/action.yml
@@ -26,7 +26,7 @@ runs:
       shell: bash
       run: |
         docker compose -f test/helpers/db/mongodb/docker-compose.yml up -d --wait
-        echo "url=mongodb://payload:payload@localhost:27017/payload?authSource=admin&directConnection=true&replicaSet=rs0" >> $GITHUB_OUTPUT
+        echo "url=mongodb://payload:payload@localhost:27018/payload?authSource=admin&directConnection=true&replicaSet=rs0" >> $GITHUB_OUTPUT

     - name: Start MongoDB Atlas Local
       id: mongodb-atlas
@@ -34,7 +34,7 @@ runs:
       shell: bash
       run: |
         docker compose -f test/helpers/db/mongodb-atlas/docker-compose.yml up -d --wait
-        echo "url=mongodb://localhost:27018/payload?directConnection=true&replicaSet=mongodb-atlas-local" >> $GITHUB_OUTPUT
+        echo "url=mongodb://localhost:27019/payload?directConnection=true&replicaSet=mongodb-atlas-local" >> $GITHUB_OUTPUT

     - name: Start PostgreSQL
       id: postgres
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index c25ba0cbc88..89202de8ad5 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -87,7 +87,9 @@ Set `PAYLOAD_DATABASE` in your `.env` file to choose the database adapter:
 - `supabase` - Supabase (PostgreSQL)
 - `d1` - D1 (SQLite)

-Then use Docker to start your database:
+Then use Docker to start your database.
+
+On MacOS, the easiest way to install Docker is to use brew. Simply run `pnpm install --cask docker`, open the docker desktop app, apply the recommended settings and you're good to go.

 ### PostgreSQL

@@ -107,7 +109,7 @@ pnpm docker:mongodb:restart:clean  # Start fresh (removes data)
 pnpm docker:mongodb:stop           # Stop
 ```

-URL: `mongodb://payload:payload@localhost:27017/payload?authSource=admin&directConnection=true&replicaSet=rs0`
+URL: `mongodb://payload:payload@localhost:27018/payload?authSource=admin&directConnection=true&replicaSet=rs0`

 ### MongoDB Atlas Local

@@ -117,7 +119,7 @@ pnpm docker:mongodb-atlas:restart:clean # Start fresh (removes data)
 pnpm docker:mongodb-atlas:stop          # Stop
 ```

-URL: `mongodb://localhost:27018/payload?directConnection=true&replicaSet=mongodb-atlas-local` (no auth required)
+URL: `mongodb://localhost:27019/payload?directConnection=true&replicaSet=mongodb-atlas-local` (no auth required)

 ### SQLite

@@ -125,9 +127,12 @@ SQLite databases don't require Docker - they're stored as files in the project.

 ### Testing with your own database

-If you wish to use your own MongoDB database for the `test` directory instead of using the docker database, all you need to do is add the following env variable to your `.env` file:
+If you wish to use your own MongoDB database for the `test` directory instead of using the docker database, add the following to your `.env` file:

-- `DATABASE_URL` to your database URL e.g. `mongodb://127.0.0.1/your-test-db`.
+```env
+MONGODB_URL=mongodb://127.0.0.1/payloadtests # Point this to your locally installed MongoDB database
+POSTGRES_URL=postgres://127.0.0.1:5432/payloadtests # Point this to your locally installed PostgreSQL database
+```

 ### Running the e2e and int tests

diff --git a/test/generateDatabaseAdapter.ts b/test/generateDatabaseAdapter.ts
index 985251b9090..cffadbb63af 100644
--- a/test/generateDatabaseAdapter.ts
+++ b/test/generateDatabaseAdapter.ts
@@ -5,11 +5,12 @@ import { fileURLToPath } from 'node:url'
 const filename = fileURLToPath(import.meta.url)
 const dirname = path.dirname(filename)

+// Runs on port 27018 to avoid conflicts with locally installed MongoDB
 const mongooseAdapterArgs = `
     ensureIndexes: true,
     url:
         process.env.MONGODB_URL || process.env.DATABASE_URL ||
-      'mongodb://payload:payload@localhost:27017/payload?authSource=admin&directConnection=true&replicaSet=rs0',
+      'mongodb://payload:payload@localhost:27018/payload?authSource=admin&directConnection=true&replicaSet=rs0',
 `

 export const allDatabaseAdapters = {
@@ -21,7 +22,7 @@ export const allDatabaseAdapters = {
   })`,
   // mongodb-atlas uses Docker-based MongoDB Atlas Local (all-in-one with search)
   // Start with: pnpm docker:mongodb-atlas:start
-  // Runs on port 27018 to avoid conflicts with mongodb
+  // Runs on port 27019 to avoid conflicts with mongodb
   'mongodb-atlas': `
   import { mongooseAdapter } from '@payloadcms/db-mongodb'

@@ -29,7 +30,7 @@ export const allDatabaseAdapters = {
     ensureIndexes: true,
     url:
         process.env.MONGODB_ATLAS_URL || process.env.DATABASE_URL ||
-      'mongodb://localhost:27018/payload?directConnection=true&replicaSet=mongodb-atlas-local',
+      'mongodb://localhost:27019/payload?directConnection=true&replicaSet=mongodb-atlas-local',
   })`,
   cosmosdb: `
   import { mongooseAdapter, compatibilityOptions } from '@payloadcms/db-mongodb'
diff --git a/test/helpers/db/mongodb-atlas/docker-compose.yml b/test/helpers/db/mongodb-atlas/docker-compose.yml
index 61d56266c78..8996cd59f6e 100644
--- a/test/helpers/db/mongodb-atlas/docker-compose.yml
+++ b/test/helpers/db/mongodb-atlas/docker-compose.yml
@@ -16,7 +16,7 @@ services:
     container_name: mongodb-atlas-payload-test
     hostname: mongodb-atlas-local # Sets a fixed replica set name (used in connection string replicaSet param)
     ports:
-      - '27018:27017'
+      - '27019:27017'
     volumes:
       - mongodb_atlas_data:/data/db
     environment:
diff --git a/test/helpers/db/mongodb-atlas/run-test-connection.ts b/test/helpers/db/mongodb-atlas/run-test-connection.ts
index b2a1422926c..f152b3ed3c8 100644
--- a/test/helpers/db/mongodb-atlas/run-test-connection.ts
+++ b/test/helpers/db/mongodb-atlas/run-test-connection.ts
@@ -9,5 +9,5 @@ import { testConnection } from '../mongodb/test-connection.js'

 await testConnection(
   process.env.MONGODB_ATLAS_URL ||
-    'mongodb://localhost:27018/payload?directConnection=true&replicaSet=mongodb-atlas-local',
+    'mongodb://localhost:27019/payload?directConnection=true&replicaSet=mongodb-atlas-local',
 )
diff --git a/test/helpers/db/mongodb/docker-compose.yml b/test/helpers/db/mongodb/docker-compose.yml
index eb6c94189a9..be447e6f21a 100644
--- a/test/helpers/db/mongodb/docker-compose.yml
+++ b/test/helpers/db/mongodb/docker-compose.yml
@@ -17,7 +17,7 @@ services:
     image: mongodb/mongodb-community-server:8.2-ubi9
     container_name: mongodb-payload-test
     ports:
-      - '27017:27017'
+      - '27018:27017'
     volumes:
       - mongodb_data:/data/db
       - ./keyfile:/etc/mongodb/keyfile:ro
diff --git a/test/helpers/db/mongodb/run-test-connection.ts b/test/helpers/db/mongodb/run-test-connection.ts
index e4deb5811e4..571456a82f7 100644
--- a/test/helpers/db/mongodb/run-test-connection.ts
+++ b/test/helpers/db/mongodb/run-test-connection.ts
@@ -9,5 +9,5 @@ import { testConnection } from './test-connection.js'

 await testConnection(
   process.env.MONGODB_URL ||
-    'mongodb://payload:payload@localhost:27017/payload?authSource=admin&directConnection=true&replicaSet=rs0',
+    'mongodb://payload:payload@localhost:27018/payload?authSource=admin&directConnection=true&replicaSet=rs0',
 )

PATCH

echo "Patch applied successfully."
