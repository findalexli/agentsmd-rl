# feat: add CLAUDE.md -> AGENTS.md symlink

Source: [OpenAgentsInc/openagents#1341](https://github.com/OpenAgentsInc/openagents/pull/1341)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

- Create CLAUDE.md as symbolic link pointing to AGENTS.md
- Both files now reference the same content
- Enables CLAUDE.md access while maintaining single source of truth

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Added new documentation file to the repository for reference.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
