# docs: improve create-pr skill with confirmation step and type/changelog guidance

Source: [ant-design/ant-design#57261](https://github.com/ant-design/ant-design/pull/57261)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/create-pr/SKILL.md`
- `.claude/skills/create-pr/references/template-notes-and-examples.md`

## What to add / change

### 🤔 这个变动的性质是？

- [x] 📝 站点、文档改进

### 🔗 相关 Issue

无

### 💡 需求背景和解决方案

改进 create-pr 这一 skill 的流程与说明：

- 增加「先给出草稿、用户确认后再执行 `gh pr create`」的步骤，避免未确认就创建 PR。
- 明确基线分支的推断方式（reflog / tracking），不默认使用 `master`。
- 补充 PR 类型判断顺序（site / docs / demo / ci 优先于 fix），以及 Change Log 何时写实质内容、何时用占位。
- 在参考文档中增加确认话术、基线判断和 changelog 占位示例。

改动仅涉及 `.claude/skills/create-pr/` 下的 SKILL.md 与 references，无组件或 API 变更。

### 📝 更新日志

| 语言    | 更新描述     |
| ------- | ------------ |
| 🇺🇸 英文 | No changelog required |
| 🇨🇳 中文 | 无需更新日志 |

Made with [Cursor](https://cursor.com)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
