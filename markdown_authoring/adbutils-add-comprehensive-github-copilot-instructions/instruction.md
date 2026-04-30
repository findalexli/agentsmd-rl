# Add comprehensive GitHub Copilot instructions for adbutils development

Source: [openatx/adbutils#190](https://github.com/openatx/adbutils/pull/190)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This PR adds a comprehensive `.github/copilot-instructions.md` file that provides GitHub Copilot coding agents with complete guidance on how to work effectively with the adbutils codebase.

## Key Features

**Complete Bootstrap Process**: Step-by-step instructions for setting up the development environment from a fresh clone, including Python 3.8+ requirements, ADB tool installation, and dependency management.

**Validated Commands with Timing**: All commands have been tested and include actual timing measurements:
- Package installation: `pip install -e .` (~2 seconds)
- Unit tests: `pytest tests/` (16 tests, ~2 seconds)
- CLI operations: Most commands complete in <1 second

**Critical Safety Warnings**: Explicit "NEVER CANCEL" warnings for operations that can hang indefinitely, particularly E2E tests that require Android devices and may hang without them.

**Essential Validation Workflows**: Fast, reliable validation steps that work in any environment:
- Unit tests that always pass and run quickly
- Basic import and CLI functionality tests
- ADB server connectivity verification

**Repository Navigation**: Comprehensive mapping of key files, directories, and their purposes, plus common development workflows and troubleshooting guidance.

## Validation

All instructions have been thoroughly validated by following them step-by-step in a clean environment. Every command works as documented, and timing estimates are based on actual measurements. The instructions enable any devel

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
