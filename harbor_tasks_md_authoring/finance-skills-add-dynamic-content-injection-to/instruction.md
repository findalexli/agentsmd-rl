# Add dynamic content injection to all CLI-dependent skills

Source: [himself65/finance-skills#18](https://github.com/himself65/finance-skills/pull/18)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `skills/discord/SKILL.md`
- `skills/options-payoff/SKILL.md`
- `skills/stock-correlation/SKILL.md`
- `skills/telegram/SKILL.md`
- `skills/twitter/SKILL.md`
- `skills/yfinance-data/SKILL.md`

## What to add / change

## Summary

- Updated 6 of 7 skills to use `!`command`` syntax for injecting runtime environment checks at skill invocation time
- **discord, telegram, twitter**: Inject tool installation + auth status so the model skips setup steps when already configured
- **yfinance-data, stock-correlation**: Inject Python dependency version checks to skip `pip install` when packages are present
- **options-payoff**: Inject live SPX price via yfinance to replace hardcoded reference price
- **generative-ui**: No changes needed (pure design system reference, no runtime dependencies)
- Documented the `!`command`` pattern in CLAUDE.md for future skill authors

## Test plan

- [x] Invoke each updated skill in Claude Code and verify the `!`command`` blocks resolve to actual output
- [x] Verify skills degrade gracefully when tools are not installed (fallback strings appear)
- [x] Confirm generative-ui skill still works unchanged on Claude.ai

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
