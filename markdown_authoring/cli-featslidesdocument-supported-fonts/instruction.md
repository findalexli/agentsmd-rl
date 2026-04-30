# feat(slides):document supported fonts

Source: [larksuite/cli#681](https://github.com/larksuite/cli/pull/681)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/lark-slides/references/supported-fonts.md`
- `skills/lark-slides/references/xml-schema-quick-ref.md`

## What to add / change

## Summary
  Document the supported font families for the Lark Slides skill so agents can choose render-safe fonts when generating slide XML.

  ## Changes
  - Add a maintained supported-fonts reference for Lark Slides XML fontFamily values
  - Link fontFamily docs in the quick reference and detailed XML guide to the supported fonts list
  - Add three common default font recommendations directly in the high-frequency docs

  ## Test Plan
  - [ ] Unit tests pass
  - [x] Static documentation inspection only; no build or test commands were run per local AGENTS.md guidance

  ## Related Issues
  - None


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

## Release Notes

* **Documentation**
  * Added comprehensive reference guide listing commonly supported font families for Lark Slides, organized by language (Chinese, Latin, other languages, and system fonts).
  * Updated schema documentation to clarify font compatibility behavior and fallback guidance for font selection.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
