#!/usr/bin/env bash
set -euo pipefail

cd /workspace/spawn

# Idempotency guard
if grep -qF "| systemd service won't start | Check `journalctl -u spawn-<name> -n 50` \u2014 commo" ".claude/skills/setup-agent-team/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/setup-agent-team/SKILL.md b/.claude/skills/setup-agent-team/SKILL.md
@@ -115,7 +115,63 @@ chmod +x .claude/skills/setup-agent-team/start-<service-name>.sh
 
 Wrapper scripts contain secrets and MUST NOT be committed.
 
-## Step 4: Create the Sprite service
+## Step 4: Create the service
+
+Choose the service management approach based on your environment:
+
+### Option A: systemd (standard Linux VMs, recommended for non-Sprite environments)
+
+Create a systemd unit file at `/etc/systemd/system/spawn-<service-name>.service`:
+
+```ini
+[Unit]
+Description=Spawn <Service Name> Trigger Server
+After=network.target
+
+[Service]
+Type=simple
+User=<run-as-user>
+Group=<run-as-group>
+WorkingDirectory=$REPO_ROOT/.claude/skills/setup-agent-team
+ExecStart=/path/to/bun run $REPO_ROOT/.claude/skills/setup-agent-team/trigger-server.ts
+Restart=on-failure
+RestartSec=10
+
+# Environment (same vars as the wrapper script)
+Environment=TRIGGER_SECRET=<secret-from-step-2>
+Environment=TARGET_SCRIPT=$REPO_ROOT/.claude/skills/setup-agent-team/<target-script>.sh
+Environment=REPO_ROOT=$REPO_ROOT
+Environment=MAX_CONCURRENT=2
+Environment=RUN_TIMEOUT_MS=7200000
+Environment=PATH=/home/<user>/.bun/bin:/home/<user>/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
+
+# Logging
+StandardOutput=journal
+StandardError=journal
+SyslogIdentifier=spawn-<service-name>
+
+[Install]
+WantedBy=multi-user.target
+```
+
+Enable and start:
+
+```bash
+systemctl daemon-reload
+systemctl enable spawn-<service-name>
+systemctl start spawn-<service-name>
+```
+
+**Service management:**
+
+```bash
+systemctl status spawn-<service-name>          # Check status
+journalctl -u spawn-<service-name> -f          # Tail logs
+systemctl restart spawn-<service-name>         # Restart
+systemctl stop spawn-<service-name>            # Stop
+```
+
+### Option B: Sprite service (Sprite VMs only)
 
 Register the trigger server as a Sprite service with HTTP port forwarding:
 
@@ -130,12 +186,18 @@ sprite-env services create <service-name> \
 - `--dir` sets the working directory
 - Only ONE service per Sprite can have `--http-port`
 
-### Verify the service
+**Service management:**
 
 ```bash
-# Check it's running
-sprite-env services list
+sprite-env services list                       # List all services
+sprite-env services stop <service-name>        # Stop
+sprite-env services start <service-name>       # Start
+sprite-env services delete <service-name>      # Delete entirely
+```
+
+### Verify the service (either option)
 
+```bash
 # Test health endpoint
 curl -sf http://localhost:8080/health
 # Expected: {"status":"ok"}
@@ -147,16 +209,7 @@ curl -sf -o /dev/null -w "%{http_code}" -X POST http://localhost:8080/trigger
 # Test valid trigger
 curl -sf -X POST "http://localhost:8080/trigger?reason=test" \
   -H "Authorization: Bearer <secret-from-step-2>"
-# Expected: {"triggered":true,"reason":"test","running":1,"max":3}
-```
-
-### Service management commands
-
-```bash
-sprite-env services list                       # List all services
-sprite-env services stop <service-name>        # Stop
-sprite-env services start <service-name>       # Start
-sprite-env services delete <service-name>      # Delete entirely
+# Expected: streaming output from the target script
 ```
 
 ## Step 5: Set the Sprite URL to public
@@ -517,10 +570,13 @@ HTTP/2's stream multiplexing does not handle long-lived chunked responses well.
 | `{"error":"max concurrent runs reached"}` | Max concurrent limit reached (default 1) — wait for runs to finish or increase `MAX_CONCURRENT` env var in wrapper script |
 | env vars not passed | Use the wrapper script pattern (not `--env` flag with commas in values) |
 | GitHub Actions secret is empty | Check `gh secret list --repo <owner>/<repo>` and re-set with `printf` (not `echo`, to avoid trailing newline) |
+| systemd service won't start | Check `journalctl -u spawn-<name> -n 50` — common issues: port in use (EADDRINUSE), wrong PATH (bun/claude not found), permission denied |
+| systemd service keeps restarting | Check exit code in `systemctl status` — if exit 1, check journal logs. If EADDRINUSE, run `fuser -k 8080/tcp` first |
 
 ## Current Deployed Services
 
-| Workflow | Sprite | Service Name | Secrets |
-|----------|--------|-------------|---------|
-| `discovery.yml` (Trigger Discovery) | `lab-spawn-discovery` | `discovery-trigger` | `DISCOVERY_SPRITE_URL`, `DISCOVERY_TRIGGER_SECRET` |
-| `refactor.yml` (Trigger Refactor) | `lab-spawn-foundations` | `refactor` | `REFACTOR_SPRITE_URL`, `REFACTOR_TRIGGER_SECRET` |
+| Workflow | Host | Service Type | Service Name | Secrets |
+|----------|------|-------------|-------------|---------|
+| `discovery.yml` (Trigger Discovery) | `lab-spawn-discovery` (Sprite) | sprite-env | `discovery-trigger` | `DISCOVERY_SPRITE_URL`, `DISCOVERY_TRIGGER_SECRET` |
+| `refactor.yml` (Trigger Refactor) | `lab-spawn-foundations` (Sprite) | sprite-env | `refactor` | `REFACTOR_SPRITE_URL`, `REFACTOR_TRIGGER_SECRET` |
+| `security.yml` (Trigger Security) | sandbox VM | systemd | `spawn-security` | `SECURITY_SPRITE_URL`, `SECURITY_TRIGGER_SECRET` |
PATCH

echo "Gold patch applied."
