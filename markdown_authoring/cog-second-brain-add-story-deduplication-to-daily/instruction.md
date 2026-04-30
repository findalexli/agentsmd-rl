# Add story deduplication to daily brief skill

Source: [huytieu/COG-second-brain#15](https://github.com/huytieu/COG-second-brain/pull/15)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/daily-brief/SKILL.md`

## What to add / change

Quite often, the `/daily-brief` skill **repeats** stories from **previous days**.

Briefs now scan the last 3 daily briefs during pre-flight to build a set of covered stories. Repeated stories are **skipped** unless there's a material update (new data, resolution, escalation), in which case they're prefixed with "Update:". New `dedup_urls` frontmatter field enables fast extraction by future briefs.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
