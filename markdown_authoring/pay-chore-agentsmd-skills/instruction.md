# chore: 更新 AGENTS.md 和 skills 文件

Source: [yansongda/pay#1150](https://github.com/yansongda/pay/pull/1150)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/container-dev/SKILL.md`
- `.agents/skills/pr-review-provider/SKILL.md`
- `AGENTS.md`

## What to add / change

## Summary

- 更新 `AGENTS.md`：删除不存在的 `Functions.php`，改为 Trait 方法；更新核心架构描述；添加 Stripe 支持
- 优化 `pr-review-provider/SKILL.md`：删除重复内容，整合 GitHub Copilot 行内评论建议，按 Phase 组织
- 优化 `container-dev/SKILL.md`：添加快速参考表格，明确 cs-fix 仅检查不修复，添加 Web 命令

## Changes

### AGENTS.md
- STRUCTURE 删除 `Functions.php`（已不存在）
- 核心架构改为通用骨架描述，避免固定管道误报
- 命名约定添加 Trait 格式 `{Provider}Trait.php`
- "辅助函数"改为"Trait 方法"，更新方法名称
- 安全表格添加 Stripe 和 Trait 方法列
- 新增 Provider 步骤第 5 步改为 Trait 方法

### pr-review-provider/SKILL.md
- 删除第310-400行重复旧内容（与新 Phase 结构完全重复）
- 整合 GitHub Copilot 4 条行内评论建议：
  1. 插件管道改为通用骨架 + Provider 差异表格
  2. `Functions.php` 改为 Trait 方法
  3. `array_filter` 改为推荐 `filter_params()`
  4. 数组回调验签说明更新（仅含 headers+body 可验签）
- 保留 Phase 结构和 Review 报告模板

### container-dev/SKILL.md
- 添加快速参考表格
- 明确 `composer cs-fix` 仅检查不修复
- 添加 Web 文档开发命令（pnpm web:dev/web:build）
- 简化命令模板结构

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
