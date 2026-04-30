# Fix hallucinated timestamps in content-generating skills

Source: [huytieu/COG-second-brain#6](https://github.com/huytieu/COG-second-brain/pull/6)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/braindump/SKILL.md`
- `.claude/skills/daily-brief/SKILL.md`
- `.claude/skills/knowledge-consolidation/SKILL.md`
- `.claude/skills/weekly-checkin/SKILL.md`

## What to add / change

Skills that produce files with `created:` frontmatter timestamps (braindump, daily-brief, weekly-checkin, knowledge-consolidation) had no mechanism to obtain the actual current time. Claude receives the current date via system prompt but not the time, resulting in fabricated HH:MM values — observed deltas ranged from 25 minutes to 7 hours off.

Added a pre-flight step to each affected skill instructing the agent to run `date '+%Y-%m-%d %H:%M'` before generating files, consistent with the pattern already used by the save skill's git commit command.

Affected skills:
- braindump (frontmatter + filename HHMM component)
- daily-brief (frontmatter)
- weekly-checkin (frontmatter)
- knowledge-consolidation (frontmatter)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
