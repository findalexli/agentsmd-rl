# chore: add version release skill

Source: [ant-design/ant-design#57514](https://github.com/ant-design/ant-design/pull/57514)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/version-release/SKILL.md`

## What to add / change

### 🤔 这个变动的性质是？

- [ ] 🆕 新特性提交
- [ ] 🐞 Bug 修复
- [x] 📝 站点、文档改进
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
- [ ] ❓ 其他改动（是关于什么的改动？）

### 🔗 相关 Issue

- #57120

### 💡 需求背景和解决方案

新增一个适用于 ant-design 仓库的 `version-release` skill，并将内容调整为仓库真实使用的发版流程。

主要改动包括：
- 补充 ant-design 的分支选择、changelog 更新、版本号维护、PR 规范与 `npm publish` 发布流程要求

### 📝 更新日志

无需更新日志

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
