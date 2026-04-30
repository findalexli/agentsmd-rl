# Add generate migration command to Agents.md

Source: [opf/openproject#22083](https://github.com/opf/openproject/pull/22083)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

# Ticket
n/a

# What are you trying to accomplish?
Currently llm-s manually create the migration files and appending timestamp to the filenames.

# What approach did you choose and why?
- Instruct llms to use the rails provided rails generator when adding migrations.
- Additionally update the other commands to use rails instead of rake, as recommended by rails.

# Merge checklist

- [ ] Added/updated tests
- [ ] Added/updated documentation in Lookbook (patterns, previews, etc)
- [ ] Tested major browsers (Chrome, Firefox, Edge, ...)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
