# chore(skills): improve create-pr skill trigger phrases

Source: [ant-design/ant-design#57529](https://github.com/ant-design/ant-design/pull/57529)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/create-pr/SKILL.md`

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
- [x] ❓ 其他改动（skill 维护：补充 create-pr 触发短句说明）

### 🔗 相关 Issue

N/A

### 💡 需求背景和解决方案

补充 `create-pr` skill 的触发说明，增加口语化中英文短句示例（如 `创建pr`、`开pr`、`create pr`、`open a pr` 等），避免因用户输入过于简短而未能正确触发本 skill。

### 📝 更新日志

| 语言    | 更新描述 |
| ------- | -------- |
| 🇺🇸 英文 | N/A      |
| 🇨🇳 中文 | N/A      |

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
