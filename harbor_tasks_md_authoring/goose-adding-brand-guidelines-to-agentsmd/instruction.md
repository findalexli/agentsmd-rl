# adding brand guidelines to AGENTS.md

Source: [aaif-goose/goose#4887](https://github.com/aaif-goose/goose/pull/4887)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `documentation/AGENTS.md`

## What to add / change

This pull request adds a documentation style guide to clarify brand guidelines for referring to the product name "goose." The guide emphasizes always using a lowercase "g" in all documentation and related content.

Documentation guidelines:

* Added a new section to `AGENTS.md` specifying that "goose" must always be written with a lowercase "g" across all documentation, blog posts, READMEs, and user-facing configuration files.
* Outlined the contexts in which this rule applies to ensure consistent brand representation.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
