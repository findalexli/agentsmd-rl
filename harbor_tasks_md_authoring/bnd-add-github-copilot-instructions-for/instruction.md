# Add GitHub Copilot instructions for bnd repository

Source: [bndtools/bnd#6857](https://github.com/bndtools/bnd/pull/6857)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

I asked copilote here to create a GitHub Copilot Instructions for bnd/bndtools what allows copilote to better work with the bnd repository:
- https://github.com/laeubi/bnd/pull/4

I fetched the commit, squashed into one and submit it here for further considerations.

This PR adds comprehensive GitHub Copilot instructions to help AI-assisted development in the bnd/bndtools repository, following the best practices documented at https://gh.io/copilot-coding-agent-tips.

## What's Added

Created `.github/copilot-instructions.md` with repository-specific guidance covering:

### Build & Development Environment
- Build system requirements (Java 17, Gradle/Maven wrappers)
- Complete build commands for workspace projects, Gradle plugins, and Maven plugins
- Testing commands including running specific test classes and methods

### Code Organization & Standards
- Project structure overview (bndlib, plugins, Eclipse components)
- Module naming conventions (`biz.aQute.*` and `bndtools.*` patterns)
- Testing best practices using soft assertions and temporary directory annotations
- Java coding conventions and commit message format

### OSGi & API Compatibility
- Backward compatibility guidelines
- Semantic versioning requirements
- Baselining tool usage

### Eclipse Plugin Development
- Instructions for launching Bndtools from Eclipse
- Guidelines for adding error/warning markers
- ExtensionFacade usage patterns

### Contribution Workflow
- Git triangular w

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
