# Add --create-style mode for custom styles from reference images

Source: [gooseworks-ai/goose-skills#20](https://github.com/gooseworks-ai/goose-skills/pull/20)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/composites/goose-graphics/SKILL.md`
- `skills/composites/goose-graphics/styles/extract-style.md`

## What to add / change

## Summary

- Adds `--create-style` invocation mode to goose-graphics that extracts a visual style from a reference image and saves it as a reusable preset
- Rewrites `extract-style.md` to output slim-format style files (4-8KB) matching the existing 36 presets, instead of verbose 9-section DESIGN.md (~30KB)
- Saves custom styles to the skill pack's `styles/` directory, immediately usable via `--style <name>`
- Adds name collision guards against shipped presets and host-aware save path documentation

## Test plan
- [ ] Verify `--create-style --ref <image>` invocation triggers extract-style workflow and stops after save
- [ ] Verify generated style file matches slim format (Palette, Typography, Layout, Do/Don't, CSS snippets)
- [ ] Verify name collision guard warns when using a shipped preset name
- [ ] Verify saved custom style works with `--style <name> --format carousel --brief "..."`

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
