#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanoclaw

# Idempotency guard
if grep -qF "Send diagnostics data by following `.claude/skills/setup/diagnostics.md`." ".claude/skills/setup/SKILL.md" && grep -qF "3. Remove the `## 9. Diagnostics` section from `.claude/skills/setup/SKILL.md` a" ".claude/skills/setup/diagnostics.md" && grep -qF "Send diagnostics data by following `.claude/skills/update-nanoclaw/diagnostics.m" ".claude/skills/update-nanoclaw/SKILL.md" && grep -qF "3. Remove the `## 9. Diagnostics` section from `.claude/skills/setup/SKILL.md` a" ".claude/skills/update-nanoclaw/diagnostics.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/setup/SKILL.md b/.claude/skills/setup/SKILL.md
@@ -278,6 +278,6 @@ Tell user to test: send a message in their registered chat. Show: `tail -f logs/
 **Unload service:** macOS: `launchctl unload ~/Library/LaunchAgents/com.nanoclaw.plist` | Linux: `systemctl --user stop nanoclaw`
 
 
-## Diagnostics
+## 9. Diagnostics
 
-Read and follow [diagnostics.md](diagnostics.md).
+Send diagnostics data by following `.claude/skills/setup/diagnostics.md`.
diff --git a/.claude/skills/setup/diagnostics.md b/.claude/skills/setup/diagnostics.md
@@ -42,5 +42,5 @@ rm /tmp/nanoclaw-diagnostics.json
 **Never ask again**:
 1. Replace contents of `.claude/skills/setup/diagnostics.md` with `# Diagnostics — opted out`
 2. Replace contents of `.claude/skills/update-nanoclaw/diagnostics.md` with `# Diagnostics — opted out`
-3. Remove the "Diagnostics" section from both `.claude/skills/setup/SKILL.md` and `.claude/skills/update-nanoclaw/SKILL.md`
+3. Remove the `## 9. Diagnostics` section from `.claude/skills/setup/SKILL.md` and the `## Diagnostics` section from `.claude/skills/update-nanoclaw/SKILL.md`
 4. `rm /tmp/nanoclaw-diagnostics.json`
diff --git a/.claude/skills/update-nanoclaw/SKILL.md b/.claude/skills/update-nanoclaw/SKILL.md
@@ -237,4 +237,4 @@ Tell the user:
 
 ## Diagnostics
 
-Read and follow [diagnostics.md](diagnostics.md).
+Send diagnostics data by following `.claude/skills/update-nanoclaw/diagnostics.md`.
diff --git a/.claude/skills/update-nanoclaw/diagnostics.md b/.claude/skills/update-nanoclaw/diagnostics.md
@@ -45,5 +45,5 @@ rm /tmp/nanoclaw-diagnostics.json
 **Never ask again**:
 1. Replace contents of `.claude/skills/setup/diagnostics.md` with `# Diagnostics — opted out`
 2. Replace contents of `.claude/skills/update-nanoclaw/diagnostics.md` with `# Diagnostics — opted out`
-3. Remove the "Diagnostics" section from both `.claude/skills/setup/SKILL.md` and `.claude/skills/update-nanoclaw/SKILL.md`
+3. Remove the `## 9. Diagnostics` section from `.claude/skills/setup/SKILL.md` and the `## Diagnostics` section from `.claude/skills/update-nanoclaw/SKILL.md`
 4. `rm /tmp/nanoclaw-diagnostics.json`
PATCH

echo "Gold patch applied."
