#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dingtalk-workspace-cli

# Idempotency guard
if grep -qF "--to-chat              \u662f\u5426\u53d1\u9001\u5230\u65e5\u5fd7\u63a5\u6536\u4eba\u5355\u804a (bool flag\uff0c\u76f4\u63a5\u52a0 --to-chat \u5373\u53ef)" "skills/references/products/report.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/references/products/report.md b/skills/references/products/report.md
@@ -35,7 +35,7 @@ Flags:
       --template-id string   日志模版 ID (必填)，从 template list 返回中取
       --contents string      日志内容 JSON 数组 (必填)，每项须含 key/sort/content/contentType/type
       --dd-from string       创建来源标识 (默认 dws)
-      --to-chat string       是否发送到日志接收人单聊 (传 "true" 发送)
+      --to-chat              是否发送到日志接收人单聊 (bool flag，直接加 --to-chat 即可)
       --to-user-ids string   接收人 userId，逗号分隔 (可选)
 ```
 
PATCH

echo "Gold patch applied."
