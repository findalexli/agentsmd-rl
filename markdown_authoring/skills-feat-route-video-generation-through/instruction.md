# feat: route video generation through @heygen/openclaw-plugin-heygen when available

Source: [heygen-com/skills#67](https://github.com/heygen-com/skills/pull/67)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary

Adds a new **OpenClaw plugin mode** to the API Mode Detection ladder in `SKILL.md`, sitting ahead of CLI and MCP modes. When the user has [`@heygen/openclaw-plugin-heygen`](https://github.com/heygen-com/openclaw-plugin-heygen) installed, the skill prefers calling \`video_generate({ model: "heygen/video_agent_v3", ... })\` directly — the plugin handles auth, session creation, three-tier polling backoff, and error surfacing natively.

This is the agentic-UX layer that pairs with the new external OpenClaw plugin spun out from [openclaw/openclaw#69578](https://github.com/openclaw/openclaw/pull/69578) (closed by maintainers in favor of external/ClawHub publication per VISION.md).

## What changed

- New mode 1 in **API Mode Detection** for OpenClaw plugin mode (CLI/MCP renumbered to 2/3/4/5)
- Added a code block showing the canonical \`video_generate\` call with provider options (\`avatar_id\`, \`voice_id\`, \`style_id\`, \`callback_url\`, \`callback_id\`)
- Updated **Hard rules** to clarify: avatar/voice discovery still goes through MCP or CLI; only the final generate call routes through \`video_generate\`. Frame Check still runs before every submission.
- SKILL.md grew from 267 → 288 lines (under the 300-line cap)

## Versioning

Release-please PR [#66](https://github.com/heygen-com/skills/pull/66) is currently tracking v2.2.0. Once this PR lands on master, release-please will roll this \`feat:\` commit into the existing 2.2.0 release. No manual version bump needed.


## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
