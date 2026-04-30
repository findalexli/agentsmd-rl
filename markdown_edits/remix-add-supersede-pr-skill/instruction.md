# Add supersede-pr Skill with TypeScript Helper Script

## Problem

GitHub's `Closes #...` keywords close issues but NOT pull requests. When a PR supersedes another PR, there is no reliable way to ensure the old PR gets closed — closing keywords simply don't work for PR-to-PR relationships. The repo needs a reusable skill that handles PR supersession end-to-end with deterministic closure.

## Expected Behavior

Create a `supersede-pr` skill under `skills/supersede-pr/` with:

1. A **SKILL.md** defining the supersession workflow: identifying PR numbers, creating/opening the replacement PR, explicitly closing the superseded PR with `gh pr close`, and verifying final states. The skill should explain why `Closes #<old_pr>` is wrong for PRs and what to use instead.

2. An executable **TypeScript helper script** (`close_superseded_pr.ts`) that the skill invokes to close superseded PRs. The script should accept `<old_pr> <new_pr>` positional arguments, support `--repo <owner/repo>` and `--dry-run` optional flags, validate inputs (numeric PR numbers, different PR numbers), check PR states before proceeding, add a "Superseded by #..." comment, close the old PR, and verify the final state is CLOSED.

3. An **agent config** (openai.yaml) for the skill.

After creating the skill, update **AGENTS.md** to:
- Document the available skills in a new "Skills" section (including supersede-pr)
- Add a note under Code Style that one-off scripts in this repo should be executable TypeScript that runs natively with modern Node.js

## Files to Look At

- `AGENTS.md` — existing code style conventions and repo guide; needs new Skills section and one-off scripts note
- `scripts/` — existing scripts in the repo for TypeScript conventions (e.g., `release-pr.ts`, `publish.ts`)
