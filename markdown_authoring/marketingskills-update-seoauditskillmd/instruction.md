# Update seo-audit/SKILL.md

Source: [coreyhaines31/marketingskills#199](https://github.com/coreyhaines31/marketingskills/pull/199)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/seo-audit/SKILL.md`

## What to add / change

Edit title tags check to not include the brand name, since brand/site name is shown in Google SERPs above the title already and Google rewrites titles including brand names (strips them).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
