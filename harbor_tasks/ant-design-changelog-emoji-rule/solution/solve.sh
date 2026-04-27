#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ant-design

if grep -qF '每条 Changelog 仅选择一个 Emoji，不要在同一条目中叠加多个 Emoji。' CLAUDE.md; then
    echo "Patch already applied (idempotent)."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CHANGELOG.en-US.md b/CHANGELOG.en-US.md
index bfb39bd1ac8c..bc7684071aa6 100644
--- a/CHANGELOG.en-US.md
+++ b/CHANGELOG.en-US.md
@@ -22,7 +22,7 @@ tag: vVERSION
 - Image
   - 💄 Improve Image preview mask blur transition for `backdrop-filter` to reduce flicker perception. [#57299](https://github.com/ant-design/ant-design/pull/57299) [@mango766](https://github.com/mango766)
   - 🐞 Fix Image showing move cursor when `movable={false}`. [#57288](https://github.com/ant-design/ant-design/pull/57288) [@ug-hero](https://github.com/ug-hero)
-- ⌨️ ♿ Improve App link `:focus-visible` outline to enhance keyboard accessibility. [#57266](https://github.com/ant-design/ant-design/pull/57266) [@ug-hero](https://github.com/ug-hero)
+- ⌨️ Improve App link `:focus-visible` outline to enhance keyboard accessibility. [#57266](https://github.com/ant-design/ant-design/pull/57266) [@ug-hero](https://github.com/ug-hero)
 - 🐞 Fix Form required mark using hardcoded `SimSun` font. [#57273](https://github.com/ant-design/ant-design/pull/57273) [@mavericusdev](https://github.com/mavericusdev)
 - 🐞 Fix Grid media size mapping issue for `xxxl` breakpoint. [#57246](https://github.com/ant-design/ant-design/pull/57246) [@guoyunhe](https://github.com/guoyunhe)
 - 🐞 Fix Tree scrolling to top when clicking node. [#57242](https://github.com/ant-design/ant-design/pull/57242) [@aojunhao123](https://github.com/aojunhao123)
diff --git a/CHANGELOG.zh-CN.md b/CHANGELOG.zh-CN.md
index e08a0dfca4d4..43eb3a35d92e 100644
--- a/CHANGELOG.zh-CN.md
+++ b/CHANGELOG.zh-CN.md
@@ -22,7 +22,7 @@ tag: vVERSION
 - Image
   - 💄 优化 Image 预览蒙层 blur 效果的 `backdrop-filter` 过渡，减少闪烁感。[#57299](https://github.com/ant-design/ant-design/pull/57299) [@mango766](https://github.com/mango766)
   - 🐞 修复 Image 在 `movable={false}` 时仍显示 move 光标的问题。[#57288](https://github.com/ant-design/ant-design/pull/57288) [@ug-hero](https://github.com/ug-hero)
-- ⌨️ ♿ 优化 App 链接的 `:focus-visible` 外框样式，提升键盘可访问性。[#57266](https://github.com/ant-design/ant-design/pull/57266) [@ug-hero](https://github.com/ug-hero)
+- ⌨️ 优化 App 链接的 `:focus-visible` 外框样式，提升键盘可访问性。[#57266](https://github.com/ant-design/ant-design/pull/57266) [@ug-hero](https://github.com/ug-hero)
 - 🐞 修复 Form 必填标记文案中硬编码 `SimSun` 字体的问题。[#57273](https://github.com/ant-design/ant-design/pull/57273) [@mavericusdev](https://github.com/mavericusdev)
 - 🐞 修复 Grid `xxxl` 断点在媒体尺寸映射中的错误。[#57246](https://github.com/ant-design/ant-design/pull/57246) [@guoyunhe](https://github.com/guoyunhe)
 - 🐞 修复 Tree 点击节点时页面回滚到顶部的问题。[#57242](https://github.com/ant-design/ant-design/pull/57242) [@aojunhao123](https://github.com/aojunhao123)
diff --git a/CLAUDE.md b/CLAUDE.md
index 11a576a787f2..bda469d67c15 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -147,6 +147,8 @@ ant-design/
 | 🛠     | 重构或工具链优化       |
 | ⚡️     | 性能提升               |

+每条 Changelog 仅选择一个 Emoji，不要在同一条目中叠加多个 Emoji。
+
 编写 Changelog 时，请参考 `CHANGELOG.zh-CN.md` 和 `CHANGELOG.en-US.md` 中已有条目的格式。

 ---
PATCH

echo "Applied gold patch."
