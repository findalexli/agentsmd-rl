#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanoclaw

# Idempotency guard
if grep -qF "- Container runtime check is unchanged (ensureContainerSystemRunning)" ".claude/skills/add-discord/modify/src/index.ts.intent.md" && grep -qF "echo '{}' | docker run -i --entrypoint /bin/echo nanoclaw-agent:latest \"Containe" ".claude/skills/add-parallel/SKILL.md" && grep -qF "- Container runtime check is unchanged (ensureContainerSystemRunning)" ".claude/skills/add-telegram/modify/src/index.ts.intent.md" && grep -qF "### Step 7: Test Voice Transcription" ".claude/skills/add-voice-transcription/SKILL.md" && grep -qF "echo '{}' | docker run -i --entrypoint /bin/echo nanoclaw-agent:latest \"OK\" 2>/d" ".claude/skills/debug/SKILL.md" && grep -qF "**If APPLE_CONTAINER=installed** (macOS only): Ask the user which runtime they'd" ".claude/skills/setup/SKILL.md" && grep -qF "docker build -t \"${IMAGE_NAME}:${TAG}\" -f container/Dockerfile ." ".claude/skills/x-integration/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/add-discord/modify/src/index.ts.intent.md b/.claude/skills/add-discord/modify/src/index.ts.intent.md
@@ -33,7 +33,7 @@ Added Discord as a channel option alongside WhatsApp, introducing multi-channel
 - The `runAgent` function is completely unchanged
 - State management (loadState/saveState) is unchanged
 - Recovery logic is unchanged
-- Apple Container check is unchanged (ensureContainerSystemRunning)
+- Container runtime check is unchanged (ensureContainerSystemRunning)
 
 ## Must-keep
 - The `escapeXml` and `formatMessages` re-exports
diff --git a/.claude/skills/add-parallel/SKILL.md b/.claude/skills/add-parallel/SKILL.md
@@ -13,7 +13,7 @@ Adds Parallel AI MCP integration to NanoClaw for advanced web research capabilit
 User must have:
 1. Parallel AI API key from https://platform.parallel.ai
 2. NanoClaw already set up and running
-3. Container system working (Apple Container or Docker)
+3. Docker installed and running
 
 ## Implementation Steps
 
@@ -224,14 +224,9 @@ Build the container with updated agent runner:
 ./container/build.sh
 ```
 
-The build script will automatically:
-- Try Apple Container first
-- Fall back to Docker if Rosetta is required
-- Import to Apple Container
-
 Verify the build:
 ```bash
-echo '{}' | container run -i --entrypoint /bin/echo nanoclaw-agent:latest "Container OK"
+echo '{}' | docker run -i --entrypoint /bin/echo nanoclaw-agent:latest "Container OK"
 ```
 
 ### 7. Restart Service
diff --git a/.claude/skills/add-telegram/modify/src/index.ts.intent.md b/.claude/skills/add-telegram/modify/src/index.ts.intent.md
@@ -40,7 +40,7 @@ Refactored from single WhatsApp channel to multi-channel architecture using the
 - The `runAgent` function is completely unchanged
 - State management (loadState/saveState) is unchanged
 - Recovery logic is unchanged
-- Apple Container check is unchanged (ensureContainerSystemRunning)
+- Container runtime check is unchanged (ensureContainerSystemRunning)
 
 ## Must-keep
 - The `escapeXml` and `formatMessages` re-exports
diff --git a/.claude/skills/add-voice-transcription/SKILL.md b/.claude/skills/add-voice-transcription/SKILL.md
@@ -296,86 +296,20 @@ if (registeredGroups[chatJid]) {
 }
 ```
 
