# refactor: rewrite SKILL.md as pure usage guide

Source: [Panniantong/Agent-Reach#78](https://github.com/Panniantong/Agent-Reach/pull/78)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `agent_reach/skill/SKILL.md`

## What to add / change

**Problem:** SKILL.md mixed installation/configuration with usage commands, and its `description` only had install-related trigger words. When users said "帮我搜推特" the skill wouldn't trigger.

**Fix:** Complete rewrite following skill-creator conventions:

- **Description** now includes trigger words for all 13 channels: "搜推特", "搜小红书", "看视频", "search twitter", "web search", etc.
- **Body** is pure usage guide — concise commands for each platform, nothing else
- Removed all installation/configuration content (belongs in install.md)
- 324 → 160 lines (51% reduction)

**Result:** Agent now loads SKILL.md whenever user mentions searching/reading ANY supported platform, and gets a clean command reference without install noise.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
