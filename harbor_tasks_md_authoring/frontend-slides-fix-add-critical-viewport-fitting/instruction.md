# Fix: Add critical viewport fitting rules for slide modifications

Source: [zarazhangrui/frontend-slides#11](https://github.com/zarazhangrui/frontend-slides/pull/11)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary
Fixes #1 - Adds comprehensive viewport fitting rules for Mode C (Existing Presentation Enhancement) to prevent content overflow when modifying slides.

## Problem
When the skill was asked to add images to existing slides, it would insert them without checking if the content would still fit in the viewport. This caused:
- Content overflow beyond viewport boundaries
- Unstable scrolling behavior
- Need for manual reorganization prompts from users

## Solution
Enhanced the SKILL.md with explicit Mode C modification rules:

### 1. **Added "Mode C: Critical Modification Rules" section** (49 new lines)
   - Pre-modification content checks
   - Special handling for images (most common issue)
   - Post-modification validation checklist
   - Proactive reorganization requirements
   - Testing guidelines

### 2. **Enhanced "When Content Doesn't Fit" section**
   - Added specific DO item: "When adding images to existing slides: Move image to new slide or reduce other content first"
   - Added specific DON'T item: "Add images without checking if existing content already fills the viewport"

### Key Changes:
- **Proactive, not reactive**: Skill must now automatically reorganize content when overflow is detected
- **Image-specific guidance**: Explicit rules for the most common overflow scenario
- **Mandatory checklist**: 5 checks required after ANY modification
- **Clear examples**: Concrete DO/DON'T scenarios for adding images

## Testing Approach
The enhanced rules require the 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
