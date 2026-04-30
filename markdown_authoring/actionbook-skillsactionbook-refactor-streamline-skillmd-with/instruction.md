# [skills/actionbook] refactor: streamline SKILL.md with two-phase workflow

Source: [actionbook/actionbook#56](https://github.com/actionbook/actionbook/pull/56)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/actionbook/SKILL.md`

## What to add / change

## Summary

Streamline SKILL.md to improve clarity and reduce verbosity (~240 → ~130 lines) while making the document more actionable for AI agents.

## Changes

### 📝 Updated SKILL.md
- Restructured usage into clear **Phase 1** (Get Manual) + **Phase 2** (Execute with Browser) workflow
- Replaced generic LinkedIn examples with concrete **arxiv search** example using real CSS selectors
- Added **Action Manual Format** section with YAML example showing selector structure
- Added **Essential Commands** reference table for quick lookup
- Added "Navigate to any new page during browser automation" as activation trigger
- Updated **Guidelines** to prioritize Action Manual CSS selectors over snapshot-based @refs
- Moved **Advanced Features** to end as concise reference links
- Removed redundant sections: "What Actionbook Provides", Playwright/Puppeteer examples, verbose command listings

## Why This Change

The previous SKILL.md was verbose and scattered across multiple sections. The new version:
1. Gives agents a clear two-phase mental model (query first, execute second)
2. Shows a real end-to-end example with actual selectors instead of abstract descriptions
3. Emphasizes using pre-verified selectors before falling back to snapshot @refs
4. Keeps advanced docs accessible via links without cluttering the main document

## Testing

- [x] Verified markdown renders correctly
- [x] Content aligns with existing documentation style
- [x] All reference links preserved

🤖 Generated with [C

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
