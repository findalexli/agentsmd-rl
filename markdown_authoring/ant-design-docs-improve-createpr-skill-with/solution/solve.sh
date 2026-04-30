#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ant-design

# Idempotency guard
if grep -qF "\u56db\u3001\u771f\u6b63\u6267\u884c `gh pr create` \u4e4b\u524d\uff0c\u5fc5\u987b\u5148\u628a `base`\u3001`title`\u3001`body` \u7ed9\u7528\u6237\u786e\u8ba4\uff0c\u786e\u8ba4\u540e\u624d\u80fd\u521b\u5efa PR\u3002" ".claude/skills/create-pr/SKILL.md" && grep -qF "- PR title: `site: adjust token panel interaction on theme preview page`" ".claude/skills/create-pr/references/template-notes-and-examples.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/create-pr/SKILL.md b/.claude/skills/create-pr/SKILL.md
@@ -13,6 +13,8 @@ description: Create pull requests for ant-design using the repository's official
 
 三、根据用户语言习惯选择中文或英文模板，但 PR 标题始终使用英文，并遵循本文档约定的命名格式。
 
+四、真正执行 `gh pr create` 之前，必须先把 `base`、`title`、`body` 给用户确认，确认后才能创建 PR。
+
 ## 触发场景
 
 当用户提及以下任一情况时使用本 skill：
@@ -55,20 +57,31 @@ description: Create pull requests for ant-design using the repository's official
 创建 PR 前，必须先看：
 
 - 当前分支名
-- 基线分支（默认优先 `master`，若仓库实际工作流不同，再按当前仓库状态判断）
+- 基线分支
 - 当前分支相对基线分支的 commit 列表
 - `base...HEAD` 的完整 diff
 
 不要只根据工作区未提交内容写 PR，也不要只根据最近一个 commit 写 PR。
 
-### 四、标题和正文要分工明确
+### 四、先给草稿，后创建 PR
+
+无论用户是否说“直接帮我创建 PR”，都要先完成以下步骤：
+
+1. 生成 `base`、`title`、`body` 草稿
+2. 明确告诉用户：这是准备提交的 PR 内容
+3. 让用户确认是否继续创建，或先修改
+4. 只有用户明确确认后，才能真正执行 `gh pr create`
+
+若用户中途要求修改标题、类型、changelog、目标分支等，应先更新草稿，再次确认。
+
+### 五、标题和正文要分工明确
 
 - PR 标题：用英文一句话概括本分支最主要的变动
 - PR 正文：说明背景、改法、关联 issue、更新日志影响
 
 正文不是逐文件流水账。要归纳“为什么改”和“改完后对开发者/用户有什么影响”。
 
-### 五、信息不足时不要硬写
+### 六、信息不足时不要硬写
 
 若以下内容缺失且无法从分支改动中可靠推断：
 
@@ -77,7 +90,7 @@ description: Create pull requests for ant-design using the repository's official
 - 变动性质
 - 测试或验证方式
 
-可以先给出草稿，并把无法确认的地方保留为待补充项；若用户要求直接创建 PR，则先向用户说明缺失项。
+可以先给出草稿，并把无法确认的地方保留为待补充项；若用户要求直接创建 PR，也必须先说明缺失项并等待确认。
 
 ## 执行步骤
 
@@ -96,19 +109,40 @@ gh auth status
 
 ### 2. 确定基线分支
 
-按以下顺序判断：
+不要默认就用 `master`。按以下顺序判断：
 
-1. 用户明确指定了 base branch -> 直接使用
-2. 远端默认分支是 `master` -> 使用 `master`
-3. 否则使用仓库默认分支
+1. 用户明确指定了 `base branch` -> 直接使用
+2. 若当前分支存在可用的“来源线索”，优先根据真实 Git 信息推断：
+   - `git branch -vv` 查看 tracking / upstream
+   - `git reflog show <current-branch>` 查看是否能看出“从哪条分支 checkout 出来”
+   - 必要时结合 `git merge-base HEAD <candidate-branch>` 比较分叉点
+3. 若能较可靠判断“当前分支是从某条分支切出来的”，优先使用该分支作为 `base`
+4. 若无法可靠推断，再退回远端默认分支或仓库默认分支
 
 建议查看：
 
 ```bash
-git remote show origin
+git branch --show-current
 git branch -vv
+git reflog show --date=local $(git branch --show-current)
+git remote show origin
 ```
 
