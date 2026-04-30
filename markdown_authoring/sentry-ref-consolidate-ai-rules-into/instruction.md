# ref: Consolidate AI rules into AGENTS.md files

Source: [getsentry/sentry#102379](https://github.com/getsentry/sentry/pull/102379)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/python.mdc`
- `.cursor/rules/typescript_tests.mdc`
- `AGENTS.md`
- `CLAUDE.md`
- `static/AGENTS.md`
- `static/CLAUDE.md`
- `static/CLAUDE.md`

## What to add / change

Consolidates all AI agent instructions into `AGENTS.md` files. All coding agents follow the nested `AGENTS.md` except for claude code, but claude reccomends just referencing `AGENTS.md` like [so](https://docs.claude.com/en/docs/claude-code/claude-code-on-the-web#best-practices) for a single source of truth.

- We remove the cursor rules besides `BUGBOT.md` and also consolidate them into the respective `AGENTS.md` files.
- Replace `CLAUDE.md` with references to `AGENTS.md` where necessary
- Update root dir `AGENTS.md` to mention not to add new cursor rules / claude files and instead update AGENT.md files instead.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
