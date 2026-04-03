#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prisma

# Idempotent: skip if already applied
if grep -q 'PrismaClient.*needs to be constructed with a non-empty' packages/client/src/runtime/getPrismaClient.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply code fix: throw error when PrismaClient constructed without args
cat > /tmp/code.patch <<'PATCH'
diff --git a/packages/client/src/runtime/getPrismaClient.ts b/packages/client/src/runtime/getPrismaClient.ts
index 0d047183ea07..3f4f30c4e3d6 100644
--- a/packages/client/src/runtime/getPrismaClient.ts
+++ b/packages/client/src/runtime/getPrismaClient.ts
@@ -236,11 +236,30 @@ export function getPrismaClient(config: GetPrismaClientConfig) {
     _createPrismaPromise = createPrismaPromiseFactory()

     constructor(optionsArg: PrismaClientOptions) {
-      config = optionsArg.__internal?.configOverride?.(config) ?? config
+      if (!optionsArg) {
+        throw new PrismaClientInitializationError(
+          `\
+\`PrismaClient\` needs to be constructed with a non-empty, valid \`PrismaClientOptions\`:
+
+\`\`\`
+new PrismaClient({
+  ...
+})
+\`\`\`
+
+or

-      if (optionsArg) {
-        validatePrismaClientOptions(optionsArg, config)
+\`\`\`
+constructor() {
+  super({ ... });
+}
+\`\`\`
+          `,
+          clientVersion,
+        )
       }
+      config = optionsArg.__internal?.configOverride?.(config) ?? config
+      validatePrismaClientOptions(optionsArg, config)

       // prevents unhandled error events when users do not explicitly listen to them
       const logEmitter = new EventEmitter().on('error', () => {}) as LogEmitter
@@ -257,7 +276,7 @@ export function getPrismaClient(config: GetPrismaClientConfig) {
        */

       let adapter: SqlDriverAdapterFactory | undefined
-      if (optionsArg?.adapter) {
+      if (optionsArg.adapter) {
         adapter = optionsArg.adapter

         // Note:
PATCH

git apply /tmp/code.patch

# Apply README fix: update broken URLs and add Prisma 7 driver adapter note
cat > /tmp/readme.patch <<'PATCH'
diff --git a/README.md b/README.md
index 7fff3e46c733..9eaef4a4a306 100644
--- a/README.md
+++ b/README.md
@@ -31,8 +31,8 @@

 Prisma ORM is a **next-generation ORM** that consists of these tools:

-- [**Prisma Client**](https://www.prisma.io/docs/concepts/components/prisma-client): Auto-generated and type-safe query builder for Node.js & TypeScript
-- [**Prisma Migrate**](https://www.prisma.io/docs/concepts/components/prisma-migrate): Declarative data modeling & migration system
+- [**Prisma Client**](https://www.prisma.io/docs/orm/prisma-client): Auto-generated and type-safe query builder for Node.js & TypeScript
+- [**Prisma Migrate**](https://www.prisma.io/docs/orm/prisma-migrate): Declarative data modeling & migration system
 - [**Prisma Studio**](https://github.com/prisma/studio): GUI to view and edit data in your database

 Prisma Client can be used in _any_ Node.js or TypeScript backend application (including serverless applications and microservices). This can be a [REST API](https://www.prisma.io/docs/concepts/overview/prisma-in-your-stack/rest), a [GraphQL API](https://www.prisma.io/docs/concepts/overview/prisma-in-your-stack/graphql), a gRPC API, or anything else that needs a database.
@@ -61,7 +61,7 @@ This section provides a high-level overview of how Prisma ORM works and its most

 ### The Prisma schema

-Every project that uses a tool from the Prisma toolkit starts with a [Prisma schema file](https://www.prisma.io/docs/concepts/components/prisma-schema). The Prisma schema allows developers to define their _application models_ in an intuitive data modeling language and configure _generators_.
+Every project that uses a tool from the Prisma toolkit starts with a [Prisma schema file](https://www.prisma.io/docs/orm/prisma-schema). The Prisma schema allows developers to define their _application models_ in an intuitive data modeling language and configure _generators_.

 ```prisma
 // Data source
@@ -160,7 +160,7 @@ On this page, the focus is on the data model. You can learn more about [Data sou

 #### Functions of Prisma models

-The data model is a collection of [models](https://www.prisma.io/docs/concepts/components/prisma-schema/data-model#defining-models). A model has two major functions:
+The data model is a collection of [models](https://www.prisma.io/docs/orm/prisma-schema/data-model/models). A model has two major functions:

 - Represent a table in the underlying database
 - Provide the foundation for the queries in the Prisma Client API
@@ -169,10 +169,10 @@ The data model is a collection of [models](https://www.prisma.io/docs/concepts/c

 There are two major workflows for "getting" a data model into your Prisma schema:

-- Generate the data model from [introspecting](https://www.prisma.io/docs/concepts/components/introspection) a database
-- Manually writing the data model and mapping it to the database with [Prisma Migrate](https://www.prisma.io/docs/concepts/components/prisma-migrate)
+- Generate the data model from [introspecting](https://www.prisma.io/docs/orm/prisma-schema/introspection) a database
+- Manually writing the data model and mapping it to the database with [Prisma Migrate](https://www.prisma.io/docs/orm/prisma-migrate)

-Once the data model is defined, you can [generate Prisma Client](https://www.prisma.io/docs/concepts/components/prisma-client/generating-prisma-client) which will expose CRUD and more queries for the defined models. If you're using TypeScript, you'll get full type-safety for all queries (even when only retrieving the subsets of a model's fields).
+Once the data model is defined, you can [generate Prisma Client](https://www.prisma.io/docs/orm/prisma-client/setup-and-configuration/generating-prisma-client) which will expose CRUD and more queries for the defined models. If you're using TypeScript, you'll get full type-safety for all queries (even when only retrieving the subsets of a model's fields).

 ---

@@ -244,7 +244,7 @@ After you change your data model, you'll need to manually re-generate Prisma Cli
 npx prisma generate
 ```

-Refer to the documentation for more information about ["generating the Prisma client"](https://www.prisma.io/docs/concepts/components/prisma-client/generating-prisma-client).
+Refer to the documentation for more information about ["generating the Prisma client"](https://www.prisma.io/docs/orm/prisma-client/setup-and-configuration/generating-prisma-client).

 #### Step 5: Use Prisma Client to send queries to your database

@@ -260,7 +260,7 @@ import { PrismaClient } from './generated/client'
 const prisma = new PrismaClient()
 ```

-**Note**: Depending on your database, you may need to use a [driver adapter](https://www.prisma.io/docs/orm/overview/databases/database-drivers#driver-adapters). For example, when using PostgreSQL with a driver adapter:
+**Note**: As of [Prisma 7](https://www.prisma.io/docs/orm/more/upgrade-guides/upgrading-versions/upgrading-to-prisma-7#driver-adapters-and-client-instantiation), you will need to use a [driver adapter](https://www.prisma.io/docs/orm/overview/databases/database-drivers#driver-adapters). For example, when using PostgreSQL with a driver adapter:

 ```ts
 import { PrismaClient } from './generated/client'
@@ -274,7 +274,7 @@ To load environment variables, you can use `dotenv` by importing `dotenv/config`

 Now you can start sending queries via the generated Prisma Client API, here are a few sample queries. Note that all Prisma Client queries return _plain old JavaScript objects_.

-Learn more about the available operations in the [Prisma Client docs](https://www.prisma.io/docs/concepts/components/prisma-client) or watch this [demo video](https://www.youtube.com/watch?v=LggrE5kJ75I&list=PLn2e1F9Rfr6k9PnR_figWOcSHgc_erDr5&index=4) (2 min).
+Learn more about the available operations in the [Prisma Client docs](https://www.prisma.io/docs/orm/prisma-client) or watch this [demo video](https://www.youtube.com/watch?v=LggrE5kJ75I&list=PLn2e1F9Rfr6k9PnR_figWOcSHgc_erDr5&index=4) (2 min).

 ##### Retrieve all `User` records from the database

@@ -325,7 +325,7 @@ const post = await prisma.post.update({

 #### Usage with TypeScript

-Note that when using TypeScript, the result of this query will be _statically typed_ so that you can't accidentally access a property that doesn't exist (and any typos are caught at compile-time). Learn more about leveraging Prisma Client's generated types on the [Advanced usage of generated types](https://www.prisma.io/docs/concepts/components/prisma-client/advanced-usage-of-generated-types) page in the docs.
+Note that when using TypeScript, the result of this query will be _statically typed_ so that you can't accidentally access a property that doesn't exist (and any typos are caught at compile-time). Learn more about leveraging Prisma Client's generated types on the [Advanced usage of generated types](https://www.prisma.io/docs/orm/prisma-client/type-safety/operating-against-partial-structures-of-model-types) page in the docs.

 ## Community

PATCH

git apply /tmp/readme.patch

rm -f /tmp/code.patch /tmp/readme.patch

echo "Patch applied successfully."
