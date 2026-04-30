# docs(skills): optimize SKILL.md descriptions for clawhub.ai discoverability

Source: [GMGNAI/gmgn-skills#97](https://github.com/GMGNAI/gmgn-skills/pull/97)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/gmgn-cooking/SKILL.md`
- `skills/gmgn-market/SKILL.md`
- `skills/gmgn-portfolio/SKILL.md`
- `skills/gmgn-swap/SKILL.md`
- `skills/gmgn-token/SKILL.md`
- `skills/gmgn-track/SKILL.md`

## What to add / change

## Summary

- Rewrote `description` fields in all 6 SKILL.md files to follow a consistent natural-language pattern: **Get [capabilities] via GMGN API. Use when user asks for [intent keywords].**
- Added high-signal intent keywords (real-time price, market cap, holder list, trader list, Smart Money, KOL trades, copy-trading signals, candlestick chart, meme coin launch, etc.) so Openclaw agents can surface the right skill when searching clawhub.ai.
- Kept `[FINANCIAL EXECUTION]` prefix on gmgn-swap and gmgn-cooking descriptions as a safety signal.

## Motivation

When an Openclaw agent can't find a local skill, it searches clawhub.ai. The previous descriptions were technical field lists — not optimized for natural-language skill search. These rewrites align descriptions with how users actually phrase requests.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
