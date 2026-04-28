# Set up GitHub Copilot instructions for repository

Source: [o1-labs/mina-rust#1424](https://github.com/o1-labs/mina-rust/pull/1424)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This PR implements GitHub Copilot instructions to help coding agents understand and work effectively with the Mina Rust codebase.

## What was added

Created `.github/copilot-instructions.md` with comprehensive guidance covering:

- **Project overview** - Mina protocol context and Redux-style state machine architecture
- **Architecture patterns** - State/Actions/Reducers flow, file organization conventions, and defensive programming practices
- **Development workflow** - Pre-change requirements, formatting procedures, and testing commands
- **Code style guidelines** - Rust conventions, commit message standards, and documentation formatting
- **Common tasks** - Feature development, debugging approaches, and dependency management

## Key highlights

The instructions emphasize critical repository requirements:

- Mandatory trailing whitespace management (`make fix-trailing-whitespace`)
- Strict formatting standards for Rust, TOML, and markdown files
- Commit message rules (no AI co-authors, no emojis, 80-character wrapping)
- Understanding of the Redux architecture central to this blockchain implementation

## Implementation approach

The content was carefully adapted from the existing comprehensive `CLAUDE.md` file, ensuring consistency with established development practices while being specifically tailored for GitHub Copilot agents.

All formatting checks pass and the file follows repository markdown standards.

Fixes #1423.

<!-- START COPILOT CODING AGENT TIPS -->
---

💡 Yo

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
