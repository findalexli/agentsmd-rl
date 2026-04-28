# Update SKILL.md with missing commands

Source: [yucchiy/UniCli#4](https://github.com/yucchiy/UniCli/pull/4)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude-plugin/unicli/skills/unicli/SKILL.md`
- `CLAUDE.md`

## What to add / change

## Summary
- Add missing commands to SKILL.md built-in commands table: `GameObject.AddComponent`, `GameObject.RemoveComponent`, `Prefab.*` (5 commands), `AssetDatabase.Delete`
- Add workflow examples for component management, prefab operations, and asset deletion

## Test plan
- [x] Verify SKILL.md content matches README.md command list

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
