#!/usr/bin/env bash
set -euo pipefail

cd /workspace/backstage

# Idempotent: skip if already applied
if grep -q 'mcp.server.operation.duration' plugins/mcp-actions-backend/src/services/McpService.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Create the new metrics.ts file
cat > plugins/mcp-actions-backend/src/metrics.ts <<'METRICSEOF'
/*
 * Copyright 2026 The Backstage Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { MetricAttributes } from '@backstage/backend-plugin-api/alpha';

/**
 * Attributes for mcp.server.operation.duration
 * Following OTel requirement levels from the spec
 *
 * @see https://opentelemetry.io/docs/specs/semconv/gen-ai/mcp/#metric-mcpserveroperationduration
 */
export interface McpServerOperationAttributes extends MetricAttributes {
  // Required
  'mcp.method.name': string;

  // Conditionally Required
  'error.type'?: string;
  'gen_ai.tool.name'?: string;
  'gen_ai.prompt.name'?: string;
  'mcp.resource.uri'?: string;
  'rpc.response.status_code'?: string;

  // Recommended
  'gen_ai.operation.name'?: 'execute_tool';
  'mcp.protocol.version'?: string;
  'mcp.session.id'?: string;
  'network.transport'?: 'tcp' | 'quic' | 'pipe' | 'unix';
  'network.protocol.name'?: string;
  'network.protocol.version'?: string;
}

/**
 * Attributes for mcp.server.session.duration
 * Following OTel requirement levels from the spec
 *
 * @see https://opentelemetry.io/docs/specs/semconv/gen-ai/mcp/#metric-mcpserversessionduration
 */
export interface McpServerSessionAttributes extends MetricAttributes {
  // Conditionally Required
  'error.type'?: string;

  // Recommended
  'mcp.protocol.version'?: string;
  'network.transport'?: 'tcp' | 'quic' | 'pipe' | 'unix';
  'network.protocol.name'?: string;
  'network.protocol.version'?: string;
}

/**
 * OTel recommended bucket boundaries for MCP metrics
 *
 * @remarks
 *
 * Based on the MCP metrics defined in the OTel semantic conventions v1.39.0
 * @see https://opentelemetry.io/docs/specs/semconv/gen-ai/mcp/
 *
 */
export const bucketBoundaries = [
  0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 30, 60, 120, 300,
];
METRICSEOF

# Apply the diff to McpService.ts
cat > /tmp/mcpservice.patch <<'PATCH'
--- a/plugins/mcp-actions-backend/src/services/McpService.ts
+++ b/plugins/mcp-actions-backend/src/services/McpService.ts
@@ -20,21 +20,43 @@ import {
   CallToolRequestSchema,
 } from '@modelcontextprotocol/sdk/types.js';
 import { JsonObject } from '@backstage/types';
-import { ActionsService } from '@backstage/backend-plugin-api/alpha';
+import {
+  ActionsService,
+  MetricsServiceHistogram,
+  MetricsService,
+} from '@backstage/backend-plugin-api/alpha';
 import { version } from '@backstage/plugin-mcp-actions-backend/package.json';
 import { NotFoundError } from '@backstage/errors';
+import { performance } from 'node:perf_hooks';

 import { handleErrors } from './handleErrors';
