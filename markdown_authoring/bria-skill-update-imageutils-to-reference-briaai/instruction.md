# Update image-utils to reference bria-ai skill

Source: [Bria-AI/bria-skill#24](https://github.com/Bria-AI/bria-skill/pull/24)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/image-utils/SKILL.md`

## What to add / change

## Summary
- Replace fictional `BriaClient` import with actual Bria API call matching the bria-ai skill docs
- Add direct link to the bria-ai skill (`../bria-ai/SKILL.md`)
- Include `sync: True` for direct response handling

## Test plan
- [ ] Verify the link to bria-ai skill resolves correctly
- [ ] Confirm the API example matches the bria-ai skill's documented endpoints

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
