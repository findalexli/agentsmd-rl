# Add BGPT paper search skill

Source: [K-Dense-AI/scientific-agent-skills#61](https://github.com/K-Dense-AI/scientific-agent-skills/pull/61)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `scientific-skills/bgpt-paper-search/SKILL.md`

## What to add / change

## Summary

Adds a new scientific skill for searching papers via [BGPT MCP](https://github.com/connerlambden/bgpt-mcp), a remote MCP server that returns structured experimental data extracted from full-text studies.

Unlike the existing `pubmed-database` skill (which queries PubMed metadata), BGPT returns 25+ fields per paper including methods, quantitative results, sample sizes, quality scores, and conclusions — data extracted from the actual paper content.

**Key features:**
- Remote MCP server (no local install needed)
- Free tier: 50 searches, no API key required
- Complements existing literature skills (`pubmed-database`, `biorxiv-database`, `literature-review`)
- Listed in the [Official MCP Registry](https://registry.modelcontextprotocol.io)

## Files

- `scientific-skills/bgpt-paper-search/SKILL.md` — Skill definition with setup, usage, and integration notes

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
