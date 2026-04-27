#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanoclaw

# Idempotency guard
if grep -qF "AskUserQuestion: What is your personal phone number? (The number you'll use to m" ".claude/skills/add-whatsapp/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/add-whatsapp/SKILL.md b/.claude/skills/add-whatsapp/SKILL.md
@@ -201,7 +201,11 @@ AskUserQuestion: Where do you want to chat with the assistant?
 node -e "const c=JSON.parse(require('fs').readFileSync('store/auth/creds.json','utf-8'));console.log(c.me?.id?.split(':')[0]+'@s.whatsapp.net')"
 ```
 
-**DM with bot:** Ask for the bot's phone number. JID = `NUMBER@s.whatsapp.net`
+**DM with bot:** The JID is the **user's** phone number — the number they will message *from* (not the bot's own number). Ask:
+
+AskUserQuestion: What is your personal phone number? (The number you'll use to message the bot — include country code without +, e.g. 1234567890)
+
+JID = `<user-number>@s.whatsapp.net`
 
 **Group (solo, existing):** Run group sync and list available groups:
 
@@ -223,7 +227,7 @@ npx tsx setup/index.ts --step register \
   --channel whatsapp \
   --assistant-name "<name>" \
   --is-main \
-  --no-trigger-required  # Only for main/self-chat
+  --no-trigger-required  # For self-chat and DM with bot (1:1 conversations don't need a trigger prefix)
 ```
 
 For additional groups (trigger-required):
PATCH

echo "Gold patch applied."
