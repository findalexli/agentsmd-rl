# Add in-repo supersede-pr skill with TypeScript helper script

## Problem

The Remix repo needs a way to explicitly close superseded pull requests. GitHub's `Closes #...` keyword only closes **issues**, not PRs — so when one PR replaces another, the old PR stays open unless manually closed. There's no in-repo skill or tooling to handle this workflow.

Additionally, the repo is missing a `make-pr` skill to standardize how pull requests are created with clear context and examples.

## What Needs to Happen

1. **Create a `supersede-pr` skill** under `skills/supersede-pr/`:
   - A `SKILL.md` with proper YAML frontmatter (`name`, `description`) describing the supersession workflow
   - A TypeScript helper script at `scripts/close_superseded_pr.ts` that takes `<old_pr> <new_pr>` arguments and uses `gh` CLI to close the superseded PR
   - The script must validate inputs (numeric PR numbers, old != new), support `--help`, `--repo`, and `--dry-run` flags
   - An `agents/openai.yaml` configuration file
   - A `tsconfig.json` for the skill's TypeScript files

2. **Create a `make-pr` skill** under `skills/make-pr/`:
   - A `SKILL.md` describing a workflow for creating well-structured GitHub PRs
   - An `agents/openai.yaml` configuration file

3. **Update `AGENTS.md`** to reflect the new additions:
   - Add a code style note that one-off scripts in this repo should be written as executable TypeScript (using modern Node.js)
   - Add a new **Skills** section documenting the available skills with their descriptions and file paths

## Files to Look At

- `AGENTS.md` — existing agent instructions for the repo (read before modifying)
- `skills/` — directory for skill definitions (does not yet exist at the base commit)
