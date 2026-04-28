#  Add AGENTS.md

Source: [symfony/ux#3426](https://github.com/symfony/ux/pull/3426)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

| Q              | A
| -------------- | ---
| Bug fix?       | no
| New feature?   | no <!-- please update src/**/CHANGELOG.md files -->
| Deprecations?  | no <!-- if yes, also update UPGRADE-*.md and src/**/CHANGELOG.md -->
| Documentation? | no <!-- required for new features, or documentation updates -->
| Issues         | Fix #... <!-- prefix each issue number with "Fix #", no need to create an issue if none exist, explain below instead -->
| License        | MIT

<!--
Replace this notice by a description of your feature/bugfix.
This will help reviewers and should be a good start for the documentation.

Additionally (see https://symfony.com/releases):
 - Always add tests and ensure they pass.
 - For new features, provide some code snippets to help understand usage.
 - Features and deprecations must be submitted against branch main.
 - Update/add documentation as required (we can help!)
 - Changelog entry should follow https://symfony.com/doc/current/contributing/code/conventions.html#writing-a-changelog-entry
 - Never break backward compatibility (see https://symfony.com/bc).
-->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
