# fix(ce-update): use correct marketplace name in cache path

Source: [EveryInc/compound-engineering-plugin#566](https://github.com/EveryInc/compound-engineering-plugin/pull/566)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-update/SKILL.md`

## What to add / change

The ce-update skill was looking at `${CLAUDE_PLUGIN_ROOT}/cache/every-marketplace/compound-engineering/`
for the cached plugin version, but the actual marketplace name registered in
`.claude-plugin/marketplace.json` is `compound-engineering-plugin`. Claude Code
caches marketplaces under their registered name, so the skill never found the
cache and always reported "no marketplace cache found".

Also align the `gh release list --repo` casing (`EveryInc`) with the canonical
owner casing used elsewhere in the repo.

Fixes EveryInc/compound-engineering-plugin#556

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
