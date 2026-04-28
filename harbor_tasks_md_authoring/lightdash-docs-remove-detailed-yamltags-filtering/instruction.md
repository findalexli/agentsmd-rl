# docs: remove detailed yamlTags filtering documentation from CLAUDE.md

Source: [lightdash/lightdash#17656](https://github.com/lightdash/lightdash/pull/17656)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `packages/backend/src/models/CatalogModel/CLAUDE.md`

## What to add / change

### Description:
Removes outdated documentation about `yamlTags` filtering logic from the CLAUDE.md file. The PR keeps the core description of the CatalogModel and the `search` method, but eliminates the specific implementation details about tag-based filtering, visibility rules, and the associated tables that explained different tagging scenarios.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
