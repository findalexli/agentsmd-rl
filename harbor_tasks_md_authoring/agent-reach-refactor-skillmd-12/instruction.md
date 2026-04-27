# refactor: 合并 SKILL.md 为单一来源，更新为 12 渠道

Source: [Panniantong/Agent-Reach#8](https://github.com/Panniantong/Agent-Reach/pull/8)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `agent-reach/SKILL.md`
- `agent_reach/integrations/skill/SKILL.md`
- `agent_reach/skill/SKILL.md`

## What to add / change

## 改了什么

之前有 3 份 SKILL.md 散落在不同目录，内容不一致。合并为一份。

### 删除的（重复文件）
- `agent-reach/SKILL.md` — 旧的 9 渠道版本
- `agent_reach/integrations/skill/SKILL.md` — 旧的中文版本

### 保留并更新的
- `agent_reach/skill/SKILL.md` — 唯一来源，更新内容：
  - 描述从 9+ → 12+ 渠道
  - 新增 `search-instagram`、`search-linkedin`、`search-bosszhipin` 命令
  - 新增渠道配置流程说明（依赖 `doctor` 输出引导，不硬编码步骤）
  - 触发词新增「帮我配」「帮我添加」「帮我安装」

### 与 PR #7 冲突吗？
不冲突。PR #7 改的是 README.md 和 docs/README_en.md，本 PR 改的是 SKILL.md 文件。

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
