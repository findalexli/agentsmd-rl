# Add tubeify + lobsterdomains skills

Source: [davepoon/buildwithclaude#86](https://github.com/davepoon/buildwithclaude/pull/86)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/all-skills/skills/lobsterdomains/SKILL.md`
- `plugins/all-skills/skills/tubeify/SKILL.md`

## What to add / change

## Two new skills

### [Tubeify](https://tubeify.xyz) — `media` category
AI video editor for YouTube. Removes pauses, filler words, and dead air from raw recordings via REST API. No manual editing needed — submit a URL, get back a polished clip. Published on ClawHub: `clawhub install tubeify`

### [LobsterDomains](https://lobsterdomains.xyz) — `web` category
Register ICANN domains (.com/.xyz/.org/1000+ TLDs) with crypto payments (USDC/USDT/ETH/BTC) via REST API. Built for AI agents to acquire domains autonomously without browser interaction. Published on ClawHub: `clawhub install lobsterdomains`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
