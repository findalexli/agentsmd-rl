# ✨ Set up Copilot instructions for Eclipse Tycho repository

Source: [eclipse-tycho/tycho#5418](https://github.com/eclipse-tycho/tycho/pull/5418)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This PR adds comprehensive GitHub Copilot instructions to help the coding agent better understand and work with the Eclipse Tycho codebase.

## Changes

Created `.github/copilot-instructions.md` with detailed guidance covering:

- **Project Overview**: Eclipse Tycho's purpose as a Maven plugin system for building Eclipse/OSGi artifacts
- **Technology Stack**: Java 17+, Maven 3.9.9+, Eclipse Platform (p2, Equinox, OSGi), JDT, and BND
- **Development Environment**: Prerequisites, build commands, and setup procedures
- **Code Guidelines**: Java code style, project structure, and common patterns
- **Commit Message Format**: Required `Bug: <number>` prefix for Eclipse genie bot integration
- **Testing Procedures**: 
  - Unit test conventions in each module
  - Integration test workflow in `tycho-its/` 
  - Test naming conventions and patterns
- **Pull Request Guidelines**: Branching from master, naming conventions
- **Debugging**: Steps to debug Tycho plugins in Eclipse or via command line
- **Common Patterns**: P2 integration, OSGi bundles, Maven Mojos
- **Eclipse Foundation Requirements**: ECA, EPL-2.0 license, IP policy
- **Resources**: Links to documentation, wiki, discussions, and issue tracker

## Benefits

With these instructions, GitHub Copilot will:
- Generate commit messages in the correct format with `Bug:` prefix
- Suggest code that follows project conventions
- Understand the Maven multi-module structure
- Know how to write integration tests following Tycho patterns
-

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
