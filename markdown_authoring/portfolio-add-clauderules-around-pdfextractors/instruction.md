# Add claude-rules around pdf-extractors

Source: [portfolio-performance/portfolio#5560](https://github.com/portfolio-performance/portfolio/pull/5560)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/pdfextractors.md`

## What to add / change

Thought it makes sense to create a dedicated Claude rules-file for pdf-extractors which is used when the files get adjust there. It can also be used as reference like the `Contributing.md` and is a little bit more detailed with the learnings I had in during the changes I did.

Used https://github.com/portfolio-performance/portfolio/pull/5561 for testing this rule

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
