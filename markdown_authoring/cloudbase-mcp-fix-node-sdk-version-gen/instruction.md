# fix: node sdk version; gen image only in node sdk

Source: [TencentCloudBase/CloudBase-MCP#285](https://github.com/TencentCloudBase/CloudBase-MCP/pull/285)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `config/.claude/skills/ai-model-cloudbase/SKILL.md`
- `config/.cursor/rules/cloudbase-rules.mdc`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
