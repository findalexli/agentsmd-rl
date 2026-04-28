# doc: Add CLAUDE.md for AI coding agent instructions

Source: [wvlet/airframe#4030](https://github.com/wvlet/airframe/pull/4030)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Add comprehensive CLAUDE.md file to provide guidance for AI coding agents
- Document build commands, testing instructions, and development guidelines
- Improve AI agent effectiveness when working with the Airframe codebase

## Description
This PR introduces a CLAUDE.md file that serves as a comprehensive guide for AI coding agents (Claude Code, GitHub Copilot) working with the Airframe project. The file consolidates essential information about the project structure, build system, testing framework, and development practices.

### Key Content Added:
- **Build System Instructions**: Complete sbt commands for compilation, testing, and cross-platform builds
- **Testing Framework Guide**: AirSpec usage with specific test running patterns
- **Project Structure Overview**: Module organization and naming conventions
- **Development Guidelines**: Code style, dependency management, and Scala version compatibility
- **Git Workflow**: Branch creation, commit message format, and PR process
- **Common Tasks**: Binary compatibility checks, benchmarking, and publishing

This documentation will help AI agents:
- Navigate the multi-module project structure efficiently
- Execute build and test commands correctly
- Follow project conventions and best practices
- Contribute code that aligns with existing patterns

The content incorporates existing guidelines from `.github/copilot-instructions.md` while adding comprehensive build and testing instructions specific to the Airframe archi

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
