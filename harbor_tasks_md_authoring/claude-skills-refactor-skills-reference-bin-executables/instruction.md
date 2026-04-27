# refactor: skills reference bin/ executables

Source: [jezweb/claude-skills#73](https://github.com/jezweb/claude-skills/pull/73)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/design-assets/skills/image-processing/SKILL.md`
- `plugins/frontend/skills/product-showcase/SKILL.md`

## What to add / change

## Summary
Updates product-showcase and image-processing SKILL.md files to use the new `bin/` executables as their primary approach instead of generating scripts at runtime.

## Changes
- **product-showcase**: Screenshot capture section now uses `capture-screenshots` CLI with concrete examples for multi-page, dark mode, mobile, and authenticated captures
- **image-processing**: Added quick reference section at top for `img-process` CLI, updated all workflow examples to use CLI commands

## Philosophy
`bin/` executables are now the default for standard operations. Custom Pillow/Playwright scripts are the fallback for complex or unusual cases. This reduces token cost, eliminates prompt drift, and gives consistent results.

## Validation
- Both skills pass `skill-lint` (491 and 217 lines respectively)
- No breaking changes — skills still work without the executables, they just won't have the CLI shortcut

Closes #70

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