+注意：
+
+- tracking / upstream 只能作为线索，不等于绝对正确的“父分支”
+- `reflog` 若已清理，可能无法得到结果
+- 若推断结果不够确定，要在草稿中明确标注为“推断值”
+
+#### 新功能分支的额外提醒
+
+如果改动性质判断为 `feat` / 新功能，且当前基线不是明显的功能分支（如 `feature/*`），应额外提醒用户：
+
+- 这个改动看起来像新功能
+- 请确认是否应该提交到对应的 `feature` 分支，而不是默认开发主分支
+
+此提醒只用于确认工作流，不要擅自改 base。
+
 ### 3. 收集本分支全部改动
 
 至少查看：
@@ -136,7 +170,34 @@ git diff --name-only <base>...HEAD
 
 读取对应模板后再填写，避免凭记忆手写 section。
 
-### 5. 归纳 PR 的核心信息
+### 5. 判断 PR 类型
+
+必须根据“主目的”判断，不要仅因为改动里包含逻辑变更就默认写成 `fix`。
+
+优先判断顺序：
+
+1. 是否主要是站点、文档、示例、演示、说明文本、主题页、官网交互等改动
+   - 是：优先考虑 `site` / `docs` / `demo`
+2. 是否主要是 CI、workflow、脚本、发布流程、校验流程等改动
+   - 是：优先考虑 `ci` / `chore`
+3. 是否主要是组件缺陷修复、行为异常修复、样式问题修复
+   - 是：考虑 `fix`
+4. 是否主要是公开能力新增
+   - 是：考虑 `feat`
+5. 是否主要是重构、测试、类型、性能等专项改动
+   - 是：使用 `refactor` / `test` / `type` / `perf`
+
+判断时以“用户感知的主结果”为准，不要被单个文件或单个 commit 干扰。
+
+例如：
+
+- 官网主题页按钮异常 -> 更偏 `site`，不是组件 `fix`
+- 文档说明修正 -> `docs`
+- demo 行为调整但不影响组件实现 -> `demo`
+- workflow / action 调整 -> `ci`
+- 组件真实行为 bug -> `fix`
+
+### 6. 归纳 PR 的核心信息
 
 至少整理出：
 
@@ -145,17 +206,38 @@ git diff --name-only <base>...HEAD
 - Background and Solution：说明问题背景、处理方式、是否有 UI/API 变化
 - Change Log：写“影响”，不要写实现流水账
 
-如果没有 changelog 价值，不要编造影响，可以写简洁但诚实的描述。
+### 7. 处理 Change Log
+
+对于以下场景，通常无需写实质 changelog：
+
+- `site`
+- `docs`
+- `demo`
+- `ci`
+- 纯测试
+- 仅内部维护、无用户可感知变化的调整
+
+这类场景：
 
-### 6. 生成 PR 标题
+- 不要硬编 changelog 文案
+- 保留模板 section
+- 使用简洁占位即可，例如：
+  - `N/A`
+  - `No changelog required`
+  - `无需更新日志`
+
+只有当改动确实会影响组件使用者、公开 API、交互行为、视觉表现或发布内容时，才写实质 changelog。
+
+### 8. 生成 PR 标题
 
 标题要求：
 
 - 按下方“写法要求 -> 标题”生成
 - 覆盖整条分支的主要目标
 - 不要照搬单个 commit message
+- `type` 要与第 5 步判断一致
 
-### 7. 按模板产出 PR 正文
+### 9. 按模板产出 PR 正文草稿
 
 填写时遵守：
 
@@ -164,26 +246,44 @@ git diff --name-only <base>...HEAD
 - 勾选最合适的类型
 - 内容尽量具体，但不要写成长篇说明
 - 若涉及 UI 变化，提醒可补截图或 GIF
+- 若某信息尚未确认，要显式标出来，不要假装确定
 
-### 8. 创建 PR
+### 10. 先给用户确认
 
-若用户要求真正发起 PR：
+输出时至少包含：
 
-1. 先确认当前分支的 tracking remote 和远端分支是否正确
-2. 再确认 PR 的目标仓库是 `ant-design/ant-design`，不要依赖 `gh` 的默认推断
-3. 若 tracking remote 缺失、指向不明确、或不是预期 fork，先向用户确认，不要默认推送
-4. 只有在推送目标 remote 明确无误时，才推送当前分支
-5. 使用 `gh pr create`
-6. 标题和正文都使用已经整理好的内容
+- `Base branch`
+- `PR title`
+- `PR body`
+- 需要用户补充或确认的点
+
+明确询问用户是否：
 
