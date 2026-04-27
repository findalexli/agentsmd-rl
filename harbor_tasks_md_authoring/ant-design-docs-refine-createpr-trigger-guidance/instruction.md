# docs: refine create-pr trigger guidance by intent

Source: [ant-design/ant-design#57559](https://github.com/ant-design/ant-design/pull/57559)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/create-pr/SKILL.md`

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

N/A

### 💡 需求背景和解决方案

PR #57529 的评论指出，create-pr skill 在“触发场景”部分罗列了过多具体触发词，表达不够聚焦，也不利于维护。

本次调整将触发条件改为基于“用户意图”判断：只要可以判断用户是在请求创建 PR，或需要为创建 PR 做准备，就进入该 skill 的工作流。与此同时，移除了大段固定触发词示例，保留更简洁、可维护的规则说明。

### 📝 更新日志

| 语言    | 更新描述 |
| ------- | -------- |
| 🇺🇸 英文 | No changelog required |
| 🇨🇳 中文 | 无需更新日志 |

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
