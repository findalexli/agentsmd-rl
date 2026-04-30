#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ant-design

# Idempotency guard
if grep -qF "- [Emoji \u89c4\u8303](../../../AGENTS.md#emoji-\u89c4\u8303) - \u6839\u636e commit \u7c7b\u578b\u81ea\u52a8\u6807\u8bb0" ".agents/skills/changelog-collect/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/changelog-collect/SKILL.md b/.agents/skills/changelog-collect/SKILL.md
@@ -267,10 +267,10 @@ const componentNames = [
 
 **AGENTS.md 规范引用：**
 
-- [核心原则](./AGENTS.md#核心原则) - 有效性过滤规则
-- [格式与结构规范](./AGENTS.md#格式与结构规范) - 分组、描述、Emoji 规范
-- [Emoji 规范](./AGENTS.md#emoji-规范严格执行) - 根据 commit 类型自动标记
-- [输出示例参考](./AGENTS.md#输出示例参考) - 中英文格式参考
+- [核心原则](../../../AGENTS.md#核心原则) - 有效性过滤规则
+- [格式规范](../../../AGENTS.md#格式规范) - 分组、描述、Emoji 规范
+- [Emoji 规范](../../../AGENTS.md#emoji-规范) - 根据 commit 类型自动标记
+- [句式](../../../AGENTS.md#句式) - 中英文格式参考
 
 根据 AGENTS.md 的规范，对 `~changelog.md` 中的条目进行过滤、分组、格式检查，并在必要时进行交互式确认和修改。
 
PATCH

echo "Gold patch applied."
