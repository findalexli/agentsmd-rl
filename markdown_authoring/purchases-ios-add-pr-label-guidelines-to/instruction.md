# Add PR label guidelines to AGENTS.md

Source: [RevenueCat/purchases-ios#6295](https://github.com/RevenueCat/purchases-ios/pull/6295)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- Adds a "Pull Request Labels" section to AGENTS.md
- Documents when to use `pr:feat`, `pr:fix`, and `pr:other` labels
- Documents scope labels like `pr:RevenueCatUI`, `feat:Paywalls_V2`, and `feat:Customer Center`

## Test plan
- [ ] Review the added documentation for accuracy

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
