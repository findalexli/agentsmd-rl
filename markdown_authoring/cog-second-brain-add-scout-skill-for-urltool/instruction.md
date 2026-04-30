# Add /scout skill for URL/tool triage before saving

Source: [huytieu/COG-second-brain#14](https://github.com/huytieu/COG-second-brain/pull/14)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/scout/SKILL.md`
- `AGENTS.md`

## What to add / change

New lightweight evaluation skill that checks vault coverage, assesses relevance against user profile/interests, and recommends **save or skip**. Keeps it binary (no watch/bookmark half-measure) — hands off to `/url-dump` when saving.

Basically, a **pre-dump check** whether a resource is **relevant** to the user's interests or not.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
