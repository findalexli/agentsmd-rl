#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'AttachOptions' packages/playwright-core/src/tools/cli-client/program.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/playwright-core/src/tools/cli-client/program.ts b/packages/playwright-core/src/tools/cli-client/program.ts
index 9721950d050b1..969aff5498221 100644
--- a/packages/playwright-core/src/tools/cli-client/program.ts
+++ b/packages/playwright-core/src/tools/cli-client/program.ts
@@ -38,17 +38,23 @@ type GlobalOptions = {
   version?: boolean;
 };

-type OpenOptions = {
+type AttachOptions = {
+  config?: string;
+  cdp?: string;
   endpoint?: string;
+  extension?: boolean | string;
+};
+
+type OpenOptions = {
   browser?: string;
   config?: string;
-  extension?: boolean;
   headed?: boolean;
   persistent?: boolean;
   profile?: string;
 };

-const globalOptions: (keyof (GlobalOptions & OpenOptions))[] = [
+const globalOptions: (keyof (GlobalOptions & OpenOptions & AttachOptions))[] = [
+  'cdp',
   'endpoint',
   'browser',
   'config',
@@ -62,7 +68,7 @@ const globalOptions: (keyof (GlobalOptions & OpenOptions))[] = [
   'version',
 ];

-const booleanOptions: (keyof (GlobalOptions & OpenOptions & { all?: boolean }))[] = [
+const booleanOptions: (keyof (GlobalOptions & OpenOptions & AttachOptions & { all?: boolean }))[] = [
   'all',
   'help',
   'raw',
@@ -140,9 +146,18 @@ export async function program(options?: { embedderVersion?: string}) {
       return;
     }
     case 'attach': {
-      const attachTarget = args._[1];
-      const attachSessionName = explicitSessionName(args.session as string) ?? attachTarget;
-      args.endpoint = attachTarget;
+      const attachTarget = args._[1] as string | undefined;
+      if (attachTarget && (args.cdp || args.endpoint || args.extension)) {
+        console.error(`Error: cannot use target name with --cdp, --endpoint, or --extension`);
+        process.exit(1);
+      }
+      if (attachTarget)
+        args.endpoint = attachTarget;
+      if (typeof args.extension === 'string') {
+        args.browser = args.extension;
+        args.extension = true;
+      }
+      const attachSessionName = explicitSessionName(args.session as string) ?? attachTarget ?? sessionName;
       args.session = attachSessionName;
       await startSession(attachSessionName, registry, clientInfo, args);
       return;
diff --git a/packages/playwright-core/src/tools/cli-client/registry.ts b/packages/playwright-core/src/tools/cli-client/registry.ts
index 018b8de7caa59..be36ae1b9f109 100644
--- a/packages/playwright-core/src/tools/cli-client/registry.ts
+++ b/packages/playwright-core/src/tools/cli-client/registry.ts
@@ -191,9 +191,5 @@ export function explicitSessionName(sessionName?: string): string | undefined {
 }

 export function resolveSessionName(sessionName?: string): string {
-  if (sessionName)
-    return sessionName;
-  if (process.env.PLAYWRIGHT_CLI_SESSION)
-    return process.env.PLAYWRIGHT_CLI_SESSION;
-  return 'default';
+  return explicitSessionName(sessionName) || 'default';
 }
diff --git a/packages/playwright-core/src/tools/cli-client/session.ts b/packages/playwright-core/src/tools/cli-client/session.ts
index 5864b5d771150..6cbebad9149b4 100644
--- a/packages/playwright-core/src/tools/cli-client/session.ts
+++ b/packages/playwright-core/src/tools/cli-client/session.ts
@@ -143,6 +143,8 @@ export class Session {
       args.push(`--profile=${cliArgs.profile}`);
     if (cliArgs.config)
       args.push(`--config=${cliArgs.config}`);
+    if (cliArgs.cdp)
+      args.push(`--cdp=${cliArgs.cdp}`);
     if (cliArgs.endpoint || process.env.PLAYWRIGHT_CLI_SESSION)
       args.push(`--endpoint=${cliArgs.endpoint || process.env.PLAYWRIGHT_CLI_SESSION}`);
diff --git a/packages/playwright-core/src/tools/cli-client/skill/SKILL.md b/packages/playwright-core/src/tools/cli-client/skill/SKILL.md
index fbf1536a67a33..cb115c65f852e 100644
--- a/packages/playwright-core/src/tools/cli-client/skill/SKILL.md
+++ b/packages/playwright-core/src/tools/cli-client/skill/SKILL.md
@@ -182,14 +182,15 @@ playwright-cli open --browser=chrome
 playwright-cli open --browser=firefox
 playwright-cli open --browser=webkit
 playwright-cli open --browser=msedge
-# Connect to browser via extension
-playwright-cli open --extension

 # Use persistent profile (by default profile is in-memory)
 playwright-cli open --persistent
 # Use persistent profile with custom directory
 playwright-cli open --profile=/path/to/profile

+# Connect to browser via extension
+playwright-cli attach --extension
+
 # Start with config file
 playwright-cli open --config=my-config.json
diff --git a/packages/playwright-core/src/tools/cli-daemon/commands.ts b/packages/playwright-core/src/tools/cli-daemon/commands.ts
index 73ef6a29a8da9..5cc69c607dfdc 100644
--- a/packages/playwright-core/src/tools/cli-daemon/commands.ts
+++ b/packages/playwright-core/src/tools/cli-daemon/commands.ts
@@ -51,7 +51,6 @@ const open = declareCommand({
   options: z.object({
     browser: z.string().optional().describe('Browser or chrome channel to use, possible values: chrome, firefox, webkit, msedge.'),
     config: z.string().optional().describe('Path to the configuration file, defaults to .playwright/cli.config.json'),
-    extension: z.boolean().optional().describe('Connect to browser extension'),
     headed: z.boolean().optional().describe('Run browser in headed mode'),
     persistent: z.boolean().optional().describe('Use persistent browser profile'),
     profile: z.string().optional().describe('Use persistent browser profile, store profile in specified directory.'),
@@ -65,11 +64,14 @@ const attach = declareCommand({
   description: 'Attach to a running Playwright browser',
   category: 'core',
   args: z.object({
-    name: z.string().describe('Name or endpoint of the browser to attach to'),
+    name: z.string().optional().describe('Bound browser name to attach to'),
   }),
   options: z.object({
+    cdp: z.string().optional().describe('Connect to an existing browser via CDP endpoint URL.'),
+    endpoint: z.string().optional().describe('Playwright browser server endpoint to attach to.'),
+    extension: z.union([z.boolean(), z.string()]).optional().describe('Connect to browser extension, optionally specify browser name (e.g. --extension=chrome)'),
     config: z.string().optional().describe('Path to the configuration file, defaults to .playwright/cli.config.json'),
-    session: z.string().optional().describe('Session name alias (defaults to the attach target name)'),
+    session: z.string().optional().describe('Session name (defaults to bound browser name or "default")'),
   }),
   toolName: 'browser_snapshot',
   toolParams: () => ({ filename: '<auto>' }),
diff --git a/packages/playwright-core/src/tools/cli-daemon/program.ts b/packages/playwright-core/src/tools/cli-daemon/program.ts
index 6afa3f42ab051..85eed4dd93cdd 100644
--- a/packages/playwright-core/src/tools/cli-daemon/program.ts
+++ b/packages/playwright-core/src/tools/cli-daemon/program.ts
@@ -36,6 +36,7 @@ program.argument('[session-name]', 'name of the session to create or connect to'
     .option('--persistent', 'use a persistent browser context')
     .option('--profile <path>', 'path to the user data dir')
     .option('--config <path>', 'path to the config file; by default uses .playwright/cli.config.json in the project directory and ~/.playwright/cli.config.json as global config')
+    .option('--cdp <url>', 'connect to an existing browser via CDP endpoint URL')
     .option('--endpoint <endpoint>', 'attach to a running Playwright browser endpoint')
     .option('--init-workspace', 'initialize workspace')
     .option('--init-skills <value>', 'install skills for the given agent type ("claude" or "agents")')
diff --git a/packages/playwright-core/src/tools/mcp/config.ts b/packages/playwright-core/src/tools/mcp/config.ts
index d95b689056152..c199bbfbec302 100644
--- a/packages/playwright-core/src/tools/mcp/config.ts
+++ b/packages/playwright-core/src/tools/mcp/config.ts
@@ -140,6 +140,7 @@ export async function resolveCLIConfigForCLI(daemonProfilesDir: string, sessionN

   const daemonOverrides = configFromCLIOptions({
     endpoint: options.endpoint,
+    cdpEndpoint: options.cdp,
     config: options.config,
     browser: options.browser,
     headless: options.headed ? false : undefined,
@@ -161,7 +162,7 @@ export async function resolveCLIConfigForCLI(daemonProfilesDir: string, sessionN
   result = mergeConfig(result, daemonOverrides);

   if (result.browser.isolated === undefined)
-    result.browser.isolated = !options.profile && !options.persistent && !result.browser.userDataDir && !result.browser.remoteEndpoint && !result.extension;
+    result.browser.isolated = !options.profile && !options.persistent && !result.browser.userDataDir && !result.browser.remoteEndpoint && !result.browser.cdpEndpoint && !result.extension;

   if (!result.extension && !result.browser.isolated && !result.browser.userDataDir && !result.browser.remoteEndpoint) {
     // No custom value provided, use the daemon data dir.

PATCH

echo "Patch applied successfully."
