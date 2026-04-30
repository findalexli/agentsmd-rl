# docs: rewrite SKILL.md as Operational Quick Reference

Source: [Auriti-Labs/geo-optimizer-skill#480](https://github.com/Auriti-Labs/geo-optimizer-skill/pull/480)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary

Rewrite SKILL.md from a platform file-selection guide into a comprehensive **Operational Quick Reference** covering all v4.9.0 capabilities.

## Motivation

The current SKILL.md (3,428 chars) only routes users to platform-specific files in `ai-context/`. It doesn't document the workflow, CLI commands, scoring system, MCP tools, or informational checks — the core value of the tool.

This was identified during the review of PR #478 (vendor rewrite from Tessl). We rejected that PR but recognized the valid insight: SKILL.md should be an operational document, not just a file router. This is our internal rewrite with verified data.

## What changed

Single file: `SKILL.md` (3,428 → 8,685 chars)

**11 sections, all numbers verified from codebase:**

| Section | Content |
|---------|---------|
| Workflow | 6-step guide (audit → robots → llms → schema → content → fix) |
| Scoring | 8 categories with descriptions |
| CLI Commands | All 11 commands with flags and examples |
| Output Formats | 7 formats (text, json, rich, html, github, ci, pdf) |
| Princeton GEO Methods | 9 core methods with measured impact %, 47 total |
| Informational Checks | 10 non-scoring checks |
| MCP Integration | 12 tools + 5 resources |
| Plugin System | Entry-point based, AuditCheck Protocol |
| Platform Context Files | 6 files with sizes, limits, copy commands (preserved from original) |

## What was NOT changed

- No files in `ai-context/` were modified
- No YAML frontmatter added
- No vendor too

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
