#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF "description: \"\u5f53\u9700\u8981\u7528 lark-cli \u64cd\u4f5c\u98de\u4e66\u591a\u7ef4\u8868\u683c\uff08Base\uff09\u65f6\u8c03\u7528\uff1a\u9002\u7528\u4e8e\u5efa\u8868\u3001\u5b57\u6bb5\u7ba1\u7406\u3001\u8bb0\u5f55\u8bfb\u5199\u3001\u8bb0\u5f55\u5206\u4eab\u94fe\u63a5\u3001\u89c6\u56fe\u914d\u7f6e\u3001\u5386\u53f2\u67e5\u8be2\uff0c\u4ee5" "skills/lark-base/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/lark-base/SKILL.md b/skills/lark-base/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: lark-base
 version: 1.2.0
-description: "当需要用 lark-cli 操作飞书多维表格（Base）时调用：适用于建表、字段管理、记录读写、视图配置、历史查询，以及角色/表单/仪表盘管理/工作流；也适用于把旧的 +table / +field / +record 写法改成当前命令写法。涉及字段设计、公式字段、查找引用、跨表计算、行级派生指标、数据分析需求时也必须使用本 skill。"
+description: "当需要用 lark-cli 操作飞书多维表格（Base）时调用：适用于建表、字段管理、记录读写、记录分享链接、视图配置、历史查询，以及角色/表单/仪表盘管理/工作流；也适用于把旧的 +table / +field / +record 写法改成当前命令写法。涉及字段设计、公式字段、查找引用、跨表计算、行级派生指标、数据分析需求时也必须使用本 skill。"
 metadata:
   requires:
     bins: ["lark-cli"]
@@ -107,6 +107,7 @@ metadata:
 | `+record-upload-attachment` | 给已有记录上传附件 | [`lark-base-record-upload-attachment.md`](references/lark-base-record-upload-attachment.md) | 附件上传专用链路，不要用 `+record-upsert` / `+record-batch-*` 伪造附件值 |
 | `lark-cli docs +media-download` | 下载 Base 附件文件到本地 | [`../lark-doc/references/lark-doc-media-download.md`](../lark-doc/references/lark-doc-media-download.md) | Base 附件的 `file_token` 从 `+record-get` 返回的附件字段数组里取；**不要用 `lark-cli drive +download`**（对 Base 附件返回 403） |
 | `+record-delete / +record-history-list` | 删除记录，或查询某条记录的变更历史 | [`lark-base-record-delete.md`](references/lark-base-record-delete.md)、[`lark-base-record-history-list.md`](references/lark-base-record-history-list.md) | 删除时用户已明确目标可直接执行并带 `--yes`；历史查询按 `table-id + record-id`，不支持整表扫描；`+record-history-list` 只能串行执行 |
+| `+record-share-link-create` | 为一条或多条记录生成分享链接 | [`lark-base-record-share-link-create.md`](references/lark-base-record-share-link-create.md) | 单次最多 100 条；重复 record_id 会自动去重；适合分享单条记录或批量分享场景 |
 
 #### 2.3.4 View 子模块
 
PATCH

echo "Gold patch applied."
