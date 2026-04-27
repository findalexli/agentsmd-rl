# chore(pr-automation): include matched critical path files in review comment

Source: [iOfficeAI/AionUi#1994](https://github.com/iOfficeAI/AionUi/pull/1994)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/pr-automation/SKILL.md`
- `.claude/skills/pr-review/SKILL.md`

## What to add / change

## Summary

- pr-review 的 `automation-result` 块新增 `CRITICAL_PATH_FILES` 字段，列出命中 `CRITICAL_PATH_PATTERN` 的具体文件
- pr-automation 的 APPROVED + NEEDS_HUMAN_REVIEW 评论中追加 📂 命中核心路径的文件列表
- 所有早退出路径（CI_NOT_READY / CI_FAILED）同步加上 `CRITICAL_PATH_FILES: (none)` 保持格式一致

## Test plan

- [ ] 对含有 `docs/` 改动的 PR 运行 `/pr-review --automation`，确认 `CRITICAL_PATH_FILES` 正确列出匹配文件
- [ ] 对不含核心路径改动的 PR 运行，确认 `CRITICAL_PATH_FILES: (none)`
- [ ] 验证 pr-automation 评论中正确显示文件列表

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
