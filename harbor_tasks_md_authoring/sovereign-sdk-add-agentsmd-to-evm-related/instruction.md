# Add `AGENTS.md` to EVM related crates

Source: [Sovereign-Labs/sovereign-sdk#2498](https://github.com/Sovereign-Labs/sovereign-sdk/pull/2498)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `crates/full-node/sov-ethereum/AGENTS.md`
- `crates/module-system/module-implementations/sov-evm/AGENTS.md`

## What to add / change

# Description

Based on analysis of EVM related PRs in the last couple weeks. I believe this will keep future work more effective

- [x] ~~I have updated `CHANGELOG.md` with a new entry if my PR makes any breaking changes or fixes a bug. If my PR removes a feature or changes its behavior, I provide help for users on how to migrate to the new behavior.~~
- [x] ~~I have carefully reviewed all my `Cargo.toml` changes before opening the PRs. (Are all new dependencies necessary? Is any module dependency leaked into the full-node (hint: it shouldn't)?)~~

## Linked Issues
- Fixes # (issue, if applicable)
- Related to # (issue) 

## Testing
No updates

## Docs
Added new documents

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
