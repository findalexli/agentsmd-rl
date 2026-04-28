# Split the root Agent.md files into subdirectories.

Source: [opf/openproject#22240](https://github.com/opf/openproject/pull/22240)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `app/AGENTS.md`
- `app/CLAUDE.md`
- `config/AGENTS.md`
- `config/CLAUDE.md`
- `db/AGENTS.md`
- `db/CLAUDE.md`
- `docker/dev/AGENTS.md`
- `docker/dev/CLAUDE.md`
- `frontend/AGENTS.md`
- `frontend/CLAUDE.md`
- `spec/AGENTS.md`
- `spec/CLAUDE.md`

## What to add / change

# Ticket
N/A

# What are you trying to accomplish?
Reduce the size of the root `AGENTS.md` by splitting it up to multiple files in subdirectories.

# Merge checklist

- [ ] Added/updated tests
- [ ] Added/updated documentation in Lookbook (patterns, previews, etc)
- [ ] Tested major browsers (Chrome, Firefox, Edge, ...)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
