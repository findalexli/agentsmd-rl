# feat: expand content repurposing in social-content

Source: [coreyhaines31/marketingskills#212](https://github.com/coreyhaines31/marketingskills/pull/212)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/social-content/SKILL.md`

## What to add / change

## Summary
- Expands repurposing section from blog-only to podcast, video, webinar, and newsletter sources
- Adds "content atoms" framework for extracting self-contained moments from long-form content
- Includes podcast-specific workflow (transcript → timestamps → clips → captions → subtitles → schedule)
- Adds per-episode output targets (3-5 clips, 1-2 LinkedIn posts, 1 thread, 1 carousel)
- Bumps version to 1.2.0

## Test plan
- [ ] Verify SKILL.md under 500 lines (currently 326)
- [ ] Verify repurposing section flows naturally from existing content

Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
