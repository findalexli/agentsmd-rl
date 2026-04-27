# docs: update CLAUDE.md with development guidelines

Source: [xpzouying/xiaohongshu-mcp#46](https://github.com/xpzouying/xiaohongshu-mcp/pull/46)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

- Add requirements for formatting Go source files after modifications
- Specify the need to delete unnecessary scripts and build files generated during testing
- Introduce a branching policy for feature changes
- Establish a rule against pushing to remote without prior approval
- Outline the review process including local and remote PR reviews

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
