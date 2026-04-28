# Add common agent skills [PeerDAS streamlining]

Source: [mratsim/constantine#603](https://github.com/mratsim/constantine/pull/603)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/debugging/SKILL.md`
- `.agents/skills/performance-investigation/SKILL.md`
- `.agents/skills/seq-arrays-openarrays-slicing-views/SKILL.md`
- `.agents/skills/serialization-hex-debugging/SKILL.md`

## What to add / change

This extracts agent skills added for PeerDAS in #593 to reduce the size of the final PR for review

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
