#!/usr/bin/env bash
set -euo pipefail

cd /workspace/orca

# Idempotency guard
if grep -qF "command playwright-cli eval \"(() => { const s = window.__store?.getState(); cons" ".agents/skills/electron/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/electron/SKILL.md b/.agents/skills/electron/SKILL.md
@@ -34,43 +34,59 @@ open -a "Slack" --args --remote-debugging-port=9222
 sleep 3
 
 # Attach playwright-cli to the app via CDP
-playwright-cli attach --cdp="http://localhost:9222"
+command playwright-cli attach --cdp="http://localhost:9222"
 
 # Standard workflow from here
-playwright-cli snapshot
-playwright-cli click e5
-playwright-cli screenshot
+command playwright-cli snapshot
+command playwright-cli click e5
+command playwright-cli screenshot
+```
+
+## Always prefix with `command`
+
+Use `command playwright-cli …` to bypass shell aliases (e.g. `alias playwright-cli='playwright-cli --persistent'`) that leak flags into subcommands. Behaves identically when no alias is set. All examples below use this form.
+
+## Pick a free CDP port
+
+Port 9333 is a convention, not a guarantee — another worktree may hold it, and electron-vite will start without a debugger, letting you silently attach to the old app.
+
+```bash
+for p in 9333 9334 9335 9336 9337 9338 9339 9340; do
+  if ! lsof -i :$p >/dev/null 2>&1; then PORT=$p; break; fi
+done
+# After attach, verify you hit the right worktree:
+command playwright-cli eval "window.__store.getState().worktreesByRepo"
 ```
 
 ## Launching Orca Dev Build with CDP
 
 Orca uses electron-vite for dev builds. The correct way to launch with CDP:
 
 ```bash
-# Launch Orca dev with remote debugging (run in background)
-node config/scripts/run-electron-vite-dev.mjs --remote-debugging-port=9333 2>&1 &
+# Launch with remote debugging (PORT picked above)
+node config/scripts/run-electron-vite-dev.mjs --remote-debugging-port=$PORT 2>&1 &
 
-# Wait for "DevTools listening on ws://..." in the output, then attach
-playwright-cli attach --cdp="http://localhost:9333"
+# Wait for "DevTools listening on ws://..." in output, then attach
+command playwright-cli attach --cdp="http://localhost:$PORT"
 ```
 
 **Key details:**
 - Pass `--remote-debugging-port=NNNN` directly to the script — do NOT use `pnpm run dev -- --` (the double `--` breaks Chromium flag parsing)
-- electron-vite also supports `REMOTE_DEBUGGING_PORT` env var: `REMOTE_DEBUGGING_PORT=9333 pnpm run dev`
+- electron-vite also supports `REMOTE_DEBUGGING_PORT` env var: `REMOTE_DEBUGGING_PORT=$PORT pnpm run dev`
 - The Zustand store is exposed at `window.__store` — use `window.__store.getState()` and `window.__store.getState().someAction()` to read/mutate state
 - Use port 9333 (not 9222) to avoid conflicts with other Electron apps
 
 ### Accessing Orca State via eval
 
 ```bash
 # Read store state
-playwright-cli eval "(() => { const s = window.__store?.getState(); return JSON.stringify({ activeWorktreeId: s.activeWorktreeId, activeTabId: s.activeTabId, activeFileId: s.activeFileId, activeTabType: s.activeTabType }); })()"
+command playwright-cli eval "(() => { const s = window.__store?.getState(); return JSON.stringify({ activeWorktreeId: s.activeWorktreeId, activeTabId: s.activeTabId, activeFileId: s.activeFileId, activeTabType: s.activeTabType }); })()"
 
 # Open an editor file
-playwright-cli eval "(() => { const s = window.__store?.getState(); const wtId = s.activeWorktreeId; s.openFile({ worktreeId: wtId, filePath: '/path/to/file', relativePath: 'file.ts', mode: 'edit', language: 'typescript' }); return 'done'; })()"
+command playwright-cli eval "(() => { const s = window.__store?.getState(); const wtId = s.activeWorktreeId; s.openFile({ worktreeId: wtId, filePath: '/path/to/file', relativePath: 'file.ts', mode: 'edit', language: 'typescript' }); return 'done'; })()"
 
 # Close a file
