# chore: Add llm cursor rules mdc

Source: [Workday/canvas-kit#3684](https://github.com/Workday/canvas-kit/pull/3684)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `modules/docs/llm/canvas-kit.mdc`

## What to add / change

## Summary

Fixes: https://github.com/Workday/canvas-kit/issues/3682

Adds a new `.mdc` (Markdown with Cursor rules) file to provide Canvas Kit best practices for developers using AI assistants like Cursor and Claude.

This file helps teams ensure consistent adherence to Canvas Kit patterns by providing:
- Token usage guidelines (system tokens, import patterns)
- Styling best practices (`createStyles`, `createStencil`, `cs` prop)
- Component patterns (compound components, controlled components)
- Accessibility guidelines (semantic HTML, ARIA, keyboard navigation)
- Theming guidelines (global vs scoped theming)
- Code style conventions

The content is derived from existing Canvas Kit documentation in `modules/docs/` and synthesized into a single, always-applied rule file.

## Release Category
Documentation

### Release Note
Added `modules/docs/llm/canvas-kit.mdc` - a Cursor/Claude rules file containing Canvas Kit best practices. Teams can add this to their `.cursor/rules/` directory to have AI assistants follow Canvas Kit conventions automatically.

---

## Checklist

- [x] MDX documentation adheres to Canvas Kit's [Documentation Guidelines](https://workday.github.io/canvas-kit/?path=/docs/guides-documentation-guidelines--docs)
- [ ] Label `ready for review` has been added to PR

## For the Reviewer

- [x] PR title is short and descriptive
- [x] PR summary describes the change (Fixes/Resolves linked correctly)
- [x] PR Release Notes describes a

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
