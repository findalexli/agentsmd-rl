# Fix incorrect commands in AGENTS.md and update related examples

## Problem

The `AGENTS.md` file at the repository root contains outdated instructions that would cause agents (and developers) to use wrong commands:

1. The test command is missing a required subcommand — running `pnpm test <file>` without it does not work as expected.
2. The scratchpad runner command uses `node` directly, but `node` cannot execute TypeScript files. The scratchpad directory is for `.ts` files.
3. There is no documentation about where to find the effect v4 source for reference.

Additionally, several JSDoc `@example` code blocks across the AI package (`packages/ai/ai/src/`) use outdated import patterns that no longer match the current module structure. The `packages/effect/src/Schema.ts` file also has a JSDoc example referencing a shorthand alias that isn't in scope.

The ESLint configuration should be updated to ignore certain development directories that are used for local clones of related repositories.

## Expected Behavior

- `AGENTS.md` should have correct, working commands for running tests and executing scratchpad files.
- `AGENTS.md` should document where to find the effect v4 source code.
- JSDoc examples should use the correct module import paths.
- `packages/sql/tsconfig.test.json` should specify an output directory for test builds.
- ESLint configuration should ignore development-only directories.

## Files to Look At

- `AGENTS.md` — agent instructions with commands that need fixing
- `eslint.config.mjs` — ESLint configuration with ignore patterns
- `packages/ai/ai/src/AiError.ts` — JSDoc examples with import issues
- `packages/ai/ai/src/Chat.ts` — JSDoc examples with import and service access issues
- `packages/ai/ai/src/EmbeddingModel.ts` — JSDoc examples with import and service access issues
- `packages/ai/ai/src/LanguageModel.ts` — JSDoc examples with import and service access issues
- `packages/ai/ai/src/Telemetry.ts` — JSDoc examples with import issues
- `packages/effect/src/Schema.ts` — JSDoc example using out-of-scope alias
- `packages/sql/tsconfig.test.json` — missing output directory configuration
