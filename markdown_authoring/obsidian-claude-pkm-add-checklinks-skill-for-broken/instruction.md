# Add /check-links skill for broken wiki-link detection

Source: [ballred/obsidian-claude-pkm#10](https://github.com/ballred/obsidian-claude-pkm/pull/10)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `vault-template/.claude/skills/check-links/SKILL.md`

## What to add / change

## Summary

Adds a `/check-links` skill that finds broken `[[wiki-links]]` across the vault. Read-only — never modifies files. Zero dependencies — uses only Grep and Glob tools.

### What it does

1. Extracts all `[[wiki-link]]` targets from markdown files via Grep
2. Strips heading anchors (`#heading`), block references (`^block`), and aliases (`|alias`)
3. Verifies each target file exists via Glob
4. Groups broken links by source file
5. Suggests close matches for misspelled targets (e.g., `[[Projet Alpha]]` → "Did you mean `[[Project Alpha]]`?")

### Usage

```
/check-links
```

### Example output

```markdown
## Broken Links Report

### Daily Notes/2024-01-15.md
- [[Projet Alpha]] — Did you mean [[Project Alpha]]?
- [[Old Goal]] — no matching file found

### Projects/Project Beta.md
- [[Meeting Notes Jan]] — no matching file found

**Summary:** 3 broken links across 2 files (out of 45 total links checked)
```

### Edge cases handled

- Embedded images (`![[image.png]]`) — skipped
- External links (`[text](url)`) — skipped
- Template placeholders (`[[{{date}}]]`) — skipped
- Empty links (`[[]]`) — reported as malformed

### Why this fits

Wiki-link integrity is the #1 maintenance headache in any Obsidian vault. File renames break links silently. A zero-dependency checker that runs on demand teaches good hygiene habits early and helps users catch link rot before it accumulates.

### Files changed

- `vault-template/.claude/skill

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
