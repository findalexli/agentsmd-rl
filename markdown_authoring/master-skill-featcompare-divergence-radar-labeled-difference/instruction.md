# feat(compare): divergence radar + labeled differences + classic debate templates

Source: [xr843/Master-skill#9](https://github.com/xr843/Master-skill/pull/9)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `prebuilt/compare/SKILL.md`

## What to add / change

## 背景

当前 \`/compare-masters\` 的输出模板只有一个松散的"共通点 / 差异点"表格，容易产出"各有侧重"式的浅层总结——这正是多祖师对比最该避免的失败模式。分歧如果不能定位到"究竟是哪一层的分歧"，学习者就学不到真正的东西。

## 改动

### 1. 五维分歧雷达（强制分析框架）

替换原有的"对比总结表"，改为强制填满的五维坐标系：

| 维度 | 说明 |
|---|---|
| **否定什么** | 各自要破的对象 |
| **安立什么** | 各自要立的对象 |
| **入手处** | 实修起点 |
| **根器设定** | 对谁说 |
| **终极表达** | 目标怎么说 |

十个单元格不得留空——强制 LLM 在每一维上做判断，而不是绕过难点。

### 2. 分歧类型标签（强制）

每条具体差异必须贴以下四种标签之一：

- \`[宗派性分歧]\` 根本立场不同
- \`[侧重性分歧]\` 立场相容但重心不同
- \`[表达性分歧]\` 究竟义相同，语言不同
- \`[根器性分歧]\` 针对不同学人的方便差异

这条约束的价值在于：它强迫 AI 先判断"这究竟是哪一层的分歧"，防止把 根器性 差异误判为 宗派性 冲突（最常见的错误）。

### 3. 经典论题预设模板

固化历史上四个真实论题，配推荐祖师对和真实争点：

- **禅净之争** — \`huineng\` + \`yinguang\`
- **性相之辩** — \`xuanzang\` + \`fazang\`
- **空有之争** — \`kumarajiva\` + \`xuanzang\`
- **顿渐之辩** — \`huineng\` + \`zhiyi\`

每个论题都列出了真实历史注脚（永明延寿、吉藏、窥基、智顗等），避免 AI 从零构造对比时瞎编。

### 4. 元问题追问引导

Step 4 自动生成 3 条"为什么他们不一样"式的追问，把单次对比带入持续学习会话。这是 Perplexity 式的"下一步提示"，对佛学学习尤其契合——初学者往往不知道下一个问题该问什么。

### 5. HARD-GATE 新增三条铁律

- **NO UNLABELED DIVERGENCE** — 无类型标签的差异视为未完成输出
- **NO EMPTY RADAR CELL** — 雷达表 10 个单元格不得留空
- 配套"理性化借口反驳表"和"红旗立即停止"条目

## 验证

- \`scripts/validate.py --strict\` 全绿（9/9 masters 通过）
- compare 作为 meta-skill，验证器已在 #8 中正确豁免 lineage/source 字段

## 下一步

本 PR merge 后，紧接着会开第二个 PR 处理"非 CLI 用户触达"——README 把 fojin.app/chat 提到第一屏，同时为 8 位法师各添加 \`starter_questions\` 字段供 fojin.app/chat 冷启动使用。

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
