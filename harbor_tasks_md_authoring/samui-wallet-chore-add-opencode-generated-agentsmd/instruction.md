# chore: add opencode generated agents.md

Source: [samui-build/samui-wallet#102](https://github.com/samui-build/samui-wallet/pull/102)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!-- ELLIPSIS_HIDDEN -->



> [!IMPORTANT]
> Adds `AGENTS.md` with build, lint, type check, test, format commands, and code style guidelines for Samui Wallet.
> 
>   - **New File**: Adds `AGENTS.md` with guidelines for Samui Wallet.
>   - **Commands**:
>     - Build: `pnpm build`
>     - Lint: `pnpm lint` / `pnpm lint:fix`
>     - Type Check: `pnpm check-types`
>     - Test All: `pnpm test` / `pnpm test:watch`
>     - Single Test: `vitest run <path/to/test.ts>`
>     - Format: `pnpm format` / `pnpm format:check`
>   - **Code Style**:
>     - TypeScript: Strict mode, consistent type definitions/imports
>     - Formatting: Prettier (single quotes, 120 width, no semicolons, trailing commas)
>     - Linting: ESLint with perfectionist (alphabetical imports/sorting)
>     - Naming: camelCase variables/functions, PascalCase types
>     - Error Handling: Use `tryCatch` from `@workspace/core`
>     - Testing: Vitest globals, jsdom env, ARRANGE/ACT/ASSERT pattern
>     - Imports: Type imports separate, alphabetical perfectionist sorting
> 
> <sup>This description was created by </sup>[<img alt="Ellipsis" src="https://img.shields.io/badge/Ellipsis-blue?color=175173">](https://www.ellipsis.dev?ref=samui-build%2Fsamui-wallet&utm_source=github&utm_medium=referral)<sup> for 577a7ba6d14eb2f5ba41c5a6c891118ab0ec36a4. You can [customize](https://app.ellipsis.dev/samui-build/settings/summaries) this summary. It will automatically update as commits are pushed.</sup>

<!-- ELLIPSIS_HIDDEN -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
