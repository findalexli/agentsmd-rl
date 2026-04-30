# chore: add `AGENTS.md`

Source: [caddyserver/caddy#7652](https://github.com/caddyserver/caddy/pull/7652)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Months ago Copilot offered generating `copilot-instructions` for Caddy. I had the file laying around. Based on recent discussion, we considered adding `AGENTS.md`, so I asked copilot to evolve the `copilot-instructions.md` into AGENTS.md while taking in consideration idiomatic Go practices, existing development practices within the Caddy project, and desired quality controls.

## Assistance Disclosure

Copilot generated the file. I reviewed it, ensuring the content is acceptable per our standards and expectation.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