-### Step 6: Fix Orphan Container Cleanup (CRITICAL)
-
-**This step is essential.** When the NanoClaw service restarts (e.g., `launchctl kickstart -k`), the running container is detached but NOT killed. The new service instance spawns a fresh container, but the orphan keeps running and shares the same IPC mount directory. Both containers race to read IPC input files, causing the new container to randomly miss messages — making it appear like the agent doesn't respond.
-
-The existing cleanup code in `ensureContainerSystemRunning()` in `src/index.ts` uses `container ls --format {{.Names}}` which **silently fails** on Apple Container (only `json` and `table` are valid format options). The catch block swallows the error, so orphans are never cleaned up.
-
-Find the orphan cleanup block in `ensureContainerSystemRunning()` (the section starting with `// Kill and clean up orphaned NanoClaw containers from previous runs`) and replace it with:
-
-```typescript
-  // Kill and clean up orphaned NanoClaw containers from previous runs
-  try {
-    const listJson = execSync('container ls -a --format json', {
-      stdio: ['pipe', 'pipe', 'pipe'],
-      encoding: 'utf-8',
-    });
-    const containers = JSON.parse(listJson) as Array<{ configuration: { id: string }; status: string }>;
-    const nanoclawContainers = containers.filter(
-      (c) => c.configuration.id.startsWith('nanoclaw-'),
-    );
-    const running = nanoclawContainers
-      .filter((c) => c.status === 'running')
-      .map((c) => c.configuration.id);
-    if (running.length > 0) {
-      execSync(`container stop ${running.join(' ')}`, { stdio: 'pipe' });
-      logger.info({ count: running.length }, 'Stopped orphaned containers');
-    }
-    const allNames = nanoclawContainers.map((c) => c.configuration.id);
-    if (allNames.length > 0) {
-      execSync(`container rm ${allNames.join(' ')}`, { stdio: 'pipe' });
-      logger.info({ count: allNames.length }, 'Cleaned up stopped containers');
-    }
-  } catch {
-    // No containers or cleanup not supported
-  }
-```
-
-### Step 7: Build and Restart
+### Step 6: Build and Restart
 
 ```bash
 npm run build
-```
-
-Before restarting the service, kill any orphaned containers manually to ensure a clean slate:
-
-```bash
-container ls -a --format json | python3 -c "
-import sys, json
-data = json.load(sys.stdin)
-nc = [c['configuration']['id'] for c in data if c['configuration']['id'].startswith('nanoclaw-')]
-if nc: print(' '.join(nc))
-" | xargs -r container stop 2>/dev/null
-container ls -a --format json | python3 -c "
-import sys, json
-data = json.load(sys.stdin)
-nc = [c['configuration']['id'] for c in data if c['configuration']['id'].startswith('nanoclaw-')]
-if nc: print(' '.join(nc))
-" | xargs -r container rm 2>/dev/null
-echo "Orphaned containers cleaned"
-```
-
-Now restart the service:
-
-```bash
 launchctl kickstart -k gui/$(id -u)/com.nanoclaw
 ```
 
-Verify it started with exactly one (or zero, before first message) nanoclaw container:
+Verify it started:
 
 ```bash
 sleep 3 && launchctl list | grep nanoclaw
-container ls -a --format json | python3 -c "
-import sys, json
-data = json.load(sys.stdin)
-nc = [c for c in data if c['configuration']['id'].startswith('nanoclaw-')]
-print(f'{len(nc)} nanoclaw container(s)')
-for c in nc: print(f'  {c[\"configuration\"][\"id\"]} - {c[\"status\"]}')
-"
 ```
 
-### Step 8: Test Voice Transcription
+### Step 7: Test Voice Transcription
 
 Tell the user:
 
@@ -431,41 +365,6 @@ The architecture supports multiple providers. To add Groq, Deepgram, or local Wh
 
 ## Troubleshooting
 
