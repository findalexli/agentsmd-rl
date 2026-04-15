# Fix incorrect commands in AGENTS.md and update related examples

## Problem

The `AGENTS.md` file at the repository root contains outdated instructions that would cause agents (and developers) to use wrong commands:

1. The test command is missing a required subcommand — running `pnpm test <file>` without it does not work as expected. The correct command includes `run` as a subcommand.
2. The scratchpad runner command uses `node` directly, but `node` cannot execute TypeScript files. The scratchpad directory is for `.ts` files. You need to use a TypeScript executor like `tsx`.
3. There is no documentation about where to find the effect v4 source for reference.

Additionally, several JSDoc `@example` code blocks across the AI package (`packages/ai/ai/src/`) use outdated import patterns that no longer match the current module structure. The import pattern `import { Effect } from "effect"` should be updated to `import * as Effect from "effect/Effect"`. The `packages/effect/src/Schema.ts` file also has a JSDoc example referencing a shorthand alias that isn't in scope.

The ESLint configuration should be updated to ignore certain development directories that are used for local clones of related repositories.

## Expected Behavior

- `AGENTS.md` should have correct, working commands for running tests (including the `run` subcommand) and executing scratchpad files (using `tsx`, not `node`).
- `AGENTS.md` should document where to find the effect v4 source code — include a section starting with `## Learning about` that mentions `v4` and references the path `.repos/effect-v4`.
- JSDoc examples should use `import * as Effect from "effect/Effect"` pattern instead of `import { Effect } from "effect"`.
- `packages/ai/ai/src/Chat.ts` JSDoc example that uses `yield* Chat` should be updated to use the fully-qualified service accessor `yield* Chat.Chat`.
- `packages/ai/ai/src/EmbeddingModel.ts` JSDoc example should include a `cosineSimilarity` helper function and use `yield* EmbeddingModel.EmbeddingModel`.
- `packages/ai/ai/src/LanguageModel.ts` JSDoc example should use `yield* LanguageModel.LanguageModel`.
- `packages/ai/ai/src/Telemetry.ts` JSDoc example with `SpanTransformer` should use `options.response.length` (not `options.model`).
- `packages/effect/src/Schema.ts` JSDoc example using `S.JsonNumber` should be changed to `Schema.JsonNumber`.
- `packages/sql/tsconfig.test.json` should specify `outDir` as `"build/test"` in compilerOptions.
- ESLint configuration should ignore the `.repos/` and `.lalph/` directories (e.g., `**/.repos/**` and `**/.lalph/**` patterns).
- `.gitignore` should include `.repos/` entry.

## Files to Look At

- `AGENTS.md` — agent instructions with commands that need fixing
- `eslint.config.mjs` — ESLint configuration with ignore patterns (the `selector` property in the `no-restricted-syntax` rule should appear on its own line, and `packageNames` should be formatted as a single line array)
- `packages/ai/ai/src/AiError.ts` — JSDoc examples with import issues (uses `import * as Option from "effect/Option"` in HttpRequestError example)
- `packages/ai/ai/src/Chat.ts` — JSDoc examples with import and service access issues
- `packages/ai/ai/src/EmbeddingModel.ts` — JSDoc examples with import and service access issues
- `packages/ai/ai/src/LanguageModel.ts` — JSDoc examples with import and service access issues
- `packages/ai/ai/src/Telemetry.ts` — JSDoc examples with import issues
- `packages/effect/src/Schema.ts` — JSDoc example using out-of-scope alias
- `packages/sql/tsconfig.test.json` — missing output directory configuration