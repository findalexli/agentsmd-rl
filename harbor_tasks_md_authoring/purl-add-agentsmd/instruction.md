# add AGENTS.md

Source: [catatsuy/purl#125](https://github.com/catatsuy/purl/pull/125)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This pull request adds a new section to the project documentation outlining repository guidelines for contributors. The new `AGENTS.md` content provides clear instructions on project structure, build and test workflows, coding standards, testing practices, and expectations for commits and pull requests.

Documentation improvements:

* Added detailed repository guidelines to `AGENTS.md`, covering project layout, build/test tooling, coding style, testing expectations, and contribution process for commits and pull requests.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
