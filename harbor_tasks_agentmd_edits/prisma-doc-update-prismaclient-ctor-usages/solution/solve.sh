#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prisma

# Idempotent: skip if already applied
if grep -q 'adapter: new PrismaPg' packages/client-generator-js/src/TSClient/PrismaClient.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/README.md b/README.md
index 9f3d2f431832..ba010b22ca1a 100644
--- a/README.md
+++ b/README.md
@@ -252,15 +252,7 @@ Once the Prisma Client is generated, you can import it in your code and send que

 ##### Import and instantiate Prisma Client

-You can import and instantiate Prisma Client from the output path specified in your generator configuration:
-
-```ts
-import { PrismaClient } from './generated/client'
-
-const prisma = new PrismaClient()
-```
-
-**Note**: As of [Prisma 7](https://www.prisma.io/docs/orm/more/upgrade-guides/upgrading-versions/upgrading-to-prisma-7#driver-adapters-and-client-instantiation), you will need to use a [driver adapter](https://www.prisma.io/docs/orm/overview/databases/database-drivers#driver-adapters). For example, when using PostgreSQL with a driver adapter:
+You can import and instantiate Prisma Client from the output path specified in your generator configuration. When instantiating the Client, you need to provide a [driver adapter](https://www.prisma.io/docs/orm/core-concepts/supported-databases/database-drivers#how-to-use-driver-adapters) to its constructor. For example, when using PostgreSQL with a driver adapter:

 ```ts
 import { PrismaClient } from './generated/client'
diff --git a/packages/client-generator-js/src/TSClient/PrismaClient.ts b/packages/client-generator-js/src/TSClient/PrismaClient.ts
index 1d834dda459c..07084b71144f 100644
--- a/packages/client-generator-js/src/TSClient/PrismaClient.ts
+++ b/packages/client-generator-js/src/TSClient/PrismaClient.ts
@@ -407,7 +407,9 @@ export class PrismaClientClass implements Generable {
  * Type-safe database client for TypeScript & Node.js
  * @example
  * \`\`\`
- * const prisma = new PrismaClient()
+ * const prisma = new PrismaClient({
+ *   adapter: new PrismaPg({ connectionString: process.env.DATABASE_URL })
+ * })
  * // Fetch zero or more ${capitalize(example.plural)}
  * const ${uncapitalize(example.plural)} = await prisma.${uncapitalize(example.model)}.findMany()
  * \`\`\`
diff --git a/packages/client-generator-ts/src/TSClient/PrismaClient.ts b/packages/client-generator-ts/src/TSClient/PrismaClient.ts
index 9e1afef9567e..7547c5e89642 100644
--- a/packages/client-generator-ts/src/TSClient/PrismaClient.ts
+++ b/packages/client-generator-ts/src/TSClient/PrismaClient.ts
@@ -237,7 +237,9 @@ export function getPrismaClientClassDocComment({ dmmf }: GenerateContext): ts.Do
     Type-safe database client for TypeScript
     @example
     \`\`\`
-    const prisma = new PrismaClient()
+    const prisma = new PrismaClient({
+      adapter: new PrismaPg({ connectionString: process.env.DATABASE_URL })
+    })
     // Fetch zero or more ${capitalize(example.plural)}
     const ${uncapitalize(example.plural)} = await prisma.${uncapitalize(example.model)}.findMany()
     \`\`\`

PATCH

echo "Patch applied successfully."
