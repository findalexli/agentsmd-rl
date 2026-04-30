# Add In-Repo Skills for PR Workflows

## Problem

The Remix monorepo needs two reusable agent skills for common PR workflows:

1. **supersede-pr**: When a PR replaces/supersedes an older PR, GitHub's `Closes #...` keywords only close *issues*, not pull requests. There's no built-in way to automatically close the superseded PR. The repo needs a skill with a TypeScript helper script that uses `gh pr close` to deterministically close superseded PRs and verify the final state.

2. **make-pr**: The team wants a standardized skill for creating pull requests with consistent, high-signal descriptions — clear context, related links, and usage examples for new features, without boilerplate sections.

Each skill should have a `SKILL.md` file with YAML frontmatter (`name` and `description` fields) and a clear workflow section.

## What Needs to Happen

- Create `skills/supersede-pr/SKILL.md` describing the supersession workflow
- Create `skills/supersede-pr/scripts/close_superseded_pr.ts` — a Node-executable TypeScript CLI script that:
  - Takes `<old_pr> <new_pr>` as positional arguments
  - Supports `--repo <owner/repo>` and `--dry-run` flags
  - Validates PR numbers are numeric and different from each other
  - When validation fails, exits non-zero and prints a message containing the word "numeric" or "number" for non-numeric input, and a message containing the word "different" when both PR numbers are identical
  - Shows usage with `--help` or `-h`; the help output must include the script name ("close_superseded_pr" or "old_pr"), the `--repo` flag, and the `--dry-run` flag
  - Uses `gh` CLI to comment on and close the old PR, then verifies closure
- Create `skills/supersede-pr/tsconfig.json` with `strict: true` and `noEmit: true` (strict TypeScript settings that prevent emission)
- Create `skills/make-pr/SKILL.md` describing the PR creation workflow
- Update `AGENTS.md` to:
  - Add a code style rule about writing one-off scripts as executable TypeScript
  - Add a new "Skills" section at the end documenting both skills with file references

## Files to Look At

- `AGENTS.md` — the repo's agent development guide (needs updates)
- `skills/` — directory for skill definitions (create new subdirectories here)

## Code Style Requirements

- **ESLint**: The repo uses ESLint (`pnpm lint`) and enforces specific rules (e.g., `import type` for type-only imports, no semicolons). All TypeScript files must pass lint.
- **Prettier**: The repo formats code with Prettier (printWidth 100, single quotes, spaces not tabs). Run `pnpm format:check` to verify formatting.
- **TypeScript**: Strict mode is enabled repo-wide. Use `let` for local variables (not `const`), `import type` for type-only imports, and include `.ts` extensions in import paths.

## Notes

- The TypeScript script should follow the repo's code style: `let` for locals, no semicolons, single quotes, `import type` for type-only imports
- The script shebang should be `#!/usr/bin/env node` (modern Node can run `.ts` natively)
- Skills should also include an `agents/openai.yaml` with basic interface metadata