# fix: use >- folded scalar for all SKILL.md descriptions

Source: [microsoft/GitHub-Copilot-for-Azure#1015](https://github.com/microsoft/GitHub-Copilot-for-Azure/pull/1015)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/sensei/references/SCORING.md`
- `plugin/skills/azure-observability/SKILL.md`
- `plugin/skills/azure-postgres/SKILL.md`
- `plugin/skills/azure-storage/SKILL.md`

## What to add / change

## Problem

When skills are installed, SKILL.md files with plain unquoted \description\ values containing \: \ (colon-space) patterns fail to parse:

\\\
Nested mappings are not allowed in compact mappings at line 2, column 14
\\\

YAML interprets \USE FOR:\, \DO NOT USE FOR:\, and similar patterns as nested mapping keys instead of literal text.

## Changes

### 1. Convert 3 plain descriptions to \>-\ folded scalar

- \zure-observability/SKILL.md\ — added \USE FOR:\ and \DO NOT USE FOR:\ triggers
- \zure-storage/SKILL.md\ — added \USE FOR:\ and \DO NOT USE FOR:\ triggers
- \zure-postgres/SKILL.md\ — added \USE FOR:\ and \DO NOT USE FOR:\ triggers

These were the only 3 skills still using plain unquoted descriptions. All other 19 skills already use \>-\ folded scalar format per the repo convention.

### 2. Add YAML safety check to sensei scoring

Added Rule 8 (YAML Description Safety) to \.github/skills/sensei/references/SCORING.md\:
- Flags plain descriptions containing \: \ as **Invalid** (will fail to parse)
- Flags descriptions over 200 chars not using \>-\ as a **Warning**
- Updated scoring algorithm and \collectSuggestions()\ to include the new check

## Validation

All 23 SKILL.md files parse correctly with \gray-matter\ (js-yaml). No description exceeds the 1024-char limit.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
