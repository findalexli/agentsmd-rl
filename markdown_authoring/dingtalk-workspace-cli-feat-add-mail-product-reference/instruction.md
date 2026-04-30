# feat: add mail product reference doc and register in SKILL.md

Source: [DingTalk-Real-AI/dingtalk-workspace-cli#167](https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli/pull/167)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/SKILL.md`
- `skills/references/products/mail.md`

## What to add / change

## 变更内容

### 新增 `skills/references/products/mail.md`
- 邮箱产品命令参考文档，覆盖 4 个子命令：
  - `dws mail mailbox list` — 查询可用邮箱地址
  - `dws mail message search` — 搜索邮件 (KQL 语法)
  - `dws mail message get` — 查看邮件完整内容
  - `dws mail message send` — 发送邮件
- 包含 KQL 查询字段说明（含正确/错误示例）、翻页机制、意图判断、核心工作流、上下文传递表

### 修改 `skills/SKILL.md`
- frontmatter description 补充「邮箱」和「收发邮件」
- 产品总览表新增 `mail` 行
- 意图判断决策树新增 `用户提到邮箱/邮件/发邮件/收邮件/搜邮件/查邮件 → mail`

### 参数准确性
- `--size` 标注为必填（与 `dws schema` 的 required 字段一致）
- `--body` 补充 Markdown 格式说明（与 schema description 一致）
- 别名 `--limit`/`--page-size`/`--sender` 均经实测验证可用

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
