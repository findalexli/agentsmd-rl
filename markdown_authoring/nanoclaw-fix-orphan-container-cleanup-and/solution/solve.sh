#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanoclaw

# Idempotency guard
if grep -qF "**This step is essential.** When the NanoClaw service restarts (e.g., `launchctl" ".claude/skills/add-voice-transcription/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/add-voice-transcription/SKILL.md b/.claude/skills/add-voice-transcription/SKILL.md
@@ -40,10 +40,10 @@ Read `package.json` and add the `openai` package to dependencies:
 }
 ```
 
-Then install it:
+Then install it. **IMPORTANT:** The OpenAI SDK requires Zod v3 as an optional peer dependency, but NanoClaw uses Zod v4. This conflict is guaranteed, so always use `--legacy-peer-deps`:
 
 ```bash
-npm install
+npm install --legacy-peer-deps
 ```
 
 ### Step 2: Create Transcription Configuration
@@ -296,41 +296,83 @@ if (registeredGroups[chatJid]) {
 }
 ```
 
-### Step 6: Update Package Lock and Build
+### Step 6: Fix Orphan Container Cleanup (CRITICAL)
 
-Run these commands to ensure everything compiles:
+**This step is essential.** When the NanoClaw service restarts (e.g., `launchctl kickstart -k`), the running container is detached but NOT killed. The new service instance spawns a fresh container, but the orphan keeps running and shares the same IPC mount directory. Both containers race to read IPC input files, causing the new container to randomly miss messages — making it appear like the agent doesn't respond.
 
-```bash
-npm install
-npm run build
+The existing cleanup code in `ensureContainerSystemRunning()` in `src/index.ts` uses `container ls --format {{.Names}}` which **silently fails** on Apple Container (only `json` and `table` are valid format options). The catch block swallows the error, so orphans are never cleaned up.
+
+Find the orphan cleanup block in `ensureContainerSystemRunning()` (the section starting with `// Kill and clean up orphaned NanoClaw containers from previous runs`) and replace it with:
+
+```typescript
+  // Kill and clean up orphaned NanoClaw containers from previous runs
+  try {
+    const listJson = execSync('container ls -a --format json', {
+      stdio: ['pipe', 'pipe', 'pipe'],
+      encoding: 'utf-8',
+    });
+    const containers = JSON.parse(listJson) as Array<{ configuration: { id: string }; status: string }>;
+    const nanoclawContainers = containers.filter(
+      (c) => c.configuration.id.startsWith('nanoclaw-'),
+    );
+    const running = nanoclawContainers
+      .filter((c) => c.status === 'running')
+      .map((c) => c.configuration.id);
+    if (running.length > 0) {
+      execSync(`container stop ${running.join(' ')}`, { stdio: 'pipe' });
+      logger.info({ count: running.length }, 'Stopped orphaned containers');
+    }
+    const allNames = nanoclawContainers.map((c) => c.configuration.id);
+    if (allNames.length > 0) {
+      execSync(`container rm ${allNames.join(' ')}`, { stdio: 'pipe' });
+      logger.info({ count: allNames.length }, 'Cleaned up stopped containers');
+    }
+  } catch {
+    // No containers or cleanup not supported
+  }
 ```
 
-If using `--legacy-peer-deps` (due to Zod version conflicts), use:
+### Step 7: Build and Restart
 
 ```bash
-npm install --legacy-peer-deps
 npm run build
 ```
 
-### Step 7: Restart NanoClaw
+Before restarting the service, kill any orphaned containers manually to ensure a clean slate:
+
+```bash
+container ls -a --format json | python3 -c "
+import sys, json
+data = json.load(sys.stdin)
+nc = [c['configuration']['id'] for c in data if c['configuration']['id'].startswith('nanoclaw-')]
+if nc: print(' '.join(nc))
+" | xargs -r container stop 2>/dev/null
+container ls -a --format json | python3 -c "
+import sys, json
+data = json.load(sys.stdin)
+nc = [c['configuration']['id'] for c in data if c['configuration']['id'].startswith('nanoclaw-')]
+if nc: print(' '.join(nc))
+" | xargs -r container rm 2>/dev/null
+echo "Orphaned containers cleaned"
+```
 
-Restart the service to load the new transcription code:
+Now restart the service:
 
 ```bash
-# If using launchd (macOS):
 launchctl kickstart -k gui/$(id -u)/com.nanoclaw
-
-# Or if running manually:
-# Stop the current process and restart with:
-npm start
 ```
 
-Verify it started:
+Verify it started with exactly one (or zero, before first message) nanoclaw container:
 
 ```bash
-sleep 2 && launchctl list | grep nanoclaw
-# or check logs:
-tail -f logs/nanoclaw.log
+sleep 3 && launchctl list | grep nanoclaw
+container ls -a --format json | python3 -c "
+import sys, json
+data = json.load(sys.stdin)
+nc = [c for c in data if c['configuration']['id'].startswith('nanoclaw-')]
+print(f'{len(nc)} nanoclaw container(s)')
+for c in nc: print(f'  {c[\"configuration\"][\"id\"]} - {c[\"status\"]}')
+"
 ```
 
 ### Step 8: Test Voice Transcription
@@ -389,6 +431,41 @@ The architecture supports multiple providers. To add Groq, Deepgram, or local Wh
 
 ## Troubleshooting
 
+### Agent doesn't respond to voice messages (or any messages after a voice note)
+
+**Most likely cause: orphaned containers.** When the service restarts, the previous container keeps running and races to consume IPC messages. Check:
+
+```bash
+container ls -a --format json | python3 -c "
+import sys, json
+data = json.load(sys.stdin)
+nc = [c for c in data if c['configuration']['id'].startswith('nanoclaw-')]
+print(f'{len(nc)} nanoclaw container(s):')
+for c in nc: print(f'  {c[\"configuration\"][\"id\"]} - {c[\"status\"]}')
+"
+```
+
+If you see more than one running container, kill the orphans:
+
+```bash
+# Stop all nanoclaw containers, then restart the service
+container ls -a --format json | python3 -c "
+import sys, json
+data = json.load(sys.stdin)
+running = [c['configuration']['id'] for c in data if c['configuration']['id'].startswith('nanoclaw-') and c['status'] == 'running']
+if running: print(' '.join(running))
+" | xargs -r container stop 2>/dev/null
+container ls -a --format json | python3 -c "
+import sys, json
+data = json.load(sys.stdin)
+nc = [c['configuration']['id'] for c in data if c['configuration']['id'].startswith('nanoclaw-')]
+if nc: print(' '.join(nc))
+" | xargs -r container rm 2>/dev/null
+launchctl kickstart -k gui/$(id -u)/com.nanoclaw
+```
+
+**Root cause:** The `ensureContainerSystemRunning()` function previously used `container ls --format {{.Names}}` which silently fails on Apple Container (only `json` and `table` formats are supported). Step 6 of this skill fixes this. If you haven't applied Step 6, the orphan problem will recur on every restart.
+
 ### "Transcription unavailable" or "Transcription failed"
 
 Check logs for specific errors:
@@ -417,13 +494,11 @@ const __dirname = dirname(__filename);
 
 ### Dependency conflicts (Zod versions)
 
-If you see Zod version conflicts during `npm install`:
+The OpenAI SDK requires Zod v3, but NanoClaw uses Zod v4. This conflict is guaranteed — always use:
 ```bash
 npm install --legacy-peer-deps
 ```
 
-This resolves conflicts between OpenAI SDK (requires Zod v3) and other dependencies.
-
 ---
 
 ## Security Notes
PATCH

echo "Gold patch applied."
