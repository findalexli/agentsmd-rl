# feat(skills): add MiniMax-AI/cli as default skill tap

Source: [agentscope-ai/OpenJudge#167](https://github.com/agentscope-ai/OpenJudge/pull/167)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/mmx-cli/SKILL.md`

## What to add / change

## Summary

- Add `MiniMax-AI/cli` (`skill/` path) to `skills/mmx-cli/SKILL.md` so the mmx-cli skill is discoverable via [openjudge.me/skills](https://openjudge.me/skills) and the `npx skills` CLI
- Users can install via `npx skills add MiniMax-AI/cli@skill -g -y` — the SKILL.md is fetched directly from [MiniMax-AI/cli](https://github.com/MiniMax-AI/cli/blob/main/skill/SKILL.md)
- Skill updates are fully decoupled: MiniMax maintains the upstream SKILL.md, no changes needed in this project

**1 new file, 83 lines.**

## What is mmx-cli?

[mmx-cli](https://github.com/MiniMax-AI/cli) is a CLI tool for the MiniMax AI platform, providing:
- **Text generation** (MiniMax-M2.7 model)
- **Image generation** (image-01)
- **Video generation** (Hailuo-2.3)
- **Speech synthesis** (speech-2.8-hd, 300+ voices)
- **Music generation** (music-2.6, with lyrics, cover, and instrumental)
- **Web search**

The [SKILL.md](https://github.com/MiniMax-AI/cli/blob/main/skill/SKILL.md) follows the [agentskills.io](https://agentskills.io) standard and includes agent-specific flags (`--non-interactive`, `--quiet`, `--output json`).

## Test plan

- `npx skills find mmx-cli` lists the mmx-cli skill
- `npx skills add MiniMax-AI/cli@skill -g -y` installs successfully
- Ask agent "generate a jazz instrumental" — agent invokes `mmx music generate` via terminal

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