-建议先检查：
+- 直接创建 PR
+- 先修改后再创建
+
+没有明确确认前，不得执行 `gh pr create`。
+
+### 11. 创建 PR
+
+只有在用户明确确认后，才执行。
+
+执行前再次检查：
 
 ```bash
 git branch -vv
 git remote -v
 gh repo view --json nameWithOwner
 ```
 
+要求：
+
+1. 确认当前分支的 tracking remote 和远端分支正确
+2. 确认 PR 的目标仓库是 `ant-design/ant-design`，不要依赖 `gh` 默认推断
+3. 若 tracking remote 缺失、指向不明确、或不是预期 fork，先向用户确认，不要默认推送
+4. 只有在推送目标 remote 明确无误时，才推送当前分支
+5. 使用已确认过的标题和正文执行 `gh pr create`
+
 若需要推送，优先使用明确的远端与分支名，例如：
 
 ```bash
@@ -224,6 +324,7 @@ EOF
 - `test`：测试改动
 - `ci`：CI 或 workflow
 - `chore`：杂项维护
+- `perf`：性能优化
 
 `scope` 使用规则：
 
@@ -239,22 +340,10 @@ EOF
 
 ### Change Log
 
-- 写对开发者或用户的影响
-- 不要把实现细节原样搬进 changelog
-- 中英文两行内容应语义一致，不要只填其中一种
-
-## 禁止
-
-- 不读取 `base...HEAD` 的 commit 和 diff 就写 PR
-- 不看模板，直接凭印象生成正文
-- 用工作区未提交内容代替 PR 内容
-- 只总结最后一个 commit
-- 不确认 PR 的目标仓库，直接依赖 `gh` 默认推断
-- 标题写成中文
-- 标题不带 `type`，却伪装成符合仓库习惯
-- 模板正文语言和所选模板不一致
-- 编造 issue 编号、测试结果或发布影响
+- 有真实用户影响时再写
+- `site` / `docs` / `demo` / `ci` / 纯测试等无须强写
+- 无需 changelog 时保留 section，但使用简洁占位
 
 ## 参考
 
-更多勾选项建议、正文压缩写法和中英文示例见 `references/template-notes-and-examples.md`。
+更多类型判断、基线分支建议、确认话术与标题示例见 `references/template-notes-and-examples.md`。
diff --git a/.claude/skills/create-pr/references/template-notes-and-examples.md b/.claude/skills/create-pr/references/template-notes-and-examples.md
@@ -6,13 +6,35 @@
 
 - 新增组件能力或公开 API：`🆕 New feature` / `🆕 新特性提交`
 - 修复缺陷：`🐞 Bug fix` / `🐞 Bug 修复`
-- 站点文档、示例、说明文字：`📝 Site / documentation improvement` / `📝 站点、文档改进`
+- 站点文档、官网页面、主题页、说明文字：`📝 Site / documentation improvement` / `📝 站点、文档改进`
 - demo 调整：`📽️ Demo improvement` / `📽️ 演示代码改进`
 - 样式或交互微调：`💄 Component style improvement` / `💄 组件样式/交互改进`
 - 类型修正：`🤖 TypeScript definition improvement` / `🤖 TypeScript 定义更新`
 - 性能问题：`⚡️ Performance optimization` / `⚡️ 性能优化`
 - 重构但无外部行为变化：`🛠 Refactoring` / `🛠 重构`
 - 测试补充：`✅ Test Case` / `✅ 测试用例`
+- CI / workflow / action：通常归到 `⏩ Workflow`、`❓ Other`，或标题使用 `ci:`
+
+## 类型判断补充说明
+
+不要因为 diff 里包含逻辑代码就直接判成 `fix`。先看“最终在修什么”。
+
+优先判断：
+
+1. **site / docs / demo / ci 优先于 fix**
+   - 若主要改的是官网、文档、演示、脚本、workflow，即使涉及一些逻辑代码，也通常不该写成组件 `fix`
+2. **fix 只用于真实缺陷修复**
+   - 组件行为异常、渲染错误、交互不符合预期、样式 bug，才优先用 `fix`
+3. **feat 只用于对外新增能力**
+   - 不是“内部代码变多了”就算 feat，而是用户真的获得了新能力
+
+示例：
+
+- 修官网主题页按钮逻辑 -> `site: ...`
+- 修文档描述错误 -> `docs: ...`
+- 修 demo 的展示逻辑 -> `demo: ...`
+- 修 GitHub Actions 校验 -> `ci: ...`
+- 修 Select 真正的组件行为 bug -> `fix(Select): ...`
 
 ## Related Issues 写法
 
@@ -55,9 +77,17 @@ Select 在搜索过程中更新选项后，下拉列表会出现滚动位置跳
 
 ## Change Log 写法
 
-写“影响”，不要写实现步骤。
+### 1) 需要写实质 changelog 的场景
 
-英文示例：
+当改动会影响：
+
+- 组件使用方式
+- 公开 API
+- 交互行为
+- UI / 视觉表现
+- 用户实际可感知结果
+
+可写成：
 
 ```markdown
 ### 📝 Change Log
