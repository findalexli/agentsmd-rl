# docs: Add prominent pre-PR checklist to enforce version bumps

Source: [23blocks-OS/ai-maestro#86](https://github.com/23blocks-OS/ai-maestro/pull/86)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Add highly visible "Pre-PR Checklist (MANDATORY)" section to CLAUDE.md
- Makes version bump requirement impossible to miss before creating PRs

## Changes
```
□ 1. BUMP VERSION: ./scripts/bump-version.sh patch
□ 2. BUILD PASSES: yarn build  
□ 3. COMMIT version bump with your changes
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
