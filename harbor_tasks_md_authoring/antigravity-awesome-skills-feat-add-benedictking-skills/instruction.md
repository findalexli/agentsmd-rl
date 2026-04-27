# feat: add BenedictKing skills

Source: [sickn33/antigravity-awesome-skills#25](https://github.com/sickn33/antigravity-awesome-skills/pull/25)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/codex-review/SKILL.md`
- `skills/context7-auto-research/SKILL.md`
- `skills/exa-search/SKILL.md`
- `skills/firecrawl-scraper/SKILL.md`
- `skills/tavily-web/SKILL.md`

## What to add / change

## New Skills Added

| Skill | Description |
|-------|-------------|
| context7-auto-research | Auto-fetch latest library/framework docs |
| tavily-web | Web search, extraction, crawling |
| exa-search | Semantic search using Exa API |
| firecrawl-scraper | Deep scraping, screenshots, PDF parsing |
| codex-review | Professional code review |

## Validation
- [x] Descriptive skill names
- [x] Proper frontmatter formatting
- [x] Tested with Claude Code
- [x] Clear, typo-free content

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
