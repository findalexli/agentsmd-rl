# Add GitHub Copilot instructions with references to existing development guidelines

Source: [mattgodbolt/jsbeeb#519](https://github.com/mattgodbolt/jsbeeb/pull/519)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This PR adds comprehensive GitHub Copilot coding agent instructions to help developers work effectively with the jsbeeb BBC Micro emulator codebase. The instructions complement the existing CLAUDE.md development guidelines by providing validated commands, timing expectations, and manual testing scenarios.

## Key Features

**References Existing Guidelines**: The instructions properly reference CLAUDE.md for general development practices (build commands, code style, test organization, architecture patterns, and git workflow) rather than duplicating content.

**Validated Command Timings**: All build and test commands have been executed and timed to provide accurate expectations:
- `npm install`: 13 seconds (Node.js 22 required)  
- `npm run test:cpu`: 66 seconds (NEVER CANCEL - critical for emulation accuracy)
- `npm run test:integration`: 18 seconds (requires git submodules)
- `npm run build`: 4 seconds

**Critical "NEVER CANCEL" Warnings**: The CPU tests take over a minute and are essential for validating emulation accuracy against real BBC Micro hardware. The instructions include explicit timeout requirements (120+ seconds) to prevent premature cancellation.

**Manual Validation Scenarios**: Complete step-by-step procedures for testing the emulator functionality:
- Development server startup and verification
- Emulator boot sequence validation (ROM loading, disc mounting)
- Interface testing (play/pause controls, menu functionality)
- Performance verification (virtual MHz co

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
