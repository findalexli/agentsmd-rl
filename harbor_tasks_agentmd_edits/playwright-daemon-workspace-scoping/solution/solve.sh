#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q "name: 'session-kill-all'" packages/playwright/src/mcp/terminal/commands.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/playwright/src/mcp/terminal/commands.ts b/packages/playwright/src/mcp/terminal/commands.ts
index cfcefac916106..528e1c22bb240 100644
--- a/packages/playwright/src/mcp/terminal/commands.ts
+++ b/packages/playwright/src/mcp/terminal/commands.ts
@@ -23,14 +23,14 @@ import type { AnyCommandSchema } from './command';

 const open = declareCommand({
   name: 'open',
-  description: 'Open browser',
+  description: 'Open the browser',
   category: 'core',
   args: z.object({
     url: z.string().optional().describe('The URL to navigate to'),
   }),
   options: z.object({
     browser: z.string().optional().describe('Browser or chrome channel to use, possible values: chrome, firefox, webkit, msedge.'),
-    config: z.string().optional().describe('Path to the configuration file'),
+    config: z.string().optional().describe('Path to the configuration file, defaults to .playwright/cli.config.json'),
     extension: z.boolean().optional().describe('Connect to browser extension'),
     headed: z.boolean().optional().describe('Run browser in headed mode'),
     persistent: z.boolean().optional().describe('Use persistent browser profile'),
@@ -42,7 +42,7 @@ const open = declareCommand({

 const close = declareCommand({
   name: 'close',
-  description: 'Close the page',
+  description: 'Close the browser',
   category: 'core',
   args: z.object({}),
   toolName: '',
@@ -771,7 +771,7 @@ const sessionCloseAll = declareCommand({
 });

 const killAll = declareCommand({
-  name: 'kill-all',
+  name: 'session-kill-all',
   description: 'Forcefully kill all daemon processes (for stale/zombie processes)',
   category: 'session',
   toolName: '',
@@ -796,22 +796,25 @@ const configPrint = declareCommand({
 });

 const install = declareCommand({
-  name: 'install-browser',
-  description: 'Install browser',
+  name: 'install',
+  description: 'Initialize workspace',
   category: 'install',
+  args: z.object({}),
   options: z.object({
-    browser: z.string().optional().describe('Browser or chrome channel to use, possible values: chrome, firefox, webkit, msedge'),
+    skills: z.boolean().optional().describe('Install skills for Claude / GitHub Copilot'),
   }),
-  toolName: 'browser_install',
+  toolName: '',
   toolParams: () => ({}),
 });

-const installSkills = declareCommand({
-  name: 'install-skills',
-  description: 'Install Claude / GitGub Copilot skills to the local workspace',
+const installBrowser = declareCommand({
+  name: 'install-browser',
+  description: 'Install browser',
   category: 'install',
-  args: z.object({}),
-  toolName: '',
+  options: z.object({
+    browser: z.string().optional().describe('Browser or chrome channel to use, possible values: chrome, firefox, webkit, msedge'),
+  }),
+  toolName: 'browser_install',
   toolParams: () => ({}),
 });

@@ -894,7 +897,7 @@ const commandsArray: AnyCommandSchema[] = [

   // install category
   install,
-  installSkills,
+  installBrowser,

   // devtools category
   networkRequests,
diff --git a/packages/playwright/src/mcp/terminal/program.ts b/packages/playwright/src/mcp/terminal/program.ts
index c66bdbf3d8d1f..4ba7c6a6f7b32 100644
--- a/packages/playwright/src/mcp/terminal/program.ts
+++ b/packages/playwright/src/mcp/terminal/program.ts
@@ -47,8 +47,7 @@ export type SessionConfig = {

 type ClientInfo = {
   version: string;
-  installationDir: string;
-  installationDirHash: string;
+  workspaceDirHash: string;
   daemonProfilesDir: string;
 };

@@ -249,12 +248,15 @@ to restart the session daemon.`);
     console.log(formatWithGap(`- playwright-cli${sessionOption} close`, `# to stop when done.`));
     console.log(formatWithGap(`- playwright-cli${sessionOption} open [options]`, `# to reopen with new config.`));
     console.log(formatWithGap(`- playwright-cli${sessionOption} delete-data`, `# to delete session data.`));
+    console.log(`---`);
+    console.log(``);

     // Wait for the socket to become available with retries.
-    const maxRetries = 50;
-    const retryDelay = 100; // ms
-    for (let i = 0; i < maxRetries; i++) {
-      await new Promise(resolve => setTimeout(resolve, retryDelay));
+    const retryDelay = [100, 200, 400]; // ms
+    let totalWaited = 0;
+    for (let i = 0; i < 10; i++) {
+      await new Promise(resolve => setTimeout(resolve, retryDelay[i] || 1000));
+      totalWaited += retryDelay[i] || 1000;
       try {
         const { socket } = await this._connect();
         if (socket)
@@ -268,7 +270,7 @@ to restart the session daemon.`);
     const outData = await fs.promises.readFile(outLog, 'utf-8').catch(() => '');
     const errData = await fs.promises.readFile(errLog, 'utf-8').catch(() => '');

-    console.error(`Failed to connect to daemon at ${this._config.socketPath} after ${maxRetries * retryDelay}ms`);
+    console.error(`Failed to connect to daemon at ${this._config.socketPath} after ${totalWaited}ms`);
     if (outData.length)
       console.log(outData);
     if (errData.length)
@@ -347,11 +349,9 @@ class SessionManager {
     const sessionName = this._resolveSessionName(args.session);
     const session = this.sessions.get(sessionName);
     if (!session) {
-      const configFromArgs = sessionConfigFromArgs(this.clientInfo, sessionName, args);
-      const formattedArgs = configToFormattedArgs(configFromArgs.cli);
-      console.log(`The session '${sessionName}' is not open, please run open first:`);
+      console.log(`The session '${sessionName}' is not open, please run open first`);
       console.log('');
-      console.log(`  playwright-cli${sessionName !== 'default' ? ` --session=${sessionName}` : ''} open ${formattedArgs.join(' ')}`);
+      console.log(`  playwright-cli${sessionName !== 'default' ? ` --session=${sessionName}` : ''} open [params]`);
       process.exit(1);
     }

@@ -395,24 +395,36 @@ class SessionManager {

 function createClientInfo(packageLocation: string): ClientInfo {
   const packageJSON = require(packageLocation);
-  const installationDir = process.env.PLAYWRIGHT_CLI_INSTALLATION_FOR_TEST || packageLocation;
+  const workspaceDir = findWorkspaceDir(process.cwd()) || packageLocation;
   const version = process.env.PLAYWRIGHT_CLI_VERSION_FOR_TEST || packageJSON.version;

   const hash = crypto.createHash('sha1');
-  hash.update(installationDir);
-  const installationDirHash = hash.digest('hex').substring(0, 16);
+  hash.update(workspaceDir);
+  const workspaceDirHash = hash.digest('hex').substring(0, 16);

   return {
     version,
-    installationDir,
-    installationDirHash,
-    daemonProfilesDir: daemonProfilesDir(installationDirHash),
+    workspaceDirHash,
+    daemonProfilesDir: daemonProfilesDir(workspaceDirHash),
   };
 }

-const daemonProfilesDir = (installationDirHash: string) => {
+function findWorkspaceDir(startDir: string): string | undefined {
+  let dir = startDir;
+  for (let i = 0; i < 10; i++) {
+    if (fs.existsSync(path.join(dir, '.playwright')))
+      return dir;
+    const parentDir = path.dirname(dir);
+    if (parentDir === dir)
+      break;
+    dir = parentDir;
+  }
+  return undefined;
+}
+
+const daemonProfilesDir = (workspaceDirHash: string) => {
   if (process.env.PLAYWRIGHT_DAEMON_SESSION_DIR)
-    return process.env.PLAYWRIGHT_DAEMON_SESSION_DIR;
+    return path.join(process.env.PLAYWRIGHT_DAEMON_SESSION_DIR, workspaceDirHash);

   let localCacheDir: string | undefined;
   if (process.platform === 'linux')
@@ -423,7 +435,7 @@ const daemonProfilesDir = (installationDirHash: string) => {
     localCacheDir = process.env.LOCALAPPDATA || path.join(os.homedir(), 'AppData', 'Local');
   if (!localCacheDir)
     throw new Error('Unsupported platform: ' + process.platform);
-  return path.join(localCacheDir, 'ms-playwright', 'daemon', installationDirHash);
+  return path.join(localCacheDir, 'ms-playwright', 'daemon', workspaceDirHash);
 };

 type GlobalOptions = {
@@ -510,6 +522,8 @@ export async function program(packageLocation: string) {
         } else {
           const restartMarker = !session.isCompatible() ? ` - v${session.config().version}, please reopen` : '';
           console.log(`  ${session.name}${restartMarker}`);
+          const config = session.config();
+          configToFormattedArgs(config.cli).forEach(arg => console.log(`     ${arg}`));
         }
       }
       if (sessions.size === 0)
@@ -525,7 +539,7 @@ export async function program(packageLocation: string) {
     case 'delete-data':
       await sessionManager.deleteData(args as GlobalOptions);
       return;
-    case 'kill-all':
+    case 'session-kill-all':
       await killAllDaemons();
       return;
     case 'open':
@@ -534,40 +548,49 @@ export async function program(packageLocation: string) {
     case 'close':
       await sessionManager.close(args as GlobalOptions);
       return;
-    case 'install-skills':
-      await installSkills();
+    case 'install':
+      await install(args);
       return;
     default:
       await sessionManager.run(args);
   }
 }

-async function installSkills() {
-  const skillSourceDir = path.join(__dirname, '../../skill');
-  const skillDestDir = path.join(process.cwd(), '.claude', 'skills', 'playwright-cli');
+async function install(args: MinimistArgs) {
+  const cwd = process.cwd();

-  if (!fs.existsSync(skillSourceDir)) {
-    console.error('Skills source directory not found:', skillSourceDir);
-    process.exit(1);
-  }
+  // Create .playwright folder to mark workspace root
+  const playwrightDir = path.join(cwd, '.playwright');
+  await fs.promises.mkdir(playwrightDir, { recursive: true });
+  console.log(`Workspace initialized at ${cwd}`);
+
+  if (args.skills) {
+    const skillSourceDir = path.join(__dirname, '../../skill');
+    const skillDestDir = path.join(cwd, '.claude', 'skills', 'playwright-cli');

-  await fs.promises.cp(skillSourceDir, skillDestDir, { recursive: true });
-  console.log(`Skills installed to ${path.relative(process.cwd(), skillDestDir)}`);
+    if (!fs.existsSync(skillSourceDir)) {
+      console.error('Skills source directory not found:', skillSourceDir);
+      process.exit(1);
+    }
+
+    await fs.promises.cp(skillSourceDir, skillDestDir, { recursive: true });
+    console.log(`Skills installed to ${path.relative(cwd, skillDestDir)}`);
+  }
 }

 function daemonSocketPath(clientInfo: ClientInfo, sessionName: string): string {
   const socketName = `${sessionName}.sock`;
   if (os.platform() === 'win32')
-    return `\\\\.\\pipe\\${clientInfo.installationDirHash}-${socketName}`;
+    return `\\\\.\\pipe\\${clientInfo.workspaceDirHash}-${socketName}`;
   const socketsDir = process.env.PLAYWRIGHT_DAEMON_SOCKETS_DIR || path.join(os.tmpdir(), 'playwright-cli');
-  return path.join(socketsDir, clientInfo.installationDirHash, socketName);
+  return path.join(socketsDir, clientInfo.workspaceDirHash, socketName);
 }

 function sessionConfigFromArgs(clientInfo: ClientInfo, sessionName: string, args: MinimistArgs): SessionConfig {
   let config = args.config ? path.resolve(args.config) : undefined;
   try {
-    if (!config && fs.existsSync('playwright-cli.json'))
-      config = path.resolve('playwright-cli.json');
+    if (!config && fs.existsSync(path.join('.playwright', 'cli.config.json')))
+      config = path.resolve('.playwright', 'cli.config.json');
   } catch {
   }

diff --git a/packages/playwright/src/skill/SKILL.md b/packages/playwright/src/skill/SKILL.md
index ea1b960e2f792..f01973e4fdabd 100644
--- a/packages/playwright/src/skill/SKILL.md
+++ b/packages/playwright/src/skill/SKILL.md
@@ -175,7 +175,10 @@ playwright-cli open --profile=/path/to/profile
 # Start with config file
 playwright-cli open --config=my-config.json

-playwright-cli close                      # stop the default session
+# Close the browser
+playwright-cli close
+# Delete user data for the default session
+playwright-cli delete-data
 ```

 ### Sessions
@@ -187,9 +190,10 @@ playwright-cli --session=mysession close  # stop a named session
 playwright-cli --session=mysession delete-data  # delete user data for named session

 playwright-cli session-list
-playwright-cli session-close-all          # stop all sessions
-playwright-cli delete-data                # delete user data for default session
-playwright-cli kill-all                   # forcefully kill all daemon processes (for stale/zombie processes)
+# Close all browsers
+playwright-cli session-close-all
+# Forcefully kill all browser processes
+playwright-cli session-kill-all
 ```

 ## Example: Form submission
diff --git a/packages/playwright/src/skill/references/session-management.md b/packages/playwright/src/skill/references/session-management.md
index 36eef9775c31c..c5eeddfab4997 100644
--- a/packages/playwright/src/skill/references/session-management.md
+++ b/packages/playwright/src/skill/references/session-management.md
@@ -42,7 +42,7 @@ playwright-cli --session=mysession close  # stop a named session
 playwright-cli session-close-all

 # Forcefully kill all daemon processes (for stale/zombie processes)
-playwright-cli kill-all
+playwright-cli session-kill-all

 # Delete session user data (profile directory)
 playwright-cli delete-data                      # delete default session data
@@ -122,7 +122,7 @@ Configure a session with specific settings when opening:

 ```bash
 # Open with config file
-playwright-cli open https://example.com --config=playwright-cli.json
+playwright-cli open https://example.com --config=.playwright/my-cli.json

 # Open with specific browser
 playwright-cli open https://example.com --browser=firefox
@@ -158,7 +158,7 @@ playwright-cli --session=scrape close
 playwright-cli session-close-all

 # If sessions become unresponsive or zombie processes remain
-playwright-cli kill-all
+playwright-cli session-kill-all
 ```

 ### 3. Delete Stale Session Data

PATCH

echo "Patch applied successfully."
