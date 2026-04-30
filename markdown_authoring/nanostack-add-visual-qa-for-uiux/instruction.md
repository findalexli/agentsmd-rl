# Add Visual QA for UI/UX quality verification

Source: [garagon/nanostack#19](https://github.com/garagon/nanostack/pull/19)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `qa/SKILL.md`

## What to add / change

## Summary

After functional tests pass, `/qa` now takes screenshots and analyzes UI quality against product standards from `/nano-plan`.

Checks: layout balance, visual hierarchy, component quality (shadcn/ui vs raw HTML), typography, empty states, responsive at 375px, dark mode contrast.

Visual findings reported as QA findings with screenshots and severity. Cross-references product standards: if the plan said shadcn/ui and the output looks like raw HTML, that's a finding.

## Context

Ran autopilot on a real project (expense splitter). The app worked functionally but had layout imbalance, inconsistent spacing and raw-looking components. QA passed because it only tested functionality. Visual QA closes this gap.

## Test plan

- [ ] Run `/qa` on a web app and verify screenshots are taken
- [ ] Verify visual findings appear in QA output with severity and screenshot references
- [ ] Verify Mode Summary table shows Visual QA row

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
