# feat: enhance document-fixer for maximized AI execution precision

Source: [shinpr/ai-coding-project-boilerplate#9](https://github.com/shinpr/ai-coding-project-boilerplate/pull/9)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/agents/document-fixer.md`

## What to add / change

- Restructure workflow to move consistency validation to final phase
- Implement two-stage modification process:
  - Stage 1: Content improvements based on review feedback
  - Stage 2: AI interpretation optimization
- Add clear guidelines for ambiguity elimination:
  - Replace vague expressions with specific conditions
  - Clarify all references and pronouns
  - Optimize structure for AI parsing
- Enhance error handling with phase-specific resolution rules
- Update output format to reflect AI precision improvements

This ensures final documents are optimized for AI interpretation while maintaining content quality through specialized review phases.

🤖 Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
