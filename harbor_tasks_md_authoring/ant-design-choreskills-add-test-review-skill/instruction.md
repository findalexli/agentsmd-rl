# chore(skills): add test review skill

Source: [ant-design/ant-design#57628](https://github.com/ant-design/ant-design/pull/57628)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/test-review/SKILL.md`

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
- [x] ❓ 其他改动（是关于什么的改动？）

### 🔗 相关 Issue

https://github.com/ant-design/ant-design/issues/57120

### 💡 需求背景和解决方案

新增一个 `antd-test-review` skill，用于静态审查 ant-design 测试用例是否值得保留。

本次 skill 聚焦于判断测试是否存在“用 A 证明 A”、重复覆盖、实现细节自证等问题，并默认只做静态审查，不主动运行测试。

### 📝 更新日志

| 语言    | 更新描述 |
| ------- | -------- |
| 🇺🇸 英文 | No changelog required |
| 🇨🇳 中文 | 无需更新日志 |

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
