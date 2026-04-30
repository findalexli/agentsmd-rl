#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prisma

# Idempotent: skip if already applied
if grep -q 'parseAuthenticationOptions' packages/adapter-mssql/src/connection-string.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/adapter-mssql/README.md b/packages/adapter-mssql/README.md
index ec8fd75484ee..cd3e08e90f6f 100644
--- a/packages/adapter-mssql/README.md
+++ b/packages/adapter-mssql/README.md
@@ -16,7 +16,7 @@ Install the Prisma ORM's driver adapter:
 npm install @prisma/adapter-mssql
 ```

-### 3. Instantiate Prisma Client using the driver adapter
+### 2. Instantiate Prisma Client using the driver adapter

 Finally, when you instantiate Prisma Client, you need to pass an instance of Prisma ORM's driver adapter to the `PrismaClient` constructor:

@@ -39,3 +39,58 @@ const config = {
 const adapter = new PrismaMssql(config)
 const prisma = new PrismaClient({ adapter })
 ```
+
+You can also instantiate the adapter with a [JDBC](https://learn.microsoft.com/en-us/sql/connect/jdbc/building-the-connection-url?view=sql-server-ver15) connection string:
+
+```ts
+import { PrismaMssql } from '@prisma/adapter-mssql'
+import { PrismaClient } from '@prisma/client'
+
+const adapter = new PrismaMssql('sqlserver://localhost:1433;database=testdb;user=sa;password=mypassword;encrypt=true')
+const prisma = new PrismaClient({ adapter })
+```
+
+### 3. Entra ID Authentication (formerly Azure Active Directory)
+
+Entra ID authentication is supported by the mssql driver used by this adapter.
+
+For options using the config object, see the options documentation for the [Tedious driver](https://github.com/tediousjs/node-mssql?tab=readme-ov-file#tedious).
+
+For example, using the config object to configure [DefaultAzureCredential](https://learn.microsoft.com/en-gb/azure/developer/javascript/sdk/authentication/credential-chains#use-defaultazurecredential-for-flexibility):
+
+```ts
+import { PrismaMssql } from '@prisma/adapter-mssql'
+import { PrismaClient } from '@prisma/client'
+
+const config = {
+  server: 'localhost',
+  port: 1433,
+  database: 'mydb',
+  authentication: {
+    type: 'azure-active-directory-default',
+  },
+  options: {
+    encrypt: true,
+  },
+}
+
+const adapter = new PrismaMssql(config)
+const prisma = new PrismaClient({ adapter })
+```
+
+Connection string parsing also supports authentication options, as per below:
+
+- to use [DefaultAzureCredential](https://learn.microsoft.com/en-gb/azure/developer/javascript/sdk/authentication/credential-chains#use-defaultazurecredential-for-flexibility), set:
+  - `authentication=DefaultAzureCredential` in your connection string
+- to use an Entra username/password, set:
+  - `authentication=ActiveDirectoryPassword`
+  - `userName=<value>`
+  - `password=<value>`
+  - `clientId=<value>`
+- to use an Entra managed identity, set:
+  - `authentication=ActiveDirectoryManagedIdentity`
+  - `clientId=<value>` (optional)
+- to use a Service Principal with clientId and secret, set:
+  - `authentication=ActiveDirectoryServicePrincipal`
+  - `userName=<client id>`
+  - `password=<client secret>`
diff --git a/packages/adapter-mssql/src/connection-string.ts b/packages/adapter-mssql/src/connection-string.ts
index 74ddd94a733c..5a624958e60a 100644
--- a/packages/adapter-mssql/src/connection-string.ts
+++ b/packages/adapter-mssql/src/connection-string.ts
@@ -74,100 +74,232 @@ export function parseConnectionString(connectionString: string): sql.config {
     config.port = port
   }

-  // Parse the remaining parameters
+  // parse all parameters into an object, checking for duplicates
+  const parameters: Record<string, string> = {}
+
   for (const part of paramParts) {
     const [key, value] = part.split('=', 2)
     if (!key) continue

     const trimmedKey = key.trim()
-    const trimmedValue = value.trim()
-
-    switch (trimmedKey) {
-      case 'database':
-      case 'initial catalog':
-        config.database = trimmedValue
-        break
-      case 'user':
-      case 'username':
-      case 'uid':
-      case 'userid':
-        config.user = trimmedValue
-        break
-      case 'password':
-      case 'pwd':
-        config.password = trimmedValue
-        break
-      case 'encrypt':
-        config.options = config.options || {}
-        config.options.encrypt = trimmedValue.toLowerCase() === 'true'
-        break
-      case 'trustServerCertificate':
-        config.options = config.options || {}
-        config.options.trustServerCertificate = trimmedValue.toLowerCase() === 'true'
-        break
-      case 'connectionLimit': {
-        config.pool = config.pool || {}
-        const limit = parseInt(trimmedValue, 10)
-        if (isNaN(limit)) {
-          throw new Error(`Invalid connection limit: ${trimmedValue}`)
-        }
-        config.pool.max = limit
-        break
+    if (trimmedKey in parameters) {
+      throw new Error(`Duplication configuration parameter: ${trimmedKey}`)
+    }
+    parameters[trimmedKey] = value.trim()
+    if (!handledParameters.includes(trimmedKey)) {
+      debug(`Unknown connection string parameter: ${trimmedKey}`)
+    }
+  }
+
+  const database = firstKey(parameters, 'database', 'initial catalog')
+  if (database !== null) {
+    config.database = database
+  }
+
+  const user = firstKey(parameters, 'user', 'username', 'uid', 'userid')
+  if (user !== null) {
+    config.user = user
+  }
+
+  const password = firstKey(parameters, 'password', 'pwd')
+  if (password !== null) {
+    config.password = password
+  }
+
+  const encrypt = firstKey(parameters, 'encrypt')
+  if (encrypt !== null) {
+    config.options = config.options || {}
+    config.options.encrypt = encrypt.toLowerCase() === 'true'
+  }
+
+  const trustServerCertificate = firstKey(parameters, 'trustServerCertificate')
+  if (trustServerCertificate !== null) {
+    config.options = config.options || {}
+    config.options.trustServerCertificate = trustServerCertificate.toLowerCase() === 'true'
+  }
+
+  const connectionLimit = firstKey(parameters, 'connectionLimit')
+  if (connectionLimit !== null) {
+    config.pool = config.pool || {}
+    const limit = parseInt(connectionLimit, 10)
+    if (isNaN(limit)) {
+      throw new Error(`Invalid connection limit: ${connectionLimit}`)
+    }
+    config.pool.max = limit
+  }
+
+  const connectionTimeout = firstKey(parameters, 'connectionTimeout', 'connectTimeout')
+  if (connectionTimeout !== null) {
+    const timeout = parseInt(connectionTimeout, 10)
+    if (isNaN(timeout)) {
+      throw new Error(`Invalid connection timeout: ${connectionTimeout}`)
+    }
+    config.connectionTimeout = timeout
+  }
+
+  const loginTimeout = firstKey(parameters, 'loginTimeout')
+  if (loginTimeout !== null) {
+    const timeout = parseInt(loginTimeout, 10)
+    if (isNaN(timeout)) {
+      throw new Error(`Invalid login timeout: ${loginTimeout}`)
+    }
+    config.connectionTimeout = timeout
+  }
+
+  const socketTimeout = firstKey(parameters, 'socketTimeout')
+  if (socketTimeout !== null) {
+    const timeout = parseInt(socketTimeout, 10)
+    if (isNaN(timeout)) {
+      throw new Error(`Invalid socket timeout: ${socketTimeout}`)
+    }
+    config.requestTimeout = timeout
+  }
+
+  const poolTimeout = firstKey(parameters, 'poolTimeout')
+  if (poolTimeout !== null) {
+    const timeout = parseInt(poolTimeout, 10)
+    if (isNaN(timeout)) {
+      throw new Error(`Invalid pool timeout: ${poolTimeout}`)
+    }
+    config.pool = config.pool || {}
+    config.pool.acquireTimeoutMillis = timeout * 1000
+  }
+
+  const appName = firstKey(parameters, 'applicationName', 'application name')
+  if (appName !== null) {
+    config.options = config.options || {}
+    config.options.appName = appName
+  }
+
+  const isolationLevel = firstKey(parameters, 'isolationLevel')
+  if (isolationLevel !== null) {
+    config.options = config.options || {}
+    config.options.isolationLevel = mapIsolationLevelFromString(isolationLevel)
+  }
+
+  const authentication = firstKey(parameters, 'authentication')
+  if (authentication !== null) {
+    config.authentication = parseAuthenticationOptions(parameters, authentication)
+  }
+
+  if (!config.server || config.server.trim() === '') {
+    throw new Error('Server host is required in connection string')
+  }
+
+  return config
+}
+
+/**
+ * Parse all the authentication options, ensuring a valid configuration is provided
+ * @param parameters configuration parameters
+ * @param authenticationValue authentication string value
+ */
+function parseAuthenticationOptions(
+  parameters: Record<string, string>,
+  authenticationValue: string,
+): sql.config['authentication'] | undefined {
+  switch (authenticationValue) {
+    /**
+     * 'DefaultAzureCredential' is not listed in the JDBC driver spec
+     * https://learn.microsoft.com/en-us/sql/connect/jdbc/setting-the-connection-properties?view=sql-server-ver15#properties
+     * but is supported by tedious so included here
+     */
+    case 'DefaultAzureCredential':
+    case 'ActiveDirectoryIntegrated':
+    case 'ActiveDirectoryInteractive':
+      // uses https://learn.microsoft.com/en-gb/azure/developer/javascript/sdk/authentication/credential-chains#use-defaultazurecredential-for-flexibility
+      return { type: 'azure-active-directory-default', options: {} }
+    case 'ActiveDirectoryPassword': {
+      const userName = firstKey(parameters, 'userName')
+      const password = firstKey(parameters, 'password')
+      const clientId = firstKey(parameters, 'clientId')
+      const tenantId = firstKey(parameters, 'tenantId')
+      if (!userName || !password || !clientId) {
+        throw new Error(`Invalid authentication, ActiveDirectoryPassword requires userName, password, clientId`)
       }
-      case 'connectTimeout':
-      case 'connectionTimeout': {
-        const connectTimeout = parseInt(trimmedValue, 10)
-        if (isNaN(connectTimeout)) {
-          throw new Error(`Invalid connection timeout: ${trimmedValue}`)
-        }
-        config.connectionTimeout = connectTimeout
-        break
+      return {
+        type: 'azure-active-directory-password',
+        options: {
+          userName,
+          password,
+          clientId,
+          tenantId: tenantId || '',
+        },
       }
-      case 'loginTimeout': {
-        const loginTimeout = parseInt(trimmedValue, 10)
-        if (isNaN(loginTimeout)) {
-          throw new Error(`Invalid login timeout: ${trimmedValue}`)
-        }
-        config.connectionTimeout = loginTimeout
-        break
+    }
+    case 'ActiveDirectoryManagedIdentity':
+    case 'ActiveDirectoryMSI': {
+      const clientId = firstKey(parameters, 'clientId')
+      const msiEndpoint = firstKey(parameters, 'msiEndpoint')
+      const msiSecret = firstKey(parameters, 'msiSecret')
+      if (!msiEndpoint || !msiSecret) {
+        throw new Error(`Invalid authentication, ActiveDirectoryManagedIdentity requires msiEndpoint, msiSecret`)
       }
-      case 'socketTimeout': {
-        const socketTimeout = parseInt(trimmedValue, 10)
-        if (isNaN(socketTimeout)) {
-          throw new Error(`Invalid socket timeout: ${trimmedValue}`)
-        }
-        config.requestTimeout = socketTimeout
-        break
+      return {
+        type: 'azure-active-directory-msi-app-service',
+        options: {
+          clientId: clientId || undefined,
+          // @ts-expect-error TODO: tedious typings don't define msiEndpoint and msiSecret -- needs to be fixed upstream
+          msiEndpoint,
+          msiSecret,
+        },
       }
-      case 'poolTimeout': {
-        const poolTimeout = parseInt(trimmedValue, 10)
-        if (isNaN(poolTimeout)) {
-          throw new Error(`Invalid pool timeout: ${trimmedValue}`)
+    }
+    case 'ActiveDirectoryServicePrincipal': {
+      const clientId = firstKey(parameters, 'userName')
+      const clientSecret = firstKey(parameters, 'password')
+      const tenantId = firstKey(parameters, 'tenantId')
+      if (clientId && clientSecret) {
+        return {
+          type: 'azure-active-directory-service-principal-secret',
+          options: {
+            clientId,
+            clientSecret,
+            tenantId: tenantId || '',
+          },
         }
-        config.pool = config.pool || {}
-        config.pool.acquireTimeoutMillis = poolTimeout * 1000
-        break
+      } else {
+        throw new Error(
+          `Invalid authentication, ActiveDirectoryServicePrincipal requires userName (clientId), password (clientSecret)`,
+        )
       }
-      case 'applicationName':
-      case 'application name':
-        config.options = config.options || {}
-        config.options.appName = trimmedValue
-        break
-      case 'isolationLevel':
-        config.options = config.options || {}
-        config.options.isolationLevel = mapIsolationLevelFromString(trimmedValue)
-        break
-      case 'schema':
-        // This is handled separately in PrismaMssqlOptions
-        break
-      default:
-        debug(`Unknown connection string parameter: ${trimmedKey}`)
     }
   }
+  return undefined
+}

-  if (!config.server || config.server.trim() === '') {
-    throw new Error('Server host is required in connection string')
+/**
+ * Return the value of the first key found in the parameters object
+ * @param parameters
+ * @param keys
+ */
+function firstKey(parameters: Record<string, string>, ...keys: string[]): string | null {
+  for (const key of keys) {
+    if (key in parameters) {
+      return parameters[key]
+    }
   }
-
-  return config
+  return null
 }
+
+const handledParameters = [
+  'application name',
+  'applicationName',
+  'connectTimeout',
+  'connectionLimit',
+  'connectionTimeout',
+  'database',
+  'encrypt',
+  'initial catalog',
+  'isolationLevel',
+  'loginTimeout',
+  'password',
+  'poolTimeout',
+  'pwd',
+  'socketTimeout',
+  'trustServerCertificate',
+  'uid',
+  'user',
+  'userid',
+  'username',
+]

PATCH

echo "Patch applied successfully."
