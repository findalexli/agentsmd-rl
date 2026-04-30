# Add in-repo supersede-pr skill with TypeScript helper script

## Problem

The Remix repo needs a way to explicitly close superseded pull requests. GitHub's `Closes #...` keyword only closes **issues**, not PRs — so when one PR replaces another, the old PR stays open unless manually closed. There's no in-repo skill or tooling to handle this workflow.

Additionally, the repo is missing a `make-pr` skill to standardize how pull requests are created with clear context and examples.

## What Needs to Happen

1. **Create a `supersede-pr` skill** under `skills/supersede-pr/`:
   - A `SKILL.md` with proper YAML frontmatter (`name`, `description`) describing the supersession workflow. The SKILL.md must explain that `Closes #<number>` keywords do NOT close pull requests (they only close issues), so explicit closure is needed.
   - A TypeScript helper script at `scripts/close_superseded_pr.ts` that takes `<old_pr> <new_pr>` arguments and uses `gh` CLI to close the superseded PR
   - The script must:
     - Validate inputs: PR numbers must be numeric; print an error containing "numeric" if validation fails
     - Reject when old_pr equals new_pr: exit non-zero and print an error containing "must be different" to stderr
     - Support `--help` flag: print "Usage" text showing command syntax, the "old_pr" argument, and the "--dry-run" flag, then exit 0
     - Support `--repo` flag to specify owner/repo
     - Support `--dry-run` flag to preview actions without executing
   - An `agents/openai.yaml` configuration file
   - A `tsconfig.json` for the skill's TypeScript files

2. **Create a `make-pr` skill** under `skills/make-pr/`:
   - A `SKILL.md` with proper YAML frontmatter (`name`, `description`) describing a workflow for creating well-structured GitHub PRs. The SKILL.md must reference `gh pr create` for creating pull requests.
   - An `agents/openai.yaml` configuration file

3. **Update `AGENTS.md`** to reflect the new additions:
   - Add a code style note that one-off scripts in this repo should be written as executable TypeScript using modern Node.js (mention "one-off" in the convention)
   - Add a new **Skills** section documenting the available skills with their descriptions. The section must reference the literal string "SKILL.md" when describing where skills are defined.

## Files to Look At

- `AGENTS.md` — existing agent instructions for the repo (read before modifying)
- `skills/` — directory for skill definitions (does not yet exist at the base commit)

## Code Style Requirements

This repository enforces code style and type safety automatically. Your changes must pass:

- **ESLint** (`pnpm lint`): JavaScript/TypeScript linting with zero warnings
- **Prettier** (`pnpm format:check`): code formatting (check-only, does not modify files)
- **TypeScript** (`pnpm typecheck`): strict type checking across all packages
