# chore: Move agents skills to .agents/skills folder

Source: [blockscout/blockscout#14081](https://github.com/blockscout/blockscout/pull/14081)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/alias-nested-modules/SKILL.md`
- `.agents/skills/alphabetically-ordered-aliases/SKILL.md`
- `.agents/skills/code-formatting/SKILL.md`
- `.agents/skills/compare-against-empty-list/SKILL.md`
- `.agents/skills/compile-project/SKILL.md`
- `.agents/skills/ecto-migration/SKILL.md`
- `.agents/skills/efficient-list-building/SKILL.md`
- `.agents/skills/heavy-db-index-operation/SKILL.md`

## What to add / change

## Motivation

Move `.github/skills/` to `.agents/skills/`

## Checklist for your Pull Request (PR)

- [ ] I verified this PR does not break any public APIs, contracts, or interfaces that external consumers depend on.
- [ ] If I added new functionality, I added tests covering it.
- [ ] If I fixed a bug, I added a regression test to prevent the bug from silently reappearing again.
- [ ] I updated documentation if needed:
  - [ ] General docs: submitted PR to [docs repository](https://github.com/blockscout/docs).
  - [ ] ENV vars: updated [env vars list](https://github.com/blockscout/docs/tree/main/setup/env-variables) and set version parameter to `master`.
  - [ ] Deprecated vars: added to [deprecated env vars list](https://github.com/blockscout/docs/tree/main/setup/env-variables/deprecated-env-variables).
- [ ] If I modified API endpoints, I updated the Swagger/OpenAPI schemas accordingly and checked that schemas are asserted in tests.
- [ ] If I added new DB indices, I checked, that they are not redundant, with PGHero or other tools.
- [ ] If I added/removed chain type, I modified the Github CI matrix and PR labels accordingly.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
