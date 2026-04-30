#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF "- \u5bf9\u9f50\u4e0d\u5141\u8bb8\u5bf9\u9f50\u81ea\u5df1\u7684\u76ee\u6807\uff0c\u4e14\u53d1\u8d77\u5bf9\u9f50\u7684\u76ee\u6807\u548c\u88ab\u5bf9\u9f50\u7684\u76ee\u6807\u6240\u5728\u5468\u671f\u65f6\u95f4\u4e0a\u5fc5\u987b\u6709\u91cd\u53e0\uff0c\u5426\u5219\u4f1a\u53c2\u6570\u6821\u9a8c\u5931\u8d25\u3002" "skills/lark-okr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/lark-okr/SKILL.md b/skills/lark-okr/SKILL.md
@@ -49,7 +49,9 @@ lark-cli okr <resource> <method> [flags] # 调用 API
 
 - `list` — 批量获取用户周期
 - `objectives_position` — 更新用户周期下全部目标的位置
+  - 请求中必须同时修改对应周期下全部目标的位置，且不允许位置重叠，否则会参数校验失败。
 - `objectives_weight` — 更新用户周期下全部目标的权重
+  - 请求中必须同时修改对应周期下全部目标的权重，且所有权重值的和必须等于 1 ，否则会参数校验失败。
 
 ### cycle.objectives
 
@@ -75,12 +77,15 @@ lark-cli okr <resource> <method> [flags] # 调用 API
 - `delete` — 删除目标
 - `get` — 获取目标
 - `key_results_position` — 更新全部关键结果的位置
+  - 请求中必须同时修改对应目标下全部关键结果的位置，且不允许位置重叠，否则会参数校验失败。
 - `key_results_weight` — 更新全部关键结果的权重
+  - 请求中必须同时修改对应目标下全部关键结果的权重，且所有权重值的和必须等于 1 ，否则会参数校验失败。
 - `patch` — 更新目标
 
 ### objective.alignments
 
 - `create` — 创建对齐关系
+  - 对齐不允许对齐自己的目标，且发起对齐的目标和被对齐的目标所在周期时间上必须有重叠，否则会参数校验失败。
 - `list` — 批量获取目标下的对齐关系
 
 ### objective.indicators
PATCH

echo "Gold patch applied."
