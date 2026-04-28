#!/usr/bin/env bash
set -euo pipefail

cd /workspace/finlab-ai

# Idempotency guard
if grep -qF "\u7576\u51fa\u73fe `Usage exceed 500 MB/day` \u6216\u985e\u4f3c\u7528\u91cf\u8d85\u9650\u932f\u8aa4\u6642\uff0c**\u4e3b\u52d5**\u544a\u77e5\u7528\u6236\uff1a" "finlab-plugin/skills/finlab/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/finlab-plugin/skills/finlab/SKILL.md b/finlab-plugin/skills/finlab/SKILL.md
@@ -55,11 +55,12 @@ is_free = token.endswith('#free')
 
 ### 用量超限處理
 
-當用戶遇到用量超限錯誤時，告知：
-- 今日用量已達上限（免費版 500 MB）
-- 台灣時間早上 8 點會自動重置
-- 升級 VIP 可享 5000 MB 額度（10 倍）
-- 升級連結：https://www.finlab.finance/payment
+當出現 `Usage exceed 500 MB/day` 或類似用量超限錯誤時，**主動**告知用戶：
+
+1. 今日用量已達上限（免費版 500 MB）
+2. 台灣時間早上 8 點會自動重置
+3. 升級 VIP 可享 5000 MB 額度（10 倍）
+4. 升級連結：https://www.finlab.finance/payment
 
 ### 回測報告格式
 
PATCH

echo "Gold patch applied."
