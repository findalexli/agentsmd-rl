# docs: update CLAUDE.md

Source: [Nagi-ovo/gemini-voyager#66](https://github.com/Nagi-ovo/gemini-voyager/pull/66)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

- Update version from 0.9.2 to 0.9.5
- Add sidebar width adjustment feature documentation
- Add auto-backup service with File System API documentation
- Update storage keys to include geminiSidebarWidth and gvBackupConfig
- Add backup service usage examples and best practices
- Update changelog with v0.9.3, v0.9.4, and v0.9.5 changes
- Update repository structure to include new directories
- Add backup service to core source files reference

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
