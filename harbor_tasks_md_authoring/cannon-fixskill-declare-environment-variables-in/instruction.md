# fix(skill): declare environment variables in SKILL.md frontmatter

Source: [usecannon/cannon#1870](https://github.com/usecannon/cannon/pull/1870)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `packages/skill/SKILL.md`

## What to add / change

## Problem
ClawHub flags the Cannon skill as suspicious because the SKILL.md references environment variables (CANNON_PRIVATE_KEY, RPC_URL, Etherscan API key) but the frontmatter doesn't declare them. This creates a transparency mismatch — users and agents can't see what secrets the skill needs without reading the entire file.

## Changes
Added `env` section to the SKILL.md frontmatter declaring:
- **CANNON_PRIVATE_KEY** (sensitive) — for signing on-chain transactions
- **RPC_URL** — for target chain RPC endpoints
- **ETHERSCAN_API_KEY** (sensitive) — for contract verification
- **CANNON_DIRECTORY** — custom storage path override

All are marked `required: false` since local development (chain 13370, dry-run) doesn't need them.

## Testing
- Frontmatter is valid YAML
- No changes to skill body or behavior

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
