#!/bin/bash
set -e

cd /workspace/playwright

# Check if already applied (idempotency check - looking for workspaceDirHash)
if grep -q "workspaceDirHash" packages/playwright/src/mcp/terminal/program.ts 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch - scopes daemon by workspace instead of installation directory
cat > /tmp/fix.patch << 'ENDPATCH'
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

ENDPATCH

git apply /tmp/fix.patch || (echo "Failed to apply patch" && exit 1)

# Now update the SKILL.md documentation files
cat > packages/playwright/src/skill/SKILL.md << 'ENDSKILL'
---
name: playwright-cli
description: Automates browser interactions for web testing, form filling, screenshots, and data extraction. Use when the user needs to navigate websites, interact with web pages, fill forms, take screenshots, test web applications, or extract information from web pages.
allowed-tools: Bash(playwright-cli:*)
---

# Browser Automation with playwright-cli

## Quick start

```bash
playwright-cli open https://playwright.dev
playwright-cli click e15
playwright-cli type "page.click"
playwright-cli press Enter
```

## Core workflow

1. Navigate: `playwright-cli open https://example.com`
2. Interact using refs from the snapshot
3. Re-snapshot after significant changes

## Commands

### Core

```bash
playwright-cli open https://example.com/
playwright-cli close
playwright-cli type "search query"
playwright-cli click e3
playwright-cli dblclick e7
playwright-cli fill e5 "user@example.com"
playwright-cli drag e2 e8
playwright-cli hover e4
playwright-cli select e9 "option-value"
playwright-cli upload ./document.pdf
playwright-cli check e12
playwright-cli uncheck e12
playwright-cli snapshot
playwright-cli snapshot --filename=after-click.yaml
playwright-cli eval "document.title"
playwright-cli eval "el => el.textContent" e5
playwright-cli dialog-accept
playwright-cli dialog-accept "confirmation text"
playwright-cli dialog-dismiss
playwright-cli resize 1920 1080
```

### Navigation

```bash
playwright-cli go-back
playwright-cli go-forward
playwright-cli reload
```

### Keyboard

```bash
playwright-cli press Enter
playwright-cli press ArrowDown
playwright-cli keydown Shift
playwright-cli keyup Shift
```

### Mouse

```bash
playwright-cli mousemove 150 300
playwright-cli mousedown
playwright-cli mousedown right
playwright-cli mouseup
playwright-cli mouseup right
playwright-cli mousewheel 0 100
```

### Save as

```bash
playwright-cli screenshot
playwright-cli screenshot e5
playwright-cli screenshot --filename=page.png
playwright-cli pdf --filename=page.pdf
```

### Tabs

```bash
playwright-cli tab-list
playwright-cli tab-new
playwright-cli tab-new https://example.com/page
playwright-cli tab-close
playwright-cli tab-close 2
playwright-cli tab-select 0
```

### Storage

```bash
playwright-cli state-save
playwright-cli state-save auth.json
playwright-cli state-load auth.json

# Cookies
playwright-cli cookie-list
playwright-cli cookie-list --domain=example.com
playwright-cli cookie-get session_id
playwright-cli cookie-set session_id abc123
playwright-cli cookie-set session_id abc123 --domain=example.com --httpOnly --secure
playwright-cli cookie-delete session_id
playwright-cli cookie-clear

# LocalStorage
playwright-cli localstorage-list
playwright-cli localstorage-get theme
playwright-cli localstorage-set theme dark
playwright-cli localstorage-delete theme
playwright-cli localstorage-clear

# SessionStorage
playwright-cli sessionstorage-list
playwright-cli sessionstorage-get step
playwright-cli sessionstorage-set step 3
playwright-cli sessionstorage-delete step
playwright-cli sessionstorage-clear
```

### Network

```bash
playwright-cli route "**/*.jpg" --status=404
playwright-cli route "https://api.example.com/**" --body='{"mock": true}'
playwright-cli route-list
playwright-cli unroute "**/*.jpg"
playwright-cli unroute
```

### DevTools

```bash
playwright-cli console
playwright-cli console warning
playwright-cli network
playwright-cli run-code "async page => await page.context().grantPermissions(['geolocation'])"
playwright-cli tracing-start
playwright-cli tracing-stop
playwright-cli video-start
playwright-cli video-stop video.webm
```

### Install

```bash
playwright-cli install-browser
playwright-cli install-skills
```

### Configuration
```bash
# Use specific browser when creating session
playwright-cli open --browser=chrome
playwright-cli open --browser=firefox
playwright-cli open --browser=webkit
playwright-cli open --browser=msedge
# Connect to browser via extension
playwright-cli open --extension

# Use persistent profile (by default profile is in-memory)
playwright-cli open --persistent
# Use persistent profile with custom directory
playwright-cli open --profile=/path/to/profile

# Start with config file
playwright-cli open --config=my-config.json

# Close the browser
playwright-cli close
# Delete user data for the default session
playwright-cli delete-data
```

### Sessions

```bash
playwright-cli --session=mysession open example.com
playwright-cli --session=mysession click e6
playwright-cli --session=mysession close  # stop a named session
playwright-cli --session=mysession delete-data  # delete user data for named session

playwright-cli session-list
# Close all browsers
playwright-cli session-close-all
# Forcefully kill all browser processes
playwright-cli session-kill-all
```

