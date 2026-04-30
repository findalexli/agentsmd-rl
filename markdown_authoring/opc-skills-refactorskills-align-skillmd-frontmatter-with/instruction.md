# refactor(skills): align SKILL.md frontmatter with Anthropic skill standard

Source: [ReScienceLab/opc-skills#51](https://github.com/ReScienceLab/opc-skills/pull/51)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/banner-creator/SKILL.md`
- `skills/domain-hunter/SKILL.md`
- `skills/logo-creator/SKILL.md`
- `skills/nanobanana/SKILL.md`
- `skills/producthunt/SKILL.md`
- `skills/reddit/SKILL.md`
- `skills/requesthunt/SKILL.md`
- `skills/seo-geo/SKILL.md`
- `skills/twitter/SKILL.md`
- `template/SKILL.md`

## What to add / change

## Summary

Align all SKILL.md frontmatter with the [Anthropic skill standard](https://skills.sh/anthropics/skills/skill-creator), which uses only `name` and `description` fields.

**Stacked on:** #50

## Changes

- Remove `triggers` field from all 9 SKILL.md files
- Merge trigger keywords into the `description` field as "Use when..." clauses
- Remove `triggers` and `dependencies` from the template SKILL.md
- Update template frontmatter guide table

## Side effect

Fixes the **seo-geo broken description on skills.sh** -- the YAML multiline block scalar (`|`) was rendering as just `|` on the website. Now it's a single-line string.

## Skills updated

| Skill | Key trigger keywords merged into description |
|-------|----------------------------------------------|
| requesthunt | demand research, feature requests, user demand |
| banner-creator | banner, header, hero image, cover image, GitHub/Twitter/readme banner |
| reddit | Reddit, subreddit, r/ links |
| seo-geo | SEO, GEO, search optimization, JSON-LD, meta tags, keyword research, AI visibility |
| nanobanana | generate/create images, Gemini image, AI image generation |
| producthunt | Product Hunt, PH, product launches |
| logo-creator | logo, icon, favicon, brand mark, mascot, emblem |
| domain-hunter | domain, registrar, domain prices, .ai/.com domains |
| twitter | Twitter, X, tweets |

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
