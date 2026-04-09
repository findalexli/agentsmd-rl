#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'const killAll = declareCommand' packages/playwright/src/mcp/terminal/commands.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/packages/playwright/src/mcp/terminal/commands.ts b/packages/playwright/src/mcp/terminal/commands.ts
index 635709269d291..ffbb59e03282e 100644
--- a/packages/playwright/src/mcp/terminal/commands.ts
+++ b/packages/playwright/src/mcp/terminal/commands.ts
@@ -773,6 +773,14 @@ const sessionStopAll = declareCommand({
   toolParams: () => ({}),
 });

+const killAll = declareCommand({
+  name: 'kill-all',
+  description: 'Forcefully kill all daemon processes (for stale/zombie processes)',
+  category: 'session',
+  toolName: '',
+  toolParams: () => ({}),
+});
+
 const sessionDelete = declareCommand({
   name: 'session-delete',
   description: 'Delete session data',
@@ -920,6 +928,7 @@ const commandsArray: AnyCommandSchema[] = [
   sessionRestart,
   sessionStopAll,
   sessionDelete,
+  killAll,
 ];

 export const commands = Object.fromEntries(commandsArray.map(cmd => [cmd.name, cmd]));
diff --git a/packages/playwright/src/mcp/terminal/program.ts b/packages/playwright/src/mcp/terminal/program.ts
index 845caf80096ac..88428051e5b78 100644
--- a/packages/playwright/src/mcp/terminal/program.ts
+++ b/packages/playwright/src/mcp/terminal/program.ts
@@ -17,7 +17,7 @@
 /* eslint-disable no-console */
 /* eslint-disable no-restricted-properties */

-import { spawn } from 'child_process';
+import { execSync, spawn } from 'child_process';

 import crypto from 'crypto';
 import fs from 'fs';
@@ -435,6 +435,11 @@ async function handleSessionCommand(sessionManager: SessionManager, subcommand:
     return;
   }

+  if (subcommand === 'kill-all') {
+    await killAllDaemons();
+    return;
+  }
+
   if (subcommand === 'delete') {
     await sessionManager.delete(args._[1]);
     return;
@@ -547,6 +552,11 @@ export async function program(packageLocation: string) {
     return;
   }

+  if (commandName === 'kill-all') {
+    await handleSessionCommand(sessionManager, 'kill-all', args);
+    return;
+  }
+
   if (commandName === 'install-skills') {
     await installSkills();
     return;
@@ -618,3 +628,51 @@ function configToFormattedArgs(config: SessionConfig['cli']): string[] {
   add('in-memory', config.isolated);
   return args;
 }
+
+async function killAllDaemons(): Promise<void> {
+  const platform = os.platform();
+  let killed = 0;
+
+  try {
+    if (platform === 'win32') {
+      const result = execSync(
+          `powershell -NoProfile -NonInteractive -Command `
+          + `"Get-CimInstance Win32_Process `
+          + `| Where-Object { $_.CommandLine -like '*run-mcp-server*' -and $_.CommandLine -like '*--daemon-session*' } `
+          + `| ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; $_.ProcessId }"`,
+          { encoding: 'utf-8' }
+      );
+      const pids = result.split('\n')
+          .map(line => line.trim())
+          .filter(line => /^\d+$/.test(line));
+      for (const pid of pids)
+        console.log(`Killed daemon process ${pid}`);
+      killed = pids.length;
+    } else {
+      const result = execSync('ps aux', { encoding: 'utf-8' });
+      const lines = result.split('\n');
+      for (const line of lines) {
+        if (line.includes('run-mcp-server') && line.includes('--daemon-session')) {
+          const parts = line.trim().split(/\s+/);
+          const pid = parts[1];
+          if (pid && /^\d+$/.test(pid)) {
+            try {
+              process.kill(parseInt(pid, 10), 'SIGKILL');
+              console.log(`Killed daemon process ${pid}`);
+              killed++;
+            } catch {
+              // Process may have already exited
+            }
+          }
+        }
+      }
+    }
+  } catch (e) {
+    // Silently handle errors - no processes to kill is fine
+  }
+
+  if (killed === 0)
+    console.log('No daemon processes found.');
+  else if (killed > 0)
+    console.log(`Killed ${killed} daemon process${killed === 1 ? '' : 'es'}.`);
+}
diff --git a/packages/playwright/src/skill/SKILL.md b/packages/playwright/src/skill/SKILL.md
index cbf8b3209eaef..df5c91e9d1aa0 100644
--- a/packages/playwright/src/skill/SKILL.md
+++ b/packages/playwright/src/skill/SKILL.md
@@ -187,6 +187,7 @@ playwright-cli session-restart mysession
 playwright-cli session-stop-all
 playwright-cli session-delete
 playwright-cli session-delete mysession
+playwright-cli kill-all  # forcefully kill all daemon processes (for stale/zombie processes)
 ```

 ## Example: Form submission
diff --git a/packages/playwright/src/skill/references/session-management.md b/packages/playwright/src/skill/references/session-management.md
index 99ce2a833d33c..4c06b7e036a0d 100644
--- a/packages/playwright/src/skill/references/session-management.md
+++ b/packages/playwright/src/skill/references/session-management.md
@@ -40,6 +40,9 @@ playwright-cli session-stop mysession
 # Stop all sessions
 playwright-cli session-stop-all

+# Forcefully kill all daemon processes (for stale/zombie processes)
+playwright-cli kill-all
+
 # Restart a session (useful after version updates)
 playwright-cli session-restart mysession

@@ -153,6 +156,9 @@ playwright-cli session-stop scrape

 # Or stop all at once
 playwright-cli session-stop-all
+
+# If sessions become unresponsive or zombie processes remain
+playwright-cli kill-all
 ```

 ### 3. Delete Stale Session Data
diff --git a/tests/mcp/cli-session.spec.ts b/tests/mcp/cli-session.spec.ts
index 76b895f25a2b0..2d36a8548694e 100644
--- a/tests/mcp/cli-session.spec.ts
+++ b/tests/mcp/cli-session.spec.ts
@@ -65,6 +65,20 @@ test('session-stop-all', async ({ cli, server }) => {
   expect(listAfter).not.toContain('[running]');
 });

+test('kill-all', async ({ cli, server }) => {
+  await cli('open', '--session=killsession1', server.HELLO_WORLD);
+  await cli('open', '--session=killsession2', server.HELLO_WORLD);
+
+  const { output: listBefore } = await cli('session-list');
+  expect(listBefore).toContain('[running] killsession1');
+  expect(listBefore).toContain('[running] killsession2');
+
+  const { output } = await cli('kill-all');
+  expect(output).toContain('Killed daemon process');
+
+  await expect.poll(() => cli('session-list').then(r => r.output)).not.toContain('[running]');
+});
+
 test('session-delete', async ({ cli, server, mcpBrowser }, testInfo) => {
   await cli('open', server.HELLO_WORLD);

PATCH

echo "Patch applied successfully."
