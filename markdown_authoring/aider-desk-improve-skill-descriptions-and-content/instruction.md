# Improve skill descriptions and content quality

Source: [hotovo/aider-desk#682](https://github.com/hotovo/aider-desk/pull/682)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.aider-desk/skills/agent-creator/SKILL.md`
- `.aider-desk/skills/skill-creator/SKILL.md`
- `.aider-desk/skills/theme-factory/SKILL.md`
- `.aider-desk/skills/writing-tests/SKILL.md`

## What to add / change

👋  hullo @hotvo / @wladimiiir 

Reviewed all 4 skills with `tessl skill review` and applied targeted improvements based on scoring feedback. Here's a summary of the results, with the actual changes listed below.

| Skill          | Before (Desc/Content) | After (Desc/Content) | Average |
|----------------|-----------------------|----------------------|---------|
| theme-factory  | 40% / 100%            | 100% / 100%          | 100%    |
| agent-creator  | 40% / 85%             | 100% / 100%          | 100%    |
| skill-creator  | 67% / 73%             | 100% / 88%           | 94%     |
| writing-tests  | 0% (validation fail)  | 100% / 100%          | 100%    |

- **All skills**: Added explicit "Use when..." trigger clauses and concrete action verbs to descriptions for better discoverability
- **writing-tests**: Fixed validation error — renamed from "Writing Tests" to "writing-tests" (lowercase-hyphenated as required); added debugging workflow section
- **agent-creator**: Consolidated redundant reference listings, moved Tool Group Reference to reference files, added inline config.json example
- **skill-creator**: Added quick workflow with verification step, complete SKILL.md example with frontmatter and body content

These were pretty straightforward changes to bring the skill in line with what performs well against Anthropic's best practices. Full disclosure, I work at @tesslio where we build tooling around this. Not a pitch, just fixes that were straightforwa

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
