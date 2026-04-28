# chore(infra): Creation of AGENTS.md for Rspress Project

Source: [web-infra-dev/rspress#2608](https://github.com/web-infra-dev/rspress/pull/2608)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This PR adds an `AGENTS.md` file to the Rspress project, providing comprehensive repository guidelines for contributors and AI agents working with the codebase.

The documentation is based on the reference structure from [Rslib's AGENTS.md](https://github.com/web-infra-dev/rslib/blob/main/AGENTS.md) but specifically tailored for Rspress's static site generator architecture and development workflow.

## What's included

The `AGENTS.md` file covers:

- **Project structure & module organization**: Monorepo layout using `pnpm` + `Nx`, package organization (`core`, `theme-default`, `plugin-*`, `create-rspress`), and test structure
- **Build, test, and development commands**: Complete workflow including installation, building, development server, linting, formatting, and testing procedures
- **Coding style & naming conventions**: TypeScript + ESM standards, Biome/Prettier configuration, and file naming requirements
- **Testing guidelines**: Unit testing with `vitest`, E2E testing with `@playwright/test`, and test organization patterns
- **Commit & pull request guidelines**: Conventional commits format and changeset requirements
- **Architecture overview**: Core CLI functionality, theme system, plugin ecosystem, and scaffolding tools
- **Security & configuration tips**: Build artifact management and CI configuration best practices

This documentation will help new contributors quickly understand the project structure and development workflow, while also providing AI agents with the 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
