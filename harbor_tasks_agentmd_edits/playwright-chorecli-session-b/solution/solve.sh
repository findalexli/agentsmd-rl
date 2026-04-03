#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q "'browsers'" packages/playwright/src/mcp/terminal/command.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/playwright/src/mcp/terminal/command.ts b/packages/playwright/src/mcp/terminal/command.ts
index 5a074653950df..09ae67611a78d 100644
--- a/packages/playwright/src/mcp/terminal/command.ts
+++ b/packages/playwright/src/mcp/terminal/command.ts
@@ -18,7 +18,7 @@ import { z } from 'playwright-core/lib/mcpBundle';

 import type zodType from 'zod';

-export type Category = 'core' | 'navigation' | 'keyboard' | 'mouse' | 'export' | 'storage' | 'tabs' | 'network' | 'devtools' | 'session' | 'config' | 'install';
+export type Category = 'core' | 'navigation' | 'keyboard' | 'mouse' | 'export' | 'storage' | 'tabs' | 'network' | 'devtools' | 'browsers' | 'config' | 'install';

 export type CommandSchema<Args extends zodType.ZodTypeAny, Options extends zodType.ZodTypeAny> = {
   name: string;
diff --git a/packages/playwright/src/mcp/terminal/commands.ts b/packages/playwright/src/mcp/terminal/commands.ts
index 5310bae85ce1a..80b7c1b608259 100644
--- a/packages/playwright/src/mcp/terminal/commands.ts
+++ b/packages/playwright/src/mcp/terminal/commands.ts
@@ -754,29 +754,29 @@ const videoStop = declareCommand({
 // Sessions

 const sessionList = declareCommand({
-  name: 'session-list',
-  description: 'List all sessions',
-  category: 'session',
+  name: 'list',
+  description: 'List browser sessions',
+  category: 'browsers',
   args: z.object({}),
   options: z.object({
-    all: z.boolean().optional().describe('List all sessions across all workspaces'),
+    all: z.boolean().optional().describe('List all browser sessions across all workspaces'),
   }),
   toolName: '',
   toolParams: () => ({}),
 });

 const sessionCloseAll = declareCommand({
-  name: 'session-close-all',
-  description: 'Stop all sessions',
-  category: 'session',
+  name: 'close-all',
+  description: 'Close all browser sessions',
+  category: 'browsers',
   toolName: '',
   toolParams: () => ({}),
 });

 const killAll = declareCommand({
-  name: 'session-kill-all',
-  description: 'Forcefully kill all daemon processes (for stale/zombie processes)',
-  category: 'session',
+  name: 'kill-all',
+  description: 'Forcefully kill all browser sessions (for stale/zombie processes)',
+  category: 'browsers',
   toolName: '',
   toolParams: () => ({}),
 });
diff --git a/packages/playwright/src/mcp/terminal/helpGenerator.ts b/packages/playwright/src/mcp/terminal/helpGenerator.ts
index 7459981243265..d60edd1a53d70 100644
--- a/packages/playwright/src/mcp/terminal/helpGenerator.ts
+++ b/packages/playwright/src/mcp/terminal/helpGenerator.ts
@@ -75,12 +75,13 @@ const categories: { name: Category, title: string }[] = [
   { name: 'devtools', title: 'DevTools' },
   { name: 'install', title: 'Install' },
   { name: 'config', title: 'Configuration' },
-  { name: 'session', title: 'Sessions' },
+  { name: 'browsers', title: 'Browser sessions' },
 ] as const;

 export function generateHelp() {
   const lines: string[] = [];
   lines.push('Usage: playwright-cli <command> [args] [options]');
+  lines.push('Usage: playwright-cli -b=<session> <command> [args] [options]');

   const commandsByCategory = new Map<string, AnyCommandSchema[]>();
   for (const c of categories)
@@ -102,7 +103,6 @@ export function generateHelp() {

   lines.push('\nGlobal options:');
   lines.push(formatWithGap('  --help [command]', 'print help'));
-  lines.push(formatWithGap('  --session', 'run command in the scope of a specific session'));
   lines.push(formatWithGap('  --version', 'print version'));

   return lines.join('\n');
diff --git a/packages/playwright/src/mcp/terminal/program.ts b/packages/playwright/src/mcp/terminal/program.ts
index 1f3d35d12f4f6..a0160ebf26dc3 100644
--- a/packages/playwright/src/mcp/terminal/program.ts
+++ b/packages/playwright/src/mcp/terminal/program.ts
@@ -92,12 +92,13 @@ to restart the session daemon.`);

   async stop(): Promise<void> {
     if (!await this.canConnect()) {
-      console.log(`Session '${this.name}' is not running.`);
+      console.log(`Browser '${this.name}' is not open.`);
       return;
     }

     await this._stopDaemon();
-    console.log(`Session '${this.name}' stopped.`);
+    console.log(`Browser '${this.name}' closed.`);
+    console.log('');
   }

   private async _send(method: string, params: any = {}): Promise<any> {
@@ -132,7 +133,7 @@ to restart the session daemon.`);
     const dataDirs = await fs.promises.readdir(this._clientInfo.daemonProfilesDir).catch(() => []);
     const matchingEntries = dataDirs.filter(file => file === `${this.name}.session` || file.startsWith(`ud-${this.name}-`));
     if (matchingEntries.length === 0) {
-      console.log(`No user data found for session '${this.name}'.`);
+      console.log(`No user data found for browser '${this.name}'.`);
       return;
     }

@@ -142,11 +143,11 @@ to restart the session daemon.`);
         try {
           await fs.promises.rm(userDataDir, { recursive: true });
           if (entry.startsWith('ud-'))
-            console.log(`Deleted user data for session '${this.name}'.`);
+            console.log(`Deleted user data for browser '${this.name}'.`);
           break;
         } catch (e: any) {
           if (e.code === 'ENOENT') {
-            console.log(`No user data found for session '${this.name}'.`);
+            console.log(`No user data found for browser '${this.name}'.`);
             break;
           }
           await new Promise(resolve => setTimeout(resolve, 1000));
@@ -239,17 +240,17 @@ to restart the session daemon.`);
     });
     child.unref();

-    console.log(`### Session \`${this.name}\` started with pid ${child.pid}.`);
+    console.log(`### Browser \`${this.name}\` opened with pid ${child.pid}.`);
     const configArgs = configToFormattedArgs(this._config.cli);
     if (configArgs.length) {
-      console.log(`- Session options:`);
+      console.log(`- Browser options:`);
       for (const flag of configArgs)
         console.log(`  ${flag}`);
     }
-    const sessionOption = this.name !== 'default' ? ` --session="${this.name}"` : '';
-    console.log(formatWithGap(`- playwright-cli${sessionOption} close`, `# to stop when done.`));
-    console.log(formatWithGap(`- playwright-cli${sessionOption} open [options]`, `# to reopen with new config.`));
-    console.log(formatWithGap(`- playwright-cli${sessionOption} delete-data`, `# to delete session data.`));
+    const sessionOption = this.name !== 'default' ? ` -b ${this.name}` : '';
+    console.log(formatWithGap(`- playwright-cli${sessionOption} close`, `# to stop when done`));
+    console.log(formatWithGap(`- playwright-cli${sessionOption} open [options]`, `# to reopen with new config`));
+    console.log(formatWithGap(`- playwright-cli${sessionOption} delete-data`, `# to delete profile data dir`));
     console.log(`---`);
     console.log(``);

@@ -339,9 +340,9 @@ class SessionManager {
     const sessionName = this._resolveSessionName(args.session);
     const session = this.sessions.get(sessionName);
     if (!session) {
-      console.log(`The session '${sessionName}' is not open, please run open first`);
+      console.log(`The browser '${sessionName}' is not open, please run open first`);
       console.log('');
-      console.log(`  playwright-cli${sessionName !== 'default' ? ` --session=${sessionName}` : ''} open [params]`);
+      console.log(`  playwright-cli${sessionName !== 'default' ? ` -b ${sessionName}` : ''} open [params]`);
       process.exit(1);
     }

@@ -356,7 +357,7 @@ class SessionManager {
     const sessionName = this._resolveSessionName(options.session);
     const session = this.sessions.get(sessionName);
     if (!session || !await session.canConnect()) {
-      console.log(`Session '${sessionName}' is not running.`);
+      console.log(`Browser '${sessionName}' is not open.`);
       return;
     }

@@ -367,7 +368,7 @@ class SessionManager {
     const sessionName = this._resolveSessionName(options.session);
     const session = this.sessions.get(sessionName);
     if (!session) {
-      console.log(`No user data found for session '${sessionName}'.`);
+      console.log(`No user data found for browser '${sessionName}'.`);
       return;
     }
     await session.deleteData();
@@ -478,6 +479,11 @@ export async function program(packageLocation: string) {
     if (!argv.includes(`--${option}`) && !argv.includes(`--no-${option}`))
       delete args[option];
   }
+  // Normalize -b alias to --session
+  if (args.b) {
+    args.session = args.b;
+    delete args.b;
+  }

   const help = require('./help.json');
   const commandName = args._?.[0];
@@ -507,14 +513,14 @@ export async function program(packageLocation: string) {
   const sessionManager = await SessionManager.create(clientInfo);

   switch (commandName) {
-    case 'session-list': {
+    case 'list': {
       if (args.all)
         await listAllSessions(clientInfo);
       else
         await listSessions(sessionManager);
       return;
     }
-    case 'session-close-all': {
+    case 'close-all': {
       const sessions = sessionManager.sessions;
       for (const session of sessions.values())
         await session.stop();
@@ -523,7 +529,7 @@ export async function program(packageLocation: string) {
     case 'delete-data':
       await sessionManager.deleteData(args as GlobalOptions);
       return;
-    case 'session-kill-all':
+    case 'kill-all':
       await killAllDaemons();
       return;
     case 'open':
@@ -664,7 +670,7 @@ async function killAllDaemons(): Promise<void> {

 async function listSessions(sessionManager: SessionManager): Promise<void> {
   const sessions = sessionManager.sessions;
-  console.log('Sessions:');
+  console.log('Browsers:');
   await gcAndPrintSessions([...sessions.values()]);
 }

@@ -697,7 +703,7 @@ async function listAllSessions(clientInfo: ClientInfo): Promise<void> {
   }

   if (sessionsByWorkspace.size === 0) {
-    console.log('No sessions found.');
+    console.log('No browsers found.');
     return;
   }

@@ -732,7 +738,7 @@ async function gcAndPrintSessions(sessions: Session[]) {
     console.log(await renderSessionStatus(session));

   if (running.length === 0 && stopped.length === 0)
-    console.log('  (no sessions)');
+    console.log('  (no browsers)');

 }

@@ -741,7 +747,7 @@ async function renderSessionStatus(session: Session) {
   const config = session.config();
   const canConnect = await session.canConnect();
   const isPersistent = config.cli.persistent;
-  const statusMarker = canConnect ? '[running]' : '[stopped]';
+  const statusMarker = canConnect ? '[open]' : '[closed]';
   const persistentMarker = isPersistent ? ' [persistent]' : '';
   const restartMarker = canConnect && !session.isCompatible() ? ` - v${config.version}, please reopen` : '';
   text.push(`  ${session.name} ${statusMarker}${persistentMarker}${restartMarker}`);
diff --git a/packages/playwright/src/skill/SKILL.md b/packages/playwright/src/skill/SKILL.md
index f01973e4fdabd..18ab060b315f7 100644
--- a/packages/playwright/src/skill/SKILL.md
+++ b/packages/playwright/src/skill/SKILL.md
@@ -181,19 +181,19 @@ playwright-cli close
 playwright-cli delete-data
 ```

-### Sessions
+### Browser Sessions

 ```bash
-playwright-cli --session=mysession open example.com
-playwright-cli --session=mysession click e6
-playwright-cli --session=mysession close  # stop a named session
-playwright-cli --session=mysession delete-data  # delete user data for named session
+playwright-cli -b mysession open example.com
+playwright-cli -b mysession click e6
+playwright-cli -b mysession close  # stop a named browser
+playwright-cli -b mysession delete-data  # delete user data for named browser

-playwright-cli session-list
+playwright-cli list
 # Close all browsers
-playwright-cli session-close-all
+playwright-cli close-all
 # Forcefully kill all browser processes
-playwright-cli session-kill-all
+playwright-cli kill-all
 ```

 ## Example: Form submission
@@ -240,7 +240,7 @@ playwright-cli tracing-stop

 * **Request mocking** [references/request-mocking.md](references/request-mocking.md)
 * **Running Playwright code** [references/running-code.md](references/running-code.md)
-* **Session management** [references/session-management.md](references/session-management.md)
+* **Browser session management** [references/session-management.md](references/session-management.md)
 * **Storage state (cookies, localStorage)** [references/storage-state.md](references/storage-state.md)
 * **Test generation** [references/test-generation.md](references/test-generation.md)
 * **Tracing** [references/tracing.md](references/tracing.md)
diff --git a/packages/playwright/src/skill/references/session-management.md b/packages/playwright/src/skill/references/session-management.md
index c5eeddfab4997..dd685a00a2bc1 100644
--- a/packages/playwright/src/skill/references/session-management.md
+++ b/packages/playwright/src/skill/references/session-management.md
@@ -1,26 +1,26 @@
-# Session Management
+# Browser Session Management

 Run multiple isolated browser sessions concurrently with state persistence.

-## Named Sessions
+## Named Browser Sessions

-Use `--session` flag to isolate browser contexts:
+Use `-b` flag to isolate browser contexts:

 ```bash
-# Session 1: Authentication flow
-playwright-cli --session=auth open https://app.example.com/login
+# Browser 1: Authentication flow
+playwright-cli -b auth open https://app.example.com/login

-# Session 2: Public browsing (separate cookies, storage)
-playwright-cli --session=public open https://example.com
+# Browser 2: Public browsing (separate cookies, storage)
+playwright-cli -b public open https://example.com

-# Commands are isolated by session
-playwright-cli --session=auth fill e1 "user@example.com"
-playwright-cli --session=public snapshot
+# Commands are isolated by browser session
+playwright-cli -b auth fill e1 "user@example.com"
+playwright-cli -b public snapshot
 ```

-## Session Isolation Properties
+## Browser Session Isolation Properties

-Each session has independent:
+Each browser session has independent:
 - Cookies
 - LocalStorage / SessionStorage
 - IndexedDB
@@ -28,30 +28,30 @@ Each session has independent:
 - Browsing history
 - Open tabs

-## Session Commands
+## Browser Session Commands

 ```bash
-# List all sessions
-playwright-cli session-list
+# List all browser sessions
+playwright-cli list

-# Stop a session (close the browser)
-playwright-cli close                      # stop the default session
-playwright-cli --session=mysession close  # stop a named session
+# Stop a browser session (close the browser)
+playwright-cli close                # stop the default browser
+playwright-cli -b mysession close   # stop a named browser

-# Stop all sessions
-playwright-cli session-close-all
+# Stop all browser sessions
+playwright-cli close-all

 # Forcefully kill all daemon processes (for stale/zombie processes)
-playwright-cli session-kill-all
+playwright-cli kill-all

-# Delete session user data (profile directory)
-playwright-cli delete-data                      # delete default session data
-playwright-cli --session=mysession delete-data  # delete named session data
+# Delete browser session user data (profile directory)
+playwright-cli delete-data                # delete default browser data
+playwright-cli -b mysession delete-data   # delete named browser data
 ```

 ## Environment Variable

-Set a default session name via environment variable:
+Set a default browser session name via environment variable:

 ```bash
 export PLAYWRIGHT_CLI_SESSION="mysession"
@@ -66,31 +66,31 @@ playwright-cli open example.com  # Uses "mysession" automatically
 #!/bin/bash
 # Scrape multiple sites concurrently

-# Start all sessions
-playwright-cli --session=site1 open https://site1.com &
-playwright-cli --session=site2 open https://site2.com &
-playwright-cli --session=site3 open https://site3.com &
+# Start all browsers
+playwright-cli -b site1 open https://site1.com &
+playwright-cli -b site2 open https://site2.com &
+playwright-cli -b site3 open https://site3.com &
 wait

 # Take snapshots from each
-playwright-cli --session=site1 snapshot
-playwright-cli --session=site2 snapshot
-playwright-cli --session=site3 snapshot
+playwright-cli -b site1 snapshot
+playwright-cli -b site2 snapshot
+playwright-cli -b site3 snapshot

 # Cleanup
-playwright-cli session-close-all
+playwright-cli close-all
 ```

 ### A/B Testing Sessions

 ```bash
 # Test different user experiences
-playwright-cli --session=variant-a open "https://app.com?variant=a"
-playwright-cli --session=variant-b open "https://app.com?variant=b"
+playwright-cli -b variant-a open "https://app.com?variant=a"
+playwright-cli -b variant-b open "https://app.com?variant=b"

 # Compare
-playwright-cli --session=variant-a screenshot
-playwright-cli --session=variant-b screenshot
+playwright-cli -b variant-a screenshot
+playwright-cli -b variant-b screenshot
 ```

 ### Persistent Profile
@@ -105,20 +105,20 @@ playwright-cli open https://example.com --persistent
 playwright-cli open https://example.com --profile=/path/to/profile
 ```

-## Default Session
+## Default Browser Session

-When `--session` is omitted, commands use the default session:
+When `-b` is omitted, commands use the default browser session:

 ```bash
-# These use the same default session
+# These use the same default browser session
 playwright-cli open https://example.com
 playwright-cli snapshot
-playwright-cli close  # Stops default session
+playwright-cli close  # Stops default browser
 ```

-## Session Configuration
+## Browser Session Configuration

-Configure a session with specific settings when opening:
+Configure a browser session with specific settings when opening:

 ```bash
 # Open with config file
@@ -136,34 +136,34 @@ playwright-cli open https://example.com --persistent

 ## Best Practices

-### 1. Name Sessions Semantically
+### 1. Name Browser Sessions Semantically

 ```bash
 # GOOD: Clear purpose
-playwright-cli --session=github-auth open https://github.com
-playwright-cli --session=docs-scrape open https://docs.example.com
+playwright-cli -b github-auth open https://github.com
+playwright-cli -b docs-scrape open https://docs.example.com

 # AVOID: Generic names
-playwright-cli --session=s1 open https://github.com
+playwright-cli -b s1 open https://github.com
 ```

 ### 2. Always Clean Up

 ```bash
-# Stop sessions when done
-playwright-cli --session=auth close
-playwright-cli --session=scrape close
+# Stop browsers when done
+playwright-cli -b auth close
+playwright-cli -b scrape close

 # Or stop all at once
-playwright-cli session-close-all
+playwright-cli close-all

-# If sessions become unresponsive or zombie processes remain
-playwright-cli session-kill-all
+# If browsers become unresponsive or zombie processes remain
+playwright-cli kill-all
 ```

-### 3. Delete Stale Session Data
+### 3. Delete Stale Browser Data

 ```bash
-# Remove old session data to free disk space
-playwright-cli --session=oldsession delete-data
+# Remove old browser data to free disk space
+playwright-cli -b oldsession delete-data
 ```

PATCH

echo "Patch applied successfully."
