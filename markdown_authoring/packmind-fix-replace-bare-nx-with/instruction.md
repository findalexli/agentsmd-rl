# fix: replace bare nx with ./node_modules/.bin/nx and remove serve/start/dev command

Source: [PackmindHub/packmind#219](https://github.com/PackmindHub/packmind/pull/219)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`
- `apps/AGENTS.md`
- `apps/CLAUDE.md`
- `apps/api/AGENTS.md`
- `apps/api/CLAUDE.md`
- `apps/cli/AGENTS.md`
- `apps/cli/CLAUDE.md`
- `apps/frontend/AGENTS.md`
- `apps/frontend/CLAUDE.md`
- `apps/mcp-server/AGENTS.md`
- `apps/mcp-server/CLAUDE.md`
- `packages/AGENTS.md`
- `packages/CLAUDE.md`
- `packages/ui/AGENTS.md`
- `packages/ui/CLAUDE.md`

## What to add / change

## Summary

- Replace all bare `nx` command references with `./node_modules/.bin/nx` in every CLAUDE.md and AGENTS.md file (16 files), so AI agents can invoke nx directly without PATH resolution issues
- Remove all `nx serve`, `nx start`, and `nx dev` command references (10 files) — AI agents have no reason to start applications

## Test plan

- [x] `grep -r '`nx ' **/*.md` returns no matches for bare `nx` in source CLAUDE.md/AGENTS.md files
- [x] `grep -r 'nx serve\|nx start\|nx dev' **/*.md` returns no matches in CLAUDE.md/AGENTS.md files
- [x] `npm run test:staged` and `npm run lint:staged` unchanged (they use npm scripts which resolve nx internally)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
