# Add initial AGENTS.md for code reviews

Source: [bitfireAT/davx5-ose#2160](https://github.com/bitfireAT/davx5-ose/pull/2160)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This pull request adds a new documentation file, `AGENTS.md`, which provides guidelines and instructions for AI agents performing automated pull request reviews. The file outlines the intended focus areas for automated reviews and introduces conventions for labeling review feedback.

Documentation additions:

* Added `AGENTS.md` with instructions for AI agents, detailing the scope and expectations for automated PR reviews, including focus on functional bugs, architectural concerns, security, and code quality.
* Introduced guidelines for using Conventional Comments in automated review feedback, specifying label usage and decorations for comment severity.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
