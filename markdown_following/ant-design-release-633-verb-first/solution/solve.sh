#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ant-design

if grep -q "## 6.3.3" CHANGELOG.en-US.md 2>/dev/null; then
    echo "Gold already applied; nothing to do."
    exit 0
fi

patch -p1 --no-backup-if-mismatch <<'PATCH'
diff --git a/.claude/skills/changelog-collect/SKILL.md b/.claude/skills/changelog-collect/SKILL.md
index 4fa285bad30d..b583e8d06e53 100644
--- a/.claude/skills/changelog-collect/SKILL.md
+++ b/.claude/skills/changelog-collect/SKILL.md
@@ -274,6 +274,12 @@ const componentNames = [

 根据 AGENTS.md 的规范，对 `~changelog.md` 中的条目进行过滤、分组、格式检查，并在必要时进行交互式确认和修改。

+#### 描述与署名补充规则
+
+- 描述必须以动作开头：中文优先使用 `修复`、`优化`、`新增`、`重构` 等动词开头；英文优先使用 `Fix`、`Improve`、`Add`、`Refactor` 开头。
+- 在“动作开头”的前提下，正文仍需包含组件名（例如：`修复 Select ...`、`Fix Select ...`）。
+- 每条 changelog 统一补充 PR 作者链接（如 `[@username](https://github.com/username)`），不再校验是否为团队成员。
+
 ### 阶段三：写入文件

 在 `---` front matter 之后、第一个版本标题之前插入新内容：
@@ -367,5 +373,6 @@ const componentNames = [
 - 需要 gh CLI 认证（运行 `gh auth login`）
 - 写入前必须预览确认
 - 保持中英文同步更新
-- 组件名在正文中要出现（如 `Select 修复...`，不是 `修复 Select...`）
+- 描述以动作开头，并保证正文包含组件名（如 `修复 Select ...`、`Fix Select ...`）
+- 统一添加 PR 作者链接（不区分是否团队成员）
 - PR body 中没有中英文描述时，使用 PR title 作为后备
diff --git a/CHANGELOG.en-US.md b/CHANGELOG.en-US.md
index 80c843d418d6..bfb39bd1ac8c 100644
--- a/CHANGELOG.en-US.md
+++ b/CHANGELOG.en-US.md
@@ -15,6 +15,18 @@ tag: vVERSION

 ---

+## 6.3.3
+
+`2026-03-16`
+
+- Image
+  - 💄 Improve Image preview mask blur transition for `backdrop-filter` to reduce flicker perception. [#57299](https://github.com/ant-design/ant-design/pull/57299) [@mango766](https://github.com/mango766)
+  - 🐞 Fix Image showing move cursor when `movable={false}`. [#57288](https://github.com/ant-design/ant-design/pull/57288) [@ug-hero](https://github.com/ug-hero)
+- ⌨️ ♿ Improve App link `:focus-visible` outline to enhance keyboard accessibility. [#57266](https://github.com/ant-design/ant-design/pull/57266) [@ug-hero](https://github.com/ug-hero)
+- 🐞 Fix Form required mark using hardcoded `SimSun` font. [#57273](https://github.com/ant-design/ant-design/pull/57273) [@mavericusdev](https://github.com/mavericusdev)
+- 🐞 Fix Grid media size mapping issue for `xxxl` breakpoint. [#57246](https://github.com/ant-design/ant-design/pull/57246) [@guoyunhe](https://github.com/guoyunhe)
+- 🐞 Fix Tree scrolling to top when clicking node. [#57242](https://github.com/ant-design/ant-design/pull/57242) [@aojunhao123](https://github.com/aojunhao123)
+
 ## 6.3.2

 `2026-03-09`
diff --git a/CHANGELOG.zh-CN.md b/CHANGELOG.zh-CN.md
index de79b3eb7cae..e08a0dfca4d4 100644
--- a/CHANGELOG.zh-CN.md
+++ b/CHANGELOG.zh-CN.md
@@ -15,6 +15,18 @@ tag: vVERSION

 ---

+## 6.3.3
+
+`2026-03-16`
+
+- Image
+  - 💄 优化 Image 预览蒙层 blur 效果的 `backdrop-filter` 过渡，减少闪烁感。[#57299](https://github.com/ant-design/ant-design/pull/57299) [@mango766](https://github.com/mango766)
+  - 🐞 修复 Image 在 `movable={false}` 时仍显示 move 光标的问题。[#57288](https://github.com/ant-design/ant-design/pull/57288) [@ug-hero](https://github.com/ug-hero)
+- ⌨️ ♿ 优化 App 链接的 `:focus-visible` 外框样式，提升键盘可访问性。[#57266](https://github.com/ant-design/ant-design/pull/57266) [@ug-hero](https://github.com/ug-hero)
+- 🐞 修复 Form 必填标记文案中硬编码 `SimSun` 字体的问题。[#57273](https://github.com/ant-design/ant-design/pull/57273) [@mavericusdev](https://github.com/mavericusdev)
+- 🐞 修复 Grid `xxxl` 断点在媒体尺寸映射中的错误。[#57246](https://github.com/ant-design/ant-design/pull/57246) [@guoyunhe](https://github.com/guoyunhe)
+- 🐞 修复 Tree 点击节点时页面回滚到顶部的问题。[#57242](https://github.com/ant-design/ant-design/pull/57242) [@aojunhao123](https://github.com/aojunhao123)
+
 ## 6.3.2

 `2026-03-09`
diff --git a/CLAUDE.md b/CLAUDE.md
index 393044ab1db7..11a576a787f2 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -106,7 +106,7 @@ ant-design/
 - 必须同时提供中英文两个版本
 - 忽略用户无感知的改动（内部重构、纯测试更新、工具链优化等）
 - 描述"对开发者的影响"，而非"具体的实现细节"
-- 尽量给出 PR 链接，社区 PR 加贡献者链接
+- 尽量给出 PR 链接，并统一添加贡献者链接

 ### 格式规范

@@ -122,7 +122,7 @@ ant-design/

 | 语言 | 格式 | 示例 |
 |---|---|---|
-| 中文 | `Emoji 组件名 动词/描述` | `🐞 Button 修复暗色主题下 \`color\` 的问题。` |
+| 中文 | `Emoji 动词 组件名 描述`（动词在前） | `🐞 修复 Button 在暗色主题下 \`color\` 的问题。` |
 | 英文 | `Emoji 动词 组件名 描述`（动词在前） | `🐞 Fix Button reversed \`hover\` colors in dark theme.` |

 #### 分组逻辑
diff --git a/package.json b/package.json
index 2bc20269227a..aef26692a3c4 100644
--- a/package.json
+++ b/package.json
@@ -1,6 +1,6 @@
 {
   "name": "antd",
-  "version": "6.3.2",
+  "version": "6.3.3",
   "description": "An enterprise-class UI design language and React components implementation",
   "license": "MIT",
   "funding": {