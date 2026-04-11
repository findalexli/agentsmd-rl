#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobe-chat

# Idempotent: skip if already applied
if grep -q '64_000' packages/model-runtime/src/core/anthropicCompatibleFactory/resolveMaxTokens.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.agents/skills/cli/SKILL.md b/.agents/skills/cli/SKILL.md
index 8555263d22e..444b3911f37 100644
--- a/.agents/skills/cli/SKILL.md
+++ b/.agents/skills/cli/SKILL.md
@@ -200,20 +200,85 @@ The base directory (`~/.lobehub/`) can be overridden with the `LOBEHUB_CLI_HOME`

 ## Development

+### Running in Dev Mode
+
+Dev mode uses `LOBEHUB_CLI_HOME=.lobehub-dev` to isolate credentials from the global `~/.lobehub/` directory, so dev and production configs never conflict.
+
+```bash
+# Run a command in dev mode (from apps/cli/)
+cd apps/cli && bun run dev -- <command>
+
+# This is equivalent to:
+LOBEHUB_CLI_HOME=.lobehub-dev bun src/index.ts <command>
+```
+
+### Connecting to Local Dev Server
+
+To test CLI against a local dev server (e.g. `localhost:3011`):
+
+**Step 1: Start the local server**
+
+```bash
+# From cloud repo root
+bun run dev
+# Server starts on http://localhost:3011 (or configured port)
+```
+
+**Step 2: Login to local server via Device Code Flow**
+
+```bash
+cd apps/cli && bun run dev -- login --server http://localhost:3011
+```
+
+This will:
+
+1. Call `POST http://localhost:3011/oidc/device/auth` to get a device code
+2. Print a URL like `http://localhost:3011/oidc/device?user_code=XXXX-YYYY`
+3. Open the URL in your browser — log in and authorize
+4. Save credentials to `apps/cli/.lobehub-dev/credentials.json`
+5. Save server URL to `apps/cli/.lobehub-dev/settings.json`
+
+After login, all subsequent `bun run dev -- <command>` calls will use the local server.
+
+**Step 3: Run commands against local server**
+
+```bash
+cd apps/cli && bun run dev -- task list
+cd apps/cli && bun run dev -- task create -i "Test task" -n "My Task"
+cd apps/cli && bun run dev -- agent list
+```
+
+**Troubleshooting:**
+
+- If login returns `invalid_grant`, make sure the local OIDC provider is properly configured (check `OIDC_*` env vars in `.env`)
+- If you get `UNAUTHORIZED` on API calls, your token may have expired — run `bun run dev -- login --server http://localhost:3011` again
+- Dev credentials are stored in `apps/cli/.lobehub-dev/` (gitignored), not in `~/.lobehub/`
+
+### Switching Between Local and Production
+
 ```bash
-# Run directly (dev mode, uses ~/.lobehub-dev for credentials)
+# Dev mode (local server) — uses .lobehub-dev/
 cd apps/cli && bun run dev -- <command>

-# Build
+# Production (app.lobehub.com) — uses ~/.lobehub/
+lh <command>
+```
+
+The two environments are completely isolated by different credential directories.
+
+### Build & Test
+
+```bash
+# Build CLI
 cd apps/cli && bun run build

-# Test (unit tests)
+# Unit tests
 cd apps/cli && bun run test

 # E2E tests (requires authenticated CLI)
 cd apps/cli && bunx vitest run e2e/kb.e2e.test.ts

-# Link globally for testing
+# Link globally for testing (installs lh/lobe/lobehub commands)
 cd apps/cli && bun run cli:link
 ```

