# Fix copilot-instructions.md to require mandatory hardware build validation

Source: [wled/WLED#4987](https://github.com/wled/WLED/pull/4987)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

✅ Fixed copilot-instructions.md to prevent PRs with failing builds

**Problem Solved:**
Copilot agents were marking PR sessions as complete without running hardware builds, causing CI failures like https://github.com/wled/WLED/actions/runs/18260044378

**Root Cause:**
The instruction "Always run a build for the common environment before finishing" was too vague:
- Didn't specify which environment or exact command
- Wasn't prominent enough in the document
- Used weak language that could be interpreted as optional
- Missing specific timeout guidance

**Solution Implemented:**
- [x] Added prominent "Before Finishing Work" section as 2nd major section
- [x] Made hardware build validation explicit and mandatory
- [x] Specified exact command: `pio run -e esp32dev`
- [x] Added clear timeout guidance (30+ minutes, 1800 seconds)
- [x] Enhanced multiple sections with stronger language
- [x] Created cross-references between sections
- [x] Verified all tests still pass (16/16)
- [x] Improved cross-references to canonical "common environments" list

**Key Changes:**

1. **New "Before Finishing Work" Section** (lines 33-52)
   - Impossible to miss - placed as 2nd major section
   - Uses "CRITICAL" and "MUST" language throughout
   - Lists 3 mandatory validation steps with exact commands
   - Step 2 explicitly requires: `pio run -e esp32dev` with 30+ min timeout
   - References "Hardware Compilation" section for full list of common environments

2. **Updated "Code Validation"** (line 68)
  

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
