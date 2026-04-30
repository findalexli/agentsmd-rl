# Add visibility/ tag system for content reach control

Source: [Ar9av/obsidian-wiki#14](https://github.com/Ar9av/obsidian-wiki/pull/14)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.skills/tag-taxonomy/SKILL.md`
- `.skills/wiki-export/SKILL.md`
- `.skills/wiki-ingest/SKILL.md`
- `.skills/wiki-query/SKILL.md`
- `AGENTS.md`

## What to add / change

## Summary

- Introduces optional `visibility/` tags (`visibility/public`, `visibility/internal`, `visibility/pii`) so users can mark pages as team-only or sensitive without splitting the vault
- Default behavior is **completely unchanged** — all pages are visible unless filtered mode is explicitly requested in a query or export
- Filtered mode is opt-in, triggered by natural language phrases like "public only", "user-facing", "no internal content"

## What changed

- **`AGENTS.md`** — documents the visibility tag system and adds it as a core principle
- **`wiki-query`** — adds a Visibility Filter section; filtered mode excludes `visibility/internal` and `visibility/pii` pages from the candidate set and never mentions they exist
- **`wiki-export`** — same filter logic for graph exports; filtered exports exclude internal/pii nodes and their edges
- **`wiki-ingest`** — guidance on when to apply visibility tags during ingest (only for genuinely internal/PII content; default is no tag)
- **`tag-taxonomy`** — documents `visibility/` as a reserved system tag group with its own rules (excluded from 5-tag limit, not subject to alias normalization, audited separately)

## Design decisions

- Single vault, single source of truth — no sync issues between separate vaults
- Tags mark content; queries filter content — clean separation
- `visibility/` tags don't count toward the 5-tag limit since they're system metadata, not domain knowledge
- Omitting the tag is equivalent to `visibility/p

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
