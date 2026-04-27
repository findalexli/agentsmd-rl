# feat(engineering): add code-tour skill

Source: [alirezarezvani/claude-skills#476](https://github.com/alirezarezvani/claude-skills/pull/476)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `engineering/code-tour/SKILL.md`

## What to add / change

## Summary
- What: Add `engineering/code-tour/SKILL.md` — a skill for creating CodeTour .tour files with persona-targeted walkthroughs
- Why: Enables AI agents to generate structured code walkthroughs linked to real files and line numbers, supporting 20 developer personas and all CodeTour step types

## Checklist
- [x] Targets dev branch
- [x] SKILL.md frontmatter: name + description only
- [x] Under 500 lines
- [x] Anti-patterns section included
- [x] Cross-references to related skills included
- [x] No modifications to `.codex/`, `.gemini/`, `marketplace.json`, or index files

Full tooling: [code-tour](https://github.com/vaddisrinivas/code-tour)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