+import { bucketBoundaries, McpServerOperationAttributes } from '../metrics';

 export class McpService {
   private readonly actions: ActionsService;
+  private readonly operationDuration: MetricsServiceHistogram<McpServerOperationAttributes>;

-  constructor(actions: ActionsService) {
+  constructor(actions: ActionsService, metrics: MetricsService) {
     this.actions = actions;
+    this.operationDuration =
+      metrics.createHistogram<McpServerOperationAttributes>(
+        'mcp.server.operation.duration',
+        {
+          description: 'MCP request duration as observed on the receiver',
+          unit: 's',
+          advice: { explicitBucketBoundaries: bucketBoundaries },
+        },
+      );
   }

-  static async create({ actions }: { actions: ActionsService }) {
-    return new McpService(actions);
+  static async create({
+    actions,
+    metrics,
+  }: {
+    actions: ActionsService;
+    metrics: MetricsService;
+  }) {
+    return new McpService(actions, metrics);
   }

   getServer({ credentials }: { credentials: BackstageCredentials }) {
@@ -48,57 +70,101 @@ export class McpService {
     );

     server.setRequestHandler(ListToolsRequestSchema, async () => {
-      // TODO: switch this to be configuration based later
-      const { actions } = await this.actions.list({ credentials });
-
-      return {
-        tools: actions.map(action => ({
-          inputSchema: action.schema.input,
-          // todo(blam): this is unfortunately not supported by most clients yet.
-          // When this is provided you need to provide structuredContent instead.
-          // outputSchema: action.schema.output,
-          name: action.name,
-          description: action.description,
-          annotations: {
-            title: action.title,
-            destructiveHint: action.attributes.destructive,
-            idempotentHint: action.attributes.idempotent,
-            readOnlyHint: action.attributes.readOnly,
-            openWorldHint: false,
-          },
-        })),
-      };
+      const startTime = performance.now();
+      let errorType: string | undefined;
+
+      try {
+        // TODO: switch this to be configuration based later
+        const { actions } = await this.actions.list({ credentials });
+
+        return {
+          tools: actions.map(action => ({
+            inputSchema: action.schema.input,
+            // todo(blam): this is unfortunately not supported by most clients yet.
+            // When this is provided you need to provide structuredContent instead.
+            // outputSchema: action.schema.output,
+            name: action.name,
+            description: action.description,
+            annotations: {
+              title: action.title,
+              destructiveHint: action.attributes.destructive,
+              idempotentHint: action.attributes.idempotent,
+              readOnlyHint: action.attributes.readOnly,
+              openWorldHint: false,
+            },
+          })),
+        };
+      } catch (err) {
+        errorType = err instanceof Error ? err.name : 'Error';
+        throw err;
+      } finally {
+        const durationSeconds = (performance.now() - startTime) / 1000;
+
+        this.operationDuration.record(durationSeconds, {
+          'mcp.method.name': 'tools/list',
+          ...(errorType && { 'error.type': errorType }),
+        });
+      }
     });

     server.setRequestHandler(CallToolRequestSchema, async ({ params }) => {
-      return handleErrors(async () => {
-        const { actions } = await this.actions.list({ credentials });
-        const action = actions.find(a => a.name === params.name);
+      const startTime = performance.now();
+      let errorType: string | undefined;
+      let isError = false;

-        if (!action) {
-          throw new NotFoundError(`Action "${params.name}" not found`);
-        }
+      try {
+        const result = await handleErrors(async () => {
+          const { actions } = await this.actions.list({ credentials });
+          const action = actions.find(a => a.name === params.name);
+
+          if (!action) {
+            throw new NotFoundError(`Action "${params.name}" not found`);
+          }
+
+          const { output } = await this.actions.invoke({
+            id: action.id,
+            input: params.arguments as JsonObject,
+            credentials,
+          });

-        const { output } = await this.actions.invoke({
-          id: action.id,
-          input: params.arguments as JsonObject,
-          credentials,
+          return {
+            // todo(blam): unfortunately structuredContent is not supported by most clients yet.
+            // so the validation for the output happens in the default actions registry
+            // and we return it as json text instead for now.
+            content: [
+              {
+                type: 'text',
+                text: ['```json', JSON.stringify(output, null, 2), '```'].join(
+                  '\n',
+                ),
+              },
+            ],
+          };
         });

-        return {
-          // todo(blam): unfortunately structuredContent is not supported by most clients yet.
-          // so the validation for the output happens in the default actions registry
-          // and we return it as json text instead for now.
-          content: [
-            {
-              type: 'text',
-              text: ['```json', JSON.stringify(output, null, 2), '```'].join(
-                '\n',
-              ),
-            },
-          ],
-        };
-      });
+        isError = !!(result as { isError?: boolean })?.isError;
+        return result;
+      } catch (err) {
+        errorType = err instanceof Error ? err.name : 'Error';
+        throw err;
+      } finally {
+        const durationSeconds = (performance.now() - startTime) / 1000;
+
+        // Determine error.type per OTel MCP spec:
+        // - Thrown exceptions use the error name
+        // - CallToolResult with isError=true uses 'tool_error'
+        let errorAttribute: string | undefined = errorType;
+        if (!errorAttribute && isError) {
+          errorAttribute = 'tool_error';
+        }
+
+        this.operationDuration.record(durationSeconds, {
+          'mcp.method.name': 'tools/call',
+          'gen_ai.tool.name': params.name,
+          'gen_ai.operation.name': 'execute_tool',
+          ...(errorAttribute && { 'error.type': errorAttribute }),
+        });
+      }
     });

     return server;
PATCH

git apply /tmp/mcpservice.patch

# Apply the diff to plugin.ts
cat > /tmp/plugin.patch <<'PATCH'
--- a/plugins/mcp-actions-backend/src/plugin.ts
+++ b/plugins/mcp-actions-backend/src/plugin.ts
@@ -25,6 +25,7 @@ import { createSseRouter } from './routers/createSseRouter';
 import {
   actionsRegistryServiceRef,
   actionsServiceRef,
+  metricsServiceRef,
 } from '@backstage/backend-plugin-api/alpha';

 /**
@@ -46,6 +47,7 @@ export const mcpPlugin = createBackendPlugin({
         rootRouter: coreServices.rootHttpRouter,
         discovery: coreServices.discovery,
         config: coreServices.rootConfig,
+        metrics: metricsServiceRef,
       },
       async init({
         actions,
@@ -55,9 +57,11 @@ export const mcpPlugin = createBackendPlugin({
         rootRouter,
         discovery,
         config,
+        metrics,
       }) {
         const mcpService = await McpService.create({
           actions,
+          metrics,
         });

         const sseRouter = createSseRouter({
@@ -69,6 +73,7 @@ export const mcpPlugin = createBackendPlugin({
           mcpService,
           httpAuth,
           logger,
+          metrics,
         });

         const router = Router();
PATCH

git apply /tmp/plugin.patch

# Apply the diff to createStreamableRouter.ts
cat > /tmp/router.patch <<'PATCH'
--- a/plugins/mcp-actions-backend/src/routers/createStreamableRouter.ts
+++ b/plugins/mcp-actions-backend/src/routers/createStreamableRouter.ts
@@ -15,23 +15,47 @@
  */
 import PromiseRouter from 'express-promise-router';
 import { Router } from 'express';
+import { performance } from 'node:perf_hooks';
 import { McpService } from '../services/McpService';
 import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
+import { LATEST_PROTOCOL_VERSION } from '@modelcontextprotocol/sdk/types.js';
 import { HttpAuthService, LoggerService } from '@backstage/backend-plugin-api';
 import { isError } from '@backstage/errors';
+import { MetricsService } from '@backstage/backend-plugin-api/alpha';
+import { bucketBoundaries, McpServerSessionAttributes } from '../metrics';

 export const createStreamableRouter = ({
   mcpService,
   httpAuth,
   logger,
+  metrics,
 }: {
   mcpService: McpService;
   logger: LoggerService;
   httpAuth: HttpAuthService;
+  metrics: MetricsService;
 }): Router => {
   const router = PromiseRouter();

+  const sessionDuration = metrics.createHistogram<McpServerSessionAttributes>(
+    'mcp.server.session.duration',
+    {
+      description:
+        'The duration of the MCP session as observed on the MCP server',
+      unit: 's',
+      advice: { explicitBucketBoundaries: bucketBoundaries },
+    },
+  );
+
   router.post('/', async (req, res) => {
+    const sessionStart = performance.now();
+
+    const baseAttributes: McpServerSessionAttributes = {
+      'mcp.protocol.version': LATEST_PROTOCOL_VERSION,
+      'network.transport': 'tcp',
+      'network.protocol.name': 'http',
+    };
+
     try {
       const server = mcpService.getServer({
         credentials: await httpAuth.credentials(req),
@@ -49,8 +73,14 @@ export const createStreamableRouter = ({
       res.on('close', () => {
         transport.close();
         server.close();
+
+        const durationSeconds = (performance.now() - sessionStart) / 1000;
+
+        sessionDuration.record(durationSeconds, baseAttributes);
       });
     } catch (error) {
+      const errorType = isError(error) ? error.name : 'Error';
+
       if (isError(error)) {
         logger.error(error.message);
       }
@@ -65,6 +95,13 @@ export const createStreamableRouter = ({
           id: null,
         });
       }
+
+      const durationSeconds = (performance.now() - sessionStart) / 1000;
+
+      sessionDuration.record(durationSeconds, {
+        ...baseAttributes,
+        'error.type': errorType,
+      });
     }
   });

PATCH

git apply /tmp/router.patch

# Apply README.md changes
cat > /tmp/readme.patch <<'PATCH'
--- a/plugins/mcp-actions-backend/README.md
+++ b/plugins/mcp-actions-backend/README.md
@@ -75,7 +75,7 @@ export const myPlugin = createBackendPlugin({

 When errors are thrown from MCP actions, the backend will handle and surface error message for any error from `@backstage/errors`. Unknown errors will be handled by `@modelcontextprotocol/sdk`'s default error handling, which may result in a generic `500 Server Error` being returned. As a result, we recommend using errors from `@backstage/errors` when applicable.

-See https://backstage.io/api/stable/modules/_backstage_errors.html for a full list of supported errors.
+See [Backstage Errors](https://backstage.io/docs/reference/errors/) for a full list of supported errors.

 When writing MCP tools, use the appropriate error from `@backstage/errors` when applicable:

@@ -178,6 +178,13 @@ There's a few different ways to configure MCP tools, but here's a snippet of the
 }
 ```

+## Metrics
+
+The MCP Actions Backend emits metrics for the following operations:
+
+- `mcp.server.operation.duration`: The duration taken to process an individual MCP operation
+- `mcp.server.session.duration`: The duration of the MCP session from the perspective of the server
+
 ## Development

 This plugin backend can be started in a standalone mode from directly in this package with `yarn start`. It is a limited setup that is most convenient when developing the plugin backend itself.
PATCH

git apply /tmp/readme.patch

# Create changeset file
mkdir -p .changeset
cat > .changeset/swift-ravens-jog.md <<'CHANGESETEOF'
---
'@backstage/plugin-mcp-actions-backend': patch
---

Adds two new metrics to track MCP server operations and sessions.

- `mcp.server.operation.duration`: The duration taken to process an individual MCP operation
- `mcp.server.session.duration`: The duration of the MCP session from the perspective of the server
CHANGESETEOF

echo "Patch applied successfully."