-### Agent doesn't respond to voice messages (or any messages after a voice note)
-
-**Most likely cause: orphaned containers.** When the service restarts, the previous container keeps running and races to consume IPC messages. Check:
-
-```bash
-container ls -a --format json | python3 -c "
-import sys, json
-data = json.load(sys.stdin)
-nc = [c for c in data if c['configuration']['id'].startswith('nanoclaw-')]
-print(f'{len(nc)} nanoclaw container(s):')
-for c in nc: print(f'  {c[\"configuration\"][\"id\"]} - {c[\"status\"]}')
-"
-```
-
-If you see more than one running container, kill the orphans:
-
-```bash
-# Stop all nanoclaw containers, then restart the service
-container ls -a --format json | python3 -c "
-import sys, json
-data = json.load(sys.stdin)
-running = [c['configuration']['id'] for c in data if c['configuration']['id'].startswith('nanoclaw-') and c['status'] == 'running']
-if running: print(' '.join(running))
-" | xargs -r container stop 2>/dev/null
-container ls -a --format json | python3 -c "
-import sys, json
-data = json.load(sys.stdin)
-nc = [c['configuration']['id'] for c in data if c['configuration']['id'].startswith('nanoclaw-')]
-if nc: print(' '.join(nc))
-" | xargs -r container rm 2>/dev/null
-launchctl kickstart -k gui/$(id -u)/com.nanoclaw
-```
-
-**Root cause:** The `ensureContainerSystemRunning()` function previously used `container ls --format {{.Names}}` which silently fails on Apple Container (only `json` and `table` formats are supported). Step 6 of this skill fixes this. If you haven't applied Step 6, the orphan problem will recur on every restart.
-
 ### "Transcription unavailable" or "Transcription failed"
 
 Check logs for specific errors:
diff --git a/.claude/skills/debug/SKILL.md b/.claude/skills/debug/SKILL.md
@@ -86,28 +86,28 @@ cat .env  # Should show one of:
 
 To verify env vars are reaching the container:
 ```bash
-echo '{}' | container run -i \
-  --mount type=bind,source=$(pwd)/data/env,target=/workspace/env-dir,readonly \
+echo '{}' | docker run -i \
+  -v $(pwd)/data/env:/workspace/env-dir:ro \
   --entrypoint /bin/bash nanoclaw-agent:latest \
   -c 'export $(cat /workspace/env-dir/env | xargs); echo "OAuth: ${#CLAUDE_CODE_OAUTH_TOKEN} chars, API: ${#ANTHROPIC_API_KEY} chars"'
 ```
 
 ### 3. Mount Issues
 
 **Container mount notes:**
-- Only mounts directories, not individual files
-- `-v` syntax may NOT support `:ro` suffix - use `--mount` for readonly:
+- Docker supports both `-v` and `--mount` syntax
+- Use `:ro` suffix for readonly mounts:
   ```bash
-  # Readonly: use --mount
-  --mount "type=bind,source=/path,target=/container/path,readonly"
+  # Readonly
+  -v /path:/container/path:ro
 
-  # Read-write: use -v
+  # Read-write
   -v /path:/container/path
   ```
 
 To check what's mounted inside a container:
 ```bash
-container run --rm --entrypoint /bin/bash nanoclaw-agent:latest -c 'ls -la /workspace/'
+docker run --rm --entrypoint /bin/bash nanoclaw-agent:latest -c 'ls -la /workspace/'
 ```
 
 Expected structure:
@@ -129,7 +129,7 @@ Expected structure:
 
 The container runs as user `node` (uid 1000). Check ownership:
 ```bash
-container run --rm --entrypoint /bin/bash nanoclaw-agent:latest -c '
+docker run --rm --entrypoint /bin/bash nanoclaw-agent:latest -c '
   whoami
   ls -la /workspace/
   ls -la /app/
@@ -152,7 +152,7 @@ grep -A3 "Claude sessions" src/container-runner.ts
 
 **Verify sessions are accessible:**
 ```bash
-container run --rm --entrypoint /bin/bash \
+docker run --rm --entrypoint /bin/bash \
   -v ~/.claude:/home/node/.claude \
   nanoclaw-agent:latest -c '
 echo "HOME=$HOME"
@@ -183,17 +183,17 @@ cp .env data/env/env
 
 # Run test query
 echo '{"prompt":"What is 2+2?","groupFolder":"test","chatJid":"test@g.us","isMain":false}' | \
