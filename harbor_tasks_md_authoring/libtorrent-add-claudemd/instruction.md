# add CLAUDE.md

Source: [arvidn/libtorrent#8278](https://github.com/arvidn/libtorrent/pull/8278)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/CLAUDE.md`
- `.claude/rules/dht.md`
- `.claude/rules/disk-cache.md`
- `.claude/rules/piece-picker.md`
- `.claude/rules/python-bindings.md`
- `.claude/rules/strong-types.md`
- `.claude/rules/v2-torrents.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
