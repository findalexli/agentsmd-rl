# feat: enhance linear skill with image extraction and in-progress status

Source: [lobehub/lobe-chat#13629](https://github.com/lobehub/lobehub/pull/13629)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/linear/SKILL.md`

## What to add / change

## Summary

- Add `extract_images` step to read image content from Linear issues for full context
- Add "Mark as In Progress" step to update issue status when starting work

## Test plan

- [ ] Verify skill triggers correctly on Linear issue references

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