-playwright-cli eval "(() => { window.__store.getState().closeFile('/path/to/file'); return 'closed'; })()"
+command playwright-cli eval "(() => { window.__store.getState().closeFile('/path/to/file'); return 'closed'; })()"
 ```
 
 ## Launching Electron Apps with CDP
@@ -128,18 +144,18 @@ lsof -i :9222
 curl -s http://localhost:9222/json
 
 # Attach playwright-cli
-playwright-cli attach --cdp="http://localhost:9222"
+command playwright-cli attach --cdp="http://localhost:9222"
 ```
 
 ## Attaching
 
 ```bash
 # Attach to a specific CDP port
-playwright-cli attach --cdp="http://localhost:9222"
+command playwright-cli attach --cdp="http://localhost:9222"
 
 # Attach with a named session (for controlling multiple apps)
-playwright-cli -s=slack attach --cdp="http://localhost:9222"
-playwright-cli -s=vscode attach --cdp="http://localhost:9223"
+command playwright-cli -s=slack attach --cdp="http://localhost:9222"
+command playwright-cli -s=vscode attach --cdp="http://localhost:9223"
 ```
 
 After `attach`, all subsequent commands (in that session) target the connected app.
@@ -150,10 +166,10 @@ Electron apps may have multiple windows or webviews. Use tab commands to list an
 
 ```bash
 # List all available targets
-playwright-cli tab-list
+command playwright-cli tab-list
 
 # Switch to a specific tab by index
-playwright-cli tab-select 2
+command playwright-cli tab-select 2
 ```
 
 If `tab-list` doesn't show all targets, query the CDP endpoint directly to see everything:
@@ -173,39 +189,39 @@ for i, t in enumerate(json.load(sys.stdin)):
 ```bash
 open -a "Slack" --args --remote-debugging-port=9222
 sleep 3
-playwright-cli attach --cdp="http://localhost:9222"
-playwright-cli snapshot
+command playwright-cli attach --cdp="http://localhost:9222"
+command playwright-cli snapshot
 # Read the snapshot output to identify UI elements
-playwright-cli click e10   # Navigate to a section
-playwright-cli snapshot    # Re-snapshot after navigation
+command playwright-cli click e10   # Navigate to a section
+command playwright-cli snapshot    # Re-snapshot after navigation
 ```
 
 ### Take Screenshots of Desktop Apps
 
 ```bash
-playwright-cli attach --cdp="http://localhost:9222"
-playwright-cli screenshot
-playwright-cli screenshot e5  # Screenshot a specific element
-playwright-cli screenshot --filename=app-state.png
+command playwright-cli attach --cdp="http://localhost:9222"
+command playwright-cli screenshot
+command playwright-cli screenshot e5  # Screenshot a specific element
+command playwright-cli screenshot --filename=app-state.png
 ```
 
 ### Extract Data from a Desktop App
 
 ```bash
-playwright-cli attach --cdp="http://localhost:9222"
-playwright-cli snapshot
-playwright-cli eval "document.title"
-playwright-cli eval "el => el.textContent" e5
+command playwright-cli attach --cdp="http://localhost:9222"
+command playwright-cli snapshot
+command playwright-cli eval "document.title"
+command playwright-cli eval "el => el.textContent" e5
 ```
 
 ### Fill Forms in Desktop Apps
 
 ```bash
-playwright-cli attach --cdp="http://localhost:9222"
-playwright-cli snapshot
-playwright-cli fill e3 "search query"
-playwright-cli press Enter
-playwright-cli snapshot
+command playwright-cli attach --cdp="http://localhost:9222"
+command playwright-cli snapshot
+command playwright-cli fill e3 "search query"
+command playwright-cli press Enter
+command playwright-cli snapshot
 ```
 
 ### Run Multiple Apps Simultaneously
@@ -214,22 +230,22 @@ Use named sessions to control multiple Electron apps at the same time:
 
 ```bash
 # Attach to Slack
-playwright-cli -s=slack attach --cdp="http://localhost:9222"
+command playwright-cli -s=slack attach --cdp="http://localhost:9222"
 
 # Attach to VS Code
-playwright-cli -s=vscode attach --cdp="http://localhost:9223"
+command playwright-cli -s=vscode attach --cdp="http://localhost:9223"
 
 # Interact with each independently
-playwright-cli -s=slack snapshot
-playwright-cli -s=vscode snapshot
+command playwright-cli -s=slack snapshot
+command playwright-cli -s=vscode snapshot
 ```
 
 ### Run Custom Playwright Code
 
 For advanced scenarios, use `run-code` to execute arbitrary Playwright code:
 
 ```bash
-playwright-cli run-code "async page => {
+command playwright-cli run-code "async page => {
   await page.waitForSelector('.loading', { state: 'hidden' });
   const items = await page.locator('.item').allTextContents();
   return items;
@@ -284,11 +300,11 @@ If an app is built with Electron, it supports `--remote-debugging-port` and can
 
 ```bash
 # Close the playwright-cli session (does NOT kill the Electron app)
-playwright-cli close
+command playwright-cli close
 
 # Close a named session
-playwright-cli -s=slack close
+command playwright-cli -s=slack close
 
 # Close all playwright-cli sessions
-playwright-cli close-all
+command playwright-cli close-all
 ```
PATCH

echo "Gold patch applied."
