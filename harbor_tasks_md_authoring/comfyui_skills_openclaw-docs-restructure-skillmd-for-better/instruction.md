# docs: restructure SKILL.md for better agent readability

Source: [HuangYuChuh/ComfyUI_Skills_OpenClaw#121](https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw/pull/121)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary

- 新增 **Quick Decision** 决策区块，agent 一眼定位该执行哪个操作
- 新增 **Core Concepts** 区块，简明解释 Skill ID / Schema / Server 概念
- **Command Reference** 补全 `upload`、`workflow import`、`history list/show` 命令
- 用 CLI `workflow import` 替代原来手动写 `workflow.json` + `schema.json` 的 Step 0
- 精简 JSON 返回值示例，压缩冗余描述（229 行 → 168 行，减少 27%）
- 保留全部核心逻辑：polling pattern、dependency check、双执行模式、troubleshooting

参考飞书 Lark CLI Skills 的"速查式"编写模式重构，提升信息密度和 agent 可读性。

## Test plan

- [ ] 验证 SKILL.md frontmatter metadata 格式正确
- [ ] 确认所有 CLI 命令在 Command Reference 表中可用
- [ ] 确认 Execution Flow 步骤完整无遗漏
- [ ] 验证 references/workflow-import.md 链接有效

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
