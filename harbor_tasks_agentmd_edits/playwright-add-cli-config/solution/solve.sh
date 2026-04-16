#!/bin/bash
set -e

cd /workspace/playwright

# Apply the gold patch for adding playwright-cli config command
cat << 'EOF' | git apply -
diff --git a/packages/playwright/src/mcp/browser/config.ts b/packages/playwright/src/mcp/browser/config.ts
index 98dde261b4a42..d4d000ee3886d 100644
--- a/packages/playwright/src/mcp/browser/config.ts
+++ b/packages/playwright/src/mcp/browser/config.ts
@@ -112,7 +112,10 @@ const defaultDaemonConfig = (cliOptions: CLIOptions) => mergeConfig(defaultConfi
     userDataDir: '<daemon-data-dir>',
     launchOptions: {
       headless: !cliOptions.daemonHeaded,
-    }
+    },
+    contextOptions: {
+      viewport: cliOptions.daemonHeaded ? null : { width: 1280, height: 720 },
+    },
   },
   outputMode: 'file',
   codegen: 'none',
diff --git a/packages/playwright/src/mcp/terminal/SKILL.md b/packages/playwright/src/mcp/terminal/SKILL.md
index b3f2eed795191..72db230f5bd71 100644
--- a/packages/playwright/src/mcp/terminal/SKILL.md
+++ b/packages/playwright/src/mcp/terminal/SKILL.md
@@ -105,6 +105,16 @@ playwright-cli tracing-start
 playwright-cli tracing-stop
 ```

+### Configuration
+```bash
+# configure the session
+playwright-cli config my-config.json
+# Configure named session
+playwright-cli --session=mysession config my-config.json
+# Start with configured session
+playwright-cli open --config=my-config.json
+```
+
 ### Sessions

 ```bash
diff --git a/packages/playwright/src/mcp/terminal/command.ts b/packages/playwright/src/mcp/terminal/command.ts
index b0e44c0b721f1..5bba0ba6150e6 100644
--- a/packages/playwright/src/mcp/terminal/command.ts
+++ b/packages/playwright/src/mcp/terminal/command.ts
@@ -17,7 +17,7 @@

 import type zodType from 'zod';

