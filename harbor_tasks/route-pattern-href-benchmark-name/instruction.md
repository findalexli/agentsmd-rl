# Task: Dynamic Benchmark Name for href Benchmark

## Problem

The `packages/route-pattern/bench/href.bench.ts` benchmark file in the `@remix-run/route-pattern` package uses a hardcoded benchmark name `'bench'` for all vitest `bench()` calls.

This causes issues when using vitest's `--compare` flag to compare benchmark results between branches. When all benchmark names across all `describe` blocks are the literal string `'bench'`, vitest cannot distinguish results from one branch vs. another in the comparison output.

## What Needs to Change

Modify `href.bench.ts` so the benchmark name is dynamically derived from the current git branch and short commit hash. The format should be `<branch> (<short commit>)` — for example `main (a2245ea)`. The short commit should be at least 7 hex characters.

When git commands fail (e.g., the file is run outside a git repository), the benchmark name must fall back to `'bench'`.

The benchmark command is expected to be run from within the git repository that contains the file.

## Code Style Requirements

- **prettier**: The repo uses prettier for code formatting (printWidth: 100, no semicolons, single quotes). Run `pnpm run format:check` to validate.
- **oxlint**: The repo uses oxlint for linting. Run `pnpm lint` to validate.
- **TypeScript**: Follow the repo's TypeScript conventions. Run `pnpm --filter @remix-run/route-pattern run typecheck` to validate the route-pattern package.

## Implementation Constraints

- Use `execSync` from Node.js built-in `child_process` module for git commands
- The repo uses **pnpm** as the package manager
- Follow the repo's TypeScript conventions: use `let` for locals, regular function declarations (not arrow functions as top-level declarations), and `import { X }` syntax
- The git commands to use are `git rev-parse --abbrev-ref HEAD` for the branch name and `git rev-parse --short HEAD` for the short commit SHA
- If git commands fail for any reason, the benchmark name must revert to the original value `'bench'` (so benchmarks don't break outside git repos)

## Verification

After making the change, these should all pass:
- The file should no longer have a hardcoded `let benchName = 'bench'` — the name should be computed
- `pnpm --filter @remix-run/route-pattern run typecheck` should pass
- `pnpm run format:check` should pass (the entire monorepo, since prettier checks all files)