diff --git a/.agents/skills/db-migrations/SKILL.md b/.agents/skills/db-migrations/SKILL.md
index 74055559024..3adcfd2f581 100644
--- a/.agents/skills/db-migrations/SKILL.md
+++ b/.agents/skills/db-migrations/SKILL.md
@@ -101,10 +101,6 @@ DROP TABLE "old_table";
 CREATE INDEX "users_email_idx" ON "users" ("email");
 ```

-## Step 4: Regenerate Client After SQL Edits
+## Step 4: Update Journal Tag

-After modifying the generated SQL (e.g., adding `IF NOT EXISTS`), regenerate the client:
-
-```bash
-bun run db:generate:client
-```
+After renaming the migration SQL file in Step 2, update the `tag` field in `packages/database/migrations/meta/_journal.json` to match the new filename (without `.sql` extension).
diff --git a/.agents/skills/trpc-router/SKILL.md b/.agents/skills/trpc-router/SKILL.md
new file mode 100644
index 00000000000..ea7ea888199
--- /dev/null
+++ b/.agents/skills/trpc-router/SKILL.md
@@ -0,0 +1,123 @@
+---
+name: trpc-router
+description: TRPC router development guide. Use when creating or modifying TRPC routers (src/server/routers/**), adding procedures, or working with server-side API endpoints. Triggers on TRPC router creation, procedure implementation, or API endpoint tasks.
+---
+
+# TRPC Router Guide
+
+## File Location
+
+- Routers: `src/server/routers/lambda/<domain>.ts`
+- Helpers: `src/server/routers/lambda/_helpers/`
+- Schemas: `src/server/routers/lambda/_schema/`
+
+## Router Structure
+
+### Imports
+
+```typescript
+import { TRPCError } from '@trpc/server';
+import { z } from 'zod';
+
+import { SomeModel } from '@/database/models/some';
+import { authedProcedure, router } from '@/libs/trpc/lambda';
+import { serverDatabase } from '@/libs/trpc/lambda/middleware';
+```
+
+### Middleware: Inject Models into ctx
+
+**Always use middleware to inject models into `ctx`** instead of creating `new Model(ctx.serverDB, ctx.userId)` inside every procedure.
+
+```typescript
+const domainProcedure = authedProcedure.use(serverDatabase).use(async (opts) => {
+  const { ctx } = opts;
+  return opts.next({
+    ctx: {
+      fooModel: new FooModel(ctx.serverDB, ctx.userId),
+      barModel: new BarModel(ctx.serverDB, ctx.userId),
+    },
+  });
+});
+```
+
+Then use `ctx.fooModel` in procedures:
+
+```typescript
+// Good
+const model = ctx.fooModel;
+
+// Bad - don't create models inside procedures
+const model = new FooModel(ctx.serverDB, ctx.userId);
+```
+
+**Exception**: When a model needs a different `userId` (e.g., watchdog iterating over multiple users' tasks), create it inline.
+
+### Procedure Pattern
+
+```typescript
+export const fooRouter = router({
+  // Query
+  find: domainProcedure.input(z.object({ id: z.string() })).query(async ({ input, ctx }) => {
+    try {
+      const item = await ctx.fooModel.findById(input.id);
+      if (!item) throw new TRPCError({ code: 'NOT_FOUND', message: 'Not found' });
+      return { data: item, success: true };
+    } catch (error) {
+      if (error instanceof TRPCError) throw error;
+      console.error('[foo:find]', error);
+      throw new TRPCError({
+        cause: error,
+        code: 'INTERNAL_SERVER_ERROR',
+        message: 'Failed to find item',
+      });
+    }
+  }),
+
+  // Mutation
+  create: domainProcedure.input(createSchema).mutation(async ({ input, ctx }) => {
+    try {
+      const item = await ctx.fooModel.create(input);
+      return { data: item, message: 'Created', success: true };
+    } catch (error) {
+      if (error instanceof TRPCError) throw error;
+      console.error('[foo:create]', error);
+      throw new TRPCError({
+        cause: error,
+        code: 'INTERNAL_SERVER_ERROR',
+        message: 'Failed to create',
+      });
+    }
+  }),
+});
+```
+
+### Aggregated Detail Endpoint
+
+For views that need multiple related data, create a single `detail` procedure that fetches everything in parallel:
+
+```typescript
+detail: domainProcedure.input(idInput).query(async ({ input, ctx }) => {
+  const item = await resolveOrThrow(ctx.fooModel, input.id);
+
+  const [children, related] = await Promise.all([
+    ctx.fooModel.findChildren(item.id),
+    ctx.barModel.findByFooId(item.id),
+  ]);
+
+  return {
+    data: { ...item, children, related },
+    success: true,
+  };
+}),
+```
+
+This avoids the CLI or frontend making N sequential requests.
+
+## Conventions
+
+- Return shape: `{ data, success: true }` for queries, `{ data?, message, success: true }` for mutations
+- Error handling: re-throw `TRPCError`, wrap others with `console.error` + new `TRPCError`
+- Input validation: use `zod` schemas, define at file top
+- Router name: `export const fooRouter = router({ ... })`
+- Procedure names: alphabetical order within the router object
+- Log prefix: `[domain:procedure]` format, e.g. `[task:create]`
diff --git a/packages/agent-tracing/src/viewer/index.ts b/packages/agent-tracing/src/viewer/index.ts
index bf68d31761b..544fe9dede8 100644
--- a/packages/agent-tracing/src/viewer/index.ts
+++ b/packages/agent-tracing/src/viewer/index.ts
@@ -818,6 +818,22 @@ export function renderStepDetail(
     }
   }

+  // Default view: show tool errors even without -t flag
+  if (!hasSpecificFlag && step.toolsResult) {
+    const failedResults = step.toolsResult.filter((tr) => tr.isSuccess === false);
+    if (failedResults.length > 0) {
+      lines.push('');
+      lines.push(bold(red('Errors:')));
+      for (const tr of failedResults) {
+        lines.push(`  ${red('✗')} ${cyan(tr.identifier || tr.apiName)}`);
+        if (tr.output) {
+          const output = tr.output.length > 500 ? tr.output.slice(0, 500) + '...' : tr.output;
+          lines.push(`    ${red(output)}`);
+        }
+      }
+    }
+  }
+
   if (options?.tools) {
     if (step.toolsCalling && step.toolsCalling.length > 0) {
       lines.push('');
diff --git a/packages/model-runtime/src/core/anthropicCompatibleFactory/generateObject.test.ts b/packages/model-runtime/src/core/anthropicCompatibleFactory/generateObject.test.ts
index 343811e2b3a..1651c834c49 100644
--- a/packages/model-runtime/src/core/anthropicCompatibleFactory/generateObject.test.ts
+++ b/packages/model-runtime/src/core/anthropicCompatibleFactory/generateObject.test.ts
@@ -55,7 +55,7 @@ describe('Anthropic generateObject', () => {

       expect(mockClient.messages.create).toHaveBeenCalledWith(
         expect.objectContaining({
-          max_tokens: 8192,
+          max_tokens: 64_000,
           messages: [{ content: 'Generate a person object', role: 'user' }],
           model: 'claude-3-5-sonnet-20241022',
           tool_choice: {
@@ -404,7 +404,7 @@ describe('Anthropic generateObject', () => {

       expect(mockClient.messages.create).toHaveBeenCalledWith(
         expect.objectContaining({
-          max_tokens: 8192,
+          max_tokens: 64_000,
           messages: [{ content: 'What is the weather and time in New York?', role: 'user' }],
           model: 'claude-3-5-sonnet-20241022',
           tool_choice: {
diff --git a/packages/model-runtime/src/core/anthropicCompatibleFactory/generateObject.ts b/packages/model-runtime/src/core/anthropicCompatibleFactory/generateObject.ts
index 348cc74c379..7dcd7c60f59 100644
--- a/packages/model-runtime/src/core/anthropicCompatibleFactory/generateObject.ts
+++ b/packages/model-runtime/src/core/anthropicCompatibleFactory/generateObject.ts
@@ -65,11 +65,11 @@ export const createAnthropicGenerateObject = async (
   }

   try {
-    log('calling Anthropic API with max_tokens: %d', 8192);
+    log('calling Anthropic API with max_tokens: %d', 64_000);

     const response = await client.messages.create(
       {
-        max_tokens: 8192,
+        max_tokens: 64_000,
         messages: anthropicMessages,
         model,
         system: systemPrompts,
diff --git a/packages/model-runtime/src/core/anthropicCompatibleFactory/resolveMaxTokens.ts b/packages/model-runtime/src/core/anthropicCompatibleFactory/resolveMaxTokens.ts
index 7e82682e17a..660916406ad 100644
--- a/packages/model-runtime/src/core/anthropicCompatibleFactory/resolveMaxTokens.ts
+++ b/packages/model-runtime/src/core/anthropicCompatibleFactory/resolveMaxTokens.ts
@@ -32,5 +32,5 @@ export const resolveMaxTokens = async ({

   const hasSmallContextWindow = smallContextWindowPatterns.some((pattern) => pattern.test(model));

-  return hasSmallContextWindow ? 4096 : 8192;
+  return hasSmallContextWindow ? 4096 : 64_000;
 };
diff --git a/packages/model-runtime/src/providers/bedrock/index.test.ts b/packages/model-runtime/src/providers/bedrock/index.test.ts
index 9c84c012ebe..9541a4215f9 100644
--- a/packages/model-runtime/src/providers/bedrock/index.test.ts
+++ b/packages/model-runtime/src/providers/bedrock/index.test.ts
@@ -477,7 +477,7 @@ describe('LobeBedrockAI', () => {
             accept: 'application/json',
             body: JSON.stringify({
               anthropic_version: 'bedrock-2023-05-31',
-              max_tokens: 8192,
+              max_tokens: 64_000,
               messages: [
                 {
                   content: [
@@ -520,7 +520,7 @@ describe('LobeBedrockAI', () => {
             accept: 'application/json',
             body: JSON.stringify({
               anthropic_version: 'bedrock-2023-05-31',
-              max_tokens: 8192,
+              max_tokens: 64_000,
               messages: [
                 {
                   content: [
@@ -609,7 +609,7 @@ describe('LobeBedrockAI', () => {
             accept: 'application/json',
             body: JSON.stringify({
               anthropic_version: 'bedrock-2023-05-31',
-              max_tokens: 8192,
+              max_tokens: 64_000,
               messages: [
                 {
                   content: [
@@ -653,7 +653,7 @@ describe('LobeBedrockAI', () => {
             accept: 'application/json',
             body: JSON.stringify({
               anthropic_version: 'bedrock-2023-05-31',
-              max_tokens: 8192,
+              max_tokens: 64_000,
               messages: [
                 {
                   content: [
diff --git a/packages/types/src/agent/chatConfig.ts b/packages/types/src/agent/chatConfig.ts
index a48f6d8a2bf..17386d11955 100644
--- a/packages/types/src/agent/chatConfig.ts
+++ b/packages/types/src/agent/chatConfig.ts
@@ -203,7 +203,7 @@ export const AgentChatConfigSchema = z
     thinkingLevel3: z.enum(['low', 'medium', 'high']).optional(),
     thinkingLevel4: z.enum(['minimal', 'high']).optional(),
     thinkingLevel5: z.enum(['minimal', 'low', 'medium', 'high']).optional(),
-    toolResultMaxLength: z.number().default(6000),
+    toolResultMaxLength: z.number().default(25000),
     urlContext: z.boolean().optional(),
     useModelBuiltinSearch: z.boolean().optional(),
   })
diff --git a/src/server/modules/AgentRuntime/RuntimeExecutors.ts b/src/server/modules/AgentRuntime/RuntimeExecutors.ts
index 558a35c4bcc..dd51a2d7578 100644
--- a/src/server/modules/AgentRuntime/RuntimeExecutors.ts
+++ b/src/server/modules/AgentRuntime/RuntimeExecutors.ts
@@ -343,6 +343,7 @@ export const createRuntimeExecutors = (

       // Construct ChatStreamPayload
       const stream = ctx.stream ?? true;
+
       const chatPayload = { messages: processedMessages, model, stream, tools };

       log(
diff --git a/src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts b/src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts
index f7233705864..3eed3dbcddd 100644
--- a/src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts
+++ b/src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts
@@ -328,7 +328,7 @@ describe('createServerAgentToolsEngine', () => {
   });

   describe('LocalSystem tool enable rules', () => {
-    it('should disable LocalSystem tool when no device context is provided', () => {
+    it('should disable LocalSystem when no device context is provided', () => {
       const context = createMockContext();
       const engine = createServerAgentToolsEngine(context, {
         agentConfig: { plugins: [LocalSystemManifest.identifier] },
@@ -345,11 +345,11 @@ describe('createServerAgentToolsEngine', () => {
       expect(result.enabledToolIds).not.toContain(LocalSystemManifest.identifier);
     });

-    it('should enable LocalSystem tool when gateway configured AND device online', () => {
+    it('should enable LocalSystem when gateway configured, device online AND auto-activated', () => {
       const context = createMockContext();
       const engine = createServerAgentToolsEngine(context, {
         agentConfig: { plugins: [LocalSystemManifest.identifier] },
-        deviceContext: { gatewayConfigured: true, deviceOnline: true },
+        deviceContext: { gatewayConfigured: true, deviceOnline: true, autoActivated: true },
         model: 'gpt-4',
         provider: 'openai',
       });
@@ -363,11 +363,50 @@ describe('createServerAgentToolsEngine', () => {
       expect(result.enabledToolIds).toContain(LocalSystemManifest.identifier);
     });

-    it('should disable LocalSystem tool when gateway configured but device offline', () => {
+    it('should disable LocalSystem when device online but NOT auto-activated', () => {
+      const context = createMockContext();
+      const engine = createServerAgentToolsEngine(context, {
+        agentConfig: { plugins: [LocalSystemManifest.identifier] },
+        deviceContext: { gatewayConfigured: true, deviceOnline: true },
+        model: 'gpt-4',
+        provider: 'openai',
+      });
+
+      const result = engine.generateToolsDetailed({
+        toolIds: [LocalSystemManifest.identifier],
+        model: 'gpt-4',
+        provider: 'openai',
+      });
+
+      expect(result.enabledToolIds).not.toContain(LocalSystemManifest.identifier);
+    });
+
+    it('should disable LocalSystem when gateway configured but device offline', () => {
+      const context = createMockContext();
+      const engine = createServerAgentToolsEngine(context, {
+        agentConfig: { plugins: [LocalSystemManifest.identifier] },
+        deviceContext: { gatewayConfigured: true, deviceOnline: false, autoActivated: true },
+        model: 'gpt-4',
+        provider: 'openai',
+      });
+
+      const result = engine.generateToolsDetailed({
+        toolIds: [LocalSystemManifest.identifier],
+        model: 'gpt-4',
+        provider: 'openai',
+      });
+
+      expect(result.enabledToolIds).not.toContain(LocalSystemManifest.identifier);
+    });
+
+    it('should disable LocalSystem when runtimeMode is explicitly set to cloud', () => {
       const context = createMockContext();
       const engine = createServerAgentToolsEngine(context, {
-        agentConfig: { plugins: [LocalSystemManifest.identifier] },
-        deviceContext: { gatewayConfigured: true, deviceOnline: false },
+        agentConfig: {
+          plugins: [LocalSystemManifest.identifier],
+          chatConfig: { runtimeEnv: { runtimeMode: { desktop: 'cloud' } } },
+        },
+        deviceContext: { gatewayConfigured: true, deviceOnline: true, autoActivated: true },
         model: 'gpt-4',
         provider: 'openai',
       });
@@ -383,7 +422,7 @@ describe('createServerAgentToolsEngine', () => {
   });

   describe('RemoteDevice tool enable rules', () => {
-    it('should enable RemoteDevice tool when gateway configured', () => {
+    it('should enable RemoteDevice when gateway configured and no device auto-activated', () => {
       const context = createMockContext();
       const engine = createServerAgentToolsEngine(context, {
         agentConfig: { plugins: [RemoteDeviceManifest.identifier] },
@@ -401,7 +440,7 @@ describe('createServerAgentToolsEngine', () => {
       expect(result.enabledToolIds).toContain(RemoteDeviceManifest.identifier);
     });

-    it('should disable RemoteDevice tool when gateway not configured', () => {
+    it('should disable RemoteDevice when gateway not configured', () => {
       const context = createMockContext();
       const engine = createServerAgentToolsEngine(context, {
         agentConfig: { plugins: [RemoteDeviceManifest.identifier] },
@@ -418,5 +457,67 @@ describe('createServerAgentToolsEngine', () => {

       expect(result.enabledToolIds).not.toContain(RemoteDeviceManifest.identifier);
     });
+
+    it('should disable RemoteDevice when device is already auto-activated', () => {
+      const context = createMockContext();
+      const engine = createServerAgentToolsEngine(context, {
+        agentConfig: { plugins: [RemoteDeviceManifest.identifier] },
+        deviceContext: { gatewayConfigured: true, autoActivated: true },
+        model: 'gpt-4',
+        provider: 'openai',
+      });
+
+      const result = engine.generateToolsDetailed({
+        toolIds: [RemoteDeviceManifest.identifier],
+        model: 'gpt-4',
+        provider: 'openai',
+      });
+
+      expect(result.enabledToolIds).not.toContain(RemoteDeviceManifest.identifier);
+    });
+  });
+
+  describe('LocalSystem + RemoteDevice interaction', () => {
+    it('should enable only RemoteDevice (not LocalSystem) when device online but not auto-activated', () => {
+      const context = createMockContext();
+      const engine = createServerAgentToolsEngine(context, {
+        agentConfig: {
+          plugins: [LocalSystemManifest.identifier, RemoteDeviceManifest.identifier],
+        },
+        deviceContext: { gatewayConfigured: true, deviceOnline: true },
+        model: 'gpt-4',
+        provider: 'openai',
+      });
+
+      const result = engine.generateToolsDetailed({
+        toolIds: [LocalSystemManifest.identifier, RemoteDeviceManifest.identifier],
+        model: 'gpt-4',
+        provider: 'openai',
+      });
+
+      expect(result.enabledToolIds).not.toContain(LocalSystemManifest.identifier);
+      expect(result.enabledToolIds).toContain(RemoteDeviceManifest.identifier);
+    });
+
+    it('should enable only LocalSystem (not RemoteDevice) when device auto-activated', () => {
+      const context = createMockContext();
+      const engine = createServerAgentToolsEngine(context, {
+        agentConfig: {
+          plugins: [LocalSystemManifest.identifier, RemoteDeviceManifest.identifier],
+        },
+        deviceContext: { gatewayConfigured: true, deviceOnline: true, autoActivated: true },
+        model: 'gpt-4',
+        provider: 'openai',
+      });
+
+      const result = engine.generateToolsDetailed({
+        toolIds: [LocalSystemManifest.identifier, RemoteDeviceManifest.identifier],
+        model: 'gpt-4',
+        provider: 'openai',
+      });
+
+      expect(result.enabledToolIds).toContain(LocalSystemManifest.identifier);
+      expect(result.enabledToolIds).not.toContain(RemoteDeviceManifest.identifier);
+    });
   });
 });
diff --git a/src/server/modules/Mecha/AgentToolsEngine/index.ts b/src/server/modules/Mecha/AgentToolsEngine/index.ts
index 086f217d31f..1cffcc42f95 100644
--- a/src/server/modules/Mecha/AgentToolsEngine/index.ts
+++ b/src/server/modules/Mecha/AgentToolsEngine/index.ts
@@ -135,7 +135,8 @@ export const createServerAgentToolsEngine = (
         [LocalSystemManifest.identifier]:
           runtimeMode === 'local' &&
           !!deviceContext?.gatewayConfigured &&
-          !!deviceContext?.deviceOnline,
+          !!deviceContext?.deviceOnline &&
+          !!deviceContext?.autoActivated,
         [MemoryManifest.identifier]: globalMemoryEnabled,
         [RemoteDeviceManifest.identifier]:
           !!deviceContext?.gatewayConfigured && !deviceContext?.autoActivated,

PATCH

echo "Patch applied successfully."
