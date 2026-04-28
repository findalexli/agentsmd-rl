# fix(growth): simpler tweets, chill replies, no jargon

Source: [OpenRouterTeam/spawn#3332](https://github.com/OpenRouterTeam/spawn/pull/3332)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/setup-agent-team/growth-prompt.md`
- `.claude/skills/setup-agent-team/tweet-prompt.md`
- `.claude/skills/setup-agent-team/x-engage-prompt.md`

## What to add / change

## Summary

Tone fixes for the daily growth output. Before: the bot wrote tweets about 'ps aux' process listings and replied on X with "One command to provision Claude Code, Codex, or OpenCode on Hetzner/AWS/DO." Neither lands with humans.

**Daily tweet**: now targeted at curious devs who don't know infra jargon. Banned terms include `ps aux`, `OAuth`, `SigV4`, `TLS`, `CORS`, `RBAC`, `syscall`, commit hashes, file paths, CLI flag names. If the only recent commits are internal infra/security, the bot is told to output `found:false` instead of forcing a technical tweet.

**X engagement replies**: rewritten to demand 5-25 words, under 120 chars ideal. With concrete vibe examples in the prompt:
- "nice. check out spawn, does all that"
- "yeah spawn handles this in one command"
- "+1, spawn does this on cheap hetzner vms"

**Reddit replies**: tightened to 1-3 sentences max, banned feature-list style.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
