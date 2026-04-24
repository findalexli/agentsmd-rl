# Fix incorrect commands in AGENTS.md and update related examples

## Problem

The `AGENTS.md` file at the repository root contains outdated instructions that would cause agents (and developers) to use wrong commands:

1. The test command is missing a required subcommand — running `pnpm test <file>` produces an error because the CLI expects a `run` subcommand. The current instruction line is broken and needs to use the correct pnpm test syntax.

2. The scratchpad runner command uses `node` directly, but `node` cannot execute TypeScript files. The scratchpad directory contains `.ts` files which require a TypeScript execution tool.

3. There is no documentation about where to find the effect v4 source for reference when working with the new API patterns.

Additionally, several JSDoc `@example` code blocks across the AI package (`packages/ai/ai/src/`) use import patterns that are incompatible with the current module structure. The examples reference barrel imports like `import { Effect } from "effect"` which are discouraged, and some examples reference services incorrectly (e.g., `yield* Chat` instead of the full service accessor pattern). These examples appear in the AI package source files and in the main Schema.ts file.

The ESLint configuration needs to ignore certain development directories (`.repos/` and `.lalph/`) that are used for local clones of related repositories, as they should not be linted as part of this codebase.

Finally, the `packages/sql/tsconfig.test.json` file is missing an output directory configuration for test builds.

## Expected Behavior

- `AGENTS.md` should have correct, working commands for running tests and executing scratchpad files.
- `AGENTS.md` should document where to find the effect v4 source code — include a section starting with `## Learning about` that mentions `v4` and references the path `.repos/effect-v4`.
- JSDoc examples should use `effect/Effect` module import pattern instead of barrel imports.
- `packages/ai/ai/src/Chat.ts` JSDoc example that references the Chat service should use the fully-qualified service accessor pattern.
- `packages/ai/ai/src/EmbeddingModel.ts` JSDoc example should include a `cosineSimilarity` helper function and use the proper EmbeddingModel service accessor.
- `packages/ai/ai/src/LanguageModel.ts` JSDoc example should use the proper LanguageModel service accessor.
- `packages/ai/ai/src/Telemetry.ts` JSDoc example with `SpanTransformer` should reference the correct property of the options object (not `options.model`).
- `packages/effect/src/Schema.ts` JSDoc example should reference `JsonNumber` correctly within the example scope.
- `packages/sql/tsconfig.test.json` should specify `outDir` in compilerOptions.
- ESLint configuration should ignore the `.repos/` and `.lalph/` directories.
- `.gitignore` should include `.repos/` entry.

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

## Verification

After making changes, verify that:
- `pnpm lint` passes on the codebase
- `pnpm docgen` can process the JSDoc examples without errors
- The repository's test suite continues to pass
