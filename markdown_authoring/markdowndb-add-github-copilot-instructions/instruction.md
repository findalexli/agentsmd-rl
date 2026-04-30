# Add GitHub Copilot instructions

Source: [flowershow/markdowndb#137](https://github.com/flowershow/markdowndb/pull/137)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds `.github/copilot-instructions.md` to provide context for GitHub Copilot when assisting with this codebase.

## Content

- **Architecture**: Data flow from markdown → remark AST → TypeScript objects → SQLite/JSON
- **Stack**: TypeScript (ES modules), Node.js, SQLite (Knex), Jest, remark ecosystem, Zod
- **Structure**: Core library in `src/lib/`, tests in `src/tests/`, CLI in `src/bin/`
- **Conventions**: 
  - ES modules with `.js` extensions in imports (TypeScript resolves to `.ts`)
  - Jest globals injected automatically (no explicit imports needed)
  - Schema classes define database tables
  - Separation of parsing logic from database operations
- **Key patterns**: Computed fields, URL path resolution, file watching, frontmatter/tag/link extraction
- **Development**: Build commands, test structure, configuration via `markdowndb.config.js`

This enables Copilot to generate code that matches existing patterns, particularly around ES module imports, Jest test structure, and the library's architectural separation of concerns.

<!-- START COPILOT ORIGINAL PROMPT -->



<details>

<summary>Original prompt</summary>

> 
> ----
> 
> *This section details on the original issue you should resolve*
> 
> <issue_title>✨ Set up Copilot instructions</issue_title>
> <issue_description>Configure instructions for this repository as documented in [Best practices for Copilot coding agent in your repository](https://gh.io/copilot-coding-agent-tips).
> 
> <Onboard this repo></issue_descripti

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
