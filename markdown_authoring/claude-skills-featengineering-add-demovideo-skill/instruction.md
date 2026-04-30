# feat(engineering): add demo-video skill

Source: [alirezarezvani/claude-skills#475](https://github.com/alirezarezvani/claude-skills/pull/475)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `engineering/demo-video/SKILL.md`

## What to add / change

## Summary
- What: Add `engineering/demo-video/SKILL.md` — a skill for creating polished demo videos from screenshots and scene descriptions
- Why: Enables AI agents to produce shareable product demos by orchestrating playwright, ffmpeg, and edge-tts MCPs with story structure, scene design, and narration guidance

## Checklist
- [x] Targets dev branch
- [x] SKILL.md frontmatter: name + description only
- [x] Under 500 lines
- [x] Anti-patterns section included
- [x] Cross-references to related skills included
- [x] No modifications to `.codex/`, `.gemini/`, `marketplace.json`, or index files

Full tooling: [framecraft](https://github.com/vaddisrinivas/framecraft)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
