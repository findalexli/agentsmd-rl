# feat(docs): Add AGENTS.md symlink for agents.md compatibility

Source: [yamadashy/repomix#832](https://github.com/yamadashy/repomix/pull/832)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Add AGENTS.md as a symlink to support the agents.md format specification.

## Summary
- Created AGENTS.md as a symlink to `.agents/rules/base.md`  
- Enables compatibility with the agents.md standard used by 20k+ open-source projects
- Allows AI coding tools to automatically discover project-specific instructions
- Maintains synchronization with existing CLAUDE.md setup

## Benefits
- Support for multiple AI coding agent formats (Cursor, GitHub Copilot, Gemini CLI, etc.)
- No duplication - both files reference the same source
- Follows the open agents.md format for predictable agent guidance

## Checklist
- [x] Run `npm run test`
- [x] Run `npm run lint`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
