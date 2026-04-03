#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'private _raw: boolean' packages/playwright-core/src/tools/backend/response.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/playwright-core/src/tools/backend/browserBackend.ts b/packages/playwright-core/src/tools/backend/browserBackend.ts
index 222b6e26cbaa1..d972782850b92 100644
--- a/packages/playwright-core/src/tools/backend/browserBackend.ts
+++ b/packages/playwright-core/src/tools/backend/browserBackend.ts
@@ -62,8 +62,9 @@ export class BrowserBackend implements ServerBackend {
     // eslint-disable-next-line no-restricted-syntax
     const parsedArguments = tool.schema.inputSchema.parse(rawArguments) as any;
     const cwd = rawArguments._meta?.cwd;
+    const raw = !!rawArguments._meta?.raw;
     const context = this._context!;
-    const response = new Response(context, name, parsedArguments, cwd);
+    const response = new Response(context, name, parsedArguments, { relativeTo: cwd, raw });
     context.setRunningTool(name);
     let responseObject: mcpServer.CallToolResult;
     try {
diff --git a/packages/playwright-core/src/tools/backend/evaluate.ts b/packages/playwright-core/src/tools/backend/evaluate.ts
index 0881ac3b65d0a..c675807c6a383 100644
--- a/packages/playwright-core/src/tools/backend/evaluate.ts
+++ b/packages/playwright-core/src/tools/backend/evaluate.ts
@@ -71,6 +71,8 @@ const evaluate = defineTabTool({

       const text = JSON.stringify(evalResult.result, null, 2) ?? 'undefined';
       await response.addResult('Evaluation result', text, { prefix: 'result', ext: 'json', suggestedFilename: params.filename });
+    }).catch(e => {
+      response.addError(e instanceof Error ? e.message : String(e));
     });
   },
 });
