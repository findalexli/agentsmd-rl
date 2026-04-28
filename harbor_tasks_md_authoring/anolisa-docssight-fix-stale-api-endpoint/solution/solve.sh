#!/usr/bin/env bash
set -euo pipefail

cd /workspace/anolisa

# Idempotency guard
if grep -qF "| `/api/interruptions/conversation-counts` | GET | \u6309 conversation \u5206\u7ec4\u7684\u4e2d\u65ad\u8ba1\u6570\uff08`start" "src/agentsight/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/agentsight/AGENTS.md b/src/agentsight/AGENTS.md
@@ -132,22 +132,25 @@ agentsight interruption --db /path/to/interruption_events.db list --last 48
 | `/api/sessions` | GET | 会话列表 |
 | `/api/sessions/{id}/traces` | GET | 会话下的 trace |
 | `/api/traces/{id}` | GET | trace 详情 |
+| `/api/conversations/{id}` | GET | conversation 事件详情 |
 | `/api/agent-names` | GET | Agent 名称列表 |
 | `/api/timeseries` | GET | 时序 Token 统计 |
 | `/api/agent-health` | GET | Agent 健康状态 |
 | `/api/agent-health/{pid}` | DELETE | 删除健康条目 |
 | `/api/agent-health/{pid}/restart` | POST | 重启 Agent |
 | `/api/export/atif/trace/{id}` | GET | ATIF trace 导出 |
 | `/api/export/atif/session/{id}` | GET | ATIF session 导出 |
+| `/api/export/atif/conversation/{id}` | GET | ATIF conversation 导出 |
+| `/api/token-savings` | GET | Token 节省统计（`start_ns`, `end_ns`, `agent_name`） |
 | `/api/interruptions` | GET | 中断事件列表（`start_ns`, `end_ns`, `agent_name`, `type`, `severity`, `resolved`, `limit`） |
 | `/api/interruptions/count` | GET | 中断计数按严重级别（`start_ns`, `end_ns`） |
 | `/api/interruptions/stats` | GET | 中断按类型统计（`start_ns`, `end_ns`） |
 | `/api/interruptions/session-counts` | GET | 按 session 分组的中断计数（`start_ns`, `end_ns`） |
-| `/api/interruptions/trace-counts` | GET | 按 trace 分组的中断计数（`start_ns`, `end_ns`） |
+| `/api/interruptions/conversation-counts` | GET | 按 conversation 分组的中断计数（`start_ns`, `end_ns`） |
 | `/api/interruptions/{id}` | GET | 单个中断事件详情 |
 | `/api/interruptions/{id}/resolve` | POST | 标记中断为已解决 |
 | `/api/sessions/{id}/interruptions` | GET | 指定 session 的所有中断 |
-| `/api/traces/{id}/interruptions` | GET | 指定 trace 的所有中断 |
+| `/api/conversations/{id}/interruptions` | GET | 指定 conversation 的所有中断 |
 
 ## 8. Frontend
 
PATCH

echo "Gold patch applied."
