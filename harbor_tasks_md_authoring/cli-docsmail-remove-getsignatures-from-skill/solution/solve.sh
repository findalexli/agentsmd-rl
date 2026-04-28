#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF "skills/lark-mail/SKILL.md" "skills/lark-mail/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/lark-mail/SKILL.md b/skills/lark-mail/SKILL.md
@@ -407,7 +407,6 @@ lark-cli mail <resource> <method> [flags] # 调用 API
 
 ### user_mailbox.settings
 
-  - `get_signatures` — 获取用户邮箱签名列表
   - `send_as` — 获取账号的所有可发信地址，包括主地址、别名地址、邮件组。可以使用用户地址访问该接口，也可以使用用户有权限的公共邮箱地址访问该接口。
 
 ### user_mailbox.threads
@@ -469,7 +468,6 @@ lark-cli mail <resource> <method> [flags] # 调用 API
 | `user_mailbox.rules.list` | `mail:user_mailbox.rule:read` |
 | `user_mailbox.rules.reorder` | `mail:user_mailbox.rule:write` |
 | `user_mailbox.rules.update` | `mail:user_mailbox.rule:write` |
-| `user_mailbox.settings.get_signatures` | `mail:user_mailbox:readonly` |
 | `user_mailbox.settings.send_as` | `mail:user_mailbox:readonly` |
 | `user_mailbox.threads.batch_modify` | `mail:user_mailbox.message:modify` |
 | `user_mailbox.threads.batch_trash` | `mail:user_mailbox.message:modify` |
PATCH

echo "Gold patch applied."
