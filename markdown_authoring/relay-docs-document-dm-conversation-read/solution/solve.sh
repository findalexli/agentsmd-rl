#!/usr/bin/env bash
set -euo pipefail

cd /workspace/relay

# Idempotency guard
if grep -qF "**Dual-auth endpoints:** Some read endpoints require the **workspace key** (`rk_" "packages/openclaw/skill/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/openclaw/skill/SKILL.md b/packages/openclaw/skill/SKILL.md
@@ -175,6 +175,24 @@ mcporter call relaycast.message.get_thread message_id=MSG_ID
 mcporter call relaycast.message.search query="keyword" limit=10
 ```
 
+### Read DMs
+
+List your DM conversations:
+
+```bash
+mcporter call relaycast.message.dm.list
+```
+
+**Reading messages inside a DM conversation** requires dual auth — the workspace key (`rk_live_...`) as `Authorization` and the agent token (`at_live_...`) as `X-Agent-Token`:
+
+```bash
+curl -s 'https://api.relaycast.dev/v1/dm/conversations/CONVERSATION_ID/messages?limit=20' \
+  -H 'Authorization: Bearer rk_live_YOUR_WORKSPACE_KEY' \
+  -H 'X-Agent-Token: at_live_YOUR_AGENT_TOKEN'
+```
+
+> **Note:** Listing conversations (`GET /v1/dm/conversations`) works with just the agent token, but reading message content within a conversation requires the workspace key. See the Token model section below for details.
+
 ---
 
 ## 6) Channels, Reactions, Agent Discovery
@@ -239,6 +257,8 @@ Storage locations:
 
 This means `status` or `list_agents` can succeed while `post_message` still fails if the agent token is stale or invalid.
 
+**Dual-auth endpoints:** Some read endpoints require the **workspace key** (`rk_live_...`) rather than the agent token. Specifically, reading DM conversation messages (`GET /v1/dm/conversations/:id/messages`) requires the workspace key as `Authorization` and the agent token as `X-Agent-Token`. Most other endpoints (posting, listing conversations, inbox check) use the agent token alone.
+
 ### Status endpoint caveat
 
 `relay-openclaw status` may report `/health` errors even when messaging works.
PATCH

echo "Gold patch applied."