@@ -68,15 +98,90 @@ Select 在搜索过程中更新选项后，下拉列表会出现滚动位置跳
 | 🇨🇳 Chinese | 修复 Select 搜索时下拉列表滚动位置跳动问题       |
 ```
 
-中文示例：
+### 2) 无需 changelog 的场景
+
+常见包括：
+
+- `site`
+- `docs`
+- `demo`
+- `ci`
+- 纯测试
+- 内部维护或重构，且无外部可感知变化
+
+这类场景不要硬写影响描述，可直接使用占位：
+
+英文：
+
+```markdown
+### 📝 Change Log
+
+| Language   | Changelog             |
+| ---------- | --------------------- |
+| 🇺🇸 English | No changelog required |
+| 🇨🇳 Chinese | 无需更新日志          |
+```
+
+中文：
 
 ```markdown
 ### 📝 更新日志
 
-| 语言    | 更新描述                                         |
-| ------- | ------------------------------------------------ |
-| 🇺🇸 英文 | Fix Select dropdown scroll jumping during search |
-| 🇨🇳 中文 | 修复 Select 搜索时下拉列表滚动位置跳动问题       |
+| 语言    | 更新描述              |
+| ------- | --------------------- |
+| 🇺🇸 英文 | No changelog required |
+| 🇨🇳 中文 | 无需更新日志          |
+```
+
+也可以更短，直接写：
+
+- `N/A`
+- `No changelog required`
+- `无需更新日志`
+
+前提是保留模板 section，不要直接删掉整个 changelog 区块。
+
+## 基线分支判断建议
+
+目标是尽量推断“当前分支实际从哪里切出来”，而不是拍脑袋默认 `master`。
+
+建议顺序：
+
+1. 用户明确指定了 `base branch` -> 直接使用
+2. 查看当前分支是否能从 `reflog` 看出 checkout 来源
+3. 查看 `git branch -vv` 的 tracking / upstream 作为辅助线索
+4. 必要时结合 `merge-base` 比较候选分支
+5. 若仍无法确定，再退回远端默认分支或仓库默认分支
+
+建议命令：
+
+```bash
+git branch --show-current
+git branch -vv
+git reflog show --date=local $(git branch --show-current)
+git remote show origin
+git merge-base HEAD <candidate-branch>
+```
+
+注意：
+
+- upstream 不是绝对父分支，只是候选线索
+- `reflog` 最接近真实答案，但不一定一直存在
+- 不确定时要明确告诉用户“这是推断值”
+
+## 创建 PR 前确认话术建议
+
+在真正执行 `gh pr create` 之前，应该先给用户一个确认版草稿，例如：
+
+```markdown
+我先整理了一版待提交的 PR 草稿，请你确认：
+
+- Base branch: `feature-x`
+- PR title: `site: adjust token panel interaction on theme preview page`
+- PR type: `📝 Site / documentation improvement`
+- Change Log: `No changelog required`
+
+如果没问题，我再继续创建 PR；如果你想改 title、type、base 或正文，我先帮你改。
 ```
 
 ## PR 标题示例
@@ -98,6 +203,7 @@ Select 在搜索过程中更新选项后，下拉列表会出现滚动位置跳
 - `test`
 - `ci`
 - `chore`
+- `perf`
 
 英文：
 
@@ -106,12 +212,14 @@ Select 在搜索过程中更新选项后，下拉列表会出现滚动位置跳
 - `refactor(Image): extract normalizePlaceholder to usePlaceholderConfig hook`
 - `site: fix ThemePreview copy button in dark theme`
 - `feat: add Typography.Shimmer component`
+- `ci: adjust pull request label workflow`
 
 更贴近当前分支时，可写成：
 
 - `fix(Select): keep dropdown scroll position stable during search`
 - `docs: clarify Upload beforeUpload return behavior`
 - `refactor(Table): simplify sticky offset calculation`
+- `site: refine AI theme page empty state copy`
 
 不要这样写：
 
PATCH

echo "Gold patch applied."
