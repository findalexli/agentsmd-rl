# feat: add CLAUDE.md files for Python and TypeScript libraries

Source: [mcp-use/mcp-use#775](https://github.com/mcp-use/mcp-use/pull/775)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `libraries/python/CLAUDE.md`
- `libraries/typescript/CLAUDE.md`

## What to add / change

- Introduced CLAUDE.md files for both the Python and TypeScript implementations of the mcp-use framework, providing comprehensive guidance on project structure, testing standards, and development workflows.
- The root CLAUDE.md outlines critical workflows for non-trivial tasks, testing requirements, and documentation standards.
- Each language-specific file emphasizes the importance of tests, integration strategies, and post-implementation checklists to ensure code quality and maintainability.


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Added comprehensive project context documentation for the mcp-use monorepo, including workflow guidance, testing standards, development commands, and architecture notes
  * Expanded Python library documentation with development setup, code quality standards, testing requirements, and post-implementation checklists
  * Added TypeScript library documentation covering package structure, coding standards, testing guidelines, workspace commands, and operational considerations

<sub>✏️ Tip: You can customize this high-level summary in your review settings.</sub>

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
