# Add /search skill for keyword vault search

Source: [ballred/obsidian-claude-pkm#8](https://github.com/ballred/obsidian-claude-pkm/pull/8)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `vault-template/.claude/skills/search/SKILL.md`

## What to add / change

## Summary

Adds a `/search` skill that searches vault content by keyword using the Grep tool. Zero dependencies — works in any vault without indexes, plugins, or setup.

### What it does

- Searches all `.md` files for a keyword or regex pattern
- Groups results by directory (Daily Notes, Goals, Projects, Archives, etc.)
- Shows matching lines with context and line numbers
- Suggests related notes by extracting `[[wiki-links]]` from matched files
- Handles no results gracefully with alternative search suggestions

### Usage

```
/search project planning
/search TODO
/search weekly review
```

### Why this fits

The starter kit is dependency-free. A grep-based search is the simplest possible search that works everywhere, requires no index rebuilding, and teaches users how to use skills with Claude Code tools. It fills the gap for users who don't have SQLite or Dataview set up yet.

### Files changed

- `vault-template/.claude/skills/search/SKILL.md` — new skill (1 file, follows existing skill conventions)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
