# Summary parser safe punctuation

Source: [Ar9av/obsidian-wiki#3](https://github.com/Ar9av/obsidian-wiki/pull/3)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.skills/wiki-update/SKILL.md`

## What to add / change

## Problem

  The `wiki-update` skill’s **Page format** template showed `summary:` as an unquoted YAML scalar.
  When generated summaries include `:` (common in technical writing), frontmatter can parse incorrectly in Obsidian/YAML tooling.

  ## What Changed

  - Updated the **Page format** template to use folded scalar style for summary:
    - `summary: >-`
    - indented summary content on the next line
  - Added explicit guidance below the template:
    - Prefer folded scalar (`>-`) for `summary` to avoid YAML parsing issues with punctuation.
    - Keep summary content indented by two spaces under `summary: >-`.
    - This avoids quote-escaping rules while remaining parser-safe.
  - Updated the instruction sentence to require folded scalar summary format for all new/updated pages.

  ## Why

  This removes an avoidable YAML footgun and makes generated frontmatter more robust across punctuation-heavy summaries without needing escaping
  logic.

  ## Scope

  Documentation/template-only change in `wiki-update/SKILL.md` (no runtime/tooling code changes).

  ## Validation

  - Confirm the template now renders `summary` using folded style (`>-`).
  - Confirm guidance is present and unambiguous.
  - Manual check: summaries containing `:`, `#`, and quotes parse correctly as frontmatter with folded style.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
