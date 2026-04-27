# Add szamlazz-invoicing skill

Source: [davepoon/buildwithclaude#117](https://github.com/davepoon/buildwithclaude/pull/117)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/all-skills/skills/szamlazz-invoicing/SKILL.md`

## What to add / change

## Summary

Adds a new `szamlazz-invoicing` skill for Hungarian invoicing via the [szamlazz.hu](https://www.szamlazz.hu/) Agent API.

This skill lets Claude Code users issue, cancel (storno), and download Hungarian invoices with natural-language prompts — including NAV taxpayer auto-lookup, automatic partner caching, and proper Hungarian VAT calculation.

## Component Details

- **Name**: szamlazz-invoicing
- **Type**: Skill
- **Category**: automation
- **File**: `plugins/all-skills/skills/szamlazz-invoicing/SKILL.md`

## What it does

- Issues regular, proforma (díjbekérő), and storno invoices
- Auto-fetches company data from the Hungarian National Tax Authority (NAV) by tax number
- Caches partners locally for instant reuse
- Interactive first-run setup (3 questions, 30 seconds)
- Cross-platform (macOS, Linux, Windows) — Python 3.9+ only dependency
- All amounts calculated with `Decimal` / `ROUND_HALF_UP` precision
- 7 error codes translated with actionable Hungarian recovery steps

## Plugin repository

[github.com/socialproKGCMG/socialpro-szamlazz](https://github.com/socialproKGCMG/socialpro-szamlazz) — MIT licensed, 61 tests, CI green.

## Testing

- [x] Tested with Claude Code via `claude --plugin-dir`
- [x] All 61 unit tests pass
- [x] No overlap with existing skills
- [x] Follows CONTRIBUTING.md structure (frontmatter + sections)

## Examples

```
/szamlazz állíts ki egy számlát Példa Kft.-nek 150 000 Ft-ról webfejlesztésről
/szamlazz sztornózd a SOC-2026-0042 számlát

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
