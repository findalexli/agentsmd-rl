# chore: Improve and split Claude.md

Source: [propeller-heads/tycho-indexer#860](https://github.com/propeller-heads/tycho-indexer/pull/860)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `tycho-client/CLAUDE.md`
- `tycho-common/CLAUDE.md`
- `tycho-ethereum/CLAUDE.md`
- `tycho-indexer/CLAUDE.md`
- `tycho-storage/CLAUDE.md`

## What to add / change

Splits CLAUDE.md per crate, so the agents can pull in more detailed context based on what files they are working on.

Also strips down Claude.md to the minimum so it doesn't repeat any obviosu bash commands or comments already avaialble in the code.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
