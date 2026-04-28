# docs: add GitHub Copilot instructions and expand AGENTS.md

Source: [igraph/rigraph#2400](https://github.com/igraph/rigraph/pull/2400)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`
- `AGENTS.md`

## What to add / change

Adds `.github/copilot-instructions.md` to configure GitHub Copilot (Desktop and GHA) with repository-specific guidelines and expands `AGENTS.md` with comprehensive development guidelines for AI agents.

## Changes Made

### `.github/copilot-instructions.md` (35 lines)

Focused Copilot-specific instructions:

- **Code generation preferences**: igraph-specific naming conventions (maximal vs maximum in graph theory), tidyverse style guide, explicit package prefixes, test file alignment
- **Documentation generation**: roxygen2 with Markdown syntax, one sentence per line formatting, `@cdocs` tags for C library references
- **Files to avoid modifying**: Generated files (`src/rinterface.c`, `R/aaa-auto.R`) with update commands
- **Common commands**: Quick reference for Copilot Chat (formatting, testing, documentation, development)
- **Reference to AGENTS.md**: Directs to comprehensive development guidelines and AI agent workflows

### `AGENTS.md` (113 lines)

Expanded with comprehensive AI agent development guidelines:

- **Project overview**: Description of igraph as an R package for network analysis
- **Key technologies**: R, C/C++, testthat, roxygen2, air formatter, build system
- **Development setup**: Installation, dependencies, building, and testing instructions
- **Code style and documentation**: Detailed conventions for PRs, commits, comments, R code, documentation, and naming
- **File structure**: Test file organization and generated files handling
- **Testing guidelines**:

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
