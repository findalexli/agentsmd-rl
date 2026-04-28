# feat: move .github/copilot-instructions.md to AGENTS.md

Source: [deepmodeling/dpdata#898](https://github.com/deepmodeling/dpdata/pull/898)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This PR moves the AI agent instructions from `.github/copilot-instructions.md` to `AGENTS.md` in the repository root, following the new GitHub standard for agent custom instructions.

## Background

According to the [GitHub changelog](https://github.blog/changelog/2025-08-28-copilot-coding-agent-now-supports-agents-md-custom-instructions/), `AGENTS.md` is now the commonly used location for custom instructions that different AI agents can reference. This change improves compatibility across various AI coding assistants.

## Changes

- **Moved** `.github/copilot-instructions.md` → `AGENTS.md`
- **No content changes** - the comprehensive dpdata development instructions remain identical
- **No functional impact** on the dpdata codebase or CLI functionality

The file contains detailed instructions for AI agents working on dpdata, including:
- Repository bootstrap and installation procedures
- Testing and linting workflows  
- Build and documentation processes
- Troubleshooting guides
- Commit and PR guidelines

## Verification

- ✅ dpdata CLI functionality remains intact (`dpdata --version`, `dpdata --help`)
- ✅ All CLI tests continue to pass (7/7 tests successful)
- ✅ File content preserved exactly (149 lines, 7,357 bytes)

Fixes #897.

<!-- START COPILOT CODING AGENT TIPS -->
---

💬 Share your feedback on Copilot coding agent for the chance to win a $200 gift card! Click [here](https://survey3.medallia.com/?EAHeSx-AP01bZqG0Ld9QLQ) to start the survey.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