diff --git a/packages/playwright-core/src/tools/backend/response.ts b/packages/playwright-core/src/tools/backend/response.ts
index 3d7218c194e97..08806c106a429 100644
--- a/packages/playwright-core/src/tools/backend/response.ts
+++ b/packages/playwright-core/src/tools/backend/response.ts
@@ -55,12 +55,14 @@ export class Response {
   readonly toolArgs: Record<string, any>;
   private _clientWorkspace: string;
   private _imageResults: { data: Buffer, imageType: 'png' | 'jpeg' }[] = [];
+  private _raw: boolean;

-  constructor(context: Context, toolName: string, toolArgs: Record<string, any>, relativeTo?: string) {
+  constructor(context: Context, toolName: string, toolArgs: Record<string, any>, options?: { relativeTo?: string, raw?: boolean }) {
     this._context = context;
     this.toolName = toolName;
     this.toolArgs = toolArgs;
-    this._clientWorkspace = relativeTo ?? context.options.cwd;
+    this._clientWorkspace = options?.relativeTo ?? context.options.cwd;
+    this._raw = options?.raw ?? false;
   }

   private _computRelativeTo(fileName: string): string {
@@ -150,18 +152,24 @@ export class Response {


   async serialize(): Promise<CallToolResult> {
-    const sections = await this._build();
+    const allSections = await this._build();
+    const rawSections = ['Error', 'Result', 'Snapshot'] as const;
+    const sections = this._raw ? allSections.filter(section => rawSections.includes(section.title as typeof rawSections[number])) : allSections;

     const text: string[] = [];
     for (const section of sections) {
       if (!section.content.length)
         continue;
-      text.push(`### ${section.title}`);
-      if (section.codeframe)
-        text.push(`\`\`\`${section.codeframe}`);
-      text.push(...section.content);
-      if (section.codeframe)
-        text.push('```');
+      if (!this._raw) {
+        text.push(`### ${section.title}`);
+        if (section.codeframe)
+          text.push(`\`\`\`${section.codeframe}`);
+        text.push(...section.content);
+        if (section.codeframe)
+          text.push('```');
+      } else {
+        text.push(...section.content);
+      }
     }

     const content: (TextContent | ImageContent)[] = [
diff --git a/packages/playwright-core/src/tools/cli-client/program.ts b/packages/playwright-core/src/tools/cli-client/program.ts
index 38ff5079a63c8..9721950d050b1 100644
--- a/packages/playwright-core/src/tools/cli-client/program.ts
+++ b/packages/playwright-core/src/tools/cli-client/program.ts
@@ -33,6 +33,7 @@ import type { MinimistArgs } from './minimist';

 type GlobalOptions = {
   help?: boolean;
+  raw?: boolean;
   session?: string;
   version?: boolean;
 };
@@ -56,6 +57,7 @@ const globalOptions: (keyof (GlobalOptions & OpenOptions))[] = [
   'help',
   'persistent',
   'profile',
+  'raw',
   'session',
   'version',
 ];
@@ -63,6 +65,7 @@ const globalOptions: (keyof (GlobalOptions & OpenOptions))[] = [
 const booleanOptions: (keyof (GlobalOptions & OpenOptions & { all?: boolean }))[] = [
   'all',
   'help',
+  'raw',
   'version',
 ];

@@ -192,10 +195,11 @@ async function startSession(sessionName: string, registry: Registry, clientInfo:
 }

 async function runInSession(entry: SessionFile, clientInfo: ClientInfo, args: MinimistArgs) {
+  const raw = !!args.raw;
   for (const globalOption of globalOptions)
     delete args[globalOption];
   const session = new Session(entry);
-  const result = await session.run(clientInfo, args);
+  const result = await session.run(clientInfo, args, { raw });
   console.log(result.text);
 }

diff --git a/packages/playwright-core/src/tools/cli-client/session.ts b/packages/playwright-core/src/tools/cli-client/session.ts
index f80f0f427d332..5864b5d771150 100644
--- a/packages/playwright-core/src/tools/cli-client/session.ts
+++ b/packages/playwright-core/src/tools/cli-client/session.ts
@@ -43,14 +43,14 @@ export class Session {
     return compareSemver(clientInfo.version, this.config.version) >= 0;
   }

-  async run(clientInfo: ClientInfo, args: MinimistArgs): Promise<{ text: string }> {
+  async run(clientInfo: ClientInfo, args: MinimistArgs, options?: { raw?: boolean }): Promise<{ text: string }> {
     if (!this.isCompatible(clientInfo))
       throw new Error(`Client is v${clientInfo.version}, session '${this.name}' is v${this.config.version}. Run\n\n  playwright-cli${this.name !== 'default' ? ` -s=${this.name}` : ''} open\n\nto restart the browser session.`);

     const { socket } = await this._connect();
     if (!socket)
       throw new Error(`Browser '${this.name}' is not open. Run\n\n  playwright-cli${this.name !== 'default' ? ` -s=${this.name}` : ''} open\n\nto start the browser session.`);
-    return await SocketConnectionClient.sendAndClose(socket, 'run', { args, cwd: process.cwd() });
+    return await SocketConnectionClient.sendAndClose(socket, 'run', { args, cwd: process.cwd(), raw: options?.raw });
   }

   async stop(quiet: boolean = false): Promise<void> {
diff --git a/packages/playwright-core/src/tools/cli-client/skill/SKILL.md b/packages/playwright-core/src/tools/cli-client/skill/SKILL.md
index 19a817069aeee..fbf1536a67a33 100644
--- a/packages/playwright-core/src/tools/cli-client/skill/SKILL.md
+++ b/packages/playwright-core/src/tools/cli-client/skill/SKILL.md
@@ -160,6 +160,21 @@ playwright-cli video-chapter "Chapter Title" --description="Details" --duration=
 playwright-cli video-stop
 ```

+## Raw output
+
+The global `--raw` option strips page status, generated code, and snapshot sections from the output, returning only the result value. Use it to pipe command output into other tools. Commands that don't produce output return nothing.
+
+```bash
+playwright-cli --raw eval "JSON.stringify(performance.timing)" | jq '.loadEventEnd - .navigationStart'
+playwright-cli --raw eval "JSON.stringify([...document.querySelectorAll('a')].map(a => a.href))" > links.json
+playwright-cli --raw snapshot > before.yml
+playwright-cli click e5
+playwright-cli --raw snapshot > after.yml
+diff before.yml after.yml
+TOKEN=$(playwright-cli --raw cookie-get session_id)
+playwright-cli --raw localstorage-get theme
+```
+
 ## Open parameters
 ```bash
 # Use specific browser when creating session
diff --git a/packages/playwright-core/src/tools/cli-daemon/daemon.ts b/packages/playwright-core/src/tools/cli-daemon/daemon.ts
index 15cb5df3e17cd..855b349082a96 100644
--- a/packages/playwright-core/src/tools/cli-daemon/daemon.ts
+++ b/packages/playwright-core/src/tools/cli-daemon/daemon.ts
@@ -89,8 +89,7 @@ export async function startCliDaemonServer(
             await sendAck();
         } else if (method === 'run') {
           const { toolName, toolParams } = parseCliCommand(params.args);
-          if (params.cwd)
-            toolParams._meta = { cwd: params.cwd };
+          toolParams._meta = { cwd: params.cwd, raw: params.raw };
           const response = await backend.callTool(toolName, toolParams);
           await connection.send({ id, result: formatResult(response) });
         } else {
diff --git a/packages/playwright-core/src/tools/cli-daemon/helpGenerator.ts b/packages/playwright-core/src/tools/cli-daemon/helpGenerator.ts
index aed0ddacd1502..ca85c7a943e77 100644
--- a/packages/playwright-core/src/tools/cli-daemon/helpGenerator.ts
+++ b/packages/playwright-core/src/tools/cli-daemon/helpGenerator.ts
@@ -105,6 +105,7 @@ export function generateHelp() {

   lines.push('\nGlobal options:');
   lines.push(formatWithGap('  --help [command]', 'print help'));
+  lines.push(formatWithGap('  --raw', 'output only the result value, without status and code'));
   lines.push(formatWithGap('  --version', 'print version'));

   return lines.join('\n');

PATCH

echo "Patch applied successfully."
