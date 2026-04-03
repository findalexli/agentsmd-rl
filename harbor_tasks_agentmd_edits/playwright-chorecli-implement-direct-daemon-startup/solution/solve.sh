#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'throwBrowserIsNotInstalledError' packages/playwright/src/mcp/browser/browserContextFactory.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/playwright/src/mcp/browser/browserContextFactory.ts b/packages/playwright/src/mcp/browser/browserContextFactory.ts
index fe79c2282a141..4feb0835f2cdf 100644
--- a/packages/playwright/src/mcp/browser/browserContextFactory.ts
+++ b/packages/playwright/src/mcp/browser/browserContextFactory.ts
@@ -140,7 +140,7 @@ class IsolatedContextFactory extends BaseContextFactory {
       handleSIGTERM: false,
     }).catch(error => {
       if (error.message.includes('Executable doesn\'t exist'))
-        throw new Error(`Browser specified in your config is not installed. Either install it (likely) or change the config.`);
+        throwBrowserIsNotInstalledError(this.config);
       throw error;
     });
   }
@@ -227,7 +227,7 @@ class PersistentContextFactory implements BrowserContextFactory {
         return { browserContext, close };
       } catch (error: any) {
         if (error.message.includes('Executable doesn\'t exist'))
-          throw new Error(`Browser specified in your config is not installed. Either install it (likely) or change the config.`);
+          throwBrowserIsNotInstalledError(this.config);
         if (error.message.includes('cannot open shared object file: No such file or directory')) {
           const browserName = launchOptions.channel ?? this.config.browser.browserName;
           throw new Error(`Missing system dependencies required to run browser ${browserName}. Install them with: sudo npx playwright install-deps ${browserName}`);
@@ -368,3 +368,11 @@ async function browserContextOptionsFromConfig(config: FullConfig, clientInfo: C
   }
   return result;
 }
+
+function throwBrowserIsNotInstalledError(config: FullConfig): never {
+  const channel = config.browser.launchOptions?.channel ?? config.browser.browserName;
+  if (config.skillMode)
+    throw new Error(`Browser "${channel}" is not installed. Run \`playwright-cli install-browser ${channel}\` to install`);
+  else
+    throw new Error(`Browser "${channel}" is not installed. Either install it (likely) or change the config.`);
+}
diff --git a/packages/playwright/src/mcp/browser/browserServerBackend.ts b/packages/playwright/src/mcp/browser/browserServerBackend.ts
index 6812b32531994..5a30c5a680657 100644
--- a/packages/playwright/src/mcp/browser/browserServerBackend.ts
+++ b/packages/playwright/src/mcp/browser/browserServerBackend.ts
@@ -34,9 +34,6 @@ export class BrowserServerBackend implements ServerBackend {
   private _config: FullConfig;
   private _browserContextFactory: BrowserContextFactory;

-  onBrowserContextClosed: (() => void) | undefined;
-  onBrowserLaunchFailed: ((error: Error) => void) | undefined;
-
   constructor(config: FullConfig, factory: BrowserContextFactory, options: { allTools?: boolean, structuredOutput?: boolean } = {}) {
     this._config = config;
     this._browserContextFactory = factory;
@@ -51,8 +48,6 @@ export class BrowserServerBackend implements ServerBackend {
       sessionLog: this._sessionLog,
       clientInfo,
     });
-    this._context.onBrowserContextClosed = () => this.onBrowserContextClosed?.();
-    this._context.onBrowserLaunchFailed = error => this.onBrowserLaunchFailed?.(error);
   }

   async listTools(): Promise<mcpServer.Tool[]> {
diff --git a/packages/playwright/src/mcp/browser/context.ts b/packages/playwright/src/mcp/browser/context.ts
index e0dbd03e891ea..2f32e6348456f 100644
--- a/packages/playwright/src/mcp/browser/context.ts
+++ b/packages/playwright/src/mcp/browser/context.ts
@@ -80,9 +80,6 @@ export class Context {
   private _runningToolName: string | undefined;
   private _abortController = new AbortController();

-  onBrowserContextClosed: (() => void) | undefined;
-  onBrowserLaunchFailed: ((error: Error) => void) | undefined;
-
   constructor(options: ContextOptions) {
     this.config = options.config;
     this.sessionLog = options.sessionLog;
@@ -289,9 +286,8 @@ export class Context {
       return this._browserContextPromise;

     this._browserContextPromise = this._setupBrowserContext();
-    this._browserContextPromise.catch(error => {
+    this._browserContextPromise.catch(() => {
       this._browserContextPromise = undefined;
-      this.onBrowserLaunchFailed?.(error);
     });
     return this._browserContextPromise;
   }
@@ -313,7 +309,6 @@ export class Context {
     for (const page of browserContext.pages())
       this._onPageCreated(page);
     browserContext.on('page', page => this._onPageCreated(page));
-    browserContext.on('close', () => this.onBrowserContextClosed?.());
     if (this.config.saveTrace) {
       await (browserContext.tracing as Tracing).start({
         name: 'trace-' + Date.now(),
diff --git a/packages/playwright/src/mcp/extension/cdpRelay.ts b/packages/playwright/src/mcp/extension/cdpRelay.ts
index 927fa96536e1e..639ac1c35e3b5 100644
--- a/packages/playwright/src/mcp/extension/cdpRelay.ts
+++ b/packages/playwright/src/mcp/extension/cdpRelay.ts
@@ -108,7 +108,7 @@ export class CDPRelayServer {
     await Promise.race([
       this._extensionConnectionPromise,
       new Promise((_, reject) => setTimeout(() => {
-        reject(new Error(`Extension connection timeout. Make sure the "Playwright MCP Bridge" extension is installed. See https://github.com/microsoft/playwright-mcp/blob/main/extension/README.md for installation instructions.`));
+        reject(new Error(`Extension connection timeout. Make sure the "Playwright MCP Bridge" extension is installed. See https://github.com/microsoft/playwright-mcp/blob/main/packages/extension/README.md for installation instructions.`));
       }, process.env.PWMCP_TEST_CONNECTION_TIMEOUT ? parseInt(process.env.PWMCP_TEST_CONNECTION_TIMEOUT, 10) : 5_000)),
       new Promise((_, reject) => abortSignal.addEventListener('abort', reject))
     ]);
diff --git a/packages/playwright/src/mcp/program.ts b/packages/playwright/src/mcp/program.ts
index ce34ad93b716d..b91650fd7fbd6 100644
--- a/packages/playwright/src/mcp/program.ts
+++ b/packages/playwright/src/mcp/program.ts
@@ -110,18 +110,18 @@ export function decorateCommand(command: Command, version: string) {

         if (config.sessionConfig) {
           const contextFactory = config.extension ? extensionContextFactory : browserContextFactory;
-          const serverBackendFactory: mcpServer.ServerBackendFactory = {
-            name: 'Playwright',
-            nameInConfig: 'playwright-daemon',
-            version,
-            create: () => new BrowserServerBackend(config, contextFactory, { allTools: true })
-          };
-          console.error(`### Config`);
-          console.error('```json');
-          console.error(JSON.stringify(config, null, 2));
-          console.error('```');
-          const socketPath = await startMcpDaemonServer(config.sessionConfig, serverBackendFactory);
-          console.error(`Daemon server listening on ${socketPath}`);
+          console.log(`### Config`);
+          console.log('```json');
+          console.log(JSON.stringify(config, null, 2));
+          console.log('```');
+          try {
+            const socketPath = await startMcpDaemonServer(config, contextFactory);
+            console.log(`### Success\nDaemon listening on ${socketPath}`);
+            console.log('<EOF>');
+          } catch (error) {
+            console.log(`### Error\n${error.message}`);
+            console.log('<EOF>');
+          }
           return;
         }

diff --git a/packages/playwright/src/mcp/sdk/server.ts b/packages/playwright/src/mcp/sdk/server.ts
index 6fa53cf1a4573..9346c720a865c 100644
--- a/packages/playwright/src/mcp/sdk/server.ts
+++ b/packages/playwright/src/mcp/sdk/server.ts
@@ -47,8 +47,6 @@ export interface ServerBackend {
   listTools(): Promise<Tool[]>;
   callTool(name: string, args: CallToolRequest['params']['arguments'], progress: ProgressCallback): Promise<CallToolResult>;
   serverClosed?(server: Server): void;
-  onBrowserContextClosed?: (() => void) | undefined;
-  onBrowserLaunchFailed?: ((error: Error) => void) | undefined;
 }

 export type ServerBackendFactory = {
diff --git a/packages/playwright/src/mcp/terminal/DEPS.list b/packages/playwright/src/mcp/terminal/DEPS.list
index c83f31a2da8cf..e67b7fc131d93 100644
--- a/packages/playwright/src/mcp/terminal/DEPS.list
+++ b/packages/playwright/src/mcp/terminal/DEPS.list
@@ -1,4 +1,5 @@
 [daemon.ts]
+../browser/browserServerBackend.ts
 ../browser/tools
 ../cli/socketConnection.ts

diff --git a/packages/playwright/src/mcp/terminal/daemon.ts b/packages/playwright/src/mcp/terminal/daemon.ts
index 2a70de6af1f62..4a1cf9abd5de8 100644
--- a/packages/playwright/src/mcp/terminal/daemon.ts
+++ b/packages/playwright/src/mcp/terminal/daemon.ts
@@ -23,13 +23,14 @@ import url from 'url';
 import { debug } from 'playwright-core/lib/utilsBundle';
 import { gracefullyProcessExitDoNotHang } from 'playwright-core/lib/utils';

+import { BrowserServerBackend } from '../browser/browserServerBackend';
 import { SocketConnection } from './socketConnection';
 import { commands } from './commands';
 import { parseCommand } from './command';

-import type { ServerBackendFactory } from '../sdk/server';
 import type * as mcp from '../sdk/exports';
-import type { SessionConfig } from './program';
+import type { BrowserContextFactory } from '../browser/browserContextFactory';
+import type { FullConfig } from '../browser/config';

 const daemonDebug = debug('pw:daemon');

@@ -44,9 +45,10 @@ async function socketExists(socketPath: string): Promise<boolean> {
 }

 export async function startMcpDaemonServer(
-  sessionConfig: SessionConfig,
-  serverBackendFactory: ServerBackendFactory,
+  config: FullConfig,
+  contextFactory: BrowserContextFactory,
 ): Promise<string> {
+  const sessionConfig = config.sessionConfig!;
   const { socketPath, version } = sessionConfig;
   // Clean up existing socket file on Unix
   if (os.platform() !== 'win32' && await socketExists(socketPath)) {
@@ -59,9 +61,8 @@ export async function startMcpDaemonServer(
     }
   }

-  const backend = serverBackendFactory.create();
   const cwd = url.pathToFileURL(process.cwd()).href;
-  await backend.initialize?.({
+  const clientInfo = {
     name: 'playwright-cli',
     version: sessionConfig.version,
     roots: [{
@@ -69,11 +70,21 @@ export async function startMcpDaemonServer(
       name: 'cwd'
     }],
     timestamp: Date.now(),
+  };
+
+  const { browserContext, close } = await contextFactory.createContext(clientInfo, new AbortController().signal, {});
+  browserContext.on('close', () => {
+    daemonDebug('browser closed, shutting down daemon');
+    shutdown(0);
   });

-  await fs.mkdir(path.dirname(socketPath), { recursive: true });
+  const existingContextFactory = {
+    createContext: () => Promise.resolve({ browserContext, close }),
+  };
+  const backend = new BrowserServerBackend(config, existingContextFactory, { allTools: true });
+  await backend.initialize?.(clientInfo);

-  let shutdownPending = false;
+  await fs.mkdir(path.dirname(socketPath), { recursive: true });

   const shutdown = (exitCode: number) => {
     daemonDebug(`shutting down daemon with exit code ${exitCode}`);
@@ -101,32 +112,18 @@ export async function startMcpDaemonServer(
           const { toolName, toolParams } = parseCliCommand(params.args);
           if (params.cwd)
             toolParams._meta = { cwd: params.cwd };
-          const response = await backend.callTool(toolName, toolParams, () => {});
+          const response = await backend.callTool(toolName, toolParams);
           await connection.send({ id, result: formatResult(response) });
-          if (shutdownPending)
-            shutdown(1);
         } else {
           throw new Error(`Unknown method: ${method}`);
         }
       } catch (e) {
         daemonDebug('command failed', e);
         await connection.send({ id, error: (e as Error).message });
-        if (shutdownPending)
-          shutdown(1);
       }
     };
   });

-  backend.onBrowserContextClosed = () => {
-    daemonDebug('browser closed, shutting down daemon');
-    shutdown(0);
-  };
-
-  backend.onBrowserLaunchFailed = error => {
-    daemonDebug('browser launch failed, will shut down after response', error);
-    shutdownPending = true;
-  };
-
   return new Promise((resolve, reject) => {
     server.on('error', (error: NodeJS.ErrnoException) => {
       daemonDebug(`server error: ${error.message}`);
diff --git a/packages/playwright/src/mcp/terminal/helpGenerator.ts b/packages/playwright/src/mcp/terminal/helpGenerator.ts
index d60edd1a53d70..96fc9a6995975 100644
--- a/packages/playwright/src/mcp/terminal/helpGenerator.ts
+++ b/packages/playwright/src/mcp/terminal/helpGenerator.ts
@@ -81,7 +81,7 @@ const categories: { name: Category, title: string }[] = [
 export function generateHelp() {
   const lines: string[] = [];
   lines.push('Usage: playwright-cli <command> [args] [options]');
-  lines.push('Usage: playwright-cli -b=<session> <command> [args] [options]');
+  lines.push('Usage: playwright-cli -s=<session> <command> [args] [options]');

   const commandsByCategory = new Map<string, AnyCommandSchema[]>();
   for (const c of categories)
diff --git a/packages/playwright/src/mcp/terminal/program.ts b/packages/playwright/src/mcp/terminal/program.ts
index 1c6799cf84c0e..7af95b509b0ed 100644
--- a/packages/playwright/src/mcp/terminal/program.ts
+++ b/packages/playwright/src/mcp/terminal/program.ts
@@ -94,15 +94,16 @@ to restart the session daemon.`);
     return await this._send('run', { args, cwd: process.cwd() });
   }

-  async stop(): Promise<void> {
+  async stop(quiet: boolean = false): Promise<void> {
     if (!await this.canConnect()) {
-      console.log(`Browser '${this.name}' is not open.`);
+      if (!quiet)
+        console.log(`Browser '${this.name}' is not open.`);
       return;
     }

     await this._stopDaemon();
-    console.log(`Browser '${this.name}' closed`);
-    console.log('');
+    if (!quiet)
+      console.log(`Browser '${this.name}' closed\n`);
   }

   private async _send(method: string, params: any = {}): Promise<any> {
@@ -226,9 +227,7 @@ to restart the session daemon.`);
     this._config.version = this._clientInfo.version;
     await fs.promises.writeFile(sessionConfigFile, JSON.stringify(this._config, null, 2));

-    const outLog = this._sessionFile('.out');
     const errLog = this._sessionFile('.err');
-    const out = fs.openSync(outLog, 'w');
     const err = fs.openSync(errLog, 'w');

     const args = [
@@ -239,53 +238,67 @@ to restart the session daemon.`);

     const child = spawn(process.execPath, args, {
       detached: true,
-      stdio: ['ignore', out, err],
+      stdio: ['ignore', 'pipe', err],
       cwd: process.cwd(), // Will be used as root.
     });
-    child.unref();

-    // Wait for the socket to become available with retries.
-    const retryDelay = [100, 200, 400]; // ms
-    let totalWaited = 0;
-    for (let i = 0; i < 10; i++) {
-      await new Promise(resolve => setTimeout(resolve, retryDelay[i] || 1000));
-      totalWaited += retryDelay[i] || 1000;
-      try {
-        const { socket } = await this._connect();
-        if (socket) {
-          console.log(`### Browser \`${this.name}\` opened with pid ${child.pid}.`);
-          const resolvedConfig = await parseResolvedConfig(errLog);
-          if (resolvedConfig) {
-            this._config.resolvedConfig = resolvedConfig;
-            console.log(`- ${this.name}:`);
-            console.log(renderResolvedConfig(resolvedConfig).join('\n'));
-          }
-          const sessionOption = this.name !== 'default' ? ` -b ${this.name}` : '';
-          console.log(``);
-          console.log(`\`\`\`bash`);
-          console.log(formatWithGap(`> playwright-cli${sessionOption} close`, `# to close when done`));
-          console.log(formatWithGap(`> playwright-cli${sessionOption} open [options]`, `# to reopen with new config`));
-          console.log(formatWithGap(`> playwright-cli${sessionOption} delete-data`, `# to delete profile data dir`));
-          console.log(`\`\`\``);
-          console.log(``);
-
-          await fs.promises.writeFile(sessionConfigFile, JSON.stringify(this._config, null, 2));
-          return socket;
+    let signalled = false;
+    const sigintHandler = () => {
+      signalled = true;
+      child.kill('SIGINT');
+    };
+    const sigtermHandler = () => {
+      signalled = true;
+      child.kill('SIGTERM');
+    };
+    process.on('SIGINT', sigintHandler);
+    process.on('SIGTERM', sigtermHandler);
+
+    let outLog = '';
+    await new Promise<void>((resolve, reject) => {
+      child.stdout!.on('data', data => {
+        outLog += data.toString();
+        if (!outLog.includes('<EOF>'))
+          return;
+        const errorMatch = outLog.match(/### Error\n([\s\S]*)<EOF>/);
+        const error = errorMatch ? errorMatch[1].trim() : undefined;
+        if (error) {
+          const errLogContent = fs.readFileSync(errLog, 'utf-8');
+          const message = error + (errLogContent ? '\n' + errLogContent : '');
+          reject(new Error(message));
         }
-      } catch (e) {
-        if (e.code !== 'ENOENT' && e.code !== 'ECONNREFUSED')
-          throw e;
+
+        const successMatch = outLog.match(/### Success\nDaemon listening on (.*)\n<EOF>/);
+        if (successMatch)
+          resolve();
+      });
+      child.on('close', code => {
+        if (!signalled)
+          reject(new Error(`Daemon process exited with code ${code}`));
+      });
+    });
+
+    process.off('SIGINT', sigintHandler);
+    process.off('SIGTERM', sigtermHandler);
+    child.stdout!.destroy();
+    child.unref();
+
+    const { socket } = await this._connect();
+    if (socket) {
+      console.log(`### Browser \`${this.name}\` opened with pid ${child.pid}.`);
+      const resolvedConfig = await parseResolvedConfig(outLog);
+      if (resolvedConfig) {
+        this._config.resolvedConfig = resolvedConfig;
+        console.log(`- ${this.name}:`);
+        console.log(renderResolvedConfig(resolvedConfig).join('\n'));
       }
-    }
+      console.log(`---`);

-    const outData = await fs.promises.readFile(outLog, 'utf-8').catch(() => '');
-    const errData = await fs.promises.readFile(errLog, 'utf-8').catch(() => '');
+      await fs.promises.writeFile(sessionConfigFile, JSON.stringify(this._config, null, 2));
+      return socket;
+    }

-    console.error(`Failed to connect to daemon at ${this._config.socketPath} after ${totalWaited}ms`);
-    if (outData.length)
-      console.log(outData);
-    if (errData.length)
-      console.error(errData);
+    console.error(`Failed to connect to daemon at ${this._config.socketPath}`);
     process.exit(1);
   }

@@ -337,7 +350,7 @@ class SessionManager {
     const sessionName = this._resolveSessionName(args.session);
     let session = this.sessions.get(sessionName);
     if (session)
-      await session.stop();
+      await session.stop(true);

     session = new Session(this.clientInfo, sessionName, sessionConfigFromArgs(this.clientInfo, sessionName, args));
     this.sessions.set(sessionName, session);
@@ -350,7 +363,7 @@ class SessionManager {
     if (!session) {
       console.log(`The browser '${sessionName}' is not open, please run open first`);
       console.log('');
-      console.log(`  playwright-cli${sessionName !== 'default' ? ` -b ${sessionName}` : ''} open [params]`);
+      console.log(`  playwright-cli${sessionName !== 'default' ? ` -s=${sessionName}` : ''} open [params]`);
       process.exit(1);
     }

@@ -487,10 +500,10 @@ export async function program(packageLocation: string) {
     if (!argv.includes(`--${option}`) && !argv.includes(`--no-${option}`))
       delete args[option];
   }
-  // Normalize -b alias to --session
-  if (args.b) {
-    args.session = args.b;
-    delete args.b;
+  // Normalize -s alias to --session
+  if (args.s) {
+    args.session = args.s;
+    delete args.s;
   }

   const help = require('./help.json');
@@ -531,7 +544,7 @@ export async function program(packageLocation: string) {
     case 'close-all': {
       const sessions = sessionManager.sessions;
       for (const session of sessions.values())
-        await session.stop();
+        await session.stop(true);
       return;
     }
     case 'delete-data':
@@ -798,22 +811,16 @@ function renderResolvedConfig(resolvedConfig: FullConfig) {
   return lines;
 }

-function formatWithGap(prefix: string, text: string, threshold: number = 40) {
-  const indent = Math.max(1, threshold - prefix.length);
-  return prefix + ' '.repeat(indent) + text;
-}
-
-async function parseResolvedConfig(logFile: string): Promise<FullConfig | null> {
-  const logData = await fs.promises.readFile(logFile, 'utf-8').catch(() => '');
+async function parseResolvedConfig(errLog: string): Promise<FullConfig | null> {
   const marker = '### Config\n```json\n';
-  const markerIndex = logData.indexOf(marker);
+  const markerIndex = errLog.indexOf(marker);
   if (markerIndex === -1)
     return null;
   const jsonStart = markerIndex + marker.length;
-  const jsonEnd = logData.indexOf('\n```', jsonStart);
+  const jsonEnd = errLog.indexOf('\n```', jsonStart);
   if (jsonEnd === -1)
     throw null;
-  const jsonString = logData.substring(jsonStart, jsonEnd).trim();
+  const jsonString = errLog.substring(jsonStart, jsonEnd).trim();
   try {
     return JSON.parse(jsonString) as FullConfig;
   } catch {
diff --git a/packages/playwright/src/skill/SKILL.md b/packages/playwright/src/skill/SKILL.md
index 18ab060b315f7..847a1764894df 100644
--- a/packages/playwright/src/skill/SKILL.md
+++ b/packages/playwright/src/skill/SKILL.md
@@ -184,10 +184,10 @@ playwright-cli delete-data
 ### Browser Sessions

 ```bash
-playwright-cli -b mysession open example.com
-playwright-cli -b mysession click e6
-playwright-cli -b mysession close  # stop a named browser
-playwright-cli -b mysession delete-data   # delete profile
+playwright-cli -s=mysession open example.com
+playwright-cli -s=mysession click e6
+playwright-cli -s=mysession close  # stop a named browser
+playwright-cli -s=mysession delete-data   # delete profile
 ```

 ### Multi-Session
diff --git a/packages/playwright/src/skill/references/session-management.md b/packages/playwright/src/skill/references/session-management.md
index 5dc5e38f3c695..1a04be1f5fe8f 100644
--- a/packages/playwright/src/skill/references/session-management.md
+++ b/packages/playwright/src/skill/references/session-management.md
@@ -4,11 +4,11 @@ Run multiple isolated browser sessions concurrently with state persistence.

 ## Named Browser Sessions

-Use `-b` flag to isolate browser contexts:
+Use `-s` flag to isolate browser contexts:

 ```bash
 # Browser 1: Authentication flow
-playwright-cli -b auth open https://app.example.com/login
+playwright-cli -s=auth open https://app.example.com/login

 # Browser 2: Public browsing (separate cookies, storage)
-playwright-cli -b public open https://example.com
+playwright-cli -s=public open https://example.com

 # Commands are isolated by browser session
-playwright-cli -b auth fill e1 "user@example.com"
-playwright-cli -b public snapshot
+playwright-cli -s=auth fill e1 "user@example.com"
+playwright-cli -s=public snapshot
 ```

 ## Browser Session Isolation Properties
@@ -36,7 +36,7 @@ playwright-cli list

 # Stop a browser session (close the browser)
 playwright-cli close                # stop the default browser
-playwright-cli -b mysession close   # stop a named browser
+playwright-cli -s=mysession close   # stop a named browser

 # Stop all browser sessions
 playwright-cli close-all
@@ -46,7 +46,7 @@ playwright-cli kill-all

 # Delete browser session user data (profile directory)
 playwright-cli delete-data                # delete default browser data
-playwright-cli -b mysession delete-data   # delete named browser data
+playwright-cli -s=mysession delete-data   # delete named browser data
 ```

 ## Environment Variable
@@ -67,15 +67,15 @@ playwright-cli open example.com  # Uses "mysession" automatically
 # Scrape multiple sites concurrently

 # Start all browsers
-playwright-cli -b site1 open https://site1.com &
-playwright-cli -b site2 open https://site2.com &
-playwright-cli -b site3 open https://site3.com &
+playwright-cli -s=site1 open https://site1.com &
+playwright-cli -s=site2 open https://site2.com &
+playwright-cli -s=site3 open https://site3.com &
 wait

 # Take snapshots from each
-playwright-cli -b site1 snapshot
-playwright-cli -b site2 snapshot
-playwright-cli -b site3 snapshot
+playwright-cli -s=site1 snapshot
+playwright-cli -s=site2 snapshot
+playwright-cli -s=site3 snapshot

 # Cleanup
 playwright-cli close-all
@@ -85,12 +85,12 @@ playwright-cli close-all

 ```bash
 # Test different user experiences
-playwright-cli -b variant-a open "https://app.com?variant=a"
-playwright-cli -b variant-b open "https://app.com?variant=b"
+playwright-cli -s=variant-a open "https://app.com?variant=a"
+playwright-cli -s=variant-b open "https://app.com?variant=b"

 # Compare
-playwright-cli -b variant-a screenshot
-playwright-cli -b variant-b screenshot
+playwright-cli -s=variant-a screenshot
+playwright-cli -s=variant-b screenshot
 ```

 ### Persistent Profile
@@ -107,7 +107,7 @@ playwright-cli open https://example.com --profile=/path/to/profile

 ## Default Browser Session

-When `-b` is omitted, commands use the default browser session:
+When `-s` is omitted, commands use the default browser session:

 ```bash
 # These use the same default browser session
@@ -140,19 +140,19 @@ playwright-cli open https://example.com --persistent

 ```bash
 # GOOD: Clear purpose
-playwright-cli -b github-auth open https://github.com
-playwright-cli -b docs-scrape open https://docs.example.com
+playwright-cli -s=github-auth open https://github.com
+playwright-cli -s=docs-scrape open https://docs.example.com

 # AVOID: Generic names
-playwright-cli -b s1 open https://github.com
+playwright-cli -s=s1 open https://github.com
 ```

 ### 2. Always Clean Up

 ```bash
 # Stop browsers when done
-playwright-cli -b auth close
-playwright-cli -b scrape close
+playwright-cli -s=auth close
+playwright-cli -s=scrape close

 # Or stop all at once
 playwright-cli close-all
@@ -165,5 +165,5 @@ playwright-cli kill-all

 ```bash
 # Remove old browser data to free disk space
-playwright-cli -b oldsession delete-data
+playwright-cli -s=oldsession delete-data
 ```

PATCH

echo "Patch applied successfully."
