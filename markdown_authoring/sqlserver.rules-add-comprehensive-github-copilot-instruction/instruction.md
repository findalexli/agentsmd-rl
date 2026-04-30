# Add comprehensive GitHub Copilot instructions for SqlServer.Rules repository

Source: [ErikEJ/SqlServer.Rules#307](https://github.com/ErikEJ/SqlServer.Rules/pull/307)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Creating comprehensive .github/copilot-instructions.md file for SqlServer.Rules repository.

## Plan:
- [x] Explore repository structure and understand codebase
- [x] Test and time .NET restore command (~25 seconds)
- [x] Test and time build command (~26 seconds) 
- [x] Test and time test execution (~27 seconds)
- [x] Test CLI tool build and functionality
- [x] Validate actual functionality by running CLI against sample files
- [x] Test Visual Studio extension build (Linux limitation documented)
- [x] Document exact commands, timeouts, and validation scenarios
- [x] Create comprehensive copilot-instructions.md file
- [x] Validate all instructions work end-to-end
- [x] Revert unintended changes to docs folder files

## Key findings and validations:
- **Build times measured**: Restore ~25s, Build ~26s, Tests ~27s
- **CLI functionality verified**: Successfully analyzes .sql and .dacpac files
- **VSIX limitation documented**: Cannot build on Linux (requires Windows Desktop frameworks)
- **Complete build cycle validated**: Full clean -> restore -> build -> test cycle successful
- **Comprehensive testing**: Validated CLI produces expected 7 warnings for simple.sql
- **Docs reverted**: Removed unintended changes to documentation files in docs folder

## Created instructions include:
- Exact build commands with appropriate timeouts (60-90 seconds)
- NEVER CANCEL warnings for all long-running operations
- Manual validation requirements with specific test scenarios
- Complete project s

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