-export type Category = 'core' | 'navigation' | 'keyboard' | 'mouse' | 'export' | 'storage' | 'tabs' | 'devtools' | 'session';
+export type Category = 'core' | 'navigation' | 'keyboard' | 'mouse' | 'export' | 'storage' | 'tabs' | 'devtools' | 'session' | 'config';

 export type CommandSchema<Args extends zodType.ZodTypeAny, Options extends zodType.ZodTypeAny> = {
   name: string;
diff --git a/packages/playwright/src/mcp/terminal/commands.ts b/packages/playwright/src/mcp/terminal/commands.ts
index eab4a6fe07cd4..f6a89064de07d 100644
--- a/packages/playwright/src/mcp/terminal/commands.ts
+++ b/packages/playwright/src/mcp/terminal/commands.ts
@@ -512,6 +512,17 @@ const sessionDelete = declareCommand({
   toolParams: ({ name }) => ({ name }),
 });

+const config = declareCommand({
+  name: 'config',
+  description: 'Restart session with new config, defaults to `playwright-cli.json`',
+  category: 'config',
+  args: z.object({
+    config: z.string().optional().describe('Path to the configuration file'),
+  }),
+  toolName: '',
+  toolParams: () => ({}),
+});
+
 const commandsArray: AnyCommandSchema[] = [
   // core category
   open,
@@ -559,6 +570,9 @@ const commandsArray: AnyCommandSchema[] = [
   tabClose,
   tabSelect,

+  // config
+  config,
+
   // devtools category
   networkRequests,
   runCode,
diff --git a/packages/playwright/src/mcp/terminal/helpGenerator.ts b/packages/playwright/src/mcp/terminal/helpGenerator.ts
index 82829029e48be..787b0d340e537 100644
--- a/packages/playwright/src/mcp/terminal/helpGenerator.ts
+++ b/packages/playwright/src/mcp/terminal/helpGenerator.ts
@@ -72,6 +72,7 @@ const categories: { name: Category, title: string }[] = [
   { name: 'tabs', title: 'Tabs' },
   { name: 'storage', title: 'Storage' },
   { name: 'devtools', title: 'DevTools' },
+  { name: 'config', title: 'Configuration' },
   { name: 'session', title: 'Sessions' },
 ] as const;

@@ -95,8 +96,8 @@ export function generateHelp() {
   }

   lines.push('\nGlobal options:');
-  lines.push(formatWithGap('  --config <path>', 'use custom configuration file, defaults to "playwright-cli.json"'));
-  lines.push(formatWithGap('  --headed', 'run in headed mode'));
+  lines.push(formatWithGap('  --config <path>', 'create a session with custom config, defaults to `playwright-cli.json`'));
+  lines.push(formatWithGap('  --headed', 'create a headed session'));
   lines.push(formatWithGap('  --help [command]', 'print help'));
   lines.push(formatWithGap('  --session', 'run command in the scope of a specific session'));
   lines.push(formatWithGap('  --version', 'print version'));
diff --git a/packages/playwright/src/mcp/terminal/program.ts b/packages/playwright/src/mcp/terminal/program.ts
index b48f89e776cd0..05686a1b847d5 100644
--- a/packages/playwright/src/mcp/terminal/program.ts
+++ b/packages/playwright/src/mcp/terminal/program.ts
@@ -104,22 +104,22 @@ class SessionManager {
     this._options = options;
   }

-  async list(): Promise<{ name: string, live: boolean }[]> {
+  async list(): Promise<Map<string, boolean>> {
     const dir = daemonProfilesDir;
     try {
       const files = await fs.promises.readdir(dir);
-      const sessions: { name: string, live: boolean }[] = [];
+      const sessions = new Map<string, boolean>();
       for (const file of files) {
         if (file.startsWith('ud-')) {
           // Session is like ud-<sessionName>-browserName
           const sessionName = file.split('-')[1];
           const live = await this._canConnect(sessionName);
-          sessions.push({ name: sessionName, live });
+          sessions.set(sessionName, live);
         }
       }
       return sessions;
     } catch {
-      return [];
+      return new Map<string, boolean>();
     }
   }

@@ -186,6 +186,19 @@ class SessionManager {
     }
   }

+  async configure(args: any): Promise<void> {
+    const sessionName = this._resolveSessionName(args.session);
+
+    if (await this._canConnect(sessionName)) {
+      const session = await this._connect(sessionName);
+      await session.stop();
+    }
+
+    this._options.config = args._[1];
+    const session = await this._connect(sessionName);
+    session.close();
+  }
+
   private async _connect(sessionName: string): Promise<Session> {
     const socketPath = this._daemonSocketPath(sessionName);
     debugCli(`Connecting to daemon at ${socketPath}`);
@@ -234,7 +247,7 @@ class SessionManager {

     console.log(`<!-- Daemon for \`${sessionName}\` session started with pid ${child.pid}.`);
     if (configFile)
-      console.log(`- Using config file at \`${configFile}\`.');
+      console.log(`- Using config file at \`${path.relative(process.cwd(), configFile)}\`.`);
     const sessionSuffix = sessionName !== 'default' ? ` "${sessionName}"` : '';
     console.log(`- You can stop the session daemon with \`playwright-cli session-stop${sessionSuffix}\` when done.`);
     console.log(`- You can delete the session data with \`playwright-cli session-delete${sessionSuffix}\` when done.`);
@@ -306,17 +319,15 @@ class SessionManager {
   }
 }

-async function handleSessionCommand(sessionManager: SessionManager, args: any): Promise<void> {
-  const subcommand = args._[0].split('-').slice(1).join('-');
-
+async function handleSessionCommand(sessionManager: SessionManager, subcommand: string, args: any): Promise<void> {
   if (subcommand === 'list') {
     const sessions = await sessionManager.list();
     console.log('Sessions:');
-    for (const session of sessions) {
-      const liveMarker = session.live ? ' (live)' : '';
-      console.log(`  ${session.name}${liveMarker}`);
+    for (const [sessionName, live] of sessions.entries()) {
+      const liveMarker = live ? ' (live)' : '';
+      console.log(`  ${sessionName}${liveMarker}`);
     }
-    if (sessions.length === 0)
+    if (sessions.size === 0)
       console.log('  (no sessions)');
     return;
   }
@@ -328,8 +339,8 @@ async function handleSessionCommand(sessionManager: SessionManager, args: any): Pr

   if (subcommand === 'stop-all') {
     const sessions = await sessionManager.list();
-    for (const session of sessions)
-      await sessionManager.stop(session.name);
+    for (const sessionName of sessions.keys())
+      await sessionManager.stop(sessionName);
     return;
   }

@@ -338,6 +349,11 @@ async function handleSessionCommand(sessionManager: SessionManager, args: any): P
     return;
   }

+  if (subcommand === 'config') {
+    await sessionManager.configure(args);
+    return;
+  }
+
   console.error(`Unknown session subcommand: ${subcommand}`);
   process.exit(1);
 }
@@ -398,7 +414,13 @@ export async function program(options: { version: string }) {

   const sessionManager = new SessionManager(args);
   if (commandName.startsWith('session')) {
-    await handleSessionCommand(sessionManager, args);
+    const subcommand = args._[0].split('-').slice(1).join('-');
+    await handleSessionCommand(sessionManager, subcommand, args);
+    return;
+  }
+
+  if (commandName === 'config') {
+    await handleSessionCommand(sessionManager, 'config', args);
     return;
   }

EOF

# Verify idempotency - check for distinctive line from patch
grep -q "playwright-cli config my-config.json" packages/playwright/src/mcp/terminal/SKILL.md && echo "SUCCESS: Patch applied"

# Rebuild after applying patch
npm run build

echo "Solve complete"
