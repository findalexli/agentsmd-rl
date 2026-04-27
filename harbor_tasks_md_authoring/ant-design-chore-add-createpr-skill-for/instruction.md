# chore: add create-pr skill for ant-design PR workflow

Source: [ant-design/ant-design#57228](https://github.com/ant-design/ant-design/pull/57228)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/create-pr/SKILL.md`
- `.claude/skills/create-pr/references/template-notes-and-examples.md`

## What to add / change

### 🤔 这个变动的性质是？

- [ ] 🆕 新特性提交
- [ ] 🐞 Bug 修复
- [ ] 📝 站点、文档改进
- [ ] 📽️ 演示代码改进
- [ ] 💄 组件样式/交互改进
- [ ] 🤖 TypeScript 定义更新
- [ ] 📦 包体积优化
- [ ] ⚡️ 性能优化
- [ ] ⭐️ 功能增强
- [ ] 🌐 国际化改进
- [ ] 🛠 重构
- [ ] 🎨 代码风格优化
- [ ] ✅ 测试用例
- [ ] 🔀 分支合并
- [ ] ⏩ 工作流程
- [x] ❓ 其他改动（新增 Claude Code create-pr skill）

### 🔗 相关 Issue

Related to https://github.com/ant-design/ant-design/issues/57120

### 💡 需求背景和解决方案

为 Claude Code 添加 `create-pr` skill，帮助 AI 助手按照 ant-design 的 PR 规范创建 Pull Request：

- 自动分析分支相对基线的全部改动（而非只看最后一个 commit）
- 强制使用仓库自带模板（中文 / 英文二选一）
- PR 标题固定使用英文，贴近仓库已合并 PR 的命名风格
- 提供详细的执行步骤和禁止事项，防止 AI 编造内容

### 📝 更新日志

| 语言    | 更新描述 |
| ------- | -------- |
| 🇺🇸 英文 | 无用户可感知变更（仅开发工具） |
| 🇨🇳 中文 | 无用户可感知变更（仅开发工具） |

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