-  container run -i \
-  --mount "type=bind,source=$(pwd)/data/env,target=/workspace/env-dir,readonly" \
+  docker run -i \
+  -v $(pwd)/data/env:/workspace/env-dir:ro \
   -v $(pwd)/groups/test:/workspace/group \
   -v $(pwd)/data/ipc:/workspace/ipc \
   nanoclaw-agent:latest
 ```
 
 ### Test Claude Code directly:
 ```bash
-container run --rm --entrypoint /bin/bash \
-  --mount "type=bind,source=$(pwd)/data/env,target=/workspace/env-dir,readonly" \
+docker run --rm --entrypoint /bin/bash \
+  -v $(pwd)/data/env:/workspace/env-dir:ro \
   nanoclaw-agent:latest -c '
   export $(cat /workspace/env-dir/env | xargs)
   claude -p "Say hello" --dangerously-skip-permissions --allowedTools ""
@@ -202,7 +202,7 @@ container run --rm --entrypoint /bin/bash \
 
 ### Interactive shell in container:
 ```bash
-container run --rm -it --entrypoint /bin/bash nanoclaw-agent:latest
+docker run --rm -it --entrypoint /bin/bash nanoclaw-agent:latest
 ```
 
 ## SDK Options Reference
@@ -235,18 +235,18 @@ npm run build
 ./container/build.sh
 
 # Or force full rebuild
-container builder prune -af
+docker builder prune -af
 ./container/build.sh
 ```
 
 ## Checking Container Image
 
 ```bash
 # List images
-container images
+docker images
 
 # Check what's in the image
-container run --rm --entrypoint /bin/bash nanoclaw-agent:latest -c '
+docker run --rm --entrypoint /bin/bash nanoclaw-agent:latest -c '
   echo "=== Node version ==="
   node --version
 
@@ -327,10 +327,10 @@ echo -e "\n2. Env file copied for container?"
 [ -f data/env/env ] && echo "OK" || echo "MISSING - will be created on first run"
 
 echo -e "\n3. Container runtime running?"
-container system status &>/dev/null && echo "OK" || echo "NOT RUNNING - NanoClaw should auto-start it; check logs"
+docker info &>/dev/null && echo "OK" || echo "NOT RUNNING - start Docker Desktop (macOS) or sudo systemctl start docker (Linux)"
 
 echo -e "\n4. Container image exists?"
-echo '{}' | container run -i --entrypoint /bin/echo nanoclaw-agent:latest "OK" 2>/dev/null || echo "MISSING - run ./container/build.sh"
+echo '{}' | docker run -i --entrypoint /bin/echo nanoclaw-agent:latest "OK" 2>/dev/null || echo "MISSING - run ./container/build.sh"
 
 echo -e "\n5. Session mount path correct?"
 grep -q "/home/node/.claude" src/container-runner.ts 2>/dev/null && echo "OK" || echo "WRONG - should mount to /home/node/.claude/, not /root/.claude/"
diff --git a/.claude/skills/setup/SKILL.md b/.claude/skills/setup/SKILL.md
@@ -43,40 +43,26 @@ Only ask the user for help if multiple retries fail with the same error.
 
 ### 3a. Choose runtime
 
-Use the environment check results from step 1 to decide which runtime to use:
+Check the preflight results for `APPLE_CONTAINER` and `DOCKER`.
 
-- PLATFORM=linux → Docker
-- PLATFORM=macos + APPLE_CONTAINER=installed → apple-container
-- PLATFORM=macos + DOCKER=running + APPLE_CONTAINER=not_found → Docker
-- PLATFORM=macos + DOCKER=installed_not_running → start Docker: `open -a Docker`. Wait 15s, re-check with `docker info`. If still not running, tell the user Docker is starting up and poll a few more times.
-- Neither available → AskUserQuestion: Apple Container (recommended for macOS) vs Docker?
-  - Apple Container: tell user to download from https://github.com/apple/container/releases and install the .pkg. Wait for confirmation, then verify with `container --version`.
-  - Docker on macOS: install via `brew install --cask docker`, then `open -a Docker` and wait for it to start. If brew not available, direct to Docker Desktop download.
-  - Docker on Linux: install with `curl -fsSL https://get.docker.com | sh && sudo usermod -aG docker $USER`. Note: user may need to log out/in for group membership.
+**If APPLE_CONTAINER=installed** (macOS only): Ask the user which runtime they'd like to use — Docker (default, cross-platform) or Apple Container (native macOS). If they choose Apple Container, run `/convert-to-apple-container` now before continuing, then skip to 3b.
 
