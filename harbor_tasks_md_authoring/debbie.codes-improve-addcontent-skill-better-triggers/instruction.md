# Improve add-content skill: better triggers, fixes & consistency

Source: [debs-obrien/debbie.codes#545](https://github.com/debs-obrien/debbie.codes/pull/545)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/add-content/SKILL.md`
- `.agents/skills/add-content/references/blog.md`
- `.agents/skills/add-content/references/environment.md`
- `.agents/skills/add-content/references/video.md`

## What to add / change

## Improvements to the add-content skill

### Changes

1. **SKILL.md** — Updated description with natural trigger phrases ("add video", "add blog post", "add podcast", etc.) so goose automatically picks this skill when those phrases are used

2. **references/video.md** — Swapped example from non-existent `supercharged-testing-playwright-mcp.md` to real file `manual-testing-with-playwright-mcp-no-code-just-prompts.md`

3. **references/blog.md** — Simplified `playwright-cli open` syntax to be consistent with video.md and podcast.md (removed `--` and variable assignment)

4. **references/environment.md** — Added `kill $(lsof -ti:3001)` step before starting the dev server to prevent port conflicts on consecutive runs

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
