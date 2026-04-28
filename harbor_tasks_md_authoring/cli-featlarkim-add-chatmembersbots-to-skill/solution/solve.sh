#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF "- `bots` \u2014 \u83b7\u53d6\u7fa4\u5185\u673a\u5668\u4eba\u5217\u8868\u3002 Identity: supports `user` and `bot`; the caller must be in" "skills/lark-im/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/lark-im/SKILL.md b/skills/lark-im/SKILL.md
@@ -86,6 +86,7 @@ lark-cli im <resource> <method> [flags] # 调用 API
 
 ### chat.members
 
+  - `bots` — 获取群内机器人列表。 Identity: supports `user` and `bot`; the caller must be in the target chat and must belong to the same tenant for internal chats.
   - `create` — 将用户或机器人拉入群聊。Identity: supports `user` and `bot`; the caller must be in the target chat; for `bot` calls, added users must be within the app's availability; for internal chats the operator must belong to the same tenant; if only owners/admins can add members, the caller must be an owner/admin, or a chat-creator bot with `im:chat:operate_as_owner`.
   - `delete` — 将用户或机器人移出群聊。Identity: supports `user` and `bot`; only group owner, admin, or creator bot can remove others; max 50 users or 5 bots per request.
   - `get` — 获取群成员列表。Identity: supports `user` and `bot`; the caller must be in the target chat and must belong to the same tenant for internal chats.
@@ -123,6 +124,7 @@ lark-cli im <resource> <method> [flags] # 调用 API
 | `chats.link` | `im:chat:read` |
 | `chats.list` | `im:chat:read` |
 | `chats.update` | `im:chat:update` |
+| `chat.members.bots` | `im:chat.members:read` |
 | `chat.members.create` | `im:chat.members:write_only` |
 | `chat.members.delete` | `im:chat.members:write_only` |
 | `chat.members.get` | `im:chat.members:read` |
PATCH

echo "Gold patch applied."
