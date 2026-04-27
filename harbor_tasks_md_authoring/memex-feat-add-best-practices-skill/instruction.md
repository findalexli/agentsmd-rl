# feat: add best practices skill for Zettelkasten card quality

Source: [iamtouchskyer/memex#18](https://github.com/iamtouchskyer/memex/pull/18)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/memex-best-practices/SKILL.md`

## What to add / change

## Motivation

The existing skills (`memex-recall`, `memex-retro`, `memex-organize`, `memex-sync`) define **when** to interact with memex. What's missing is a **quality reference** — guidance on **how** to write good cards.

New users (both humans and AI agents) often struggle with:
- How atomic should a card be?
- What makes a good slug?
- When to link vs. when not to?
- How to use tags effectively?
- What the anti-patterns look like

## What This Adds

`skills/memex-best-practices/SKILL.md` — a reference skill covering:

- **Card quality checklist** — atomic, own words, non-obvious, linked in context
- **Card format** — required/optional frontmatter fields with examples
- **Slug naming** — kebab-case conventions, special prefixes (`adr-`, `gotcha-`, `pattern-`, `tool-`)
- **Categories and tag system** — domain tags + type tags, guidelines for consistent tagging
- **Linking strategy** — link-in-context rule, when to link, avoiding over-linking
- **The keyword index** — purpose, format, maintenance
- **Recall → Work → Retro loop** — the core learning cycle explained
- **Graph health maintenance** — orphans, hubs, contradictions, staleness
- **Anti-patterns** — common mistakes and what to do instead

## Design Decisions

- **Reference, not workflow** — this complements the existing workflow skills rather than replacing them
- **Matches existing skill format** — YAML frontmatter with `name` and `description`, Markdown body
- **Platform-agnostic** — works for any memex user rega

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
