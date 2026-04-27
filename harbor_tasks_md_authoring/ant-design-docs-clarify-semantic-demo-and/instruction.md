# docs: clarify semantic demo and .dumi import rules

Source: [ant-design/ant-design#57736](https://github.com/ant-design/ant-design/pull/57736)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

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

<img width="794" height="529" alt="image" src="https://github.com/user-attachments/assets/208e4748-ab3a-4b22-9da9-e022149de91a" />


线上 AI review 会把 `components/**/demo/_semantic*.tsx` 中相对引用 `.dumi` 辅助模块的写法误判为违规导入。

这次更新了仓库中的 AI 协作说明，明确：
1. 常规 demo 仍应优先使用公开入口或已配置别名。
2. `_semantic*.tsx` 属于语义文档专用 demo，允许相对引用 `.dumi/hooks/useLocale`、`.dumi/theme/common/*` 等站点辅助模块。
3. `.dumi/*` 不是仓库通用的 TS 路径别名，避免继续误导 review agent 给出错误建议。

本次改动仅涉及说明文档，不影响运行时代码。

### 📝 更新日志

| 语言    | 更新描述 |
| ------- | -------- |
| 🇺🇸 英文 | No changelog required |
| 🇨🇳 中文 | 无需更新日志 |

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
