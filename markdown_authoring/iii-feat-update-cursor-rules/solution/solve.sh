#!/usr/bin/env bash
set -euo pipefail

cd /workspace/iii

# Idempotency guard
if grep -qF "* for each HTTP Status Code, you need to define a schema that defines the respon" "packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/api-steps.mdc" && grep -qF "* Optional: Virtually subscribed topics for documentation/lineage purposes." "packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/event-steps.mdc" && grep -qF "Adapters allow you to customize the underlying infrastructure for state manageme" "packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/motia-config.mdc" && grep -qF "baseConfig: { storageType: 'default' } | { storageType: 'custom'; factory: () =>" "packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/realtime-streaming.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/api-steps.mdc b/packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/api-steps.mdc
@@ -30,6 +30,9 @@ Defining an API Step is done by two elements. Configuration and Handler.
 **Python**: You need to define a `config` dictionary with the same properties as the TypeScript `ApiRouteConfig`.
 
 ```typescript
+export type ZodInput = ZodObject<any> | ZodArray<any>
+export type StepSchemaInput = ZodInput | JsonSchema
+
 export type Emit = string | { 
   /**
    * The topic name to emit to.
@@ -120,19 +123,23 @@ export interface ApiRouteConfig {
   middleware?: ApiMiddleware<any, any, any>[]
 
   /**
-   * Defined with Zod library, can be a ZodObject OR a ZodArray.
+   * Schema for the request body. Accepts either:
+   * - Zod schema (ZodObject or ZodArray)
+   * - JSON Schema object
    * 
    * Note: This is not validated automatically, you need to validate it in the handler.
    */
-  bodySchema?: ZodInput
+  bodySchema?: StepSchemaInput
 
   /**
-   * Defined with Zod library, can be a ZodObject OR a ZodArray
+   * Schema for response bodies. Accepts either:
+   * - Zod schema (ZodObject or ZodArray)
+   * - JSON Schema object
    * 
    * The key (number) is the HTTP status code this endpoint can return and
-   * for each HTTP Status Code, you need to define a Zod schema that defines the response body
+   * for each HTTP Status Code, you need to define a schema that defines the response body
    */
-  responseSchema?: Record<number, ZodInput>
+  responseSchema?: Record<number, StepSchemaInput>
 
   /**
    * Mostly for documentation purposes, it will show up in Endpoints section in Workbench
@@ -173,6 +180,15 @@ export interface ApiRequest<TBody = unknown> {
   headers: Record<string, string | string[]>
 }
 
+export type ApiResponse<
+  TStatus extends number = number, 
+  TBody = string | Buffer | Record<string, unknown>
+> = {
+  status: TStatus
+  headers?: Record<string, string>
+  body: TBody
+}
+
 export type ApiRouteHandler<
   /** 
    * The type defined by config['bodySchema']
@@ -219,7 +235,7 @@ const bodySchema = z.object({
   title: z.string().min(1, "Title cannot be empty"),
   description: z.string().optional(),
   category: z.string().min(1, "Category is required"),
-  metadata: z.record(z.any()).optional()
+  metadata: z.record(z.string(), z.any()).optional()
 })
 
 export const config: ApiRouteConfig = {
diff --git a/packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/event-steps.mdc b/packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/event-steps.mdc
@@ -26,7 +26,7 @@ Steps need to be created in the `steps` folder, it can be in subfolders.
 
 ## Definition
 
-Defining an API Step is done by two elements. Configuration and Handler.
+Defining an Event Step is done by two elements. Configuration and Handler.
 
 ### Schema Definition
 
@@ -40,6 +40,9 @@ Defining an API Step is done by two elements. Configuration and Handler.
 **Python**: You need to define a `config` dictionary with the same properties as the TypeScript `EventConfig`.
 
 ```typescript
