#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanoclaw

# Idempotency guard
if grep -qF "Read and follow [diagnostics.md](diagnostics.md)." ".claude/skills/setup/SKILL.md" && grep -qF "3. Remove the \"Diagnostics\" section from both `.claude/skills/setup/SKILL.md` an" ".claude/skills/setup/diagnostics.md" && grep -qF "Read and follow [diagnostics.md](diagnostics.md)." ".claude/skills/update-nanoclaw/SKILL.md" && grep -qF "3. Remove the \"Diagnostics\" section from both `.claude/skills/setup/SKILL.md` an" ".claude/skills/update-nanoclaw/diagnostics.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/setup/SKILL.md b/.claude/skills/setup/SKILL.md
@@ -216,3 +216,8 @@ Tell user to test: send a message in their registered chat. Show: `tail -f logs/
 **Channel not connecting:** Verify the channel's credentials are set in `.env`. Channels auto-enable when their credentials are present. For WhatsApp: check `store/auth/creds.json` exists. For token-based channels: check token values in `.env`. Restart the service after any `.env` change.
 
 **Unload service:** macOS: `launchctl unload ~/Library/LaunchAgents/com.nanoclaw.plist` | Linux: `systemctl --user stop nanoclaw`
+
+
+## Diagnostics
+
+Read and follow [diagnostics.md](diagnostics.md).
diff --git a/.claude/skills/setup/diagnostics.md b/.claude/skills/setup/diagnostics.md
@@ -0,0 +1,46 @@
+# Diagnostics
+
+Gather system info:
+
+```bash
+node -p "require('./package.json').version"
+uname -s
+uname -m
+node -p "process.versions.node.split('.')[0]"
+```
+
+Write `/tmp/nanoclaw-diagnostics.json`. No paths, usernames, hostnames, or IP addresses.
+
+```json
+{
+  "api_key": "phc_fx1Hhx9ucz8GuaJC8LVZWO8u03yXZZJJ6ObS4yplnaP",
+  "event": "setup_complete",
+  "distinct_id": "<uuid>",
+  "properties": {
+    "success": true,
+    "nanoclaw_version": "1.2.21",
+    "os_platform": "darwin",
+    "arch": "arm64",
+    "node_major_version": 22,
+    "channels_selected": ["telegram", "whatsapp"],
+    "error_count": 0,
+    "failed_step": null
+  }
+}
+```
+
+Show the entire JSON to the user and ask via AskUserQuestion: **Yes** / **No** / **Never ask again**
+
+**Yes**:
+```bash
+curl -s -X POST https://us.i.posthog.com/capture/ -H 'Content-Type: application/json' -d @/tmp/nanoclaw-diagnostics.json
+rm /tmp/nanoclaw-diagnostics.json
+```
+
+**No**: `rm /tmp/nanoclaw-diagnostics.json`
+
+**Never ask again**:
+1. Replace contents of `.claude/skills/setup/diagnostics.md` with `# Diagnostics — opted out`
+2. Replace contents of `.claude/skills/update-nanoclaw/diagnostics.md` with `# Diagnostics — opted out`
+3. Remove the "Diagnostics" section from both `.claude/skills/setup/SKILL.md` and `.claude/skills/update-nanoclaw/SKILL.md`
+4. `rm /tmp/nanoclaw-diagnostics.json`
diff --git a/.claude/skills/update-nanoclaw/SKILL.md b/.claude/skills/update-nanoclaw/SKILL.md
@@ -233,3 +233,8 @@ Tell the user:
 - Restart the service to apply changes:
   - If using launchd: `launchctl unload ~/Library/LaunchAgents/com.nanoclaw.plist && launchctl load ~/Library/LaunchAgents/com.nanoclaw.plist`
   - If running manually: restart `npm run dev`
+
+
+## Diagnostics
+
+Read and follow [diagnostics.md](diagnostics.md).
diff --git a/.claude/skills/update-nanoclaw/diagnostics.md b/.claude/skills/update-nanoclaw/diagnostics.md
@@ -0,0 +1,49 @@
+# Diagnostics
+
+Gather system info:
+
+```bash
+node -p "require('./package.json').version"
+uname -s
+uname -m
+node -p "process.versions.node.split('.')[0]"
+git log -1 --format=%ci HEAD@{1} 2>/dev/null || echo "unknown"
+```
+
+Write `/tmp/nanoclaw-diagnostics.json`. No paths, usernames, hostnames, or IP addresses.
+
+```json
+{
+  "api_key": "phc_fx1Hhx9ucz8GuaJC8LVZWO8u03yXZZJJ6ObS4yplnaP",
+  "event": "update_complete",
+  "distinct_id": "<uuid>",
+  "properties": {
+    "success": true,
+    "nanoclaw_version": "1.2.21",
+    "os_platform": "darwin",
+    "arch": "arm64",
+    "node_major_version": 22,
+    "version_age_days": 45,
+    "update_method": "merge",
+    "conflict_count": 0,
+    "breaking_changes_found": false,
+    "error_count": 0
+  }
+}
+```
+
+Show the entire JSON to the user and ask via AskUserQuestion: **Yes** / **No** / **Never ask again**
+
+**Yes**:
+```bash
+curl -s -X POST https://us.i.posthog.com/capture/ -H 'Content-Type: application/json' -d @/tmp/nanoclaw-diagnostics.json
+rm /tmp/nanoclaw-diagnostics.json
+```
+
+**No**: `rm /tmp/nanoclaw-diagnostics.json`
+
+**Never ask again**:
+1. Replace contents of `.claude/skills/setup/diagnostics.md` with `# Diagnostics — opted out`
+2. Replace contents of `.claude/skills/update-nanoclaw/diagnostics.md` with `# Diagnostics — opted out`
+3. Remove the "Diagnostics" section from both `.claude/skills/setup/SKILL.md` and `.claude/skills/update-nanoclaw/SKILL.md`
+4. `rm /tmp/nanoclaw-diagnostics.json`
PATCH

echo "Gold patch applied."
