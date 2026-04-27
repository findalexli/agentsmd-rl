# feat: add inline editing feature documentation

Source: [zarazhangrui/frontend-slides#23](https://github.com/zarazhangrui/frontend-slides/pull/23)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary

- Add **Question 5 (Inline Editing)** to Phase 1 content discovery, letting users opt in to browser-based text editing
- Add **Edit Button Implementation** section in Phase 3 with complete HTML/CSS/JS code patterns (hotzone hover with 400ms delay, E key shortcut, click toggle)
- Add **editing instructions** to Phase 5 delivery summary so users know how to enter edit mode

## Why

The inline editing feature allows users to tweak presentation text directly in the browser without reopening the HTML source. This was previously supported but the documentation was removed — this PR restores it as an opt-in capability.

## Key design decisions

- **Opt-in, not default** — users choose during Phase 1; if declined, zero edit-related code is generated
- **JS-based hover, not CSS `~` sibling selector** — the CSS-only approach breaks because `pointer-events: none` interrupts the hover chain
- **400ms grace period** — prevents the edit button from disappearing when the mouse moves from hotzone to button

## Test plan

- [ ] Verify Phase 1 now asks 5 questions (Purpose, Length, Content, Images, Editing)
- [ ] When user opts in, generated HTML includes edit hotzone, toggle button, and toolbar
- [ ] When user opts out, no edit-related code is generated
- [ ] Edit button appears on hover over top-left 80×80px area
- [ ] Pressing E toggles edit mode (except when typing in contenteditable)
- [ ] Delivery summary includes editing instructions only when opted in

🤖 Generated with [Cla

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
