# Add AGENTS.md and CLAUDE.md

Source: [ForumMagnum/ForumMagnum#12453](https://github.com/ForumMagnum/ForumMagnum/pull/12453)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Summary
- Adds `AGENTS.md` with EA Forum-focused orientation for coding agents: branching/deploy rules, settings systems, local dev commands, migrations, codegen, testing prerequisites, CI quirks, and common pitfalls.
- Adds `CLAUDE.md` as a thin pointer to `AGENTS.md` so Claude Code picks up the same context.

## Test plan
- [ ] Skim `AGENTS.md` top-to-bottom; confirm every `yarn` command named resolves in `package.json` and behaves as described.
- [ ] Spot-check file paths referenced (routes, forumSpecificRoutes, logging, migrations).
- [ ] Confirm no references to the empty `pull_request_template.md`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

┆Issue is synchronized with this [Asana task](https://app.asana.com/0/1201302964208280/1214150728405321) by [Unito](https://www.unito.io)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
