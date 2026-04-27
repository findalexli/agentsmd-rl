# feat: add banner-design, slides, ui-styling, design-system, brand skills

Source: [nextlevelbuilder/ui-ux-pro-max-skill#179](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/pull/179)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/ui-ux-pro-max/SKILL.md`

## What to add / change

## Summary
- Add `banner-design` skill for social media, ads, website hero banner design
- Add `slides` skill for presentation slides/deck design
- Add `ui-styling` skill with shadcn/ui components, Tailwind CSS, and canvas-based design
- Add `design-system` skill with token architecture and component specifications
- Add `design` skill with brand identity, logo generation, and CIP mockups
- Add `brand` skill for voice, visual identity, and messaging frameworks
- Add Google Fonts collection (1923 fonts searchable database)
- Expand product types to 161, color palettes to 161, UX guidelines to 99
- Translate Chinese text to English in SKILL.md
- Sync CLI assets with source of truth

## Test plan
- [x] All skills have valid SKILL.md with proper frontmatter
- [x] Search scripts work with new data files
- [x] Design system generation produces valid output
- [x] Canvas font files included for ui-styling skill

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
