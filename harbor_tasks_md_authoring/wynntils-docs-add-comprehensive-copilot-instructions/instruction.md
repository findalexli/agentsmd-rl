# docs: add comprehensive Copilot instructions for repository onboarding

Source: [Wynntils/Wynntils#3584](https://github.com/Wynntils/Wynntils/pull/3584)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Overview

This PR adds a comprehensive `.github/copilot-instructions.md` file to onboard the Wynntils repository for efficient use with GitHub Copilot coding agents. This is a one-time setup that will significantly improve the quality and speed of AI-assisted contributions by providing essential context that agents would otherwise need to discover through extensive exploration.

## What This Adds

A **264-line, ~11KB instruction file** (approximately 1.5-2 pages) that documents:

### Critical Build Information
- **Java 21 requirement** - Emphasized as mandatory to prevent build failures
- Complete build command sequences with proper flags (`./gradlew buildDependents -x spotlessCheck -x test`)
- Testing commands with stacktrace and info flags
- Expected timing (2-5 minutes for clean builds)
- 5-step CI workflow that matches GitHub Actions exactly

### Code Quality Requirements
- **Spotless formatting** - Commands for `spotlessCheck` and `spotlessApply` with emphasis on running before commits
- All 6 code style rules from CONTRIBUTING.md (braces, fields, imports, annotations, method organization, comments)
- Custom Spotless rules including non-auto-fixable restrictions (no wildcard imports, no IntelliJ annotations)
- **Conventional Commits requirement** for PR titles (critical for release logs and auto-build)

### Repository Architecture
- Multi-module structure (common/fabric/neoforge) with purpose of each module
- Detailed source code organization mapping across 100+ packa

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