-### 3b. Docker conversion gate (REQUIRED before building)
+**If APPLE_CONTAINER=not_found**: Use Docker (the default). Proceed to install/start Docker below.
 
-**If the chosen runtime is Docker**, you MUST check whether the source code has already been converted from Apple Container to Docker. Do NOT skip this step. Run:
+### 3a-docker. Install Docker
 
-```bash
-grep -q 'container system status' src/index.ts && echo "NEEDS_CONVERSION" || echo "ALREADY_CONVERTED"
-```
+- DOCKER=running → continue to 3b
+- DOCKER=installed_not_running → start Docker: `open -a Docker` (macOS) or `sudo systemctl start docker` (Linux). Wait 15s, re-check with `docker info`. If still not running, tell the user Docker is starting up and poll a few more times.
+- DOCKER=not_found → **ask the user for confirmation before installing.** Tell them Docker is required for running agents and ask if they'd like you to install it. If confirmed:
+  - macOS: install via `brew install --cask docker`, then `open -a Docker` and wait for it to start. If brew not available, direct to Docker Desktop download at https://docker.com/products/docker-desktop
+  - Linux: install with `curl -fsSL https://get.docker.com | sh && sudo usermod -aG docker $USER`. Note: user may need to log out/in for group membership.
 
-Check these three files for Apple Container references:
-- `src/index.ts` — look for `container system status` or `ensureContainerSystemRunning`
-- `src/container-runner.ts` — look for `spawn('container'`
-- `container/build.sh` — look for `container build`
-
-**If ANY of those Apple Container references exist**, the source code has NOT been converted. You MUST run the `/convert-to-docker` skill NOW, before proceeding to the build step. Do not attempt to build the container image until the conversion is complete.
-
-**If none of those references exist** (i.e. the code already uses `docker info`, `spawn('docker'`, `docker build`), the conversion has already been done. Continue to 3c.
-
-### 3c. Build and test
+### 3b. Build and test
 
 Run `./.claude/skills/setup/scripts/03-setup-container.sh --runtime <chosen>` and parse the status block.
 
 **If BUILD_OK=false:** Read `logs/setup.log` tail for the build error.
-- If it's a cache issue (stale layers): run `container builder stop && container builder rm && container builder start` (Apple Container) or `docker builder prune -f` (Docker), then retry.
+- If it's a cache issue (stale layers): run `docker builder prune -f`, then retry.
 - If Dockerfile syntax or missing files: diagnose from the log and fix.
 - Retry the build script after fixing.
 
diff --git a/.claude/skills/x-integration/SKILL.md b/.claude/skills/x-integration/SKILL.md
@@ -200,11 +200,11 @@ Add to the end of tools array (before the closing `]`):
 Change build context from `container/` to project root (required to access `.claude/skills/`):
 ```bash
 # Find:
-container build -t "${IMAGE_NAME}:${TAG}" .
+docker build -t "${IMAGE_NAME}:${TAG}" .
 
 # Replace with:
 cd "$SCRIPT_DIR/.."
-container build -t "${IMAGE_NAME}:${TAG}" -f container/Dockerfile .
+docker build -t "${IMAGE_NAME}:${TAG}" -f container/Dockerfile .
 ```
 
 ---
@@ -402,7 +402,7 @@ If MCP tools not found in container:
 ./container/build.sh 2>&1 | grep -i skill
 
 # Check container has the file
-container run nanoclaw-agent ls -la /app/src/skills/
+docker run nanoclaw-agent ls -la /app/src/skills/
 ```
 
 ## Security
PATCH

echo "Gold patch applied."