## Example: Form submission

```bash
playwright-cli open https://example.com/form
playwright-cli snapshot

playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "password123"
playwright-cli click e3
playwright-cli snapshot
```

## Example: Multi-tab workflow

```bash
playwright-cli open https://example.com
playwright-cli tab-new https://example.com/other
playwright-cli tab-list
playwright-cli tab-select 0
playwright-cli snapshot
```

## Example: Debugging with DevTools

```bash
playwright-cli open https://example.com
playwright-cli click e4
playwright-cli fill e7 "test"
playwright-cli console
playwright-cli network
```

```bash
playwright-cli open https://example.com
playwright-cli tracing-start
playwright-cli click e4
playwright-cli fill e7 "test"
playwright-cli tracing-stop
```

## Specific tasks

* **Request mocking** [references/request-mocking.md](references/request-mocking.md)
* **Running Playwright code** [references/running-code.md](references/running-code.md)
* **Session management** [references/session-management.md](references/session-management.md)
* **Storage state (cookies, localStorage)** [references/storage-state.md](references/storage-state.md)
* **Test generation** [references/test-generation.md](references/test-generation.md)
* **Tracing** [references/tracing.md](references/tracing.md)
* **Video recording** [references/video-recording.md](references/video-recording.md)
ENDSKILL

# Update session-management.md reference file
cat > packages/playwright/src/skill/references/session-management.md << 'ENDSESSION'
# Session Management

Run multiple isolated browser sessions concurrently with state persistence.

## Named Sessions

Use `--session` flag to isolate browser contexts:

```bash
# Session 1: Authentication flow
playwright-cli --session=auth open https://app.example.com/login

# Session 2: Public browsing (separate cookies, storage)
playwright-cli --session=public open https://example.com

# Commands are isolated by session
playwright-cli --session=auth fill e1 "user@example.com"
playwright-cli --session=public snapshot
```

## Session Isolation Properties

Each session has independent:
- Cookies
- LocalStorage / SessionStorage
- IndexedDB
- Cache
- Browsing history
- Open tabs

## Session Commands

```bash
# List all sessions
playwright-cli session-list

# Stop a session (close the browser)
playwright-cli close                      # stop the default session
playwright-cli --session=mysession close  # stop a named session

# Stop all sessions
playwright-cli session-close-all

# Forcefully kill all daemon processes (for stale/zombie processes)
playwright-cli session-kill-all

# Delete session user data (profile directory)
playwright-cli delete-data                      # delete default session data
playwright-cli --session=mysession delete-data  # delete named session data
```

## Environment Variable

Set a default session name via environment variable:

```bash
export PLAYWRIGHT_CLI_SESSION="mysession"
playwright-cli open example.com  # Uses "mysession" automatically
```

## Common Patterns

### Concurrent Scraping

```bash
#!/bin/bash
# Scrape multiple sites concurrently

# Start all sessions
playwright-cli --session=site1 open https://site1.com &
playwright-cli --session=site2 open https://site2.com &
playwright-cli --session=site3 open https://site3.com &
wait

# Take snapshots from each
playwright-cli --session=site1 snapshot
playwright-cli --session=site2 snapshot
playwright-cli --session=site3 snapshot

# Cleanup
playwright-cli session-close-all
```

### A/B Testing Sessions

```bash
# Test different user experiences
playwright-cli --session=variant-a open "https://app.com?variant=a"
playwright-cli --session=variant-b open "https://app.com?variant=b"

# Compare
playwright-cli --session=variant-a screenshot
playwright-cli --session=variant-b screenshot
```

### Persistent Profile

By default, browser profile is kept in memory only. Use `--persistent` flag on `open` to persist the browser profile to disk:

```bash
# Use persistent profile (auto-generated location)
playwright-cli open https://example.com --persistent

# Use persistent profile with custom directory
playwright-cli open https://example.com --profile=/path/to/profile
```

## Default Session

When `--session` is omitted, commands use the default session:

```bash
# These use the same default session
playwright-cli open https://example.com
playwright-cli snapshot
playwright-cli close  # Stops default session
```

## Session Configuration

Configure a session with specific settings when opening:

```bash
# Open with config file
playwright-cli open https://example.com --config=.playwright/my-cli.json

# Open with specific browser
playwright-cli open https://example.com --browser=firefox

# Open in headed mode
playwright-cli open https://example.com --headed

# Open with persistent profile
playwright-cli open https://example.com --persistent
```

## Best Practices

### 1. Name Sessions Semantically

```bash
# GOOD: Clear purpose
playwright-cli --session=github-auth open https://github.com
playwright-cli --session=docs-scrape open https://docs.example.com

# AVOID: Generic names
playwright-cli --session=s1 open https://github.com
```

### 2. Always Clean Up

```bash
# Stop sessions when done
playwright-cli --session=auth close
playwright-cli --session=scrape close

# Or stop all at once
playwright-cli session-close-all

# If sessions become unresponsive or zombie processes remain
playwright-cli session-kill-all
```

### 3. Delete Stale Session Data

```bash
# Remove old session data to free disk space
playwright-cli --session=oldsession delete-data
```
ENDSESSION

echo "Fix applied successfully!"
