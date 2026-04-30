# feat: add agents.md file

Source: [appwrite/sdk-generator#1363](https://github.com/appwrite/sdk-generator/pull/1363)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Added comprehensive guidance for AI agents covering rules, template practices, SDK mappings, testing, and a pre-submit checklist.
  * Added a short reference file linking to the new agent documentation for quick discovery.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
