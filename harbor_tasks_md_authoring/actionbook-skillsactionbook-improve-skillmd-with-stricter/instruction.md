# [skills/actionbook] Improve SKILL.md with stricter workflow rules

Source: [actionbook/actionbook#105](https://github.com/actionbook/actionbook/pull/105)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/actionbook/SKILL.md`

## What to add / change

## Summary
- Add **"Action Manual First (Per-Page-Type)"** critical rule — enforces `actionbook search` → `actionbook get` before any browser command on each new page type
- Add **Prohibited Patterns** section to prevent common workflow violations (memorized selectors, skipping search, snapshot-first)
- Add **multi-page-type workflow** example showing re-search on navigation between different URL patterns
- Reorganize Guidelines into clear subsections: Selector Priority, Prohibited Patterns, Extension Mode, Browser Lifecycle
- Merge extension lifecycle cleanup flow (debug release before bridge stop) with the improved structure

## Test plan
- [ ] Verify SKILL.md renders correctly on GitHub
- [ ] Validate the actionbook skill activates correctly with updated description
- [ ] Test multi-page-type workflow example end-to-end

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
