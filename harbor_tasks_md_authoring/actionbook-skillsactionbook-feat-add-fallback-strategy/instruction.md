# [skills/actionbook] feat: add Fallback Strategy section to SKILL.md

Source: [actionbook/actionbook#55](https://github.com/actionbook/actionbook/pull/55)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/actionbook/SKILL.md`

## What to add / change

## Summary

Add Fallback Strategy documentation to the actionbook skill, explaining when and how to handle situations where Actionbook data may not work as expected.

## Changes

### 📝 Updated SKILL.md
- Added **Fallback Strategy** section explaining recovery approaches when Actionbook selectors fail
- Documented three key failure signals:
  - Selector execution failure (CSS/XPath doesn't match)
  - Element mismatch (wrong element type or behavior)
  - Multiple consecutive selector failures
- Described fallback approach: direct browser access for real-time page structure retrieval

## Why This Change

Actionbook stores pre-computed page data that may become outdated as websites evolve. Users need clear guidance on:
1. Recognizing when Actionbook data is stale
2. Understanding that these issues are detected at runtime, not via API responses
3. Knowing the fallback option (direct browser automation)

## Testing

- [x] Verified markdown renders correctly
- [x] Content aligns with existing documentation style

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