+export type ZodInput = ZodObject<any> | ZodArray<any>
+export type StepSchemaInput = ZodInput | JsonSchema
+
 export type Emit = string | { 
   /**
    * The topic name to emit to.
@@ -92,7 +95,14 @@ export type EventConfig = {
   virtualEmits?: Emit[]
 
   /**
-   * The Zod schema of the input data of events this step processes.
+   * Optional: Virtually subscribed topics for documentation/lineage purposes.
+   */
+  virtualSubscribes?: string[]
+
+  /**
+   * Schema for input data. Accepts either:
+   * - Zod schema (ZodObject or ZodArray)
+   * - JSON Schema object
    * 
    * This is used by Motia to create the correct types for whoever emits the event 
    * to this step.
@@ -102,17 +112,23 @@ export type EventConfig = {
    * recommended to store it in the state and fetch it from the state on the 
    * Event Step handler.
    */
-  input: ZodInput
+  input?: StepSchemaInput
 
   /**
    * Optional: An array of flow names this step belongs to.
    */
   flows?: string[]
+
   /**
    * Files to include in the step bundle.
    * Needs to be relative to the step file.
    */
   includeFiles?: string[]
+
+  /**
+   * Optional: Infrastructure configuration for handler and queue settings.
+   */
+  infrastructure?: Partial<InfrastructureConfig>
 }
 ```
 
diff --git a/packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/motia-config.mdc b/packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/motia-config.mdc
@@ -0,0 +1,359 @@
+---
+description: Application configuration for Motia projects
+globs: motia.config.ts,motia.config.js
+alwaysApply: false
+---
+# Motia Configuration Guide
+
+The `motia.config.ts` file is the central configuration file for your Motia application. It allows you to customize plugins, adapters, stream authentication, and Express app settings.
+
+## Creating the Configuration File
+
+Create a `motia.config.ts` file in the root of your project:
+
+```typescript
+import { config } from 'motia'
+
+export default config({
+  plugins: [],
+  adapters: {},
+  streamAuth: undefined,
+  app: undefined,
+})
+```
+
+## Type Definitions
+
+```typescript
+import type { Express } from 'express'
+
+export type Config = {
+  /**
+   * Optional: Callback to customize the Express app instance.
+   * Use this to add custom middleware, routes, or configurations.
+   */
+  app?: (app: Express) => void
+
+  /**
+   * Optional: Array of plugin builders to extend Motia functionality.
+   * Plugins can add workbench UI components and custom steps.
+   */
+  plugins?: MotiaPluginBuilder[]
+
+  /**
+   * Optional: Custom adapters for state, events, cron, and streams.
+   * Use this for horizontal scaling or custom storage backends.
+   */
+  adapters?: AdapterConfig
+
+  /**
+   * Optional: Stream authentication configuration.
+   * Use this to secure real-time stream subscriptions.
+   */
+  streamAuth?: StreamAuthConfig
+}
+
+export type AdapterConfig = {
+  state?: StateAdapter
+  streams?: StreamAdapterManager
+  events?: EventAdapter
+  cron?: CronAdapter
+}
+
+export type StreamAuthRequest = {
+  headers: Record<string, string | string[] | undefined>
+  url?: string
+}
+
+export type StreamAuthConfig<TSchema extends z.ZodTypeAny = z.ZodTypeAny> = {
+  /**
+   * JSON Schema defining the shape of the auth context.
+   * Use z.toJSONSchema() to convert a Zod schema.
+   */
+  contextSchema: JsonSchema
+
+  /**
+   * Authentication callback that receives the request and returns
+   * the auth context or null if authentication fails.
+   */
+  authenticate: (request: StreamAuthRequest) => Promise<z.infer<TSchema> | null> | (z.infer<TSchema> | null)
+}
+```
+
+## Plugins
+
+Plugins extend Motia functionality by adding workbench UI components and custom steps.
+
+### Plugin Type Definition
+
+```typescript
+export type WorkbenchPlugin = {
+  packageName: string
+  componentName?: string
+  label?: string
+  labelIcon?: string
+  position?: 'bottom' | 'top'
+  cssImports?: string[]
+  props?: Record<string, any>
+}
+
+export type MotiaPlugin = {
+  workbench: WorkbenchPlugin[]
+  dirname?: string
+  steps?: string[]
+}
+
+export type MotiaPluginBuilder = (motia: MotiaPluginContext) => MotiaPlugin
+```
+
+### Using Built-in Plugins
+
+```typescript
+import { config } from 'motia'
+
+const statesPlugin = require('@motiadev/plugin-states/plugin')
+const endpointPlugin = require('@motiadev/plugin-endpoint/plugin')
+const logsPlugin = require('@motiadev/plugin-logs/plugin')
+const observabilityPlugin = require('@motiadev/plugin-observability/plugin')
+
+export default config({
+  plugins: [observabilityPlugin, statesPlugin, endpointPlugin, logsPlugin],
+})
+```
+
+### Creating a Local Plugin
+
+```typescript
+import path from 'node:path'
+import { config, type MotiaPlugin, type MotiaPluginContext } from 'motia'
+
+function myLocalPlugin(motia: MotiaPluginContext): MotiaPlugin {
+  motia.registerApi(
+    {
+      method: 'GET',
+      path: '/__motia/my-plugin',
+    },
+    async (_req, _ctx) => {
+      return {
+        status: 200,
+        body: { message: 'Hello from my plugin!' },
+      }
+    },
+  )
+
+  return {
+    dirname: path.join(__dirname, 'plugins'),
+    steps: ['**/*.step.ts'],
+    workbench: [
+      {
+        componentName: 'MyComponent',
+        packageName: '~/plugins/components/my-component',
+        label: 'My Plugin',
+        position: 'top',
+        labelIcon: 'toy-brick',
+      },
+    ],
+  }
+}
+
+export default config({
+  plugins: [myLocalPlugin],
+})
+```
+
+## Adapters
+
+Adapters allow you to customize the underlying infrastructure for state management, event handling, cron jobs, and streams. This is useful for horizontal scaling or using custom storage backends.
+
+### Available Adapter Packages
+
+| Package | Description |
+|---------|-------------|
+| `@motiadev/adapter-redis-state` | Redis-based state management for distributed systems |
+| `@motiadev/adapter-redis-cron` | Redis-based cron scheduling with distributed locking |
+| `@motiadev/adapter-redis-streams` | Redis Streams for real-time data |
+| `@motiadev/adapter-rabbitmq-events` | RabbitMQ for event messaging |
+| `@motiadev/adapter-bullmq-events` | BullMQ for event queue processing |
+
+### Using Custom Adapters
+
+```typescript
+import { config } from 'motia'
+import { RedisStateAdapter } from '@motiadev/adapter-redis-state'
+import { RabbitMQEventAdapter } from '@motiadev/adapter-rabbitmq-events'
+import { RedisCronAdapter } from '@motiadev/adapter-redis-cron'
+
+export default config({
+  adapters: {
+    state: new RedisStateAdapter(
+      { url: process.env.REDIS_URL },
+      { keyPrefix: 'myapp:state:', ttl: 3600 }
+    ),
+    events: new RabbitMQEventAdapter({
+      url: process.env.RABBITMQ_URL!,
+      exchangeType: 'topic',
+      exchangeName: 'motia-events',
+    }),
+    cron: new RedisCronAdapter(
+      { url: process.env.REDIS_URL },
+      { keyPrefix: 'myapp:cron:', lockTTL: 30000 }
+    ),
+  },
+})
+```
+
+## Stream Authentication
+
+Stream authentication secures real-time stream subscriptions by validating client credentials.
+
+### Configuration
+
+```typescript
+import { config, type StreamAuthRequest } from 'motia'
+import { z } from 'zod'
+
+const authContextSchema = z.object({
+  userId: z.string(),
+  permissions: z.array(z.string()).optional(),
+})
+
+export default config({
+  streamAuth: {
+    contextSchema: z.toJSONSchema(authContextSchema),
+    authenticate: async (request: StreamAuthRequest) => {
+      const token = extractToken(request)
+      
+      if (!token) {
+        return null
+      }
+
+      const user = await validateToken(token)
+      if (!user) {
+        throw new Error('Invalid token')
+      }
+
+      return {
+        userId: user.id,
+        permissions: user.permissions,
+      }
+    },
+  },
+})
+
+function extractToken(request: StreamAuthRequest): string | undefined {
+  const protocol = request.headers['sec-websocket-protocol'] as string | undefined
+  if (protocol?.includes('Authorization')) {
+    const [, token] = protocol.split(',')
+    return token?.trim()
+  }
+
+  if (request.url) {
+    try {
+      const url = new URL(request.url)
+      return url.searchParams.get('authToken') ?? undefined
+    } catch {
+      return undefined
+    }
+  }
+
+  return undefined
+}
+```
+
+### Using Auth Context in Streams
+
+Once configured, the auth context is available in the `canAccess` callback of stream configurations:
+
+```typescript
+import { StreamConfig } from 'motia'
+import { z } from 'zod'
+
+export const config: StreamConfig = {
+  name: 'protectedStream',
+  schema: z.object({ data: z.string() }),
+  baseConfig: { storageType: 'default' },
+  canAccess: (subscription, authContext) => {
+    if (!authContext) return false
+    return authContext.permissions?.includes('read:stream')
+  },
+}
+```
+
+## Express App Customization
+
+Use the `app` callback to customize the Express application instance:
+
+```typescript
+import { config } from 'motia'
+import cors from 'cors'
+import helmet from 'helmet'
+
+export default config({
+  app: (app) => {
+    app.use(helmet())
+    app.use(cors({ origin: process.env.ALLOWED_ORIGINS?.split(',') }))
+    
+    app.get('/health', (_req, res) => {
+      res.json({ status: 'healthy' })
+    })
+  },
+})
+```
+
+## Complete Example
+
+```typescript
+import path from 'node:path'
+import { config, type MotiaPlugin, type MotiaPluginContext, type StreamAuthRequest } from 'motia'
+import { z } from 'zod'
+
+const statesPlugin = require('@motiadev/plugin-states/plugin')
+const logsPlugin = require('@motiadev/plugin-logs/plugin')
+
+const authContextSchema = z.object({
+  userId: z.string(),
+  role: z.enum(['admin', 'user']).optional(),
+})
+
+type AuthContext = z.infer<typeof authContextSchema>
+
+const tokens: Record<string, AuthContext> = {
+  'admin-token': { userId: 'admin-1', role: 'admin' },
+  'user-token': { userId: 'user-1', role: 'user' },
+}
+
+function extractAuthToken(request: StreamAuthRequest): string | undefined {
+  const protocol = request.headers['sec-websocket-protocol'] as string | undefined
+  if (protocol?.includes('Authorization')) {
+    const [, token] = protocol.split(',')
+    return token?.trim()
+  }
+
+  if (request.url) {
+    try {
+      const url = new URL(request.url)
+      return url.searchParams.get('authToken') ?? undefined
+    } catch {
+      return undefined
+    }
+  }
+
+  return undefined
+}
+
+export default config({
+  plugins: [statesPlugin, logsPlugin],
+  streamAuth: {
+    contextSchema: z.toJSONSchema(authContextSchema),
+    authenticate: async (request: StreamAuthRequest) => {
+      const token = extractAuthToken(request)
+      if (!token) return null
+
+      const context = tokens[token]
+      if (!context) throw new Error(`Invalid token: ${token}`)
+
+      return context
+    },
+  },
+})
+```
diff --git a/packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/realtime-streaming.mdc b/packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/realtime-streaming.mdc
@@ -18,6 +18,41 @@ It's called Streams.
 
 Creating a Stream means defining a data schema that will be stored and served to the clients who are subscribing.
 
+### StreamConfig Type Definition
+
+```typescript
+export type ZodInput = ZodObject<any> | ZodArray<any>
+export type StepSchemaInput = ZodInput | JsonSchema
+
+export type StreamSubscription = { groupId: string; id?: string }
+
+export interface StreamConfig {
+  /**
+   * The stream name, used on the client side to subscribe.
+   */
+  name: string
+
+  /**
+   * Schema for stream data. Accepts either:
+   * - Zod schema (ZodObject or ZodArray)
+   * - JSON Schema object
+   */
+  schema: StepSchemaInput
+
+  /**
+   * Storage configuration for the stream.
+   * Use 'default' for built-in storage or 'custom' with a factory function.
+   */
+  baseConfig: { storageType: 'default' } | { storageType: 'custom'; factory: () => MotiaStream<any> }
+
+  /**
+   * Optional: Access control callback to authorize subscriptions.
+   * Return true to allow access, false to deny.
+   */
+  canAccess?: (subscription: StreamSubscription, authContext: any) => boolean | Promise<boolean>
+}
+```
+
 ### TypeScript Example
 
 ```typescript
@@ -35,24 +70,8 @@ export const chatMessageSchema = z.object({
 export type ChatMessage = z.infer<typeof chatMessageSchema>
 
 export const config: StreamConfig = {
-  /**
-   * This is the stream name, it's extremely important to
-   * be used on the client side.
-   */
   name: 'chatMessage',
-
-  /**
-   * This is the schema of the data that will be stored in the stream.
-   * 
-   * It helps Motia to create the types on the steps to enforce the 
-   * streams objects are created correctly.
-   */
   schema: chatMessageSchema,
-
-  /**
-   * Let's not worry about base config for now, all streams
-   * have this storage type default
-   */
   baseConfig: { storageType: 'default' },
 }
 ```
@@ -106,6 +125,8 @@ Streams managers are automatically injected into the context of the steps.
 The interface of each stream is this
 
 ```typescript
+export type BaseStreamItem<TData = unknown> = TData & { id: string }
+
 interface MotiaStream<TData> {
   /**
    * Retrieves a single item from the stream
PATCH

echo "Gold patch applied."
