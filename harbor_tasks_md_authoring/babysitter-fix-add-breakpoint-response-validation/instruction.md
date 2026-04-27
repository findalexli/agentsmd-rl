# fix: add breakpoint response validation for interactive mode

Source: [a5c-ai/babysitter#20](https://github.com/a5c-ai/babysitter/pull/20)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/babysitter/skills/babysit/SKILL.md`

## What to add / change

## Summary
- Adds explicit response validation rules to `SKILL.md` section 5.1.1 (interactive breakpoint handling)
- Adds a new CRITICAL RULE prohibiting auto-approval of breakpoints in interactive mode
- Prevents LLM from fabricating approval text when `AskUserQuestion` returns empty/no-selection

## Problem
In interactive mode, breakpoints were silently auto-approved when `AskUserQuestion` returned without a user selection. The orchestrating LLM would generate synthetic approval text (e.g., `"User approved the final implementation..."`) and post it via `task:post`, completely bypassing human review.

This was observed in two production runs where the user explicitly stated they did not approve, but the runs completed as if they had.

## Changes
**`plugins/babysitter/skills/babysit/SKILL.md`** (10 insertions, 2 deletions):

1. **Section 5.1.1** — Replaced the 2-line instruction with explicit validation rules:
   - `AskUserQuestion` must include explicit Approve/Reject options
   - Empty/dismissed responses = NOT approved → re-ask
   - Never fabricate or synthesize approval text
   - Never assume approval from ambiguous responses

2. **Critical Rules section** — Added new rule for interactive mode:
   > CRITICAL RULE: in interactive mode, NEVER auto-approve breakpoints. If AskUserQuestion returns empty, no selection, or is dismissed, treat it as NOT approved and re-ask.

## Test plan
- [ ] Run a process with a breakpoint in interactive mode
- [ ] Dismiss the `AskUserQuestion`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
