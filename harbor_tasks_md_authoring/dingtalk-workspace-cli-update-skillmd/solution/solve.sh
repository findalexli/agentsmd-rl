#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dingtalk-workspace-cli

# Idempotency guard
if grep -qF "cli_version: \">=1.0.6\"" "skills/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/SKILL.md b/skills/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: dws
 description: 管理钉钉产品能力(AI表格/日历/通讯录/群聊与机器人/待办/审批/考勤/日志/DING消息/工作台/开放平台文档等)。当用户需要操作表格数据、管理日程会议、查询通讯录、管理群聊、机器人发消息、创建待办、提交审批、查看考勤、提交日报周报（钉钉日志模版）时使用。
-cli_version: ">=1.1.0"
+cli_version: ">=1.0.6"
 ---
 
 # 钉钉全产品 Skill
PATCH

echo "Gold patch applied."
