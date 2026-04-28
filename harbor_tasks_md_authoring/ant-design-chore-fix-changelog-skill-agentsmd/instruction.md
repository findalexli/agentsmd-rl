# chore: fix changelog skill AGENTS.md references

Source: [ant-design/ant-design#57397](https://github.com/ant-design/ant-design/pull/57397)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/changelog-collect/SKILL.md`

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
- [ ] ⌨️ 无障碍改进
- [x] ❓ 其他改动（Codex skill 文档维护）

### 🔗 相关 Issue

N/A

### 💡 需求背景和解决方案

`changelog-collect` skill 中引用 `AGENTS.md` 的相对链接写成了从 skill 目录出发的错误路径，且部分锚点名与仓库中的实际标题不一致。

本次改动将这些引用更新为指向仓库根目录 `AGENTS.md` 的正确相对路径，并对齐到实际存在的章节锚点，保证 skill 在引用 changelog 规范时可以正确跳转和定位。

### 📝 更新日志

| 语言    | 更新描述 |
| ------- | -------- |
| 🇺🇸 英文 | N/A |
| 🇨🇳 中文 | 无需更新日志 |

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
