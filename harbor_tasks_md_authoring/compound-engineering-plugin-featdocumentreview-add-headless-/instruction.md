# feat(document-review): add headless mode for programmatic callers

Source: [EveryInc/compound-engineering-plugin#425](https://github.com/EveryInc/compound-engineering-plugin/pull/425)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/document-review/SKILL.md`

## What to add / change

## Summary

- Adds `mode:headless` support to document-review for programmatic callers (other skills, pipelines)
- In headless mode: `auto` fixes applied silently, `batch_confirm` + `present` findings returned as structured text with classifications intact — no interactive prompts
- Headless mode changes the interaction model, not the classification boundaries
- Interactive mode completely unchanged when `mode:headless` is not present

## Motivation

Other plugins (e.g., open-source-contributor) want to use document-review as a utility in their plan-creation pipelines. The current interactive flow (AskUserQuestion for batch confirms, present-tier findings) doesn't fit pipelines where the calling skill should handle remaining findings with domain-specific knowledge.

Headless mode enables a multi-tier auto-fix cascade:
1. **document-review** auto-fixes `auto` items (deterministic, same as interactive)
2. **document-review** returns `batch_confirm` + `present` findings as structured text with classifications
3. **Calling skill** resolves findings using its domain knowledge (e.g., maintainer preferences, repo conventions)
4. **User** handles only truly ambiguous items

## Changes

Single file: `plugins/compound-engineering/skills/document-review/SKILL.md`

- **Phase 0**: Detect `mode:headless` in skill arguments. `mode:*` tokens are flags, not file paths — stripped from arguments before the remainder is used as the document path.
- **Phase 1**: Headless mode requires a document 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
