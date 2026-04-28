#!/usr/bin/env bash
set -euo pipefail

cd /workspace/spawn

# Idempotency guard
if grep -qF "**Note:** The wrapper script (`start-<service-name>.sh`) sets the actual env var" ".claude/skills/setup-agent-team/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/setup-agent-team/SKILL.md b/.claude/skills/setup-agent-team/SKILL.md
@@ -12,6 +12,38 @@ Set up a **Bun-based HTTP trigger server** on a VM and configure a **GitHub Acti
 
 The user wants to set up a trigger service for: **$ARGUMENTS**
 
+## CRITICAL: Repository Path — Ask the User
+
+**NEVER guess the repository path. NEVER invent home directories (e.g., `/home/claude-runner`). ASK the user where the repo lives.**
+
+There are two common environments:
+
+| Environment | Home dir | Typical repo path |
+|---|---|---|
+| **Sprite VM** (Fly.io managed) | `/home/sprite/` | `/home/sprite/spawn` |
+| **Normal VM** (bare metal, cloud) | `/root/` | `/root/spawn` |
+
+### How to determine the path
+
+1. Run `pwd` and check the current working directory
+2. If unclear, **ask the user** where the spawn repo is checked out
+3. Use that path consistently for ALL configuration: systemd services, wrapper scripts, PATH variables
+
+### Rules
+
+- **NEVER** create new user accounts or home directories for the service
+- **NEVER** assume a path like `/home/claude-runner/` — that doesn't exist
+- All systemd services, wrapper scripts, and PATH variables MUST use the **same base path** as the repo checkout
+- The wrapper scripts (e.g., `start-security.sh`) MUST live inside the repo at `{REPO_ROOT}/.claude/skills/setup-agent-team/`
+
+### Examples (for a repo at `/root/spawn`)
+
+- ✅ `WorkingDirectory=/root/spawn/.claude/skills/setup-agent-team`
+- ✅ `ExecStart=/bin/bash /root/spawn/.claude/skills/setup-agent-team/start-security.sh`
+- ✅ `Environment="PATH=/root/.bun/bin:/root/.local/bin:/usr/local/bin:/usr/bin:/bin"`
+- ❌ `WorkingDirectory=/home/claude-runner/spawn/...` (invented path)
+- ❌ `Environment="PATH=/home/claude-runner/.bun/bin:..."` (invented path)
+
 ## Overview
 
 This skill sets up a trigger server that GitHub Actions can call to run a script:
@@ -80,17 +112,24 @@ Save this — you'll use it in Steps 3 and 5.
 
 Create a **gitignored** wrapper script that sets env vars and launches the server.
 
-Create `start-<service-name>.sh` in the skill directory:
+Create `start-<service-name>.sh` in `{REPO_ROOT}/.claude/skills/setup-agent-team/`:
 
 ```bash
 #!/bin/bash
-SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
+# Wrapper script — sets env vars and launches the trigger server.
+# CRITICAL: SCRIPT_DIR must match the actual repo path on this machine.
+# On a Sprite VM this is /home/sprite/spawn, on a normal VM it's /root/spawn.
+SCRIPT_DIR="<REPO_ROOT>/.claude/skills/setup-agent-team"
 export TRIGGER_SECRET="<secret-from-step-2>"
 export TARGET_SCRIPT="${SCRIPT_DIR}/<target-script>.sh"
-export REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
+export REPO_ROOT="<REPO_ROOT>"
+export MAX_CONCURRENT=5
+export RUN_TIMEOUT_MS=7200000
 exec bun run "${SCRIPT_DIR}/trigger-server.ts"
 ```
 
+Replace `<REPO_ROOT>` with the actual path (e.g., `/root/spawn` or `/home/sprite/spawn`).
+
 Make it executable:
 
 ```bash
@@ -111,39 +150,42 @@ Choose the service management approach based on your environment:
 
 ### Option A: systemd (recommended)
 
-Create a systemd unit file at `/etc/systemd/system/spawn-<service-name>.service`:
+Create a systemd unit file at `/etc/systemd/system/<service-name>-trigger.service`.
+
+**CRITICAL: Replace `<REPO_ROOT>` and `<HOME>` with the actual paths. Ask the user if unsure.**
+
+| Environment | `<REPO_ROOT>` | `<HOME>` | User/Group |
+|---|---|---|---|
+| Sprite VM | `/home/sprite/spawn` | `/home/sprite` | `sprite` / `sprite` |
+| Normal VM | `/root/spawn` | `/root` | `root` / `root` |
 
 ```ini
 [Unit]
-Description=Spawn <Service Name> Trigger Server
+Description=<Service Name> Trigger Server
 After=network.target
 
 [Service]
 Type=simple
-User=<run-as-user>
-Group=<run-as-group>
-WorkingDirectory=$REPO_ROOT/.claude/skills/setup-agent-team
-ExecStart=/path/to/bun run $REPO_ROOT/.claude/skills/setup-agent-team/trigger-server.ts
-Restart=on-failure
+User=<user>
+Group=<group>
+WorkingDirectory=<REPO_ROOT>/.claude/skills/setup-agent-team
+ExecStart=/bin/bash <REPO_ROOT>/.claude/skills/setup-agent-team/start-<service-name>.sh
+Restart=always
 RestartSec=10
-
-# Environment (same vars as the wrapper script)
-Environment=TRIGGER_SECRET=<secret-from-step-2>
-Environment=TARGET_SCRIPT=$REPO_ROOT/.claude/skills/setup-agent-team/<target-script>.sh
-Environment=REPO_ROOT=$REPO_ROOT
-Environment=MAX_CONCURRENT=2
-Environment=RUN_TIMEOUT_MS=7200000
-Environment=PATH=/home/<user>/.bun/bin:/home/<user>/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
-
-# Logging
 StandardOutput=journal
 StandardError=journal
-SyslogIdentifier=spawn-<service-name>
+
+# Environment
+Environment="IS_SANDBOX=1"
+Environment="PATH=<HOME>/.bun/bin:<HOME>/.local/bin:<HOME>/.claude/local/bin:/usr/local/bin:/usr/bin:/bin"
+Environment="HOME=<HOME>"
 
 [Install]
 WantedBy=multi-user.target
 ```
 
+**Note:** The wrapper script (`start-<service-name>.sh`) sets the actual env vars (`TRIGGER_SECRET`, `TARGET_SCRIPT`, etc.). The systemd service just executes the wrapper.
+
 Enable and start:
 
 ```bash
PATCH

echo "Gold patch applied."
