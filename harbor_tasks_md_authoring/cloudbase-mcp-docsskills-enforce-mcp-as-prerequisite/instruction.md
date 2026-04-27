# docs(skills): ⚠️ enforce MCP as prerequisite in CloudBase skill

Source: [TencentCloudBase/CloudBase-MCP#404](https://github.com/TencentCloudBase/CloudBase-MCP/pull/404)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `config/source/guideline/cloudbase/SKILL.md`

## What to add / change

## Summary
- Promote CloudBase MCP from "recommended" to **required** prerequisite
- Separate configuration into two approaches: **IDE Native MCP** (ToolSearch check) and **mcporter CLI** (check/configure/verify steps)
- Use `config/mcporter.json` with `description` + `lifecycle: keep-alive` for mcporter configuration
- Remove redundant duplicated content

## Test plan
- [ ] Verify SKILL.md renders correctly
- [ ] Confirm no duplicated JSON config blocks
- [ ] Run `node scripts/build-compat-config.mjs` to verify compatibility artifacts

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
